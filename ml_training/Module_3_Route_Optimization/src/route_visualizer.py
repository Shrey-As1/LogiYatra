import os
import folium


class RouteVisualizer:

    def __init__(
        self,
        output_directory="outputs/maps"
    ):

        self.output_directory = (
            output_directory
        )

        os.makedirs(
            self.output_directory,
            exist_ok=True
        )

    def create_map(
        self,
        route_coordinates,
        origin,
        destination,
        filename="route_map.html"
    ):

        if not route_coordinates:

            raise ValueError(
                "Route coordinates are empty."
            )

        center_lat = (
            route_coordinates[0][0]
        )

        center_lon = (
            route_coordinates[0][1]
        )

        route_map = folium.Map(
            location=[
                center_lat,
                center_lon
            ],
            zoom_start=13,
            control_scale=True
        )

        # Origin
        folium.Marker(
            location=[
                origin["lat"],
                origin["lon"]
            ],
            tooltip="Origin",
            popup="Delivery Origin",
            icon=folium.Icon(
                icon="play",
                prefix="fa"
            )
        ).add_to(route_map)

        # Destination
        folium.Marker(
            location=[
                destination["lat"],
                destination["lon"]
            ],
            tooltip="Destination",
            popup="Delivery Destination",
            icon=folium.Icon(
                icon="flag",
                prefix="fa"
            )
        ).add_to(route_map)

        # Route
        folium.PolyLine(
            locations=route_coordinates,
            weight=6,
            opacity=0.9,
            tooltip="Optimized Route"
        ).add_to(route_map)

        # Fit map
        route_map.fit_bounds(
            route_coordinates
        )

        filepath = os.path.join(
            self.output_directory,
            filename
        )

        route_map.save(
            filepath
        )

        print(
            f"\nMap saved to: {filepath}"
        )

        return filepath