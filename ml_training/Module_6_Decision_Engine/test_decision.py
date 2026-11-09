try:
    from decision_engine import DecisionEngine
except ImportError:
    from ml_training.Module_6_Decision_Engine.decision_engine import DecisionEngine


def test_decision_engine():
    engine = DecisionEngine()
    result = engine.evaluate(
        delay_risk=0.90,
        congestion_risk=0.90,
        route_risk=0.20,
        inventory_status="REPLENISH",
        stock_level=400,
        reorder_point=750
    )
    assert result["overall_status"] == "CRITICAL"
    assert len(result["actions"]) >= 2


if __name__ == "__main__":
    test_decision_engine()
    print("Module 6 smoke test passed")