try:
    from src.traffic_api import TrafficAPI
    from src.traffic_processor import TrafficProcessor
except ImportError:
    from ml_training.Module_3_Route_Optimization.src.traffic_api import TrafficAPI
    from ml_training.Module_3_Route_Optimization.src.traffic_processor import TrafficProcessor



LATITUDE = 20.2961
LONGITUDE = 85.8245


api = TrafficAPI()

processor = TrafficProcessor()


print("\n" + "=" * 70)
print("MODULE 3 — REAL-TIME TRAFFIC TEST")
print("=" * 70)


flow = api.get_flow_segment(
    LATITUDE,
    LONGITUDE
)


result = processor.process(
    flow
)


print("\nTraffic Information")
print("-" * 70)

print(
    "Current Speed:",
    result["current_speed"],
    "km/h"
)

print(
    "Free Flow Speed:",
    result["free_flow_speed"],
    "km/h"
)

print(
    "Current Travel Time:",
    result["current_travel_time"],
    "seconds"
)

print(
    "Free Flow Travel Time:",
    result["free_flow_travel_time"],
    "seconds"
)

print(
    "Delay:",
    result["delay_seconds"],
    "seconds"
)

print(
    "Congestion:",
    result["congestion"] * 100,
    "%"
)

print(
    "Status:",
    result["status"]
)

print(
    "Confidence:",
    result["confidence"]
)

print(
    "Road Closure:",
    result["road_closure"]
)

print("\nTraffic test completed.")