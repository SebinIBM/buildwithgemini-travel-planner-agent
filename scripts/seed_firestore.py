"""Script to seed initial Firestore data for travel-planner-agent."""

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-01-e84785f988a0"

SEED_DESTINATIONS = [
    {
        "id": "tokyo-japan",
        "name": "Tokyo",
        "country": "Japan",
        "category": "Culture & Tech",
        "description": "Vibrant metropolis blending ultra-modern skyscrapers with historic temples.",
        "budget_per_day": 180,
        "rating": 4.9,
        "popular_attractions": ["Shibuya Crossing", "Senso-ji Temple", "Akihabara", "Tokyo Skytree"],
    },
    {
        "id": "paris-france",
        "name": "Paris",
        "country": "France",
        "category": "Art & Romance",
        "description": "Global center for art, fashion, gastronomy, and iconic architecture.",
        "budget_per_day": 220,
        "rating": 4.8,
        "popular_attractions": ["Eiffel Tower", "Louvre Museum", "Notre-Dame Cathedral", "Montmartre"],
    },
    {
        "id": "kyoto-japan",
        "name": "Kyoto",
        "country": "Japan",
        "category": "Historic Temples",
        "description": "Famed for its classical Buddhist temples, gardens, imperial palaces, and wooden houses.",
        "budget_per_day": 150,
        "rating": 4.9,
        "popular_attractions": ["Fushimi Inari Shrine", "Arashiyama Bamboo Grove", "Kinkaku-ji"],
    },
    {
        "id": "new-york-usa",
        "name": "New York",
        "country": "USA",
        "category": "City & Nightlife",
        "description": "Bustling city known for Times Square, Central Park, Broadway shows, and diverse dining.",
        "budget_per_day": 250,
        "rating": 4.7,
        "popular_attractions": ["Central Park", "Statue of Liberty", "Empire State Building", "Broadway"],
    },
]


def seed_firestore():
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection("destinations")

    print(f"Seeding Firestore collection 'destinations' in project '{PROJECT_ID}'...")
    for item in SEED_DESTINATIONS:
        doc_id = item["id"]
        collection_ref.document(doc_id).set(item)
        print(f"  - Seeded destination: {item['name']} ({doc_id})")

    print("Firestore seeding completed successfully!")


if __name__ == "__main__":
    seed_firestore()
