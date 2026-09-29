"""Firestore backend tools for travel-planner-agent."""

from typing import Any
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-01-e84785f988a0"


def _get_firestore_client() -> firestore.Client:
    """Initialize Firestore client with hardcoded GCP project ID."""
    return firestore.Client(project=PROJECT_ID)


def list_destinations(category: str = "", country: str = "") -> list[dict[str, Any]]:
    """List or search travel destinations stored in the Firestore database.

    Args:
        category: Optional category filter (e.g. 'Culture & Tech', 'Art & Romance', 'Historic Temples', 'City & Nightlife').
        country: Optional country filter (e.g. 'Japan', 'France', 'USA').

    Returns:
        A list of destination dictionaries containing details such as name, country, budget per day, rating, and attractions.
    """
    db = _get_firestore_client()
    query_ref = db.collection("destinations")

    if country:
        query_ref = query_ref.where("country", "==", country)
    if category:
        query_ref = query_ref.where("category", "==", category)

    docs = query_ref.stream()
    destinations = [doc.to_dict() for doc in docs]
    return destinations


def get_destination(destination_id: str) -> dict[str, Any] | str:
    """Fetch details for a specific travel destination from Firestore by ID.

    Args:
        destination_id: Unique ID of the destination (e.g. 'tokyo-japan', 'paris-france').

    Returns:
        Destination details dictionary, or an error message if not found.
    """
    db = _get_firestore_client()
    doc_ref = db.collection("destinations").document(destination_id)
    doc = doc_ref.get()

    if not doc.exists:
        return f"Destination with ID '{destination_id}' not found."

    return doc.to_dict()


def add_destination(
    id: str,
    name: str,
    country: str,
    category: str,
    description: str,
    budget_per_day: int,
    rating: float = 4.5,
    popular_attractions: list[str] | None = None,
) -> dict[str, Any]:
    """Add or update a travel destination in the Firestore database.

    Args:
        id: Unique identifier for the destination (e.g. 'rome-italy').
        name: Name of the destination city or region.
        country: Country where the destination is located.
        category: Travel category (e.g., 'Historical', 'Beach', 'Culinary').
        description: Brief description of the destination.
        budget_per_day: Estimated daily budget in USD.
        rating: Rating out of 5.0 (default: 4.5).
        popular_attractions: List of popular tourist attractions.

    Returns:
        The newly created or updated destination record dictionary.
    """
    db = _get_firestore_client()
    destination_data = {
        "id": id,
        "name": name,
        "country": country,
        "category": category,
        "description": description,
        "budget_per_day": budget_per_day,
        "rating": rating,
        "popular_attractions": popular_attractions or [],
    }

    db.collection("destinations").document(id).set(destination_data)
    return destination_data
