try:
    from src.route_service import RouteService
except ImportError:
    from ml_training.Module_3_Route_Optimization.src.route_service import RouteService



# ============================================================
# CONFIGURATION
# ============================================================

CENTER_LAT = 20.2961
CENTER_LON = 85.8245

TEST_CASES = [
    {
        "name": "Test Route 1",
        "origin": {
            "lat": 20.2961,
            "lon": 85.8245
        },
        "destination": {
            "lat": 20.3300,
            "lon": 85.8200
        }
    },
    {
        "name": "Test Route 2",
        "origin": {
            "lat": 20.2961,
            "lon": 85.8245
        },
        "destination": {
            "lat": 20.2800,
            "lon": 85.8500
        }
    },
    {
        "name": "Test Route 3",
        "origin": {
            "lat": 20.2961,
            "lon": 85.8245
        },
        "destination": {
            "lat": 20.3150,
            "lon": 85.8700
        }
    }
]


# ============================================================
# INITIALIZE MODULE 3
# ============================================================

print("\n" + "=" * 80)
print("MODULE 3 — MULTI-ROUTE TEST")
print("=" * 80)

service = RouteService()

service.initialize(
    CENTER_LAT,
    CENTER_LON,
    radius=12000
)


# ============================================================
# RUN TESTS
# ============================================================

for test_case in TEST_CASES:

    print("\n")
    print("=" * 80)
    print(test_case["name"])
    print("=" * 80)

    origin = test_case["origin"]
    destination = test_case["destination"]

    try:

        result = service.optimize_route(
            origin_lat=origin["lat"],
            origin_lon=origin["lon"],
            destination_lat=destination["lat"],
            destination_lon=destination["lon"],
            k=5
        )

        best = result["best_route"]

        print("\nBEST ROUTE")
        print("-" * 80)

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
            "Delay:",
            best["delay_min"],
            "minutes"
        )

        print(
            "Average congestion:",
            round(
                best["average_congestion"] * 100,
                2
            ),
            "%"
        )

        print(
            "Maximum congestion:",
            round(
                best["maximum_congestion"] * 100,
                2
            ),
            "%"
        )

        print(
            "Traffic status:",
            best["traffic_status"]
        )

        print(
            "Road closure:",
            best["road_closure"]
        )

        print(
            "Route score:",
            best["route_score"]
        )

    except Exception as error:

        print(
            "ERROR:",
            error
        )


print("\n")
print("=" * 80)
print("MULTI-ROUTE TEST COMPLETED")
print("=" * 80)