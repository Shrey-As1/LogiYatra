"""Unit and integration tests for Modules 1 through 7 API inference interfaces."""
import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# -----------------------------------------------------------------------------
# MODULE 1 TESTS
# -----------------------------------------------------------------------------

def test_module1_summary(client):
    res = client.get("/api/module1/summary")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["summary"]["artifacts_available"] is True


def test_module1_predict_valid(client):
    payload = {
        "Store": 1,
        "Dept": 1,
        "sales_lag_1": 17000.0,
        "Size": 151315,
        "is_holiday": 0,
    }
    res = client.post("/api/module1/predict", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "forecast_weekly_demand" in data["result"]
    assert "forecast_daily_demand" in data["result"]
    assert data["result"]["forecast_weekly_demand"] > 0


def test_module1_predict_invalid_feature(client):
    payload = {"sales_lag_1": "not-a-number"}
    res = client.post("/api/module1/predict", json=payload)
    assert res.status_code == 400


# -----------------------------------------------------------------------------
# MODULE 2 TESTS
# -----------------------------------------------------------------------------

def test_module2_summary(client):
    res = client.get("/api/module2/summary")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert abs(data["summary"]["optimized_threshold"] - 0.36) < 0.01


def test_module2_predict_valid_features(client):
    payload = {
        "Shipping Mode": "Standard Class",
        "Days for shipment (scheduled)": 4,
        "Market": "LATAM",
        "Type": "TRANSFER"
    }
    res = client.post("/api/module2/predict", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "delay_probability" in data["result"]
    assert 0.0 <= data["result"]["delay_probability"] <= 1.0
    assert abs(data["result"]["threshold"] - 0.36) < 0.01


def test_module2_predict_probability_override(client):
    payload = {"test_probability": 0.85}
    res = client.post("/api/module2/predict", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["result"]["predicted_late"] is True
    assert data["result"]["risk_level"] == "CRITICAL"


# -----------------------------------------------------------------------------
# MODULE 3 TESTS
# -----------------------------------------------------------------------------

def test_module3_traffic_unconfigured(client):
    res = client.post("/api/module3/traffic", json={"lat": 20.2961, "lon": 85.8245})
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "traffic" in data


def test_module3_route_valid(client):
    payload = {
        "origin": {"lat": 20.2961, "lon": 85.8245},
        "destination": {"lat": 20.4625, "lon": 85.8828},
        "k": 3
    }
    res = client.post("/api/module3/route", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "best_route" in data["result"]
    assert data["result"]["best_route"]["distance_km"] > 0


def test_module3_presets(client):
    res = client.get("/api/module3/presets")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert len(data["presets"]) >= 5


def test_module3_summary(client):
    res = client.get("/api/module3/summary")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "algorithms" in data["summary"]
    assert "vehicles" in data["summary"]


def test_module3_route_fleet_and_tsp(client):
    payload = {
        "origin": {"lat": 41.8781, "lon": -87.6298},
        "destination": {"lat": 42.3314, "lon": -83.0458},
        "vehicle_type": "ev_truck",
        "routing_mode": "eco",
        "waypoints": [
            {"name": "South Bend Hub", "lat": 41.6764, "lon": -86.2520},
            {"name": "Kalamazoo Drop", "lat": 42.2917, "lon": -85.5872}
        ]
    }
    res = client.post("/api/module3/route", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    result = data["result"]
    assert result["vehicle_profile"]["type"] == "ev_truck"
    assert result["tsp_solution"] is not None
    assert len(result["tsp_solution"]["ordered_waypoints"]) == 2
    assert result["best_route"]["co2_emissions_kg"] >= 0


def test_module3_route_invalid_coordinates(client):
    payload = {
        "origin": {"lat": 999.0, "lon": 85.8245},
        "destination": {"lat": 20.4625, "lon": 85.8828}
    }
    res = client.post("/api/module3/route", json=payload)
    assert res.status_code == 400


# -----------------------------------------------------------------------------
# MODULE 4 TESTS
# -----------------------------------------------------------------------------

def test_module4_summary(client):
    res = client.get("/api/module4/summary")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["summary"]["sequence_length"] == 12


def test_module4_predict_valid_sequence(client):
    observations = [
        {
            "hour": (8 + i) % 24,
            "dock_utilization": 0.5 + (i * 0.03),
            "order_volume": 250 + (i * 10),
            "staff_count": 16,
            "truck_arrivals": 12
        }
        for i in range(12)
    ]
    res = client.post("/api/module4/predict", json={"observations": observations})
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert 0.0 <= data["prediction"]["congestion_risk"] <= 1.0
    assert data["prediction"]["status"] in {"NORMAL", "MODERATE", "HEAVY", "CRITICAL"}


def test_module4_predict_insufficient_sequence(client):
    # Only 5 observations instead of required 12
    res = client.post("/api/module4/predict", json={"observations": [{"hour": 1}] * 5})
    assert res.status_code == 400


# -----------------------------------------------------------------------------
# MODULE 5 TESTS
# -----------------------------------------------------------------------------

def test_module5_summary(client):
    res = client.get("/api/module5/summary")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "summary" in data
    assert data["summary"]["policy"] == "s,S Continuous Review with Integer Batch Pack Rounding"
    assert "formulas" in data["summary"]


def test_module5_optimize_valid(client):
    payload = {
        "current_stock": 100,
        "forecast_daily_demand": 25,
        "lead_time_days": 4,
        "safety_stock_days": 3,
        "pack_size": 10
    }
    res = client.post("/api/module5/optimize", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["result"]["status"] == "REPLENISH"
    assert data["result"]["recommended_order_quantity"] > 0
    assert data["result"]["recommended_order_quantity"] % 10 == 0


def test_module5_optimize_invalid_negative_stock(client):
    payload = {
        "current_stock": -50,
        "forecast_daily_demand": 25,
        "lead_time_days": 4
    }
    res = client.post("/api/module5/optimize", json=payload)
    assert res.status_code == 400


# -----------------------------------------------------------------------------
# MODULE 6 TESTS
# -----------------------------------------------------------------------------

def test_module6_decide_prioritization(client):
    payload = {
        "delay_risk": 0.90,       # Breaches 0.85 -> EXPEDITE_AND_NOTIFY (CRITICAL)
        "congestion_risk": 0.65,  # Breaches 0.60 -> RESCHEDULE_WAREHOUSE_FLOW (HIGH)
        "route_risk": 0.10,
        "inventory_status": "HEALTHY"
    }
    res = client.post("/api/module6/decide", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["result"]["overall_status"] == "CRITICAL"
    assert data["result"]["primary_action"] == "EXPEDITE_AND_NOTIFY"
    assert data["result"]["requires_human_approval"] is True


def test_module6_decide_missing_inputs(client):
    payload = {
        "delay_risk": 0.20
        # congestion_risk, route_risk, inventory missing
    }
    res = client.post("/api/module6/decide", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert len(data["result"]["missing_inputs"]) > 0


# -----------------------------------------------------------------------------
# MODULE 7 TESTS
# -----------------------------------------------------------------------------

def test_module7_explain(client):
    decision_payload = {
        "overall_status": "CRITICAL",
        "primary_action": "EXPEDITE_AND_NOTIFY",
        "actions": [
            {
                "action": "EXPEDITE_AND_NOTIFY",
                "priority": "CRITICAL",
                "score": 0.92,
                "reason": "Delay probability is 92.0%.",
                "source_module": "Module 2",
                "condition_triggered": "delay_risk >= 0.85"
            }
        ],
        "inputs_used": {"delay_risk": 0.92},
        "missing_inputs": []
    }
    res = client.post("/api/module7/explain", json=decision_payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "action_breakdown" in data["explanation"]
    assert data["explanation"]["requires_human_approval"] is True


def test_module7_what_if_comparison(client):
    payload = {
        "current": {"delay_risk": 0.85, "congestion_risk": 0.80, "route_risk": 0.20},
        "scenario": {"delay_risk": 0.20, "congestion_risk": 0.30}
    }
    res = client.post("/api/module7/what-if", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    comp = data["result"]["comparison"]
    assert comp["risk_reduced"] is True
    assert comp["delta_percentage_points"] < 0
    assert "difference" in data["result"]
    assert "summary" in data["result"]


def test_module7_explain_frontend_direct_inputs(client):
    # Tests the exact payload sent by module7.html form
    frontend_payload = {
        "action": "EXPEDITE_AND_NOTIFY",
        "delay_risk": 0.88,
        "congestion_risk": 0.70
    }
    res = client.post("/api/module7/explain", json=frontend_payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    # Verify both 'result' and 'explanation' fields are populated for client compatibility
    assert "result" in data
    assert "explanation" in data
    assert "contributing_factors" in data["result"]
    assert len(data["result"]["contributing_factors"]) >= 2
    assert "action_breakdown" in data["result"]
    assert data["result"]["risk_level"] in ["CRITICAL", "HIGH"]
    assert data["result"]["requires_human_approval"] is True


def test_module6_invalid_risk_bounds(client):
    # Probabilities must be within [0, 1]
    bad_payload = {"delay_risk": 1.5}
    res = client.post("/api/module6/decide", json=bad_payload)
    assert res.status_code == 400

