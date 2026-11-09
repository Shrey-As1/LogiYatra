try:
    from what_if import compare_scenarios
except ImportError:
    from ml_training.Module_7_Explainability.what_if import compare_scenarios


def test_what_if_scenario():
    result = compare_scenarios(
        {"staff": 20},
        {"staff": 30},
        lambda data: 0.8 if data["staff"] == 20 else 0.4
    )
    assert result["risk_reduced"] is True
    assert result["change_percentage_points"] == -40.0


if __name__ == "__main__":
    test_what_if_scenario()
    print("Module 7 smoke test passed")