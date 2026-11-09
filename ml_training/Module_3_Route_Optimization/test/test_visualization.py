try:
    from src.route_service import RouteService
    from src.route_visualizer import RouteVisualizer
except ImportError:
    from ml_training.Module_3_Route_Optimization.src.route_service import RouteService
    from ml_training.Module_3_Route_Optimization.src.route_visualizer import RouteVisualizer



CENTER_LAT = 20.2961
CENTER_LON = 85.8245

ORIGIN = {
    "lat": 20.2961,
    "lon": 85.8245
}

DESTINATION = {
    "lat": 20.3300,
    "lon": 85.8200
}


print("\n" + "=" * 80)
print("MODULE 3 — ROUTE VISUALIZATION TEST")
print("=" * 80)


service = RouteService()

service.initialize(
    CENTER_LAT,
    CENTER_LON,
    radius=12000
)


result = service.optimize_route(
    origin_lat=ORIGIN["lat"],
    origin_lon=ORIGIN["lon"],
    destination_lat=DESTINATION["lat"],
    destination_lon=DESTINATION["lon"],
    k=5
)


best_route = result[
    "best_route"
]


visualizer = RouteVisualizer()

filepath = visualizer.create_map(
    route_coordinates=(
        best_route["coordinates"]
    ),
    origin=ORIGIN,
    destination=DESTINATION,
    filename="best_route.html"
)


print("\nBest route:")
print(
    best_route["route_number"]
)

print(
    "Distance:",
    best_route["distance_km"],
    "km"
)

print(
    "Traffic ETA:",
    best_route["traffic_eta_min"],
    "minutes"
)

print(
    "Congestion:",
    best_route[
        "average_congestion"
    ] * 100,
    "%"
)

print(
    "\nOpen:",
    filepath
)