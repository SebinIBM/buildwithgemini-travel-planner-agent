"""Public Wikipedia REST API tool for landmark and attraction details."""

import os
import urllib.parse
import requests


def get_landmark_info(landmark_name: str) -> str:
    """Fetch encyclopedic information and summary for a travel landmark, attraction, or city.

    Args:
        landmark_name: Name of the landmark, sight, or city (e.g., 'Eiffel Tower', 'Shibuya Crossing', 'Colosseum', 'Kyoto').

    Returns:
        A text summary describing the landmark, its location, and key facts.
    """
    try:
        user_agent = os.getenv(
            "TRAVEL_AGENT_USER_AGENT", "TravelPlannerAgent/1.0 (travel@example.com)"
        )
        api_key = os.getenv("WIKIPEDIA_API_KEY", "")

        formatted_title = urllib.parse.quote(landmark_name.strip().replace(" ", "_"))
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{formatted_title}"

        headers = {"User-Agent": user_agent}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 404:
            return f"No landmark information found for '{landmark_name}'."
        if res.status_code != 200:
            return f"Unable to fetch info for '{landmark_name}' (HTTP {res.status_code})."

        data = res.json()
        title = data.get("title", landmark_name)
        extract = data.get("extract", "No description available.")
        description = data.get("description", "")

        result = f"Landmark: {title}\n"
        if description:
            result += f"Type: {description}\n"
        result += f"Summary: {extract}"

        return result
    except Exception as e:
        return f"Error fetching landmark info for '{landmark_name}': {e}"
