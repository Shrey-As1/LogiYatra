"""Integration tests for LogiYantra Flask routes, page delivery, and health status."""
from pathlib import Path
import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"LogiYantra" in response.data


def test_login_page(client):
    response = client.get("/login.html")
    assert response.status_code == 200
    assert b"Sign In" in response.data


def test_dashboard_page(client):
    response = client.get("/dashboard.html")
    assert response.status_code == 200
    assert b"Control" in response.data and b"Tower" in response.data


def test_all_seven_module_pages(client):
    for i in range(1, 8):
        page = f"module{i}.html"
        response = client.get(f"/modules/{page}")
        assert response.status_code == 200, f"Page /modules/{page} failed with {response.status_code}"
        assert b"LogiYantra" in response.data


def test_static_assets(client):
    assets = [
        "/css/styles.css",
        "/css/dashboard.css",
        "/css/landing.css",
        "/css/modules.css",
        "/js/api.js",
        "/js/dashboard.js",
        "/js/landing-bg.js",
        "/css/chatbot.css",
        "/js/chatbot.js",
    ]
    for asset in assets:
        response = client.get(asset)
        assert response.status_code == 200, f"Asset {asset} failed with {response.status_code}"


def test_api_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "operational"
    assert "modules" in data
    assert len(data["modules"]) == 7
    # Verify no raw secrets are leaked
    response_text = response.data.decode("utf-8")
    assert "abc123xxxxxxxx" not in response_text


def test_auth_registration_company_key_required(client):
    # Registration fails when company key is missing or invalid
    payload = {
        "unit_name": "Fleet Ops",
        "full_name": "Agent Carter",
        "employee_id": "EMP-9999",
        "role": "Logistics Analyst",
        "password": "SecretPassword123!",
        "company_key": "WRONG_KEY"
    }
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 403
    assert b"Invalid Company Authorization Key" in res.data


def test_auth_registration_and_login_success(client):
    # Valid company key succeeds
    reg_payload = {
        "unit_name": "Rapid Response Logistics",
        "full_name": "Marcus Kane",
        "employee_id": "EMP-5050",
        "role": "Warehouse Flow Supervisor",
        "password": "SecurePassword#2026",
        "company_key": "LOGIYANTRA-AUTH-2026-Cntrl"
    }
    res = client.post("/api/auth/register", json=reg_payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True

    # Sign in with matching attributes
    login_payload = {
        "unit_name": "Rapid Response Logistics",
        "full_name": "Marcus Kane",
        "employee_id": "EMP-5050",
        "password": "SecurePassword#2026"
    }
    res_login = client.post("/api/auth/login", json=login_payload)
    assert res_login.status_code == 200
    assert res_login.get_json()["success"] is True


def test_assistant_chat_endpoints(client):
    # Greeting test
    res = client.post("/api/assistant/chat", json={"message": "hello"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "LogiBot" in data["reply"]

    # Model accuracy query test
    res_acc = client.post("/api/assistant/chat", json={"message": "what is the accuracy of all models?"})
    assert res_acc.status_code == 200
    data_acc = res_acc.get_json()
    assert data_acc["success"] is True
    assert len(data_acc["reply"]) > 20
    assert any(term in data_acc["reply"].lower() for term in ["demand", "forecast", "module", "accuracy", "xgboost", "lstm"])

    # Empty payload defaults to greeting
    res_empty = client.post("/api/assistant/chat", json={})
    assert res_empty.status_code == 200
    assert res_empty.get_json()["success"] is True
