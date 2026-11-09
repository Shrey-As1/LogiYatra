"""Autonomous Decision Engine for LogiYantra (Module 6).

Consolidates operational predictions from Module 2 (Delivery Delay), Module 3 (Route Alternatives),
Module 4 (Warehouse Congestion), and Module 5 (Inventory Optimization).
Applies configurable policy thresholds to generate prioritized, explainable operational recommendations.
All proposed actions require human verification before execution.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class Action:
    action: str
    priority: str          # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    score: float
    reason: str
    source_module: str     # "Module 2", "Module 3", "Module 4", "Module 5"
    condition_triggered: str
    evidence: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DecisionEngine:
    DEFAULT_POLICIES = {
        "delay_high": 0.70,
        "delay_critical": 0.85,
        "congestion_high": 0.60,
        "congestion_critical": 0.85,
        "route_high": 0.60,
        "route_critical": 0.85,
    }

    def __init__(self, policies: Optional[Dict[str, Any]] = None):
        self.p = dict(self.DEFAULT_POLICIES)
        if policies:
            for k, v in policies.items():
                if isinstance(v, (int, float)):
                    self.p[k] = float(v)

    @staticmethod
    def _validate_prob(name: str, value: Any) -> Optional[float]:
        if value is None:
            return None
        try:
            val = float(value)
        except (ValueError, TypeError):
            raise ValueError(f"{name} must be a valid numeric probability, got {value}")
        if not (0.0 <= val <= 1.0):
            raise ValueError(f"{name} must be between 0.0 and 1.0, got {val}")
        return val

    def evaluate(
        self,
        delay_risk: Optional[float] = None,
        congestion_risk: Optional[float] = None,
        route_risk: Optional[float] = None,
        inventory_status: Optional[str] = None,
        stock_level: Optional[float] = None,
        reorder_point: Optional[float] = None,
        route_alternatives: Optional[List[Dict[str, Any]]] = None,
        inventory_result: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Evaluates operational status and prioritizes recommendations."""
        delay = self._validate_prob("delay_risk", delay_risk)
        congestion = self._validate_prob("congestion_risk", congestion_risk)
        route = self._validate_prob("route_risk", route_risk)

        inputs_used: Dict[str, Any] = {}
        missing_inputs: List[str] = []

        if delay is not None:
            inputs_used["delay_risk"] = delay
        else:
            missing_inputs.append("delay_risk (Module 2)")

        if congestion is not None:
            inputs_used["congestion_risk"] = congestion
        else:
            missing_inputs.append("congestion_risk (Module 4)")

        if route is not None:
            inputs_used["route_risk"] = route
        else:
            missing_inputs.append("route_risk (Module 3)")

        if inventory_status is not None:
            inputs_used["inventory_status"] = str(inventory_status).upper()
        elif inventory_result and "status" in inventory_result:
            inventory_status = str(inventory_result["status"]).upper()
            inputs_used["inventory_status"] = inventory_status
        else:
            inventory_status = "HEALTHY"
            missing_inputs.append("inventory_status (Module 5)")

        actions: List[Action] = []
        reasons: List[str] = []

        # -------------------------------------------------------------
        # 1. DELIVERY DELAY EVALUATION (Module 2)
        # -------------------------------------------------------------
        if delay is not None:
            if delay >= self.p["delay_critical"]:
                msg = f"Delivery delay probability is {delay:.1%}, breaching critical threshold ({self.p['delay_critical']:.1%})."
                actions.append(Action(
                    action="EXPEDITE_AND_NOTIFY",
                    priority="CRITICAL",
                    score=delay,
                    reason=msg,
                    source_module="Module 2 (Delivery Delay)",
                    condition_triggered=f"delay_risk >= {self.p['delay_critical']:.2f}"
                ))
                reasons.append(msg)
            elif delay >= self.p["delay_high"]:
                msg = f"Delivery delay probability is {delay:.1%}, exceeding alert threshold ({self.p['delay_high']:.1%})."
                actions.append(Action(
                    action="NOTIFY_CUSTOMER",
                    priority="HIGH",
                    score=delay,
                    reason=msg,
                    source_module="Module 2 (Delivery Delay)",
                    condition_triggered=f"delay_risk >= {self.p['delay_high']:.2f}"
                ))
                reasons.append(msg)

        # -------------------------------------------------------------
        # 2. ROUTE & TRAFFIC EVALUATION (Module 3)
        # -------------------------------------------------------------
        if route is not None:
            route_evidence = None
            if route_alternatives:
                # Find best alternative with lowest risk score
                candidates = sorted(route_alternatives, key=lambda r: r.get("route_risk_score", 1.0))
                if candidates:
                    route_evidence = {
                        "alternatives_count": len(route_alternatives),
                        "suggested_alternate_route": candidates[0].get("name", "Alternate Corridor"),
                        "estimated_alternate_time": candidates[0].get("estimated_time_minutes"),
                        "alternate_risk": candidates[0].get("route_risk_score")
                    }

            if route >= self.p["route_critical"]:
                msg = f"Transit route risk is {route:.1%}, indicating severe bottleneck or blockage."
                actions.append(Action(
                    action="REROUTE_SHIPMENT",
                    priority="CRITICAL",
                    score=route,
                    reason=msg,
                    source_module="Module 3 (Route Optimization)",
                    condition_triggered=f"route_risk >= {self.p['route_critical']:.2f}",
                    evidence=route_evidence
                ))
                reasons.append(msg)
            elif route >= self.p["route_high"]:
                msg = f"Transit route risk is {route:.1%}, indicating heavy congestion ahead."
                actions.append(Action(
                    action="REVIEW_ALTERNATIVE_ROUTE",
                    priority="HIGH",
                    score=route,
                    reason=msg,
                    source_module="Module 3 (Route Optimization)",
                    condition_triggered=f"route_risk >= {self.p['route_high']:.2f}",
                    evidence=route_evidence
                ))
                reasons.append(msg)

        # -------------------------------------------------------------
        # 3. WAREHOUSE CONGESTION EVALUATION (Module 4)
        # -------------------------------------------------------------
        if congestion is not None:
            if congestion >= self.p["congestion_critical"]:
                msg = f"Warehouse congestion probability is {congestion:.1%}, threatening dock lockup."
                actions.append(Action(
                    action="RESCHEDULE_WAREHOUSE_FLOW",
                    priority="CRITICAL",
                    score=congestion,
                    reason=msg,
                    source_module="Module 4 (Warehouse Congestion)",
                    condition_triggered=f"congestion_risk >= {self.p['congestion_critical']:.2f}"
                ))
                reasons.append(msg)
            elif congestion >= self.p["congestion_high"]:
                msg = f"Warehouse congestion probability is {congestion:.1%}, above target threshold."
                actions.append(Action(
                    action="RESCHEDULE_WAREHOUSE_FLOW",
                    priority="HIGH",
                    score=congestion,
                    reason=msg,
                    source_module="Module 4 (Warehouse Congestion)",
                    condition_triggered=f"congestion_risk >= {self.p['congestion_high']:.2f}"
                ))
                reasons.append(msg)

        # -------------------------------------------------------------
        # 4. INVENTORY REPLENISHMENT EVALUATION (Module 5)
        # -------------------------------------------------------------
        inv_stat = str(inventory_status or "HEALTHY").upper()
        if inv_stat == "CRITICAL_REPLENISH":
            msg = "Inventory level is at or below safety stock buffer. Immediate replenishment required."
            actions.append(Action(
                action="TRIGGER_REPLENISHMENT",
                priority="CRITICAL",
                score=1.0,
                reason=msg,
                source_module="Module 5 (Inventory Optimization)",
                condition_triggered="inventory_status == CRITICAL_REPLENISH",
                evidence=inventory_result
            ))
            reasons.append(msg)
        elif inv_stat == "REPLENISH":
            msg = "Inventory has breached reorder point. Standard replenishment order recommended."
            actions.append(Action(
                action="TRIGGER_REPLENISHMENT",
                priority="HIGH",
                score=0.8,
                reason=msg,
                source_module="Module 5 (Inventory Optimization)",
                condition_triggered="inventory_status == REPLENISH",
                evidence=inventory_result
            ))
            reasons.append(msg)

        # Direct stock check if provided
        if stock_level is not None and reorder_point is not None:
            inputs_used["stock_level"] = float(stock_level)
            inputs_used["reorder_point"] = float(reorder_point)
            if float(stock_level) <= float(reorder_point):
                if not any("REPLENISHMENT" in a.action for a in actions):
                    msg = f"Stock level ({stock_level}) is below reorder point ({reorder_point})."
                    actions.append(Action(
                        action="TRIGGER_REPLENISHMENT",
                        priority="HIGH",
                        score=0.75,
                        reason=msg,
                        source_module="Module 5 (Inventory Optimization)",
                        condition_triggered="stock_level <= reorder_point"
                    ))
                    reasons.append(msg)

        # -------------------------------------------------------------
        # DEDUPLICATION & PRIORITY SORTING
        # -------------------------------------------------------------
        # Deduplicate actions with identical action string, keeping highest priority
        rank_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        unique_actions: Dict[str, Action] = {}
        for a in actions:
            if a.action not in unique_actions:
                unique_actions[a.action] = a
            else:
                existing = unique_actions[a.action]
                if rank_order[a.priority] < rank_order[existing.priority]:
                    unique_actions[a.action] = a
                elif rank_order[a.priority] == rank_order[existing.priority] and a.score > existing.score:
                    unique_actions[a.action] = a

        sorted_actions = sorted(
            unique_actions.values(),
            key=lambda a: (rank_order[a.priority], -a.score)
        )

        if any(a.priority == "CRITICAL" for a in sorted_actions):
            overall_status = "CRITICAL"
        elif any(a.priority == "HIGH" for a in sorted_actions):
            overall_status = "HIGH"
        elif sorted_actions:
            overall_status = "MODERATE"
        else:
            overall_status = "NORMAL"

        primary = sorted_actions[0].action if sorted_actions else "MAINTAIN_STANDARD_OPERATIONS"

        return {
            "overall_status": overall_status,
            "primary_action": primary,
            "actions": [a.to_dict() for a in sorted_actions],
            "reasons": reasons if reasons else ["All evaluated logistics metrics are within normal operational thresholds."],
            "inputs_used": inputs_used,
            "missing_inputs": missing_inputs,
            "requires_human_approval": True,
            "status_description": (
                "Proposed recommendations require human verification before operational execution."
            )
        }