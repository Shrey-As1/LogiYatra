class TrafficProcessor:

    def calculate_congestion(
        self,
        current_speed,
        free_flow_speed
    ):

        if free_flow_speed <= 0:
            return 0.0

        ratio = (
            current_speed /
            free_flow_speed
        )

        congestion = 1 - ratio

        congestion = max(
            0.0,
            min(congestion, 1.0)
        )

        return round(
            congestion,
            4
        )

    def calculate_delay(
        self,
        current_travel_time,
        free_flow_travel_time
    ):

        if (
            current_travel_time is None
            or free_flow_travel_time is None
        ):
            return None

        delay = (
            current_travel_time -
            free_flow_travel_time
        )

        return max(
            0.0,
            delay
        )

    def classify(
        self,
        congestion
    ):

        if congestion < 0.20:
            return "NORMAL"

        elif congestion < 0.50:
            return "MODERATE"

        elif congestion < 0.75:
            return "HEAVY"

        else:
            return "SEVERE"

    def process(
        self,
        flow_data
    ):

        current_speed = float(
            flow_data["currentSpeed"]
        )

        free_flow_speed = float(
            flow_data["freeFlowSpeed"]
        )

        current_travel_time = flow_data.get(
            "currentTravelTime"
        )

        free_flow_travel_time = flow_data.get(
            "freeFlowTravelTime"
        )

        confidence = flow_data.get(
            "confidence"
        )

        road_closure = flow_data.get(
            "roadClosure",
            False
        )

        congestion = (
            self.calculate_congestion(
                current_speed,
                free_flow_speed
            )
        )

        delay = (
            self.calculate_delay(
                current_travel_time,
                free_flow_travel_time
            )
        )

        status = self.classify(
            congestion
        )

        return {
            "current_speed": current_speed,
            "free_flow_speed": free_flow_speed,
            "current_travel_time": current_travel_time,
            "free_flow_travel_time": free_flow_travel_time,
            "delay_seconds": delay,
            "congestion": congestion,
            "status": status,
            "confidence": confidence,
            "road_closure": road_closure
        }