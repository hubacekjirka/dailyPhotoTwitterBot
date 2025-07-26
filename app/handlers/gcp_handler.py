import requests
from core.custom_types import GeoCoordinates
from logger import logger


class GcpHandler:
    def __init__(self, api_token: str):
        self.api_token = api_token

    def get_reverse_geolocation(self, coordinates: GeoCoordinates) -> str | None:

        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "key": self.api_token,
            "latlng": f"{coordinates.latitude},{coordinates.longitude}",
        }

        try:
            response = requests.get(url, params=params)
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch reverse geocode from Google API: {e}")
            return None

        if response.status_code == 200:
            data = response.json()
            logger.debug(f"Reverse geocode response: {data['results']}")

            locality: str = ""
            state: str = ""

            for result in data.get("results", []):
                if "locality" in result["types"] and "political" in result["types"]:
                    locality = result["formatted_address"]
                if "administrative_area_level_1" in result["types"] and "political" in result["types"]:
                    state = result["formatted_address"]

            if not locality or not state:
                logger.warning(f"No valid location found in reverse geocode response. Got: {data['results']}")
                return None

            return locality or state

        else:
            logger.error(f"Failed to get reverse geolocation: {response.status_code} - {response.text}")
            return None
