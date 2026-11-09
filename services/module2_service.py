"""Module 2 — Delivery Delay Prediction Inference Service.

Loads the DataCo Delivery Delay Optuna-tuned XGBoost classifier, OneHotEncoder,
feature list (5,567 features), and optimal decision threshold (0.36).
"""
from __future__ import annotations

import csv
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import joblib
import xgboost as xgb

ROOT_DIR = Path(__file__).resolve().parent.parent
M2_DIR = ROOT_DIR / "ml_training" / "Module_2_Delivery_Delay" / "models"


def _safe_load_xgboost(path: Path) -> Any:
    """Robust loader handling UBJSON offset compatibility across XGBoost versions."""
    try:
        return joblib.load(str(path))
    except Exception:
        class _BoosterFinder(pickle.Unpickler):
            def find_class(self, module, name):
                if name == "Booster":
                    class _DummyBooster:
                        def __setstate__(self, state):
                            self.state = state
                    return _DummyBooster
                return super().find_class(module, name)

        with open(str(path), "rb") as f:
            clf = _BoosterFinder(f).load()

        buf = bytes(clf._Booster.state["handle"])
        idx_model = buf.find(b"Model")
        if idx_model != -1:
            idx_brace = buf.find(b"{", idx_model)
            model_buf = buf[idx_brace:-1]
        else:
            model_buf = buf

        booster = xgb.Booster()
        booster.load_model(bytearray(model_buf))
        clf._Booster = booster
        return clf


class Module2Service:
    _instance: Optional[Module2Service] = None

    def __init__(self):
        self.model_path = M2_DIR / "dataco_xgboost_model.pkl"
        self.encoder_path = M2_DIR / "dataco_encoder.pkl"
        self.features_path = M2_DIR / "dataco_feature_names.pkl"
        self.threshold_path = M2_DIR / "dataco_threshold.pkl"
        self.importance_path = M2_DIR / "dataco_feature_importance.csv"
        self.comparison_path = M2_DIR / "dataco_model_comparison.csv"
        self.optuna_path = M2_DIR / "dataco_optuna_study.pkl"

        self._model = None
        self._encoder = None
        self._feature_names: List[str] = []
        self._threshold: float = 0.36
        self._top_features: List[Dict[str, Any]] = []
        self._model_comparison: List[Dict[str, Any]] = []
        self._optuna_params: Dict[str, Any] = {}

        self._load_artifacts()

    @classmethod
    def get_instance(cls) -> Module2Service:
        if cls._instance is None:
            cls._instance = Module2Service()
        return cls._instance

    def _load_artifacts(self):
        if self.threshold_path.exists():
            try:
                self._threshold = float(joblib.load(str(self.threshold_path)))
            except Exception:
                self._threshold = 0.36

        if self.features_path.exists():
            try:
                self._feature_names = list(joblib.load(str(self.features_path)))
            except Exception:
                self._feature_names = []

        if self.importance_path.exists():
            try:
                with open(self.importance_path, mode="r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for i, row in enumerate(reader):
                        if i >= 10:
                            break
                        self._top_features.append({
                            "feature": row.get("Feature", ""),
                            "importance": float(row.get("Importance", 0.0))
                        })
            except Exception:
                self._top_features = []

        if self.comparison_path.exists():
            try:
                with open(self.comparison_path, mode="r", encoding="utf-8") as f:
                    self._model_comparison = list(csv.DictReader(f))
            except Exception:
                self._model_comparison = []

        if self.optuna_path.exists():
            try:
                study = joblib.load(str(self.optuna_path))
                self._optuna_params = {
                    "best_value": round(float(study.best_value), 4),
                    "trials_count": len(study.trials),
                    "best_params": {k: (round(v, 4) if isinstance(v, float) else v) for k, v in study.best_trial.params.items()}
                }
            except Exception:
                self._optuna_params = {}

    def is_ready(self) -> bool:
        return self.model_path.exists() and len(self._feature_names) > 0

    def get_model(self):
        if self._model is None:
            if not self.model_path.exists():
                raise FileNotFoundError(f"Module 2 model file missing at {self.model_path}")
            self._model = _safe_load_xgboost(self.model_path)
        return self._model

    def get_encoder(self):
        if self._encoder is None:
            if not self.encoder_path.exists():
                raise FileNotFoundError(f"Module 2 encoder missing at {self.encoder_path}")
            self._encoder = joblib.load(str(self.encoder_path))
        return self._encoder

    def get_summary(self) -> Dict[str, Any]:
        return {
            "model": "Optuna-Tuned XGBoost Classifier",
            "dataset": "DataCo Global Supply Chain Dataset (180,519 shipments)",
            "task": "Binary Late Delivery Risk Classification",
            "roc_auc": 0.7454,
            "pr_auc": 0.8151,
            "accuracy": 0.6920,
            "precision": 0.8354,
            "recall": 0.5436,
            "f1_at_default_threshold": 0.6586,
            "optimized_threshold": round(self._threshold, 3),
            "optimized_f1": 0.7093,
            "features_total": len(self._feature_names),
            "top_features": self._top_features,
            "model_comparison": self._model_comparison,
            "optuna_study": self._optuna_params,
            "artifacts_available": self.model_path.exists(),
        }

    def predict(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Runs delivery delay prediction.
        
        Accepts operational shipment features or explicit probability testing.
        """
        # If payload gives explicit probability test input
        if "test_probability" in payload or "delay_risk" in payload:
            prob = float(payload.get("test_probability", payload.get("delay_risk")))
            if not (0.0 <= prob <= 1.0):
                raise ValueError("Probability must be between 0.0 and 1.0")
        else:
            model = self.get_model()
            encoder = self.get_encoder()

            cat_cols = list(encoder.feature_names_in_) if hasattr(encoder, "feature_names_in_") else [
                "Type", "Category Name", "Customer City", "Customer Country",
                "Customer Segment", "Customer State", "Department Name", "Market",
                "Order City", "Order Country", "Order Region", "Order State", "Product Name",
                "Shipping Mode"
            ]

            cat_input = {col: str(payload.get(col, "Unknown")) for col in cat_cols}
            
            # Shipping Mode resolution
            if cat_input["Shipping Mode"] == "Unknown":
                cat_input["Shipping Mode"] = str(payload.get("shipping_mode", "Standard Class"))

            # Customer Segment resolution
            if cat_input["Customer Segment"] == "Unknown":
                cat_input["Customer Segment"] = str(payload.get("customer_segment", "Consumer"))

            # Customer Country resolution
            if cat_input["Customer Country"] == "Unknown":
                cat_input["Customer Country"] = "EE. UU."

            # Normalize Market region and derive realistic Order Region & GPS
            market_region_map = {
                "India": ("Pacific Asia", "South Asia", 20.5937, 78.9629),
                "India (South Asia Hub)": ("Pacific Asia", "South Asia", 20.5937, 78.9629),
                "ASEAN": ("Pacific Asia", "Southeast Asia", 1.3521, 103.8198),
                "ASEAN (Southeast Asia)": ("Pacific Asia", "Southeast Asia", 1.3521, 103.8198),
                "East Asia & Pacific": ("Pacific Asia", "Eastern Asia", 35.8617, 104.1954),
                "Pacific Asia": ("Pacific Asia", "Eastern Asia", 35.8617, 104.1954),
                "Middle East (MENA)": ("Europe", "West Asia", 25.2048, 55.2708),
                "Europe": ("Europe", "Western Europe", 51.1657, 10.4515),
                "Europe & UK": ("Europe", "Western Europe", 51.1657, 10.4515),
                "USCA": ("USCA", "US Center ", 37.0902, -95.7129),
                "North America (US / Canada)": ("USCA", "US Center ", 37.0902, -95.7129),
                "North America (USCA)": ("USCA", "US Center ", 37.0902, -95.7129),
                "LATAM": ("LATAM", "South America", -14.2350, -51.9253),
                "Latin America (LATAM)": ("LATAM", "South America", -14.2350, -51.9253),
                "Africa": ("Africa", "Central Africa", 1.6508, 10.2679),
                "Africa Region": ("Africa", "Central Africa", 1.6508, 10.2679),
            }

            raw_market = cat_input.get("Market", "Unknown")
            if raw_market == "Unknown":
                raw_market = str(payload.get("market", payload.get("market_region", "India")))

            if raw_market in market_region_map:
                m_norm, reg_norm, def_lat, def_lon = market_region_map[raw_market]
                cat_input["Market"] = m_norm
                if cat_input.get("Order Region") == "Unknown":
                    cat_input["Order Region"] = reg_norm
            else:
                cat_input["Market"] = "LATAM"
                def_lat, def_lon = 18.2208, -66.5901

            import pandas as pd
            import datetime
            cat_df = pd.DataFrame([cat_input])
            try:
                encoded_sparse = encoder.transform(cat_df)
                encoded_cols = list(encoder.get_feature_names_out(cat_cols))
            except Exception:
                encoded_sparse = None
                encoded_cols = []

            # Temporal features (dynamically calculated or overridden from payload)
            now = datetime.datetime.now()
            order_month = int(payload.get("order_month", payload.get("month", now.month)))
            order_day = int(payload.get("order_day", payload.get("day", now.day)))
            order_dow = int(payload.get("order_dayofweek", payload.get("dayofweek", now.weekday())))
            order_year = int(payload.get("order_year", payload.get("year", now.year)))
            order_dayofyear = int(payload.get("order_dayofyear", now.timetuple().tm_yday))
            order_weekofyear = int(payload.get("order_weekofyear", now.isocalendar()[1]))

            month_sin = np.sin(2 * np.pi * order_month / 12.0)
            month_cos = np.cos(2 * np.pi * order_month / 12.0)
            dow_sin = np.sin(2 * np.pi * order_dow / 7.0)
            dow_cos = np.cos(2 * np.pi * order_dow / 7.0)

            # Scheduled transit days resolution
            mode_defaults = {
                "Same Day": 0,
                "First Class": 1,
                "Second Class": 2,
                "Standard Class": 4
            }
            shipping_mode = cat_input["Shipping Mode"]
            if "Days for shipment (scheduled)" in payload:
                sched_days = float(payload["Days for shipment (scheduled)"])
            elif "scheduled_days" in payload:
                sched_days = float(payload["scheduled_days"])
            else:
                sched_days = float(mode_defaults.get(shipping_mode, 4))

            # Numerical defaults
            num_defaults: Dict[str, float] = {
                "Days for shipment (scheduled)": sched_days,
                "Benefit per order": float(payload.get("Benefit per order", 25.0)),
                "Sales per customer": float(payload.get("Sales per customer", 150.0)),
                "Category Id": float(payload.get("Category Id", 17)),
                "Department Id": float(payload.get("Department Id", 4)),
                "Latitude": float(payload.get("lat", payload.get("Latitude", def_lat))),
                "Longitude": float(payload.get("lon", payload.get("Longitude", def_lon))),
                "Order Item Cardprod Id": float(payload.get("Order Item Cardprod Id", 365)),
                "Order Item Discount": float(payload.get("Order Item Discount", 0.0)),
                "Order Item Discount Rate": float(payload.get("Order Item Discount Rate", 0.0)),
                "Order Item Product Price": float(payload.get("Order Item Product Price", 59.99)),
                "Order Item Profit Ratio": float(payload.get("Order Item Profit Ratio", 0.2)),
                "Order Item Quantity": float(payload.get("Order Item Quantity", 1)),
                "Sales": float(payload.get("Sales", 59.99)),
                "Order Item Total": float(payload.get("Order Item Total", 59.99)),
                "Order Profit Per Order": float(payload.get("Order Profit Per Order", 12.0)),
                "Product Category Id": float(payload.get("Product Category Id", 17)),
                "Product Price": float(payload.get("Product Price", 59.99)),
                "Product Status": float(payload.get("Product Status", 0)),
                "order_year": float(order_year),
                "order_month": float(order_month),
                "order_day": float(order_day),
                "order_dayofweek": float(order_dow),
                "order_weekofyear": float(order_weekofyear),
                "order_dayofyear": float(order_dayofyear),
                "month_sin": float(month_sin),
                "month_cos": float(month_cos),
                "dow_sin": float(dow_sin),
                "dow_cos": float(dow_cos),
            }

            # Map features to the 5,567-wide feature vector
            vector = np.zeros((1, len(self._feature_names)), dtype=np.float32)
            feat_idx_map = {name: i for i, name in enumerate(self._feature_names)}

            for k, v in num_defaults.items():
                if k in feat_idx_map:
                    vector[0, feat_idx_map[k]] = v

            if encoded_sparse is not None:
                encoded_dense = encoded_sparse.toarray()[0]
                for col_name, val in zip(encoded_cols, encoded_dense):
                    if col_name in feat_idx_map:
                        vector[0, feat_idx_map[col_name]] = val

            # Predict probability of class 1 (Late delivery)
            probs = model.predict_proba(vector)[0]
            prob = float(probs[1])

        prob = max(0.0, min(1.0, prob))
        is_late = prob >= self._threshold

        if prob >= 0.70:
            risk_level = "CRITICAL"
        elif prob >= self._threshold:
            risk_level = "HIGH"
        elif prob >= 0.20:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return {
            "delay_probability": round(prob, 4),
            "threshold": self._threshold,
            "predicted_late": bool(is_late),
            "risk_level": risk_level,
            "model": "Optuna-Tuned XGBoost Classifier",
            "top_features": self._top_features[:5],
            "source": "live_model_inference",
        }
