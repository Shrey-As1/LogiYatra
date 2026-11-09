from __future__ import annotations

import os

import joblib

import numpy as np

import pandas as pd


def _load_xgboost_safe(model_path: str):
    import pickle
    import xgboost as xgb
    try:
        return joblib.load(model_path)
    except Exception:
        # XGBoost 3.4.1 unpickle compatibility fallback
        class _BoosterFinder(pickle.Unpickler):
            def find_class(self, module, name):
                if name == "Booster":
                    class _DummyBooster:
                        def __setstate__(self, state):
                            self.state = state
                    return _DummyBooster
                return super().find_class(module, name)

        with open(model_path, "rb") as f:
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


def load_delivery_model(project_root: str):
    model_dir = os.path.join(
        project_root,
        "ml_training",
        "Module_2_Delivery_Delay",
        "models"
    )

    model = _load_xgboost_safe(
        os.path.join(model_dir, "dataco_xgboost_model.pkl")
    )

    encoder = joblib.load(
        os.path.join(model_dir, "dataco_encoder.pkl")
    )

    feature_names = joblib.load(
        os.path.join(model_dir, "dataco_feature_names.pkl")
    )

    threshold = float(
        joblib.load(
            os.path.join(model_dir, "dataco_threshold.pkl")
        )
    )

    return (
        model,
        encoder,
        feature_names,
        threshold
    )


def explain_xgboost(

    model,

    X,

    feature_names=None,

    class_index=1,

    top_k=10
):

    try:

        import shap

    except ImportError as exc:

        raise ImportError(

            "Install shap to use "
            "Module 7 explanations."
        ) from exc

    X = (

        X
        if isinstance(X, np.ndarray)
        else np.asarray(X)
    )

    explainer = shap.TreeExplainer(
        model
    )

    values = explainer.shap_values(X)

    if isinstance(values, list):

        values = values[class_index]

    values = np.asarray(values)

    if values.ndim == 3:

        values = values[
            :,
            :,
            class_index
        ]

    row = values[0]

    if feature_names is None:

        names = [

            f"feature_{i}"

            for i in range(
                len(row)
            )
        ]

    else:

        names = list(
            feature_names
        )

    order = np.argsort(

        np.abs(row)

    )[::-1][:top_k]

    return [

        {

            "feature":
                names[i],

            "shap_value":
                float(row[i]),

            "impact":

                (
                    "increases_risk"

                    if row[i] > 0

                    else
                    "decreases_risk"
                )
        }

        for i in order
    ]


def explain_prediction_vector(

    model,

    X,

    feature_names,

    threshold=0.5,

    top_k=10

):

    X = np.asarray(X)

    if X.ndim == 1:

        X = X.reshape(
            1,
            -1
        )

    probability = float(

        model.predict_proba(X)[0, 1]
    )

    explanation = explain_xgboost(

        model,

        X,

        feature_names,

        top_k=top_k
    )

    return {

        "prediction_probability":
            probability,

        "threshold":
            threshold,

        "predicted_class":

            int(
                probability >= threshold
            ),

        "risk_level":

            (
                "HIGH"

                if probability >= threshold

                else
                "LOW"
            ),

        "top_features":
            explanation
    }


def sequence_permutation_importance(

    model,

    sequence,

    feature_names,

    repeats=2

):

    x = np.asarray(
        sequence,
        dtype=np.float32
    )

    if x.ndim == 2:

        x = x[None, ...]

    base = float(

        np.asarray(

            model.predict(
                x,
                verbose=0
            )

        ).reshape(-1)[0]
    )

    rng = np.random.default_rng(
        42
    )

    results = []

    for j, name in enumerate(
        feature_names
    ):

        changes = []

        for _ in range(repeats):

            perturbed = x.copy()

            flat = (

                perturbed[:, :, j]
                .reshape(-1)
            )

            rng.shuffle(flat)

            prediction = float(

                np.asarray(

                    model.predict(
                        perturbed,
                        verbose=0
                    )

                ).reshape(-1)[0]
            )

            changes.append(

                abs(
                    prediction - base
                )
            )

        results.append({

            "feature": name,

            "importance":
                float(
                    np.mean(changes)
                )
        })

    return sorted(

        results,

        key=lambda r:
            r["importance"],

        reverse=True
    )