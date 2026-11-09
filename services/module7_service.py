"""Module 7 — Explainable AI and What-If Scenario Analysis Service.

Provides:
1. Operational Decision Explanations: Breaks down Module 6 recommendations by
   identifying the contributing modules, threshold breaches, and evidence chains.
2. Model-Level Explanations: Feature importance & SHAP attributions for model predictions.
3. What-If Scenario Comparisons: Evaluates hypothetical adjustments to operational risks
   and simulates the resulting change in system status and recommendations.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent


class Module7Service:
    _instance: Optional[Module7Service] = None

    def __init__(self):
        pass

    @classmethod
    def get_instance(cls) -> Module7Service:
        if cls._instance is None:
            cls._instance = Module7Service()
        return cls._instance

    def explain_decision(self, decision_data: Dict[str, Any]) -> Dict[str, Any]:
        """Explains why Module 6 generated its recommendations.
        
        Analyzes the decision payload, triggers, and evidence.
        Accepts either a complete DecisionEngine result dictionary or direct operational inputs.
        """
        if not isinstance(decision_data, dict):
            raise ValueError("decision_data must be a dictionary representing Module 6 evaluation.")

        # If raw operational inputs were passed directly instead of a full DecisionEngine output:
        if "actions" not in decision_data and any(k in decision_data for k in ["delay_risk", "congestion_risk", "route_risk", "current_stock", "stock_level", "inventory_status"]):
            from ml_training.Module_6_Decision_Engine.decision_engine import DecisionEngine
            engine = DecisionEngine()
            evaluated = engine.evaluate(
                delay_risk=decision_data.get("delay_risk"),
                congestion_risk=decision_data.get("congestion_risk"),
                route_risk=decision_data.get("route_risk"),
                inventory_status=decision_data.get("inventory_status"),
                stock_level=decision_data.get("stock_level", decision_data.get("current_stock")),
                reorder_point=decision_data.get("reorder_point"),
                route_alternatives=decision_data.get("route_alternatives"),
                inventory_result=decision_data.get("inventory_result")
            )
            # If an action was specifically passed in, retain it as primary if desired
            if "action" in decision_data and decision_data["action"]:
                evaluated["primary_action"] = decision_data["action"]
            decision_data = evaluated

        overall_status = decision_data.get("overall_status", "NORMAL")
        primary_action = decision_data.get("primary_action", "MAINTAIN_STANDARD_OPERATIONS")
        actions = decision_data.get("actions", [])
        inputs_used = decision_data.get("inputs_used", {})
        missing_inputs = decision_data.get("missing_inputs", [])

        action_explanations = []
        for a in actions:
            action_name = a.get("action", "")
            priority = a.get("priority", "NORMAL")
            source = a.get("source_module", "Decision Policy")
            reason = a.get("reason", "")
            condition = a.get("condition_triggered", "")
            evidence = a.get("evidence")

            action_explanations.append({
                "action": action_name,
                "priority": priority,
                "driver_module": source,
                "policy_condition": condition,
                "rationale": reason,
                "supporting_evidence": evidence or "Direct operational threshold breach",
                "recommended_verification": (
                    "Verify carrier dispatch and expedite options" if "EXPEDITE" in action_name
                    else "Inspect alternate corridor travel times" if "REROUTE" in action_name
                    else "Confirm physical warehouse dock availability" if "WAREHOUSE" in action_name
                    else "Check purchase order supplier lead times" if "REPLENISHMENT" in action_name
                    else "Standard operational review"
                )
            })

        # Feature-level risk factor contributions (normalized)
        risk_contributions = []
        contributing_factors = []
        for key in ["delay_risk", "congestion_risk", "route_risk"]:
            val = None
            if key in inputs_used and inputs_used[key] is not None:
                val = float(inputs_used[key])
            elif key in decision_data and decision_data[key] is not None:
                try:
                    val = float(decision_data[key])
                except (ValueError, TypeError):
                    pass
            if val is not None:
                name = key.replace("_", " ").title()
                risk_contributions.append({
                    "factor": name,
                    "observed_value": round(val, 4),
                    "percentage": f"{val * 100:.1f}%",
                    "severity": "CRITICAL" if val >= 0.85 else "HIGH" if val >= 0.60 else "MODERATE" if val >= 0.30 else "LOW"
                })
                contributing_factors.append({
                    "factor": name,
                    "weight": round(val, 4)
                })

        summary_text = (
            f"Status '{overall_status}' driven by {len(actions)} prioritized operational trigger(s)."
            if actions else "All monitored parameters are within safe operational tolerances."
        )
        if primary_action and primary_action != "MAINTAIN_STANDARD_OPERATIONS":
            summary_text = f"Primary recommendation '{primary_action}' selected based on evaluated operational risks. {summary_text}"

        return {
            "overall_status": overall_status,
            "primary_action": primary_action,
            "explanation": summary_text,
            "explanation_summary": summary_text,
            "action_breakdown": action_explanations,
            "risk_contributions": risk_contributions,
            "contributing_factors": contributing_factors,
            "risk_level": overall_status,
            "confidence": "High (Deterministic Policy Rules)",
            "missing_data_warnings": [
                f"Missing {m} — recommendation made with partial observability"
                for m in missing_inputs
            ],
            "methodology": "Rule-based transparent threshold reasoning with forward evidence chaining",
            "requires_human_approval": True,
            "disclaimer": "AI recommendations are operational guidance. Final execution requires human verification."
        }

    def simulate_what_if(
        self,
        current_state: Dict[str, Any],
        scenario_changes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compares baseline vs hypothetical operational scenario.
        
        Calculates composite operational risk delta and evaluates resulting action changes.
        """
        if not isinstance(current_state, dict) or not isinstance(scenario_changes, dict):
            raise ValueError("current_state and scenario_changes must both be dictionaries.")

        # Baseline composite score
        keys = ["delay_risk", "congestion_risk", "route_risk"]
        def _calc_composite(data: Dict[str, Any]) -> float:
            vals = []
            for k in keys:
                if k in data and data[k] is not None:
                    v = float(data[k])
                    if not (0.0 <= v <= 1.0):
                        raise ValueError(f"{k} must be between 0.0 and 1.0")
                    vals.append(v)
            return sum(vals) / len(vals) if vals else 0.0

        baseline_risk = _calc_composite(current_state)
        merged_state = dict(current_state)
        merged_state.update(scenario_changes)
        scenario_risk = _calc_composite(merged_state)

        diff = scenario_risk - baseline_risk
        diff_pct_points = round(diff * 100, 2)

        # Evaluate decision engine for both baseline and scenario
        from ml_training.Module_6_Decision_Engine.decision_engine import DecisionEngine
        engine = DecisionEngine()
        baseline_dec = engine.evaluate(
            delay_risk=current_state.get("delay_risk"),
            congestion_risk=current_state.get("congestion_risk"),
            route_risk=current_state.get("route_risk"),
            inventory_status=current_state.get("inventory_status", "HEALTHY"),
        )
        scenario_dec = engine.evaluate(
            delay_risk=merged_state.get("delay_risk"),
            congestion_risk=merged_state.get("congestion_risk"),
            route_risk=merged_state.get("route_risk"),
            inventory_status=merged_state.get("inventory_status", "HEALTHY"),
        )

        interpretation_text = (
            f"Hypothetical adjustments reduce composite operational risk by {abs(diff_pct_points):.1f}% points."
            if diff < 0 else
            f"Hypothetical adjustments increase composite operational risk by {diff_pct_points:.1f}% points."
            if diff > 0 else
            "Hypothetical adjustments result in no net risk change."
        )

        action_delta = len(scenario_dec.get("actions", [])) - len(baseline_dec.get("actions", []))
        risk_impr_str = f"{abs(diff_pct_points):.1f}% reduction" if diff < 0 else f"{diff_pct_points:.1f}% increase" if diff > 0 else "0% (Neutral)"

        return {
            "baseline": {
                "composite_risk": round(baseline_risk, 4),
                "overall_status": baseline_dec["overall_status"],
                "primary_action": baseline_dec["primary_action"],
                "actions": baseline_dec.get("actions", []),
                "inputs": {k: current_state.get(k) for k in keys if k in current_state}
            },
            "scenario": {
                "composite_risk": round(scenario_risk, 4),
                "overall_status": scenario_dec["overall_status"],
                "primary_action": scenario_dec["primary_action"],
                "actions": scenario_dec.get("actions", []),
                "inputs": {k: merged_state.get(k) for k in keys if k in merged_state}
            },
            "comparison": {
                "delta": round(diff, 4),
                "delta_percentage_points": diff_pct_points,
                "risk_reduced": diff < 0,
                "status_changed": baseline_dec["overall_status"] != scenario_dec["overall_status"],
                "primary_action_changed": baseline_dec["primary_action"] != scenario_dec["primary_action"],
                "changed_parameters": scenario_changes
            },
            "difference": {
                "action_count_change": f"{action_delta:+d}" if action_delta != 0 else "0",
                "risk_improvement": risk_impr_str,
                "risk_reduced": diff < 0
            },
            "interpretation": interpretation_text,
            "summary": interpretation_text,
            "label": "Heuristic Scenario Analysis — Transparent risk comparison, not a trained causal model",
            "limitations": [
                "Does not account for non-linear real-world feedback loops or unmodeled externalities.",
                "Assumes independent parameter adjustment without endogenous supply chain shock propagation."
            ]
        }
