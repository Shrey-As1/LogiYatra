"""TomTom Traffic Flow API Client.

Requests real-time flowSegmentData from TomTom's traffic REST service.
Validates credentials and handles timeouts, rate limits, and network errors gracefully.
"""
import os
import time
from typing import Any, Dict, Optional, Tuple
import requests
from dotenv import load_dotenv

load_dotenv()

PLACEHOLDER_KEYS = {"", "abc123xxxxxxxx", "your_tomtom_api_key_here"}


class TrafficAPI:
    BASE_URL = "https://api.tomtom.com/traffic/services/4/flowSegmentData"

    def __init__(self, zoom: int = 10, unit: str = "KMPH", cache_seconds: int = 60):
        self.api_key = os.getenv("TOMTOM_API_KEY", "").strip()
        self.zoom = zoom
        self.unit = unit
        self.cache_seconds = cache_seconds
        self.cache: Dict[Tuple[float, float], Tuple[float, Dict[str, Any]]] = {}

    def is_configured(self) -> bool:
        """Returns True only when a non-placeholder API key is available."""
        return bool(self.api_key and self.api_key not in PLACEHOLDER_KEYS)

    def get_flow(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Fetches traffic flow for the given coordinates, using caching when fresh."""
        if not self.is_configured():
            raise RuntimeError(
                "TomTom API key is not configured or is a placeholder in .env. Real-time traffic unavailable."
            )

        if not (-90.0 <= latitude <= 90.0 and -180.0 <= longitude <= 180.0):
            raise ValueError(f"Coordinates ({latitude}, {longitude}) are out of range.")

        cache_key = (round(latitude, 4), round(longitude, 4))
        current_time = time.time()

        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            if current_time - cached_time < self.cache_seconds:
                return cached_data

        url = f"{self.BASE_URL}/absolute/{self.zoom}/json"
        params = {
            "key": self.api_key,
            "point": f"{latitude},{longitude}",
            "unit": self.unit,
            "openLr": "false"
        }

        try:
            response = requests.get(url, params=params, timeout=8)
            if response.status_code == 403:
                raise RuntimeError("TomTom API key is invalid or quota has expired (HTTP 403).")
            elif response.status_code == 429:
                raise RuntimeError("TomTom API rate limit exceeded (HTTP 429).")
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.Timeout:
            raise RuntimeError("TomTom traffic API request timed out after 8 seconds.")
        except requests.exceptions.RequestException as exc:
            raise RuntimeError(f"TomTom network error: {exc}")

        self.cache[cache_key] = (current_time, data)
        return data

    def get_flow_segment(self, latitude: float, longitude: float) -> Dict[str, Any]:
        data = self.get_flow(latitude, longitude)
        if "flowSegmentData" not in data:
            raise ValueError("Invalid TomTom response: flowSegmentData missing.")
        return data["flowSegmentData"]