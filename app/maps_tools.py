"""Google Maps Geocoding & Places (New) API tools."""

import os
from typing import Any
import requests
from dotenv import load_dotenv

load_dotenv()


def _get_api_key() -> str:
    """Retrieve Google Maps API Key from environment."""
    key = os.getenv("GOOGLE_MAPS_API_KEY", "").strip()
    if not key or key == "PASTE_KEY_HERE":
        raise ValueError(
            "GOOGLE_MAPS_API_KEY environment variable is not set with a valid API key in .env"
        )
    return key


def geocode_address(address: str) -> dict[str, Any] | str:
    """Geocode a physical address or place name into geographic coordinates (latitude, longitude).

    Args:
        address: Full address or location query (e.g., '1600 Amphitheatre Pkwy, Mountain View, CA' or 'Tokyo Tower').

    Returns:
        A dictionary containing formatted address, latitude, and longitude.
    """
    try:
        api_key = _get_api_key()
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": address, "key": api_key}

        res = requests.get(url, params=params, timeout=5)
        if res.status_code != 200:
            return f"Geocoding request failed with status code {res.status_code}."

        data = res.json()
        status = data.get("status")
        if status != "OK" or not data.get("results"):
            return f"Geocoding error or no results found for '{address}' (Status: {status})."

        first_result = data["results"][0]
        formatted_address = first_result.get("formatted_address", address)
        location = first_result.get("geometry", {}).get("location", {})

        return {
            "query": address,
            "address": formatted_address,
            "location": {
                "latitude": location.get("lat"),
                "longitude": location.get("lng"),
            },
        }
    except Exception as e:
        return f"Error geocoding address '{address}': {e}"


def find_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "tourist_attraction",
    radius_meters: float = 1000.0,
) -> list[dict[str, Any]] | str:
    """Find nearby places (attractions, restaurants, museums) using Google Places API (New).

    Args:
        latitude: Center latitude coordinate.
        longitude: Center longitude coordinate.
        place_type: Type of place to search for (e.g., 'tourist_attraction', 'restaurant', 'museum', 'park').
        radius_meters: Search radius in meters (default: 1000.0).

    Returns:
        A list of nearby place dictionaries with name, address, and coordinates.
    """
    try:
        api_key = _get_api_key()
        url = "https://places.googleapis.com/v1/places:searchNearby"

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location",
        }

        body = {
            "includedTypes": [place_type],
            "maxResultCount": 10,
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": latitude,
                        "longitude": longitude,
                    },
                    "radius": radius_meters,
                }
            },
        }

        res = requests.post(url, headers=headers, json=body, timeout=5)
        if res.status_code != 200:
            return f"Places API request failed with status code {res.status_code}: {res.text}"

        data = res.json()
        places_raw = data.get("places", [])
        if not places_raw:
            return f"No nearby places of type '{place_type}' found within {radius_meters}m."

        results = []
        for p in places_raw:
            display_name = p.get("displayName", {}).get("text", "Unknown Place")
            formatted_addr = p.get("formattedAddress", "No address available")
            loc = p.get("location", {})
            results.append({
                "name": display_name,
                "address": formatted_addr,
                "location": {
                    "latitude": loc.get("latitude"),
                    "longitude": loc.get("longitude"),
                },
            })

        return results
    except Exception as e:
        return f"Error finding nearby places: {e}"
