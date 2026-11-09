from __future__ import annotations

from typing import Callable
from typing import Dict
from typing import Any


def compare_scenarios(

    current: Dict[str, Any],

    scenario: Dict[str, Any],

    predictor: Callable[
        [Dict[str, Any]],
        float
    ]

):

    baseline_probability = float(

        predictor(current)
    )

    new_inputs = dict(
        current
    )

    new_inputs.update(
        scenario
    )

    scenario_probability = float(

        predictor(new_inputs)
    )

    if not (
        0 <= baseline_probability <= 1
    ):

        raise ValueError(
            "Baseline probability must "
            "be between 0 and 1."
        )

    if not (
        0 <= scenario_probability <= 1
    ):

        raise ValueError(
            "Scenario probability must "
            "be between 0 and 1."
        )

    change = (

        scenario_probability
        - baseline_probability
    )

    return {

        "baseline_probability":
            round(
                baseline_probability,
                6
            ),

        "scenario_probability":
            round(
                scenario_probability,
                6
            ),

        "change":
            round(
                change,
                6
            ),

        "change_percentage_points":
            round(
                change * 100,
                4
            ),

        "risk_reduced":
            change < 0,

        "changed_inputs":
            scenario
    }


def threshold_label(

    probability: float,

    threshold: float = 0.5

):

    return (

        "HIGH"

        if probability >= threshold

        else "LOW"
    )