"""Module 4 — Warehouse Congestion Prediction Service.

Loads the LSTM sequence classifier and StandardScaler, validates sequential input
(sequence length = 12), scales selected features, and returns predicted congestion risk.
"""
from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent
M4_DIR = ROOT_DIR / "ml_training" / "Module_4_warehouse_congestion" / "models"


class Module4Service:
    _instance: Optional[Module4Service] = None

    def __init__(self):
        self.model_path = M4_DIR / "congestion_lstm.keras"
        self.scaler_path = M4_DIR / "congestion_scaler.pkl"
        self.features_path = M4_DIR / "congestion_features.json"
        self.metadata_path = M4_DIR / "congestion_metadata.json"

        self._lstm = None
        self._scaler = None
        self._selected_features: List[str] = [
            "dock_utilization", "order_volume", "burst_event", "trucks_per_staff",
            "orders_per_staff", "shift_change", "truck_arrivals", "hour_cos"
        ]
        self._sequence_length: int = 12
        self._threshold: float = 0.5
        self._metadata: Dict[str, Any] = {}

        self._load_metadata()

    @classmethod
    def get_instance(cls) -> Module4Service:
        if cls._instance is None:
            cls._instance = Module4Service()
        return cls._instance

    def _load_metadata(self):
        if self.features_path.exists():
            try:
                with open(self.features_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._selected_features = data.get("selected_features", self._selected_features)
                    self._sequence_length = data.get("sequence_length", 12)
            except Exception:
                pass

        if self.metadata_path.exists():
            try:
                with open(self.metadata_path, "r", encoding="utf-8") as f:
                    self._metadata = json.load(f)
                    self._threshold = self._metadata.get("threshold", 0.5)
            except Exception:
                pass

    def is_ready(self) -> bool:
        return self.model_path.exists() and self.scaler_path.exists()

    def get_lstm(self):
        if self._lstm is None:
            if not self.model_path.exists():
                raise FileNotFoundError(f"LSTM model missing at {self.model_path}")
            import tensorflow as tf
            self._lstm = tf.keras.models.load_model(str(self.model_path))
        return self._lstm

    def get_scaler(self):
        if self._scaler is None:
            if not self.scaler_path.exists():
                raise FileNotFoundError(f"Scaler missing at {self.scaler_path}")
            with open(self.scaler_path, "rb") as f:
                self._scaler = pickle.load(f)
        return self._scaler

    def get_summary(self) -> Dict[str, Any]:
        return {
            "model_type": "XGBoost Feature Selection + LSTM Sequence Classifier",
            "dataset": "Distribution Center Telemetry (25,000 hourly operational sequences)",
            "sequence_length": self._sequence_length,
            "threshold": self._threshold,
            "selected_features": self._selected_features,
            "feature_importance": [
                {"feature": "dock_utilization", "gain": 44.68, "importance": 0.4468},
                {"feature": "order_volume", "gain": 8.24, "importance": 0.0824},
                {"feature": "burst_event", "gain": 5.87, "importance": 0.0587},
                {"feature": "trucks_per_staff", "gain": 5.69, "importance": 0.0569},
                {"feature": "orders_per_staff", "gain": 5.33, "importance": 0.0533},
                {"feature": "shift_change", "gain": 4.65, "importance": 0.0465},
                {"feature": "truck_arrivals", "gain": 4.08, "importance": 0.0408},
                {"feature": "hour_cos", "gain": 3.17, "importance": 0.0317},
            ],
            "metrics": self._metadata.get("metrics", {
                "accuracy": 0.7662,
                "precision": 0.7253,
                "recall": 0.8312,
                "f1": 0.7746,
                "roc_auc": 0.8371
            }),
            "architecture": {
                "input_shape": "(12, 8)",
                "layers": [
                    {"name": "LSTM-1", "units": 64, "dropout": 0.20, "return_sequences": True},
                    {"name": "LSTM-2", "units": 32, "dropout": 0.20, "return_sequences": False},
                    {"name": "Dense-1", "units": 16, "activation": "relu"},
                    {"name": "Dense-Output", "units": 1, "activation": "sigmoid"}
                ],
                "scaler": "StandardScaler (Z-Score Normalization)",
                "loss": "binary_crossentropy",
                "optimizer": "Adam (lr=0.001)"
            },
            "artifacts_available": self.model_path.exists() and self.scaler_path.exists()
        }

    def predict(
        self,
        observations: List[Dict[str, Any]],
        mitigation: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Runs LSTM inference on at least 12 sequential hourly records with optional what-if mitigations."""
        if not isinstance(observations, list) or len(observations) < self._sequence_length:
            raise ValueError(
                f"Observations must be a list containing at least {self._sequence_length} hourly time records."
            )

        lstm = self.get_lstm()
        scaler = self.get_scaler()

        mit = mitigation or {}
        add_staff = float(mit.get("additional_staff", 0))
        overflow_docks = float(mit.get("overflow_docks", 0))
        stagger_trucks = bool(mit.get("stagger_trucks", False))

        # Take the most recent `sequence_length` observations
        seq_records = observations[-self._sequence_length:]
        rows = []
        for r in seq_records:
            # Derived / computed fields
            hour = float(r.get("hour", 12))
            hour_cos = float(r.get("hour_cos", np.cos(2 * np.pi * hour / 24)))
            dock_util = float(r.get("dock_utilization", 0.5))
            order_vol = float(r.get("order_volume", 200.0))
            burst = float(r.get("burst_event", 0.0))
            shift_chg = float(r.get("shift_change", 0.0))
            truck_arr = float(r.get("truck_arrivals", 10.0))
            staff = float(r.get("staff_count", 15.0))

            # Apply what-if operational mitigations if specified
            if overflow_docks > 0:
                dock_util = max(0.0, dock_util * (20.0 / (20.0 + overflow_docks)))
            if stagger_trucks:
                truck_arr = max(0.0, truck_arr * 0.82)
            if add_staff > 0:
                staff += add_staff

            if staff <= 0:
                staff = 1.0

            trucks_per_staff = float(r.get("trucks_per_staff", truck_arr / staff))
            orders_per_staff = float(r.get("orders_per_staff", order_vol / staff))

            feat_dict = {
                "dock_utilization": dock_util,
                "order_volume": order_vol,
                "burst_event": burst,
                "trucks_per_staff": trucks_per_staff,
                "orders_per_staff": orders_per_staff,
                "shift_change": shift_chg,
                "truck_arrivals": truck_arr,
                "hour_cos": hour_cos,
            }
            row = [feat_dict[f] for f in self._selected_features]
            rows.append(row)

        X_raw = np.array(rows, dtype=np.float32)  # shape (12, 8)
        X_scaled = scaler.transform(X_raw)         # shape (12, 8)
        X_input = np.expand_dims(X_scaled, axis=0) # shape (1, 12, 8)

        raw_pred = float(lstm.predict(X_input, verbose=0)[0][0])
        prob = max(0.0, min(1.0, raw_pred))

        if prob >= 0.85:
            status = "CRITICAL"
            recommended_action = "🚨 Immediate Emergency: Open 4 overflow docks, divert line-haul trailers to regional staging yard, and call swing-shift material handlers."
        elif prob >= self._threshold:
            status = "HEAVY"
            recommended_action = "⚠️ Elevated Risk: Delay Wave 4 picking batch by 45 minutes and stagger dock slot appointments."
        elif prob >= 0.30:
            status = "MODERATE"
            recommended_action = "ℹ️ Watch Status: Monitor inbound truck arrivals and prepare overflow yard staging if dock saturation exceeds 75%."
        else:
            status = "NORMAL"
            recommended_action = "✅ Optimal Flow: Operations within standard parameters; maintain regular wave picking."

        # Compute Operational Impact KPIs
        latest_dock = round(float(rows[-1][0]), 3)
        dock_velocity = round((float(rows[-1][0]) - float(rows[0][0])) / 11.0, 4)

        if latest_dock >= 0.85:
            time_to_gridlock = "Immediate (Facility Saturated)"
            hours_to_sat = 0.0
        elif dock_velocity > 0.005:
            hours_to_sat = round(max(0.4, (0.85 - latest_dock) / dock_velocity), 1)
            time_to_gridlock = f"~{hours_to_sat} Hours"
        else:
            hours_to_sat = None
            time_to_gridlock = "Stable (No Immediate Saturation)"

        latest_trucks = float(rows[-1][6]) if len(rows[-1]) > 6 else 10.0
        excess_trucks = max(0.0, latest_trucks - 8.0) * (1.0 if prob >= 0.50 else 0.35)
        detention_cost = round(excess_trucks * 85.0 * prob, 0)

        return {
            "congestion_risk": round(prob, 4),
            "status": status,
            "risk_level": status,
            "threshold": self._threshold,
            "sequence_length": self._sequence_length,
            "observations_processed": len(seq_records),
            "latest_dock_utilization": latest_dock,
            "dock_velocity_pct_per_hr": round(dock_velocity * 100, 2),
            "time_to_gridlock": time_to_gridlock,
            "hours_to_saturation": hours_to_sat,
            "estimated_detention_cost": detention_cost,
            "recommended_action": recommended_action,
            "mitigation_applied": bool(mit),
            "source": "live_model_inference",
        }
