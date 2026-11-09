"""LogiYantra — AI-Powered Autonomous Logistics Intelligence Backend.
Tagline: Think Smarter. Move Faster.

Shared Flask application serving the multipage frontend and 7 connected logistics modules.

Entrypoint:
    python app.py
"""
from __future__ import annotations

import json
import logging
import math
import os
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

FRONTEND_DIR = ROOT / "frontend"
TRAINING_DIR = ROOT / "ml_training"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("LogiYantra")

app = Flask(
    __name__,
    static_folder=str(FRONTEND_DIR),
    static_url_path=""
)
CORS(app)

# Service lazy singletons
_route_service = None
_route_graph_ready = False


def _json_error(message: str, status: int = 400):
    return jsonify({"success": False, "error": message}), status


def _get_route_service():
    global _route_service
    if _route_service is None:
        from ml_training.Module_3_Route_Optimization.src.route_service import RouteService
        _route_service = RouteService()
    return _route_service


def _get_module1_service():
    from services.module1_service import Module1Service
    return Module1Service.get_instance()


def _get_module2_service():
    from services.module2_service import Module2Service
    return Module2Service.get_instance()


def _get_module4_service():
    from services.module4_service import Module4Service
    return Module4Service.get_instance()


def _get_module7_service():
    from services.module7_service import Module7Service
    return Module7Service.get_instance()


# -----------------------------------------------------------------------------
# FRONTEND STATIC ROUTES
# -----------------------------------------------------------------------------

@app.get("/")
def home():
    return send_from_directory(str(FRONTEND_DIR), "index.html")


@app.get("/login.html")
def login_page():
    return send_from_directory(str(FRONTEND_DIR / "html"), "login.html")


@app.get("/dashboard.html")
def dashboard_page():
    return send_from_directory(str(FRONTEND_DIR / "html"), "dashboard.html")


@app.get("/modules/<page>")
def module_page(page: str):
    allowed = {
        "login.html", "dashboard.html", "presentation.html",
        "module1.html", "module2.html", "module3.html", "module4.html",
        "module5.html", "module6.html", "module7.html"
    }
    if page not in allowed:
        return _json_error(f"Page '{page}' not found.", 404)
    return send_from_directory(str(FRONTEND_DIR / "html"), page)


@app.get("/html/<page>")
def html_page(page: str):
    allowed = {
        "login.html", "dashboard.html", "presentation.html",
        "module1.html", "module2.html", "module3.html", "module4.html",
        "module5.html", "module6.html", "module7.html"
    }
    if page not in allowed:
        return _json_error(f"Page '{page}' not found.", 404)
    return send_from_directory(str(FRONTEND_DIR / "html"), page)


@app.get("/<page>")
def root_page(page: str):
    allowed = {
        "login.html", "dashboard.html", "presentation.html",
        "module1.html", "module2.html", "module3.html", "module4.html",
        "module5.html", "module6.html", "module7.html"
    }
    if page in allowed:
        return send_from_directory(str(FRONTEND_DIR / "html"), page)
    # Check if file exists in root FRONTEND_DIR
    if (FRONTEND_DIR / page).is_file():
        return send_from_directory(str(FRONTEND_DIR), page)
    return _json_error(f"Page '{page}' not found.", 404)


# -----------------------------------------------------------------------------
# SYSTEM HEALTH & READINESS ENDPOINT
# -----------------------------------------------------------------------------

@app.get("/api/health")
def health():
    m1_ready = (TRAINING_DIR / "Module_1_Demand_Forecasting" / "ALIP_Demand_Models" / "demand_xgb.json").exists()
    m2_ready = (TRAINING_DIR / "Module_2_Delivery_Delay" / "models" / "dataco_xgboost_model.pkl").exists()
    m3_ready = (TRAINING_DIR / "Module_3_Route_Optimization" / "src" / "route_service.py").exists()
    m4_ready = (TRAINING_DIR / "Module_4_warehouse_congestion" / "models" / "congestion_lstm.keras").exists()
    m5_ready = (TRAINING_DIR / "Module_5_Inventory_Optimization" / "inventory_optimizer.py").exists()
    m6_ready = (TRAINING_DIR / "Module_6_Decision_Engine" / "decision_engine.py").exists()
    m7_ready = (TRAINING_DIR / "Module_7_Explainability" / "what_if.py").exists()

    tomtom_key = os.getenv("TOMTOM_API_KEY", "").strip()
    tomtom_active = bool(tomtom_key and tomtom_key not in {"abc123xxxxxxxx", "your_tomtom_api_key_here"})

    return jsonify({
        "project": "LogiYantra — AI-Powered Autonomous Logistics Intelligence",
        "tagline": "Think Smarter. Move Faster.",
        "status": "operational",
        "modules": {
            "module_1": {"name": "Demand Forecasting", "status": "ready" if m1_ready else "missing_artifact"},
            "module_2": {"name": "Delivery Delay Prediction", "status": "ready" if m2_ready else "missing_artifact"},
            "module_3": {"name": "Route Optimization & Traffic", "status": "ready" if m3_ready else "missing_artifact"},
            "module_4": {"name": "Warehouse Congestion", "status": "ready" if m4_ready else "missing_artifact"},
            "module_5": {"name": "Inventory Optimization", "status": "ready" if m5_ready else "missing_artifact"},
            "module_6": {"name": "Autonomous Decision Engine", "status": "ready" if m6_ready else "missing_artifact"},
            "module_7": {"name": "Explainable AI & What-If", "status": "ready" if m7_ready else "missing_artifact"},
        },
        "providers": {
            "tomtom_live_traffic": {
                "configured": tomtom_active,
                "status": "connected" if tomtom_active else "offline_using_osm_corridor_fallback"
            },
            "osm_road_network": {"status": "available"}
        }
    })


# -----------------------------------------------------------------------------
# MODULE 1 — DEMAND FORECASTING
# -----------------------------------------------------------------------------

@app.get("/api/module1/summary")
def module1_summary():
    try:
        service = _get_module1_service()
        summary = service.get_summary()
        return jsonify({"success": True, "module": 1, "summary": summary})
    except Exception as exc:
        logger.exception("Module 1 summary failed")
        return _json_error(f"Module 1 summary unavailable: {exc}", 500)


@app.post("/api/module1/predict")
def module1_predict():
    data = request.get_json(silent=True) or {}
    try:
        service = _get_module1_service()
        result = service.predict(data)
        return jsonify({"success": True, "module": 1, "result": result})
    except ValueError as exc:
        return _json_error(str(exc), 400)
    except Exception as exc:
        logger.exception("Module 1 prediction error")
        return _json_error(f"Demand forecasting failed: {exc}", 500)


# -----------------------------------------------------------------------------
# MODULE 2 — DELIVERY DELAY PREDICTION
# -----------------------------------------------------------------------------

@app.get("/api/module2/summary")
def module2_summary():
    try:
        service = _get_module2_service()
        summary = service.get_summary()
        return jsonify({"success": True, "module": 2, "summary": summary})
    except Exception as exc:
        logger.exception("Module 2 summary error")
        return _json_error(f"Module 2 summary unavailable: {exc}", 500)


@app.post("/api/module2/predict")
def module2_predict():
    data = request.get_json(silent=True) or {}
    try:
        service = _get_module2_service()
        result = service.predict(data)
        return jsonify({"success": True, "module": 2, "result": result})
    except ValueError as exc:
        return _json_error(str(exc), 400)
    except Exception as exc:
        logger.exception("Module 2 prediction error")
        return _json_error(f"Delivery delay prediction failed: {exc}", 500)


# -----------------------------------------------------------------------------
# MODULE 3 — ROUTE OPTIMIZATION & TRAFFIC
# -----------------------------------------------------------------------------

@app.post("/api/module3/traffic")
def module3_traffic():
    data = request.get_json(silent=True) or {}
    if "lat" not in data or "lon" not in data:
        return _json_error("Request must include numeric lat and lon coordinates.")
    try:
        lat, lon = float(data["lat"]), float(data["lon"])
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            return _json_error("Latitude/longitude values are out of bounds.")
        service = _get_route_service()
        traffic = service.get_traffic(lat, lon)
        return jsonify({"success": True, "module": 3, "traffic": traffic})
    except ValueError as exc:
        return _json_error(str(exc), 400)
    except Exception as exc:
        logger.exception("Module 3 traffic error")
        return _json_error(f"Traffic query failed: {exc}", 502)


@app.get("/api/module3/presets")
def module3_presets():
    """Returns curated high-volume freight logistics corridors."""
    presets = [
        {
            "id": "chicago_detroit",
            "name": "Midwest Auto Corridor (Chicago ➔ Detroit)",
            "origin": {"name": "Chicago Intermodal Hub, IL", "lat": 41.8781, "lon": -87.6298},
            "destination": {"name": "Detroit Assembly Center, MI", "lat": 42.3314, "lon": -83.0458},
            "typical_corridor": "I-94 Interstate Freight Highway",
            "distance_approx_km": 455
        },
        {
            "id": "la_ontario",
            "name": "Port of LA ➔ Ontario Inland Empire Hub",
            "origin": {"name": "Port of Los Angeles / San Pedro, CA", "lat": 33.7432, "lon": -118.2673},
            "destination": {"name": "Ontario Inland Logistics Park, CA", "lat": 34.0633, "lon": -117.6509},
            "typical_corridor": "I-710 / I-10 Intermodal Corridor",
            "distance_approx_km": 95
        },
        {
            "id": "dallas_houston",
            "name": "Texas Triangle Freight (Dallas ➔ Houston)",
            "origin": {"name": "Dallas-Fort Worth Freight Center, TX", "lat": 32.7767, "lon": -96.7970},
            "destination": {"name": "Port of Houston Terminal, TX", "lat": 29.7604, "lon": -95.3698},
            "typical_corridor": "I-45 Heavy Freight Corridor",
            "distance_approx_km": 385
        },
        {
            "id": "mumbai_pune",
            "name": "Western India Freight (JNPT Port ➔ Pune Chakan)",
            "origin": {"name": "Jawaharlal Nehru Port (JNPT), Mumbai", "lat": 18.9499, "lon": 72.9515},
            "destination": {"name": "Chakan Industrial Hub, Pune", "lat": 18.7606, "lon": 73.8636},
            "typical_corridor": "Mumbai-Pune Expressway / NH-48",
            "distance_approx_km": 140
        },
        {
            "id": "frankfurt_rotterdam",
            "name": "Euro-Rhine Corridor (Frankfurt ➔ Rotterdam)",
            "origin": {"name": "Frankfurt Airport CargoCity, Germany", "lat": 50.0379, "lon": 8.5622},
            "destination": {"name": "Port of Rotterdam (Maasvlakte), Netherlands", "lat": 51.9244, "lon": 4.4777},
            "typical_corridor": "A3 / A12 Trans-European Freight Network",
            "distance_approx_km": 460
        }
    ]
    return jsonify({"success": True, "module": 3, "presets": presets})


@app.get("/api/module3/summary")
def module3_summary():
    """Returns Module 3 algorithms, vehicle profiles, and environmental models."""
    from ml_training.Module_3_Route_Optimization.src.route_service import (
        VEHICLE_PROFILES, WEATHER_IMPACTS, DEPARTURE_MODELS
    )
    summary = {
        "engine": "LogiYantra Multi-Objective Fleet & Corridor Optimizer",
        "algorithms": {
            "Dijkstra": "Guaranteed shortest path with edge travel-time weights.",
            "A*": "Directed search utilizing Haversine distance heuristic towards destination.",
            "Yen K-Shortest Paths": "Calculates k distinct corridors with edge diversity enforcement.",
            "TSP 2-Opt": "Sequences intermediate multi-stop delivery waypoints for minimum total mileage."
        },
        "vehicles": VEHICLE_PROFILES,
        "weather_models": WEATHER_IMPACTS,
        "departure_windows": DEPARTURE_MODELS,
        "environmental_standards": {
            "diesel_emission_factor": "2.68 kg CO2 / Liter diesel",
            "ev_grid_emission_factor": "0.05 kg CO2 / kWh average commercial grid"
        }
    }
    return jsonify({"success": True, "module": 3, "summary": summary})


@app.post("/api/module3/route")
def module3_route():
    data = request.get_json(silent=True) or {}
    try:
        # Flexible payload parsing: accepts nested or flat coordinate keys
        if "origin" in data and "destination" in data:
            origin = data["origin"]
            dest = data["destination"]
            origin_lat = float(origin.get("lat", origin.get("latitude", 0)))
            origin_lon = float(origin.get("lon", origin.get("longitude", 0)))
            dest_lat = float(dest.get("lat", dest.get("latitude", 0)))
            dest_lon = float(dest.get("lon", dest.get("longitude", 0)))
        elif "origin_lat" in data and "origin_lon" in data:
            origin_lat = float(data["origin_lat"])
            origin_lon = float(data["origin_lon"])
            dest_lat = float(data.get("dest_lat", data.get("destination_lat", 0)))
            dest_lon = float(data.get("dest_lon", data.get("destination_lon", 0)))
        else:
            return _json_error("Request requires origin and destination coordinates (nested {origin, destination} or flat {origin_lat, origin_lon, dest_lat, dest_lon}).")

        k = max(1, min(int(data.get("k", 3)), 5))
        algorithm = str(data.get("algorithm", "Yen K-Shortest Paths"))
        vehicle_type = str(data.get("vehicle_type", "semi_truck"))
        routing_mode = str(data.get("routing_mode", "fastest"))
        departure_time = str(data.get("departure_time", "now"))
        weather = str(data.get("weather", "clear"))
        waypoints = data.get("waypoints") or []
        use_live_osrm = bool(data.get("use_live_osrm", False))

        service = _get_route_service()
        result = service.optimize_route(
            origin_lat=origin_lat, origin_lon=origin_lon,
            destination_lat=dest_lat, destination_lon=dest_lon,
            k=k, algorithm=algorithm,
            vehicle_type=vehicle_type, routing_mode=routing_mode,
            departure_time=departure_time, weather=weather,
            waypoints=waypoints, use_live_osrm=use_live_osrm
        )
        # Enrich result with top-level routes list and algorithm info for frontend convenience
        if "routes" not in result:
            all_routes = []
            if "best_route" in result and result["best_route"]:
                all_routes.append(result["best_route"])
            if "alternatives" in result and isinstance(result["alternatives"], list):
                all_routes.extend(result["alternatives"])
            result["routes"] = all_routes

        result["algorithm"] = algorithm
        result["provider"] = result.get("data_source", "LogiYantra Routing Engine")

        return jsonify({"success": True, "module": 3, "result": result})
    except (KeyError, TypeError, ValueError) as exc:
        return _json_error(f"Invalid coordinate parameters: {exc}", 400)
    except Exception as exc:
        logger.exception("Module 3 route error")
        return _json_error(f"Route optimization failed: {exc}", 502)


# -----------------------------------------------------------------------------
# MODULE 4 — WAREHOUSE CONGESTION PREDICTION
# -----------------------------------------------------------------------------

@app.get("/api/module4/summary")
def module4_summary():
    try:
        service = _get_module4_service()
        return jsonify({"success": True, "module": 4, "summary": service.get_summary()})
    except Exception as exc:
        return _json_error(f"Module 4 summary unavailable: {exc}", 500)


@app.post("/api/module4/predict")
def module4_predict():
    data = request.get_json(silent=True) or {}
    observations = data.get("observations")
    if not isinstance(observations, list):
        # Allow single snapshot payload by broadcasting across 12 temporal steps
        if any(k in data for k in ("dock_utilization", "order_volume", "truck_arrivals")):
            dock = float(data.get("dock_utilization", 0.5))
            orders = float(data.get("order_volume", 100))
            trucks = float(data.get("truck_arrivals", 10))
            observations = [
                {
                    "dock_utilization": max(0.0, min(1.0, dock + (i - 6) * 0.02)),
                    "order_volume": max(0.0, orders + (i - 6) * 3),
                    "truck_arrivals": max(0.0, trucks + (i - 6) * 0.5),
                    "burst_event": 1 if i >= 9 and dock > 0.75 else 0,
                    "trucks_per_staff": trucks / 5.0,
                    "orders_per_staff": orders / 20.0,
                    "shift_change": 1 if i % 3 == 0 else 0,
                    "hour_cos": math.cos(2 * math.pi * i / 12)
                }
                for i in range(12)
            ]
        else:
            return _json_error("Provide 'observations' (list of 12 sequential hourly readings) or snapshot metrics (dock_utilization, order_volume, truck_arrivals).")
    elif len(observations) < 12:
        return _json_error("Provide 'observations' as a list of at least 12 sequential warehouse hourly records.")

    try:
        service = _get_module4_service()
        mitigation = data.get("mitigation")
        result = service.predict(observations, mitigation=mitigation)
        return jsonify({"success": True, "module": 4, "prediction": result, "result": result})
    except ValueError as exc:
        return _json_error(str(exc), 400)
    except Exception as exc:
        logger.exception("Module 4 prediction error")
        return _json_error(f"Warehouse congestion prediction failed: {exc}", 500)


# -----------------------------------------------------------------------------
# MODULE 5 — INVENTORY OPTIMIZATION
# -----------------------------------------------------------------------------

@app.get("/api/module5/summary")
def module5_summary():
    try:
        config_path = TRAINING_DIR / "Module_5_Inventory_Optimization" / "config.json"
        defaults = json.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}
        summary = {
            "model_type": "Continuous Review (s, S) Operations Research Inventory Engine",
            "policy": "s,S Continuous Review with Integer Batch Pack Rounding",
            "upstream_integration": "Module 1 Demand Forecasting (Automated daily demand consumption)",
            "downstream_integration": "Module 6 Autonomous Decision Engine & Module 7 What-If Simulator",
            "defaults": defaults,
            "formulas": {
                "safety_stock": "forecast_daily_demand * safety_stock_days",
                "reorder_point": "(forecast_daily_demand * lead_time_days) + safety_stock",
                "target_stock": "forecast_daily_demand * (lead_time_days + safety_stock_days + review_period_days)",
                "recommended_order_quantity": "ceil(max(0, target_stock - current_stock) / pack_size) * pack_size",
                "days_of_supply": "current_stock / forecast_daily_demand"
            },
            "status_thresholds": {
                "critical": "current_stock <= safety_stock (Immediate Expedite)",
                "replenish": "current_stock <= reorder_point (Standard Reorder)",
                "healthy": "current_stock > reorder_point (Adequate Coverage)"
            }
        }
        return jsonify({"success": True, "module": 5, "summary": summary})
    except Exception as exc:
        logger.exception("Module 5 summary failed")
        return _json_error(f"Module 5 summary unavailable: {exc}", 500)


@app.post("/api/module5/optimize")
def module5_optimize():
    data = request.get_json(silent=True) or {}
    try:
        from ml_training.Module_5_Inventory_Optimization.inventory_optimizer import optimize_inventory
        result = optimize_inventory(data)
        return jsonify({"success": True, "module": 5, "result": result})
    except (KeyError, TypeError, ValueError) as exc:
        return _json_error(str(exc), 400)
    except Exception as exc:
        logger.exception("Inventory optimization failed")
        return _json_error(f"Inventory optimization failed: {exc}", 500)


# -----------------------------------------------------------------------------
# MODULE 6 — AUTONOMOUS DECISION ENGINE
# -----------------------------------------------------------------------------

@app.post("/api/module6/decide")
def module6_decide():
    data = request.get_json(silent=True) or {}
    try:
        from ml_training.Module_6_Decision_Engine.decision_engine import DecisionEngine
        policies_path = TRAINING_DIR / "Module_6_Decision_Engine" / "policies.json"
        policies = json.loads(policies_path.read_text(encoding="utf-8")) if policies_path.exists() else {}
        policies = {k: v for k, v in policies.items() if isinstance(v, (int, float))}

        stock = data.get("stock_level") if data.get("stock_level") is not None else data.get("current_stock")
        rop = data.get("reorder_point")
        inv_stat = data.get("inventory_status")
        if not inv_stat and stock is not None and rop is not None:
            try:
                if float(stock) <= float(rop) * 0.5:
                    inv_stat = "CRITICAL_REPLENISH"
                elif float(stock) <= float(rop):
                    inv_stat = "REPLENISH"
            except (ValueError, TypeError):
                pass

        engine = DecisionEngine(policies)
        result = engine.evaluate(
            delay_risk=data.get("delay_risk"),
            congestion_risk=data.get("congestion_risk"),
            route_risk=data.get("route_risk"),
            inventory_status=inv_stat,
            stock_level=stock,
            reorder_point=rop,
            route_alternatives=data.get("route_alternatives"),
            inventory_result=data.get("inventory_result")
        )
        return jsonify({"success": True, "module": 6, "result": result})
    except (TypeError, ValueError) as exc:
        return _json_error(str(exc), 400)
    except Exception as exc:
        logger.exception("Decision engine evaluation error")
        return _json_error(f"Decision evaluation failed: {exc}", 500)


# -----------------------------------------------------------------------------
# MODULE 7 — EXPLAINABLE AI & WHAT-IF ENGINE
# -----------------------------------------------------------------------------

@app.post("/api/module7/explain")
def module7_explain():
    data = request.get_json(silent=True) or {}
    try:
        service = _get_module7_service()
        # Accept either complete decision dictionary or direct params
        decision = data.get("decision", data)
        explanation = service.explain_decision(decision)
        return jsonify({"success": True, "module": 7, "explanation": explanation, "result": explanation})
    except ValueError as exc:
        return _json_error(str(exc), 400)
    except Exception as exc:
        logger.exception("Module 7 explain error")
        return _json_error(f"Decision explanation failed: {exc}", 500)


@app.route("/api/module7/what-if", methods=["POST"])
@app.route("/api/module7/whatif", methods=["POST"])
def module7_what_if():
    data = request.get_json(silent=True) or {}
    baseline = data.get("current") or data.get("baseline") or data.get("base_inputs")
    scenario = data.get("scenario") or data.get("scenario_inputs")
    if not isinstance(baseline, dict) or not isinstance(scenario, dict):
        return _json_error("Request requires baseline/current state and scenario changes dictionaries.")
    try:
        service = _get_module7_service()
        result = service.simulate_what_if(baseline, scenario)
        return jsonify({"success": True, "module": 7, "result": result})
    except ValueError as exc:
        return _json_error(str(exc), 400)
    except Exception as exc:
        logger.exception("What-if analysis error")
        return _json_error(f"What-if simulation failed: {exc}", 500)


# -----------------------------------------------------------------------------
# END-TO-END PIPELINE ORCHESTRATION
# -----------------------------------------------------------------------------

@app.post("/api/pipeline/run")
def run_pipeline():
    data = request.get_json(silent=True) or {}
    try:
        from services.module5_6_7_service import PipelineService
        pipeline = PipelineService.get_instance()
        result = pipeline.run_pipeline(data)
        return jsonify({"success": True, "pipeline": result})
    except Exception as exc:
        logger.exception("Pipeline execution failed")
        return _json_error(f"Pipeline execution failed: {exc}", 500)


# -----------------------------------------------------------------------------
# AI LOGISTICS ASSISTANT / COPILOT ENDPOINT
# -----------------------------------------------------------------------------

@app.route("/api/assistant/chat", methods=["POST", "OPTIONS"])
def assistant_chat():
    if request.method == "OPTIONS":
        return "", 204
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    history = data.get("history", [])
    try:
        from services.chatbot_service import ChatbotService
        service = ChatbotService.get_instance()
        response = service.process_message(message, history)
        return jsonify(response)
    except Exception as exc:
        logger.exception("Assistant chat error")
        return _json_error(f"Assistant processing error: {exc}", 500)


# -----------------------------------------------------------------------------
# AUTHENTICATION & REGISTRATION ENDPOINTS
# -----------------------------------------------------------------------------

# In-memory storage with initial default admin/operator accounts for testing
_REGISTERED_USERS: Dict[str, Dict[str, Any]] = {
    "EMP-1001": {
        "unit_name": "Fleet Operations HQ",
        "full_name": "Chief Dispatcher",
        "employee_id": "EMP-1001",
        "role": "Operations Controller",
        "password": "Password123!"
    }
}


@app.post("/api/auth/register")
def register_user():
    data = request.get_json(silent=True) or {}
    unit_name = str(data.get("unit_name", "")).strip()
    full_name = str(data.get("full_name", "")).strip()
    employee_id = str(data.get("employee_id", "")).strip()
    role = str(data.get("role", "")).strip()
    password = str(data.get("password", ""))
    company_key = str(data.get("company_key", "")).strip()

    if not (unit_name and full_name and employee_id and role and password):
        return _json_error("All registration fields (Team/Unit, Full Name, Employee ID, Role, Password) are required.", 400)

    expected_key = os.getenv("LOGIYANTRA_COMPANY_AUTH_KEY", "LOGIYANTRA-AUTH-2026-Cntrl").strip()

    # Company authorization key verification (only LOGIYANTRA-AUTH-2026-Cntrl allowed)
    if not company_key:
        return _json_error("Registration rejected: Company Authorization Key is required for instant onboarding.", 403)

    if company_key.strip() != expected_key:
        return _json_error("Invalid Company Authorization Key. Contact your logistics administrator.", 403)

    if employee_id in _REGISTERED_USERS:
        return _json_error(f"Employee ID '{employee_id}' is already registered.", 409)

    _REGISTERED_USERS[employee_id] = {
        "unit_name": unit_name,
        "full_name": full_name,
        "employee_id": employee_id,
        "role": role,
        "password": password
    }

    logger.info("New employee registered: %s (%s, %s)", employee_id, full_name, role)

    return jsonify({
        "success": True,
        "message": "Company authorization verified. Account successfully activated.",
        "user": {
            "unit_name": unit_name,
            "full_name": full_name,
            "employee_id": employee_id,
            "role": role
        }
    })


@app.post("/api/auth/login")
def login_user():
    data = request.get_json(silent=True) or {}
    unit_name = str(data.get("unit_name", "")).strip()
    full_name = str(data.get("full_name", "")).strip()
    employee_id = str(data.get("employee_id", "")).strip()
    password = str(data.get("password", ""))

    if not (unit_name and full_name and employee_id and password):
        return _json_error("All sign-in fields (Team/Unit Name, Employee Full Name, Employee ID, Password) are required.", 400)

    user = _REGISTERED_USERS.get(employee_id)
    if not user:
        return _json_error(f"No account found for Employee ID '{employee_id}'. Please register first.", 404)

    # Check credentials
    if user["password"] != password:
        return _json_error("Incorrect password.", 401)

    if user["unit_name"].lower() != unit_name.lower():
        return _json_error(f"Assigned Team/Unit does not match records for Employee ID '{employee_id}'.", 401)

    if user["full_name"].lower() != full_name.lower():
        return _json_error(f"Full name does not match records for Employee ID '{employee_id}'.", 401)

    logger.info("Employee signed in: %s (%s)", employee_id, user["full_name"])

    return jsonify({
        "success": True,
        "message": "Authentication successful.",
        "user": {
            "unit_name": user["unit_name"],
            "full_name": user["full_name"],
            "employee_id": user["employee_id"],
            "role": user.get("role", "Logistics Analyst")
        }
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    debug_mode = os.getenv("FLASK_DEBUG", "0") == "1"
    print("\n" + "=" * 70)
    print("  LOGIYANTRA — AI-Powered Autonomous Logistics Intelligence")
    print("  Tagline: Think Smarter. Move Faster.")
    print("=" * 70)
    print(f"  Server URL:    http://127.0.0.1:{port}")
    print(f"  Health Status: http://127.0.0.1:{port}/api/health")
    print("=" * 70 + "\n")
    app.run(host="127.0.0.1", port=port, debug=debug_mode)
