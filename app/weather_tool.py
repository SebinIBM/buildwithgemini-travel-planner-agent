"""Live weather tool using public wttr.in REST API."""

import requests


def get_destination_weather(location: str) -> str:
    """Fetch real-time live weather forecast for a destination city or region.

    Args:
        location: City or location name (e.g., 'Tokyo', 'Paris', 'New York', 'Kyoto').

    Returns:
        A string summarizing the current weather condition, temperature in °C and °F, and humidity.
    """
    try:
        url = f"https://wttr.in/{location}?format=j1"
        response = requests.get(
            url, headers={"User-Agent": "curl/7.68.0"}, timeout=5
        )
        if response.status_code != 200:
            return f"Unable to fetch weather for {location} (HTTP {response.status_code})."

        data = response.json()
        if "current_condition" not in data or not data["current_condition"]:
            return f"No weather data found for {location}."

        curr = data["current_condition"][0]
        condition = curr.get("weatherDesc", [{}])[0].get("value", "Unknown")
        temp_c = curr.get("temp_C", "N/A")
        temp_f = curr.get("temp_F", "N/A")
        feels_c = curr.get("FeelsLikeC", "N/A")
        humidity = curr.get("humidity", "N/A")

        return (
            f"Live weather for {location}: {condition}, {temp_c}°C ({temp_f}°F), "
            f"feels like {feels_c}°C, humidity {humidity}%."
        )
    except Exception as e:
        return f"Error fetching live weather for {location}: {e}"
