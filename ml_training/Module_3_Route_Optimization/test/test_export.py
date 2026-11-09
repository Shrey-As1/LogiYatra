try:
    from src.route_service import RouteService
except ImportError:
    from ml_training.Module_3_Route_Optimization.src.route_service import RouteService



CENTER_LAT = 20.2961
CENTER_LON = 85.8245

ORIGIN_LAT = 20.2961
ORIGIN_LON = 85.8245

DESTINATION_LAT = 20.3300
DESTINATION_LON = 85.8200


print("\n" + "=" * 80)
print("MODULE 3 — RESULT EXPORT TEST")
print("=" * 80)


service = RouteService()

service.initialize(
    CENTER_LAT,
    CENTER_LON,
    radius=12000
)


result, filepath = (
    service.optimize_and_save(
        origin_lat=ORIGIN_LAT,
        origin_lon=ORIGIN_LON,
        destination_lat=DESTINATION_LAT,
        destination_lon=DESTINATION_LON,
        k=5,
        filename="route_result.json"
    )
)


print("\nBest route:")
print(
    result["best_route"]
)

print("\nFile:")
print(filepath)

print("\nExport test completed.")