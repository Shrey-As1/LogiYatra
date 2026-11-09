"""Rule-based inventory optimizer for LogiYantra Module 5.

This is a transparent, deterministic operations research baseline that consumes
a daily demand forecast (from Module 1 or user-specified) and replenishment parameters.
It calculates safety stock, reorder point (ROP), target stock, and pack-aligned order quantity.
"""
from __future__ import annotations

from typing import Any, Dict, Optional


def optimize_inventory(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Calculates replenishment metrics and recommended order quantity."""
    # Check for demand source (accept forecast_daily_demand, daily_demand, dailyDemand)
    demand_val = payload.get("forecast_daily_demand")
    if demand_val is None:
        demand_val = payload.get("daily_demand")
    if demand_val is None:
        demand_val = payload.get("dailyDemand")
    demand_source = payload.get("forecast_source", "user_specified")

    if demand_val is None:
        # Check if weekly demand was passed
        weekly = payload.get("forecast_weekly_demand") or payload.get("weekly_demand")
        if weekly is not None:
            try:
                demand_val = float(weekly) / 7.0
                demand_source = "module1_forecast_weekly_converted"
            except (ValueError, TypeError):
                pass

    if demand_val is None:
        raise ValueError("Missing required field: forecast_daily_demand (or forecast_weekly_demand).")

    if "current_stock" not in payload and "currentStock" not in payload:
        raise ValueError("Missing required field: current_stock.")
    lead_time_val = payload.get("lead_time_days")
    if lead_time_val is None:
        lead_time_val = payload.get("lead_time")
    if lead_time_val is None:
        lead_time_val = payload.get("leadTimeDays")
    if lead_time_val is None:
        raise ValueError("Missing required field: lead_time_days.")

    try:
        stock = float(payload.get("current_stock", payload.get("currentStock")))
        demand = float(demand_val)
        lead_time = float(lead_time_val)
        safety_days = float(payload.get("safety_stock_days", payload.get("safety_days", payload.get("safetyDays", 3.0))))
        review_days = float(payload.get("review_period_days", payload.get("review_days", payload.get("reviewDays", 7.0))))
        pack_size = float(payload.get("pack_size", payload.get("packSize", 1.0)))
        holding_cost = float(payload.get("holding_cost_per_unit", 1.5))
        stockout_cost = float(payload.get("stockout_cost_per_unit", 25.0))
    except (ValueError, TypeError) as exc:
        raise ValueError(f"All inventory numeric parameters must be valid numbers: {exc}")

    if stock < 0:
        raise ValueError("current_stock cannot be negative.")
    if demand < 0:
        raise ValueError("forecast_daily_demand cannot be negative.")
    if lead_time < 0:
        raise ValueError("lead_time_days cannot be negative.")
    if safety_days < 0:
        raise ValueError("safety_stock_days cannot be negative.")
    if review_days < 0:
        raise ValueError("review_period_days cannot be negative.")
    if pack_size <= 0:
        raise ValueError("pack_size must be greater than zero.")

    safety_stock = demand * safety_days
    reorder_point = demand * lead_time + safety_stock
    target_stock = demand * (lead_time + safety_days + review_days)

    # Replenishment calculation
    if stock <= reorder_point:
        raw_reorder_qty = max(0.0, target_stock - stock)
        # Round up to next full multiple of pack_size
        reorder_qty = int(((raw_reorder_qty + pack_size - 1e-9) // pack_size) * pack_size)
    else:
        reorder_qty = 0

    # Categorize inventory status
    if stock <= safety_stock:
        status = "CRITICAL_REPLENISH"
        recommendation = "CRITICAL: Stock is at or below safety buffer. Trigger urgent replenishment order immediately."
    elif stock <= reorder_point:
        status = "REPLENISH"
        recommendation = f"ACTION: Stock has breached reorder point ({round(reorder_point, 1)} units). Place standard replenishment order."
    else:
        status = "HEALTHY"
        recommendation = f"NORMAL: Stock ({round(stock, 1)} units) is above reorder point ({round(reorder_point, 1)} units). No order required."

    # Days of supply currently on hand
    days_of_supply = round(stock / demand, 1) if demand > 0 else 999.0

    return {
        "status": status,
        "current_stock": round(stock, 2),
        "forecast_daily_demand": round(demand, 2),
        "lead_time_days": round(lead_time, 2),
        "safety_stock_days": round(safety_days, 1),
        "safety_stock_units": round(safety_stock, 2),
        "reorder_point": round(reorder_point, 2),
        "target_stock": round(target_stock, 2),
        "recommended_order_quantity": int(reorder_qty),
        "order_quantity": int(reorder_qty),
        "needs_replenishment": status in ("CRITICAL_REPLENISH", "REPLENISH"),
        "safety_stock": round(safety_stock, 2),
        "policy": "s,S Continuous Review",
        "days_of_supply": days_of_supply,
        "pack_size": int(pack_size),
        "forecast_source": demand_source,
        "recommendation": recommendation,
        "method": "Continuous review (s, S) policy with safety stock buffer and integer pack rounding",
        "assumptions": [
            f"Lead time demand estimated at {round(demand * lead_time, 1)} units.",
            f"Safety buffer sized for {safety_days} days of demand ({round(safety_stock, 1)} units).",
            f"Orders aligned to pack multiple of {int(pack_size)} units.",
        ]
    }
