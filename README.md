# GlobeTrotter Travel Planner Agent

GlobeTrotter is an AI-powered travel concierge built using the **Google Agent Development Kit (ADK)** and deployed on **Google Cloud Agent Runtime**. It assists users with multi-day itinerary planning, destination discovery, real-time weather reports, currency conversion, visual media generation, and persistent memory across conversations.

![GlobeTrotter Agent Demo](./demo.gif)

---

## 🚀 Wired Features & Tools

This repository contains the following implemented capabilities:

### 🧠 Cross-Session Memory
- **Vertex AI Memory Bank Service**: Automatically extracts and retains user preferences, dietary allergies, and past travel choices across sessions using ADK callbacks (`ensure_memory_service_callback` and `generate_memories_callback`).

### 🎴 Rich UI Card Rendering
- **Agent-to-User Interface (A2UI v0.8)**: Generates structured, responsive UI cards (Cards, Columns, Rows, Text, and Images) rendered natively in the frontend chat view.

### 🎨 Visual & Video Generation
- **Image Generation Tool (`generate_destination_image`)**: Generates travel destination visuals using `gemini-3.1-flash-lite-image`. Saves generated images to the ADK Playground Artifacts panel and uploads directly to **Google Cloud Storage**.
- **Video Generation Tool (`generate_destination_video`)**: Generates short travel preview videos using Google's Omni model (`gemini-omni-flash-preview` in the `global` region). Saves artifacts and uploads media to **Google Cloud Storage**.

### 🗄️ Database & Storage
- **Google Cloud Firestore (`add_destination`, `get_destination`, `list_destinations`)**: Persists saved trip destinations and saved items in Firestore collections.
- **Google Cloud Storage**: Public bucket storage for serving generated destination images and videos via public HTTPS URLs.

### 🛠️ Location, Weather & Travel Utilities
- **Google Maps API (`geocode_address`, `find_nearby_places`)**: Converts location addresses to geographic coordinates and searches nearby travel spots.
- **Destination Weather Tool (`get_destination_weather`)**: Fetches weather forecasts for requested cities.
- **Currency Converter (`convert_travel_currency`)**: Converts travel budgets between global currencies.
- **Landmark Info Tool (`get_landmark_info`)**: Fetches historical and practical travel details for world landmarks.
- **City Time Tool (`get_current_time`)**: Checks current time and timezone details for travel destinations.

---

## ☁️ Google Cloud Infrastructure

The project integrates with the following Google Cloud services:
- **Vertex AI Agent Runtime (Reasoning Engines)**
- **Vertex AI Memory Bank**
- **Google Cloud Firestore**
- **Google Cloud Storage**
- **Google GenAI API (Gemini 2.5 Flash, Gemini 3.1 Flash Lite Image, Gemini Omni Flash)**
- **Google Maps Platform API**

---

## ⚙️ Local Development & Setup

### Prerequisites
- Python 3.10+
- `uv` or `pip` package manager
- Google Cloud SDK (`gcloud`) authenticated with an active GCP project

### 1. Clone & Install Dependencies

```bash
git clone <your-repo-url>
cd travel-planner-agent

# Create virtual environment and install dependencies
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
export GOOGLE_CLOUD_PROJECT="<your-gcp-project-id>"
export GOOGLE_CLOUD_LOCATION="us-east1"
export GOOGLE_MAPS_API_KEY="<your-google-maps-api-key>"
```

### 3. Run Agent Backend Locally

To test the agent locally using the ADK Web Dev UI:

```bash
uv run adk web
```

### 4. Run Frontend Proxy Server Locally

To run the custom chat web interface locally:

```bash
cd frontend
uv pip install -r requirements.txt
export AGENT_ENGINE_RESOURCE_NAME="projects/<project-id>/locations/us-east1/reasoningEngines/<agent-runtime-id>"
export AGENT_DIRECTORY="app"
uv run python main.py
```

Open your browser to the local address output by the dev server (default port `8080`).

---

## 🛠️ Deployment

Deploy the agent to Vertex AI Agent Runtime:

```bash
agents-cli deploy --no-confirm-project
```
