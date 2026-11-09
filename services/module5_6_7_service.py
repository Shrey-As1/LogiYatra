"""Unified Logistics Intelligence Orchestration Service.

Bridges the 7 modules into an end-to-end operational pipeline:
Supply Chain Inputs -> Predictions (M1, M2, M4) -> Inventory (M5) -> Decision (M6)
-> Route Evaluation (M3) -> Explanation & What-If (M7) -> Human Review.
"""
from __future__ import annotations

from typing import Any, Dict, Optional
from services.module1_service import Module1Service
from services.module2_service import Module2Service
from services.module4_service import Module4Service
from services.module7_service import Module7Service
from ml_training.Module_5_Inventory_Optimization.inventory_optimizer import optimize_inventory
from ml_training.Module_6_Decision_Engine.decision_engine import DecisionEngine


class PipelineService:
    _instance: Optional[PipelineService] = None

    def __init__(self):
        self.m1 = Module1Service.get_instance()
        self.m2 = Module2Service.get_instance()
        self.m4 = Module4Service.get_instance()
        self.m7 = Module7Service.get_instance()
        self.decision_engine = DecisionEngine()

    @classmethod
    def get_instance(cls) -> PipelineService:
        if cls._instance is None:
            cls._instance = PipelineService()
        return cls._instance

    def run_pipeline(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Executes the connected 7-module logistics intelligence workflow."""
        results: Dict[str, Any] = {
            "pipeline_status": "COMPLETED",
            "modules_executed": []
        }

        # Step 1: Module 1 Demand Forecast
        demand_forecast = None
        if "module1" in payload or "demand_inputs" in payload:
            m1_inputs = payload.get("module1", payload.get("demand_inputs", {}))
            try:
                demand_forecast = self.m1.predict(m1_inputs)
                results["module1_demand"] = demand_forecast
                results["modules_executed"].append(1)
            except Exception as exc:
                results["module1_error"] = str(exc)

        # Step 2: Module 2 Delivery Delay Risk
        delivery_risk = None
        if "module2" in payload or "delivery_inputs" in payload:
            m2_inputs = payload.get("module2", payload.get("delivery_inputs", {}))
            try:
                delivery_result = self.m2.predict(m2_inputs)
                delivery_risk = delivery_result["delay_probability"]
                results["module2_delivery"] = delivery_result
                results["modules_executed"].append(2)
            except Exception as exc:
                results["module2_error"] = str(exc)

        # Step 3: Module 4 Warehouse Congestion Risk
        congestion_risk = None
        if "module4" in payload or "warehouse_observations" in payload:
            obs = payload.get("module4", {}).get("observations", payload.get("warehouse_observations"))
            if isinstance(obs, list) and len(obs) >= 12:
                try:
                    congestion_result = self.m4.predict(obs)
                    congestion_risk = congestion_result["congestion_risk"]
                    results["module4_warehouse"] = congestion_result
                    results["modules_executed"].append(4)
                except Exception as exc:
                    results["module4_error"] = str(exc)

        # Step 4: Module 5 Inventory Optimization (feeds from Module 1 if available)
        inventory_result = None
        m5_inputs = payload.get("module5", payload.get("inventory_inputs", {})).copy()
        if demand_forecast and "forecast_daily_demand" not in m5_inputs:
            m5_inputs["forecast_daily_demand"] = demand_forecast["forecast_daily_demand"]
            m5_inputs["forecast_source"] = "module1_forecast_automated"

        if "current_stock" in m5_inputs and "lead_time_days" in m5_inputs:
            try:
                inventory_result = optimize_inventory(m5_inputs)
                results["module5_inventory"] = inventory_result
                results["modules_executed"].append(5)
            except Exception as exc:
                results["module5_error"] = str(exc)

        # Step 5: Route alternatives (Module 3 placeholder or passed from frontend)
        route_alternatives = payload.get("route_alternatives")
        route_risk = payload.get("route_risk", 0.15)
        if route_alternatives:
            results["modules_executed"].append(3)

        # Step 6: Module 6 Autonomous Decision Engine
        decision = self.decision_engine.evaluate(
            delay_risk=delivery_risk,
            congestion_risk=congestion_risk,
            route_risk=route_risk,
            inventory_status=inventory_result["status"] if inventory_result else None,
            route_alternatives=route_alternatives,
            inventory_result=inventory_result
        )
        results["module6_decision"] = decision
        results["modules_executed"].append(6)

        # Step 7: Module 7 Decision Explanation
        explanation = self.m7.explain_decision(decision)
        results["module7_explanation"] = explanation
        results["modules_executed"].append(7)

        return results
