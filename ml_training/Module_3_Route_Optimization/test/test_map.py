try:
    from src.map_loader import MapLoader
except ImportError:
    from ml_training.Module_3_Route_Optimization.src.map_loader import MapLoader



# Example test location
LATITUDE = 20.2961
LONGITUDE = 85.8245


loader = MapLoader()

graph = loader.load_graph(
    LATITUDE,
    LONGITUDE,
    radius=12000
)

print("\n" + "=" * 70)
print("MAP TEST")
print("=" * 70)

print("Graph loaded:", graph is not None)
print("Nodes:", len(graph.nodes))
print("Edges:", len(graph.edges))

sample_node = list(graph.nodes)[0]

print("\nSample node:")
print(sample_node)

sample_edge = list(graph.edges(data=True))[0]

print("\nSample edge:")
print(sample_edge)

print("\nMap test completed successfully.")