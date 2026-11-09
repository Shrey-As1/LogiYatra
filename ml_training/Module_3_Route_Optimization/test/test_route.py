try:
    from src.route_service import RouteService
except ImportError:
    from ml_training.Module_3_Route_Optimization.src.route_service import RouteService



# ---------------------------------------------------------
# TEST LOCATION
# ---------------------------------------------------------

CENTER_LAT = 20.2961
CENTER_LON = 85.8245

# Example origin
ORIGIN_LAT = 20.2961
ORIGIN_LON = 85.8245

# Example destination
DESTINATION_LAT = 20.3300
DESTINATION_LON = 85.8200


# ---------------------------------------------------------
# INITIALIZE
# ---------------------------------------------------------

service = RouteService()

service.initialize(
    CENTER_LAT,
    CENTER_LON,
    radius=12000
)


# ---------------------------------------------------------
# OPTIMIZE
# ---------------------------------------------------------

result = service.optimize_route(
    origin_lat=ORIGIN_LAT,
    origin_lon=ORIGIN_LON,
    destination_lat=DESTINATION_LAT,
    destination_lon=DESTINATION_LON,
    k=5
)


# ---------------------------------------------------------
# DISPLAY
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("MODULE 3 — ROUTE OPTIMIZATION RESULT")
print("=" * 70)


best = result["best_route"]

print("\nBEST ROUTE")
print("-" * 70)

print(
    "Route Number:",
    best["route_number"]
)

print(
    "Distance:",
    best["distance_km"],
    "km"
)

print(
    "Free-flow ETA:",
    best["free_flow_eta_min"],
    "minutes"
)

print(
    "Traffic ETA:",
    best["traffic_eta_min"],
    "minutes"
)

print(
    "Traffic Delay:",
    best["delay_min"],
    "minutes"
)

print(
    "Average Congestion:",
    best["average_congestion"] * 100,
    "%"
)

print(
    "Maximum Congestion:",
    best["maximum_congestion"] * 100,
    "%"
)

print(
    "Traffic Status:",
    best["traffic_status"]
)

print(
    "Road Closure:",
    best["road_closure"]
)

print(
    "Route Score:",
    best["route_score"]
)


print("\n" + "=" * 70)
print("ALL CANDIDATE ROUTES")
print("=" * 70)


for route in result["alternatives"]:

    print(
        f"\nRoute {route['route_number']}"
    )

    print(
        "Distance:",
        route["distance_km"],
        "km"
    )

    print(
        "Traffic ETA:",
        route["traffic_eta_min"],
        "min"
    )

    print(
        "Congestion:",
        round(
            route[
                "average_congestion"
            ] * 100,
            2
        ),
        "%"
    )

    print(
        "Status:",
        route["traffic_status"]
    )

    print(
        "Score:",
        route["route_score"]
    )

