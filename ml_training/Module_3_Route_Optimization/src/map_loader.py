import osmnx as ox


class MapLoader:

    def __init__(self):
        self.graph = None

    def load_graph(
        self,
        latitude,
        longitude,
        radius=12000
    ):
        print("\n" + "=" * 70)
        print("MODULE 3 — LOADING ROAD NETWORK")
        print("=" * 70)

        print(f"Center: {latitude}, {longitude}")
        print(f"Radius: {radius} meters")

        self.graph = ox.graph_from_point(
            (latitude, longitude),
            dist=radius,
            network_type="drive",
            simplify=True
        )

        print(
            f"Nodes loaded : {len(self.graph.nodes):,}"
        )

        print(
            f"Edges loaded : {len(self.graph.edges):,}"
        )

        # Add free-flow speed information
        self.graph = ox.add_edge_speeds(
            self.graph
        )

        # Add free-flow travel time
        self.graph = ox.add_edge_travel_times(
            self.graph
        )

        print("Free-flow speeds calculated.")
        print("Free-flow travel times calculated.")

        return self.graph

    def get_graph(self):
        return self.graph