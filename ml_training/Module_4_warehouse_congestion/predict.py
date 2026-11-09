"""
Module 4 — Warehouse Congestion Prediction API Helper

Loads:
    congestion_lstm.keras
    congestion_scaler.pkl
    congestion_features.json
    congestion_metadata.json

Input:
    A sequence of recent warehouse observations.

Output:
    congestion_risk
    status

Example:

    python predict.py
"""

import os
import json
import pickle

import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

ML_DIR = os.path.join(BASE_DIR, "models")


LSTM_PATH = os.path.join(
    ML_DIR,
    "congestion_lstm.keras"
)

SCALER_PATH = os.path.join(
    ML_DIR,
    "congestion_scaler.pkl"
)

FEATURES_PATH = os.path.join(
    ML_DIR,
    "congestion_features.json"
)

METADATA_PATH = os.path.join(
    ML_DIR,
    "congestion_metadata.json"
)


# ============================================================
# LOAD ARTIFACTS
# ============================================================

def load_artifacts():

    import tensorflow as tf

    model = tf.keras.models.load_model(
        LSTM_PATH
    )

    with open(
        SCALER_PATH,
        "rb"
    ) as f:

        scaler = pickle.load(
            f
        )

    with open(
        FEATURES_PATH,
        "r"
    ) as f:

        feature_config = json.load(
            f
        )

    with open(
        METADATA_PATH,
        "r"
    ) as f:

        metadata = json.load(
            f
        )

    return (
        model,
        scaler,
        feature_config,
        metadata
    )


# ============================================================
# FEATURE ENGINEERING
# ============================================================

def prepare_features(
    df
):

    df = df.copy()

    # Cyclic hour
    df["hour_sin"] = np.sin(
        2 * np.pi * df["hour"] / 24
    )

    df["hour_cos"] = np.cos(
        2 * np.pi * df["hour"] / 24
    )

    # Cyclic day
    df["day_sin"] = np.sin(
        2 * np.pi * df["day_of_week"] / 7
    )

    df["day_cos"] = np.cos(
        2 * np.pi * df["day_of_week"] / 7
    )

    # Derived operational features
    df["orders_per_staff"] = (
        df["order_volume"]
        / np.maximum(
            df["staff_count"],
            1
        )
    )

    df["trucks_per_staff"] = (
        df["truck_arrivals"]
        / np.maximum(
            df["staff_count"],
            1
        )
    )

    return df


# ============================================================
# PREDICT
# ============================================================

def predict_congestion(
    observations
):

    (
        model,
        scaler,
        feature_config,
        metadata
    ) = load_artifacts()

    selected_features = (
        feature_config[
            "selected_features"
        ]
    )

    sequence_length = (
        feature_config[
            "sequence_length"
        ]
    )

    threshold = metadata.get(
        "threshold",
        0.50
    )

    # --------------------------------------------------------
    # INPUT DATA
    # --------------------------------------------------------

    if isinstance(
        observations,
        pd.DataFrame
    ):

        df = observations.copy()

    else:

        df = pd.DataFrame(
            observations
        )

    # --------------------------------------------------------
    # VALIDATE INPUT
    # --------------------------------------------------------

    required_columns = [
        "hour",
        "day_of_week",
        "shift",
        "shift_change",
        "order_volume",
        "truck_arrivals",
        "dock_utilization",
        "staff_count",
        "burst_event"
    ]

    missing = [
        col
        for col in required_columns
        if col not in df.columns
    ]

    if missing:

        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing)
        )

    if len(df) < sequence_length:

        raise ValueError(
            f"At least {sequence_length} "
            "time observations are required."
        )

    # --------------------------------------------------------
    # FEATURES
    # --------------------------------------------------------

    df = prepare_features(
        df
    )

    # Only the most recent sequence
    sequence_df = df.tail(
        sequence_length
    )

    # --------------------------------------------------------
    # SCALE
    # --------------------------------------------------------

    scaled = scaler.transform(
        sequence_df[
            selected_features
        ]
    )

    X = np.expand_dims(
        scaled.astype(np.float32),
        axis=0
    )

    # --------------------------------------------------------
    # PREDICT
    # --------------------------------------------------------

    risk = float(
        model.predict(
            X,
            verbose=0
        )[0][0]
    )

    risk = float(
        np.clip(
            risk,
            0.0,
            1.0
        )
    )

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    status = (
        "high"
        if risk >= threshold
        else "low"
    )

    return {
        "congestion_risk": round(
            risk,
            4
        ),
        "status": status,
        "threshold": threshold
    }


# ============================================================
# EXAMPLE
# ============================================================

if __name__ == "__main__":

    print(
        "=" * 60
    )

    print(
        "Warehouse Congestion Prediction"
    )

    print(
        "=" * 60
    )

    # --------------------------------------------------------
    # Example 12-period warehouse history
    # --------------------------------------------------------

    rows = []

    for i in range(12):

        hour = (
            8 + i
        ) % 24

        rows.append({
            "hour":
                hour,

            "day_of_week":
                2,

            "shift":
                1,

            "shift_change":
                0,

            "order_volume":
                130 + i * 5,

            "truck_arrivals":
                12 + i,

            "dock_utilization":
                min(
                    0.65 + i * 0.025,
                    0.98
                ),

            "staff_count":
                max(
                    30 - i,
                    12
                ),

            "burst_event":
                1 if i >= 8 else 0
        })

    result = predict_congestion(
        rows
    )

    print()
    print(
        "Prediction:"
    )

    print(
        json.dumps(
            result,
            indent=4
        )
    )