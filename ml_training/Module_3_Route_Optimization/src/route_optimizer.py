import math
import networkx as nx
import osmnx as ox


class RouteOptimizer:

    def __init__(
        self,
        graph,
        traffic_api,
        traffic_processor
    ):

        self.graph = graph
        self.traffic_api = traffic_api
        self.traffic_processor = traffic_processor

    # ---------------------------------------------------------
    # BASIC GRAPH
    # ---------------------------------------------------------

    def create_simple_graph(self):

        simple_graph = nx.DiGraph()

        for node, data in self.graph.nodes(
            data=True
        ):

            simple_graph.add_node(
                node,
                **data
            )

        for u, v, data in self.graph.edges(
            data=True
        ):

            travel_time = data.get(
                "travel_time",
                float("inf")
            )

            length = data.get(
                "length",
                0
            )

            if not simple_graph.has_edge(
                u,
                v
            ):

                simple_graph.add_edge(
                    u,
                    v,
                    length=length,
                    travel_time=travel_time
                )

            else:

                existing = simple_graph[
                    u
                ][v]

                if travel_time < existing[
                    "travel_time"
                ]:

                    simple_graph[u][v] = {
                        "length": length,
                        "travel_time": travel_time
                    }

        return simple_graph

    # ---------------------------------------------------------
    # FIND K CANDIDATE ROUTES
    # ---------------------------------------------------------

    def find_candidate_routes(
        self,
        origin_lat,
        origin_lon,
        destination_lat,
        destination_lon,
        k=5
    ):

        simple_graph = (
            self.create_simple_graph()
        )

        origin_node = ox.distance.nearest_nodes(
            self.graph,
            X=origin_lon,
            Y=origin_lat
        )

        destination_node = (
            ox.distance.nearest_nodes(
                self.graph,
                X=destination_lon,
                Y=destination_lat
            )
        )

        try:

            paths = nx.shortest_simple_paths(
                simple_graph,
                origin_node,
                destination_node,
                weight="travel_time"
            )

        except nx.NetworkXNoPath:

            raise ValueError(
                "No route exists between "
                "origin and destination."
            )

        candidates = []

        for index, path in enumerate(paths):

            if index >= k:
                break

            candidates.append(path)

        return candidates

    # ---------------------------------------------------------
    # ROUTE DISTANCE
    # ---------------------------------------------------------

    def calculate_distance(
        self,
        route
    ):

        total_length = 0.0

        for u, v in zip(
            route[:-1],
            route[1:]
        ):

            edge_data = self.graph[
                u
            ][v]

            best_edge = min(
                edge_data.values(),
                key=lambda x: x.get(
                    "length",
                    float("inf")
                )
            )

            total_length += (
                best_edge.get(
                    "length",
                    0
                )
            )

        return total_length / 1000

    # ---------------------------------------------------------
    # FREE FLOW ETA
    # ---------------------------------------------------------

    def calculate_free_flow_time(
        self,
        route
    ):

        total_seconds = 0.0

        for u, v in zip(
            route[:-1],
            route[1:]
        ):

            edge_data = self.graph[
                u
            ][v]

            best_edge = min(
                edge_data.values(),
                key=lambda x: x.get(
                    "travel_time",
                    float("inf")
                )
            )

            total_seconds += (
                best_edge.get(
                    "travel_time",
                    0
                )
            )

        return total_seconds

    # ---------------------------------------------------------
    # SAMPLE ROUTE POINTS
    # ---------------------------------------------------------

    def sample_route_points(
        self,
        route,
        max_samples=8
    ):

        if len(route) <= max_samples:

            indices = range(
                len(route)
            )

        else:

            step = (
                len(route) - 1
            ) / (
                max_samples - 1
            )

            indices = [
                round(i * step)
                for i in range(
                    max_samples
                )
            ]

        points = []

        for index in indices:

            node = route[index]

            latitude = self.graph.nodes[
                node
            ]["y"]

            longitude = self.graph.nodes[
                node
            ]["x"]

            points.append(
                (
                    latitude,
                    longitude
                )
            )

        return points

    # ---------------------------------------------------------
    # REAL-TIME TRAFFIC
    # ---------------------------------------------------------

    def analyze_route_traffic(
        self,
        route
    ):

        points = (
            self.sample_route_points(
                route
            )
        )

        traffic_results = []

        for latitude, longitude in points:

            try:

                flow = (
                    self.traffic_api
                    .get_flow_segment(
                        latitude,
                        longitude
                    )
                )

                processed = (
                    self.traffic_processor
                    .process(flow)
                )

                traffic_results.append(
                    processed
                )

            except Exception as error:

                print(
                    "Traffic request failed:",
                    error
                )

        if not traffic_results:

            return {
                "average_congestion": 0.0,
                "maximum_congestion": 0.0,
                "traffic_delay_seconds": 0.0,
                "road_closure": False,
                "traffic_status": "UNKNOWN",
                "samples": []
            }

        congestions = [
            item["congestion"]
            for item in traffic_results
        ]

        delays = [
            item["delay_seconds"]
            for item in traffic_results
            if item["delay_seconds"]
            is not None
        ]

        closures = [
            item["road_closure"]
            for item in traffic_results
        ]

        average_congestion = (
            sum(congestions)
            / len(congestions)
        )

        maximum_congestion = max(
            congestions
        )

        average_delay = (
            sum(delays)
            / len(delays)
            if delays
            else 0.0
        )

        road_closure = any(
            closures
        )

        if road_closure:

            status = "CLOSED"

        elif average_congestion < 0.20:

            status = "NORMAL"

        elif average_congestion < 0.50:

            status = "MODERATE"

        elif average_congestion < 0.75:

            status = "HEAVY"

        else:

            status = "SEVERE"

        return {
            "average_congestion":
                round(
                    average_congestion,
                    4
                ),

            "maximum_congestion":
                round(
                    maximum_congestion,
                    4
                ),

            "traffic_delay_seconds":
                round(
                    average_delay,
                    2
                ),

            "road_closure":
                road_closure,

            "traffic_status":
                status,

            "samples":
                traffic_results
        }

    # ---------------------------------------------------------
    # ROUTE SCORE
    # ---------------------------------------------------------

    def calculate_route_score(
        self,
        distance_km,
        free_flow_time_seconds,
        traffic_data
    ):

        congestion = (
            traffic_data[
                "average_congestion"
            ]
        )

        delay = (
            traffic_data[
                "traffic_delay_seconds"
            ]
        )

        closure = (
            traffic_data[
                "road_closure"
            ]
        )

        # Normalize approximate quantities
        distance_score = (
            distance_km / 20
        )

        time_score = (
            free_flow_time_seconds
            / 3600
        )

        delay_score = (
            delay / 1800
        )

        congestion_score = (
            congestion
        )

        closure_penalty = (
            100
            if closure
            else 0
        )

        score = (
            0.20 * distance_score
            + 0.25 * time_score
            + 0.30 * congestion_score
            + 0.25 * delay_score
            + closure_penalty
        )

        return round(
            score,
            4
        )

    # ---------------------------------------------------------
    # BEST ROUTE
    # ---------------------------------------------------------

    def optimize(
        self,
        origin_lat,
        origin_lon,
        destination_lat,
        destination_lon,
        k=5
    ):

        candidates = (
            self.find_candidate_routes(
                origin_lat,
                origin_lon,
                destination_lat,
                destination_lon,
                k=k
            )
        )

        results = []

        for route_number, route in enumerate(
            candidates,
            start=1
        ):

            print(
                f"\nAnalyzing candidate route "
                f"{route_number}/{len(candidates)}..."
            )

            distance_km = (
                self.calculate_distance(
                    route
                )
            )

            free_flow_time = (
                self.calculate_free_flow_time(
                    route
                )
            )

            traffic_data = (
                self.analyze_route_traffic(
                    route
                )
            )

            score = (
                self.calculate_route_score(
                    distance_km,
                    free_flow_time,
                    traffic_data
                )
            )

            coordinates = []

            for node in route:

                latitude = (
                    self.graph.nodes[
                        node
                    ]["y"]
                )

                longitude = (
                    self.graph.nodes[
                        node
                    ]["x"]
                )

                coordinates.append(
                    [
                        latitude,
                        longitude
                    ]
                )

            traffic_delay = (
                traffic_data[
                    "traffic_delay_seconds"
                ]
            )

            traffic_eta = (
                free_flow_time
                + traffic_delay
            )

            results.append(
                {
                    "route_number":
                        route_number,

                    "coordinates":
                        coordinates,

                    "nodes":
                        len(route),

                    "distance_km":
                        round(
                            distance_km,
                            3
                        ),

                    "free_flow_eta_min":
                        round(
                            free_flow_time
                            / 60,
                            2
                        ),

                    "traffic_eta_min":
                        round(
                            traffic_eta
                            / 60,
                            2
                        ),

                    "delay_min":
                        round(
                            traffic_delay
                            / 60,
                            2
                        ),

                    "average_congestion":
                        traffic_data[
                            "average_congestion"
                        ],

                    "maximum_congestion":
                        traffic_data[
                            "maximum_congestion"
                        ],

                    "traffic_status":
                        traffic_data[
                            "traffic_status"
                        ],

                    "road_closure":
                        traffic_data[
                            "road_closure"
                        ],

                    "route_score":
                        score
                }
            )

        # Never choose a closed route unless
        # all available routes are closed.
        open_routes = [
            result
            for result in results
            if not result[
                "road_closure"
            ]
        ]

        if open_routes:

            best_route = min(
                open_routes,
                key=lambda x:
                    x["route_score"]
            )

        else:

            best_route = min(
                results,
                key=lambda x:
                    x["route_score"]
            )

        return {
            "best_route": best_route,
            "alternatives": results
        }