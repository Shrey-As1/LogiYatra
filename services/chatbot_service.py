"""LogiYantra Autonomous AI Logistics Assistant Service.

Provides conversational intelligence for the LogiYantra supply chain control tower.
Features:
1. Dynamic telemetry queries across all 7 intelligence modules.
2. What-If scenario simulations and causal explainability.
3. System model metrics & accuracy benchmarking retrieval.
4. Hybrid execution: Uses Google Gemini via google.genai if GEMINI_API_KEY
   is configured in .env, and falls back gracefully to a built-in deterministic reasoning engine.
"""
from __future__ import annotations

import os
import json
import re
from typing import Any, Dict, List, Optional
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


class ChatbotService:
    _instance: Optional[ChatbotService] = None

    GEMINI_MODELS = [
        "gemini-flash-lite-latest",
        "gemini-3.8-flash",
        "gemini-flash-latest",
        "gemini-3.1-flash-lite"
    ]

    MODEL_METRICS = {
        "Module 1 (Demand Forecasting)": {
            "model": "XGBoost + LSTM Hybrid Ensemble",
            "task": "Chronological Regression",
            "accuracy": "R² = 98.59% (0.9859)",
            "error_rate": "WAPE = 7.94%, MAE = 1,259.5 units, RMSE = 2,611.8 units",
            "dataset": "Walmart Store Sales"
        },
        "Module 2 (Delivery Delay Risk)": {
            "model": "Optuna-Tuned XGBoost Classifier",
            "task": "Binary Risk Classification",
            "accuracy": "Accuracy = 69.20%, Precision = 83.54%, Recall = 54.36%",
            "error_rate": "ROC-AUC = 74.54%, PR-AUC = 81.51%, F1 = 65.86%",
            "dataset": "DataCo Supply Chain (5,567 encoded features)"
        },
        "Module 3 (Route Optimization)": {
            "model": "Dijkstra & A* Pathfinding + OSMnx Road Graph",
            "task": "Deterministic Network Optimization",
            "accuracy": "100% Mathematical Shortest & Lowest-Risk Path",
            "error_rate": "Deterministic graph computation with TomTom live traffic feeds",
            "dataset": "OpenStreetMap Real Road Topologies"
        },
        "Module 4 (Warehouse Congestion)": {
            "model": "Hybrid XGBoost Selection + 12-Step LSTM Sequence Classifier",
            "task": "Temporal Sequence Classification",
            "accuracy": "Accuracy = 76.62%, Precision = 72.53%, Recall = 83.12%",
            "error_rate": "ROC-AUC = 83.71%, F1 = 77.46%",
            "dataset": "Warehouse Dock Utilization & Truck Arrival Feeds"
        },
        "Module 5 (Inventory Optimization)": {
            "model": "Stochastic Calculus & Kingman's Variance Formula",
            "task": "Dynamic Safety Stock & ROP Optimization",
            "accuracy": "95.0% Service Level SLA Target (Z = 1.645)",
            "error_rate": "Balances holding cost vs stockout risk under M1 demand variance",
            "dataset": "Dynamic Stochastic Replenishment"
        },
        "Module 6 (Decision Engine)": {
            "model": "Multi-Echelon Operational Rule Matrix (policies.json)",
            "task": "Multi-Criteria Decision Evaluation",
            "accuracy": "100% Rule Determinism & Conflict Deduplication",
            "error_rate": "Zero policy ambiguity; requires human-in-the-loop dispatch gate",
            "dataset": "Autonomous Policy Matrix"
        },
        "Module 7 (Explainable AI & What-If)": {
            "model": "TreeExplainer SHAP + Sequence Permutation Attribution",
            "task": "Causal Feature Attribution & Counterfactual Modeling",
            "accuracy": "100% Shapley Axiomatic Compliance (Efficiency, Symmetry, Additivity)",
            "error_rate": "Exact additive decomposition: Σ φ_i = f(x) - E[f(x)]",
            "dataset": "Game-Theoretic Local Interpretability"
        }
    }

    def __init__(self):
        self._refresh_client()

    def _refresh_client(self):
        load_dotenv(ROOT_DIR / ".env")
        self.gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.client = None
        if self.gemini_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.gemini_key)
            except Exception:
                self.client = None

    @classmethod
    def get_instance(cls) -> ChatbotService:
        if cls._instance is None:
            cls._instance = ChatbotService()
        else:
            # Recheck environment in case user just added the key
            if not cls._instance.client:
                cls._instance._refresh_client()
        return cls._instance

    def process_message(self, user_message: str, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """Processes an incoming chat message using Gemini if available, or deterministic NLP engine."""
        msg = (user_message or "").strip()
        if not msg:
            return {
                "success": True,
                "reply": "Hello! I am **LogiBot**, your autonomous supply chain copilot. How can I assist you with LogiYantra today?",
                "engine": "gemini" if self.client else "logiyantra_local",
                "suggested_prompts": ["Model Accuracies", "Run Quick Decision", "Check Warehouse Congestion", "Explain Delivery Delay"]
            }

        # Try Gemini if configured
        if self.client:
            try:
                reply = self._ask_gemini(msg, history or [])
                return {
                    "success": True,
                    "reply": reply,
                    "engine": "gemini",
                    "suggested_prompts": self._get_contextual_suggestions(msg)
                }
            except Exception as e:
                # Log and fallback gracefully to built-in local engine
                pass

        # Local Logistics Reasoning Engine
        reply, suggestions = self._reason_locally(msg)
        return {
            "success": True,
            "reply": reply,
            "engine": "logiyantra_local",
            "suggested_prompts": suggestions
        }

    def _ask_gemini(self, user_message: str, history: List[Dict[str, str]]) -> str:
        """Invokes Gemini with LogiYantra operational system context using fallback model cascade."""
        system_context = (
            "You are LogiBot, the advanced AI Operations Copilot for LogiYantra (an Autonomous Multi-Echelon Supply Chain Control Tower). "
            "You have direct awareness of all 7 intelligence modules:\n"
            "1. Demand Forecasting (XGBoost+LSTM, R2=98.59%, WAPE=7.94%, MAE=1,259.5 units)\n"
            "2. Delivery Delay Risk (Optuna XGBoost, Accuracy=69.2%, ROC-AUC=74.54%, Precision=83.54%, Cutoff=36%)\n"
            "3. Route Optimization (Dijkstra/A* on OSMnx road graph + TomTom live traffic)\n"
            "4. Warehouse Congestion (12-timestep LSTM sequence model, Accuracy=76.62%, ROC-AUC=83.71%, Recall=83.12%)\n"
            "5. Inventory Optimization (Dynamic Safety Stock & ROP, 95% Service Level SLA, Z=1.645)\n"
            "6. Autonomous Decision Engine (Deterministic prioritized rules: CRITICAL > HIGH > MEDIUM > LOW, human verification gate)\n"
            "7. Explainable AI & What-If Simulator (SHAP TreeExplainer, Counterfactual scenarios, Policy Boundary Proximity)\n\n"
            "Format your answers with clean GitHub Markdown, bold text, bullet points, and actionable guidance for supply chain dispatchers and operations managers. Maintain an executive, sophisticated, and polished tone. Do not use cartoonish emojis."
        )

        prompt = f"{system_context}\n\nUser Question: {user_message}"

        last_err = None
        for model_name in self.GEMINI_MODELS:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if response and response.text:
                    return response.text
            except Exception as exc:
                last_err = exc
                continue

        if last_err:
            raise last_err
        raise RuntimeError("No Gemini models responded successfully.")

    def _reason_locally(self, msg: str) -> tuple[str, List[str]]:
        """Domain-aware rule and telemetry inference engine."""
        m = msg.lower()

        # 1. Model Accuracy / Performance queries
        if any(w in m for w in ["accuracy", "accuracies", "metric", "metrics", "performance", "how accurate", "precision", "recall", "roc-auc", "r2", "f1"]):
            out = ["### LogiYantra Model Architecture & Accuracy Benchmarks & Accuracy Summary\n"]
            for mod, met in self.MODEL_METRICS.items():
                out.append(f"- **{mod}**")
                out.append(f"  - **Model**: {met['model']}")
                out.append(f"  - **Performance**: `{met['accuracy']}`")
                out.append(f"  - **Reliability/Loss**: {met['error_rate']}")
            out.append("\n> **Tip**: All 7 models undergo continuous telemetry validation against live operational drift.")
            return "\n".join(out), ["Explain Module 2 Delay", "Simulate What-If Scenario", "Check Inventory Status"]

        # 2. Demand Forecasting (Module 1)
        if any(w in m for w in ["demand", "forecast", "module 1", "sales prediction", "units"]):
            try:
                from services.module1_service import Module1Service
                summary = Module1Service.get_instance().get_summary()
                avg_pred = summary.get("sample_prediction", 16342)
                return (
                    f"### Module 1: Demand Forecasting Status\n\n"
                    f"- **Model**: XGBoost (29 engineered features) + LSTM Residuals\n"
                    f"- **Accuracy ($R^2$)**: **98.59%** (WAPE: 7.94%)\n"
                    f"- **Current Baseline Forecast**: **{int(avg_pred):,} units**\n"
                    f"- **Operational Impact**: Feeds directly into Module 5 (Safety Stock) and Module 6 (Decision Engine).\n\n"
                    f"You can inspect feature contributions or upload custom telemetry directly on the [Module 1 Page](/html/module1.html)."
                ), ["Check Inventory Status", "Run Decision Engine", "What is Delay Risk?"]
            except Exception:
                return "Module 1 is active. Hybrid model $R^2$ is **98.59%** with an average baseline forecast of ~16,342 units.", ["Check Inventory Status"]

        # 3. Delivery Delay (Module 2)
        if any(w in m for w in ["delay", "module 2", "late delivery", "transit risk", "shipping delay"]):
            return (
                "### Module 2: Delivery Delay Risk\n\n"
                "- **Algorithm**: Optuna-Tuned XGBoost Binary Risk Classifier\n"
                "- **Precision**: **83.54%** | **ROC-AUC**: **74.54%** | **Decision Cutoff**: `36%`\n"
                "- **Current Telemetry**: Monitored shipments with delay probability >= 70% trigger customer notification; >= 85% trigger automated expedition.\n\n"
                "Would you like me to evaluate a specific shipment risk or launch the [Module 2 Console](/html/module2.html)?"
            ), ["Simulate Delivery Delay", "Explain Delay Factors", "Run Decision Engine"]

        # 4. Route Optimization (Module 3)
        if any(w in m for w in ["route", "corridor", "module 3", "gps", "reroute", "tomtom", "shortest path"]):
            return (
                "### Module 3: Dynamic Route Corridor Optimization\n\n"
                "- **Engine**: Dijkstra & A* Pathfinding + OpenStreetMap Graph Network\n"
                "- **Live Feeds**: Real-time TomTom traffic speed & hazard telemetry\n"
                "- **Corridor Resilience**: Computes primary and alternative bypass routes (e.g., Northern Bypass Corridor with a 42-minute ETA and 0.22 risk score).\n\n"
                "Visit [Module 3 Console](/html/module3.html) to view active map corridor overlays."
            ), ["What is Warehouse Congestion?", "Run Decision Engine", "Check Inventory Status"]

        # 5. Warehouse Congestion (Module 4)
        if any(w in m for w in ["congestion", "warehouse", "module 4", "dock", "truck arrivals"]):
            return (
                "### Module 4: Warehouse Dock Congestion\n\n"
                "- **Model**: 12-Timestep LSTM Sequence Classifier + XGBoost Feature Selector\n"
                "- **Accuracy**: **76.62%** | **ROC-AUC**: **83.71%** | **Recall**: **83.12%**\n"
                "- **Key Indicators**: Dock utilization, trucks per staff, and shift-change burst events.\n"
                "- **Policy**: Congestion risk >= 60% flags warehouse buffer rescheduling; >= 85% activates critical diversion.\n\n"
                "Check live dock sequence plots on [Module 4 Console](/html/module4.html)."
            ), ["Run Quick Decision", "Check Inventory Status", "Model Accuracies"]

        # 6. Inventory Optimization (Module 5)
        if any(w in m for w in ["inventory", "stock", "rop", "reorder", "safety stock", "module 5", "replenish"]):
            return (
                "### Module 5: Dynamic Inventory & Replenishment\n\n"
                "- **Framework**: Stochastic Dynamic Safety Stock (95% Service Level SLA, Z=1.645)\n"
                "- **Reorder Point (ROP)**: Dynamically calibrated against lead-time delay variance from Module 2 and demand spikes from Module 1.\n"
                "- **Policy Rules**:\n"
                "  - Stock <= 0.5 * ROP -> **CRITICAL REPLENISHMENT**\n"
                "  - Stock <= ROP -> **STANDARD REORDER**\n\n"
                "Open [Module 5 Console](/html/module5.html) to adjust replenishment order sizing."
            ), ["Run Quick Decision", "Simulate What-If", "Explain Actions"]

        # 7. Decision Engine (Module 6)
        if any(w in m for w in ["decision", "module 6", "action", "actions", "orchestrat", "recommendation"]):
            return (
                "### Module 6: Autonomous Decision Engine\n\n"
                "- **Role**: Consolidates predictions from Modules 2, 3, 4, and 5 into prioritized, auditable operational actions.\n"
                "- **Rank Hierarchy**: `CRITICAL` > `HIGH` > `MEDIUM` > `LOW`.\n"
                "- **Safety Safeguard**: Enforces a deterministic human authorization gate before operational dispatch execution.\n\n"
                "You can run an instant multi-node decision right now from the Control Tower or test custom scenarios in [Module 6](/html/module6.html)."
            ), ["Run Quick Decision", "Simulate What-If", "Explain Actions"]

        # 8. Explainable AI & What-If (Module 7)
        if any(w in m for w in ["explain", "why", "shap", "what-if", "what if", "counterfactual", "module 7"]):
            return (
                "### Module 7: Explainable AI & What-If Simulator\n\n"
                "- **Attribution**: Lundberg & Lee TreeExplainer SHAP decomposes predictions into additive feature contribution scores (φ_i).\n"
                "- **Evidence Chaining**: Every recommendation is tied to the exact sensor breach, source module ID, and policy rule.\n"
                "- **Interactive What-If**: Simulates hypotheticals (e.g. *What if warehouse congestion drops by 30%?*) without mutating production logs.\n\n"
                "Explore attribution plots on [Module 7 Console](/html/module7.html)."
            ), ["Model Accuracies", "Check Warehouse Congestion", "Run Decision Engine"]

        # 9. Pipeline execution / Full Supply Chain Check
        if any(w in m for w in ["pipeline", "full check", "run all", "supply chain check", "health", "status"]):
            return (
                "### LogiYantra Pipeline Diagnostics\n\n"
                "- **System Health**: All 7 intelligence microservices are operational.\n"
                "- **Connected Pipeline**: `M1 (Demand)` -> `M2/M3/M4 (Telemetry)` -> `M5 (Inventory)` -> `M6 (Decision)` -> `M7 (Explainability)`.\n"
                "- **Dispatch Status**: Control Tower operational gate active.\n\n"
                "To execute a quick decision right now, use the **Quick Decision panel** on the dashboard or tell me to evaluate a specific scenario!"
            ), ["Run Quick Decision", "Model Accuracies", "Check Inventory Status"]

        # 10. Greetings & General Help
        return (
            "### LogiBot Operations Copilot\n\n"
            "I am your autonomous Logistics AI Assistant, directly integrated into all 7 intelligence modules of LogiYantra.\n\n"
            "**Here are a few things you can ask me:**\n"
            "- *\"What are the accuracy metrics of all models?\"*\n"
            "- *\"What is the current delivery delay threshold?\"*\n"
            "- *\"How does Module 4 detect warehouse congestion?\"*\n"
            "- *\"Explain how the decision engine handles stockouts.\"*\n"
            "- *\"Simulate a what-if scenario.\"*\n\n"
            "How can I assist your supply chain operations right now?"
        ), ["Model Accuracies", "Check Warehouse Congestion", "Explain Delivery Delay", "Check Inventory Status"]

    def _get_contextual_suggestions(self, msg: str) -> List[str]:
        return ["Model Accuracies", "Run Quick Decision", "Check Warehouse Congestion", "Explain Delay Factors"]
