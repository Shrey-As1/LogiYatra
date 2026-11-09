import json
import os
from datetime import datetime


class ResultExporter:

    def __init__(self, output_directory="outputs"):

        self.output_directory = output_directory

        os.makedirs(
            self.output_directory,
            exist_ok=True
        )

    def save_json(
        self,
        result,
        filename="route_result.json"
    ):

        filepath = os.path.join(
            self.output_directory,
            filename
        )

        output = {
            "generated_at": datetime.now().isoformat(),
            "result": result
        }

        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                output,
                file,
                indent=4
            )

        print(
            f"\nResult saved to: {filepath}"
        )

        return filepath