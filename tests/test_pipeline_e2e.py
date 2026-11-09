"""End-to-End multi-module pipeline integration tests."""
import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_full_pipeline_solve(client):
    """Executes the connected 7-module workflow from demand forecast to explanation."""
    payload = {
        # Module 1 Demand Forecast input
        "module1": {
            "Store": 1,
            "Dept": 1,
            "sales_lag_1": 18000.0,
            "Size": 151315,
            "is_holiday": 0
        },
        # Module 2 Delivery Delay input
        "module2": {
            "Shipping Mode": "Standard Class",
            "Days for shipment (scheduled)": 4,
            "Market": "LATAM"
        },
        # Module 4 Warehouse Congestion (12 observations)
        "module4": {
            "observations": [
                {
                    "hour": (8 + i) % 24,
                    "dock_utilization": 0.55 + (i * 0.02),
                    "order_volume": 300 + (i * 12),
                    "staff_count": 16,
                    "truck_arrivals": 10
                }
                for i in range(12)
            ]
        },
        # Module 5 Inventory input (omits demand to test automatic forwarding from Module 1)
        "module5": {
            "current_stock": 250,
            "lead_time_days": 4,
            "safety_stock_days": 3,
            "pack_size": 25
        },
        # Module 3 Route Risk
        "route_risk": 0.18
    }

    res = client.post("/api/pipeline/run", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    pipeline = data["pipeline"]

    # Verify Module 1 ran and produced daily demand
    assert "module1_demand" in pipeline
    daily_demand = pipeline["module1_demand"]["forecast_daily_demand"]
    assert daily_demand > 0

    # Verify Module 5 consumed Module 1 demand
    assert "module5_inventory" in pipeline
    assert pipeline["module5_inventory"]["forecast_daily_demand"] == daily_demand
    assert pipeline["module5_inventory"]["status"] in {"REPLENISH", "CRITICAL_REPLENISH", "HEALTHY"}

    # Verify Module 6 consumed available operational risks and produced recommendations
    assert "module6_decision" in pipeline
    assert pipeline["module6_decision"]["overall_status"] in {"NORMAL", "HIGH", "CRITICAL"}
    assert pipeline["module6_decision"]["requires_human_approval"] is True

    # Verify Module 7 explained the decision
    assert "module7_explanation" in pipeline
    assert "action_breakdown" in pipeline["module7_explanation"]
    assert pipeline["module7_explanation"]["requires_human_approval"] is True
