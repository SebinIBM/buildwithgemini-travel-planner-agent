# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


import json
from pathlib import Path
from google.adk.agents.callback_context import CallbackContext
from google.adk.code_executors.agent_engine_sandbox_code_executor import (
    AgentEngineSandboxCodeExecutor,
)
from google.adk.memory import VertexAiMemoryBankService
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from app.a2ui_utils import a2ui_callback
from app.currency_tool import convert_travel_currency
from app.firestore_tools import add_destination, get_destination, list_destinations
from app.image_tool import generate_destination_image
from app.video_tool import generate_destination_video
from app.landmark_tool import get_landmark_info
from app.maps_tools import find_nearby_places, geocode_address
from app.weather_tool import get_destination_weather


def _get_agent_engine_resource_name() -> str:
    metadata_file = Path(__file__).parent.parent / "deployment_metadata.json"
    if metadata_file.exists():
        try:
            data = json.loads(metadata_file.read_text())
            if "pending_operation" in data and "operation_name" in data["pending_operation"]:
                op_name = data["pending_operation"]["operation_name"]
                if "/operations/" in op_name:
                    return op_name.split("/operations/")[0]
            if "remote_agent_runtime_id" in data and data["remote_agent_runtime_id"] != "None":
                return data["remote_agent_runtime_id"]
        except Exception:
            pass
    return "projects/qwiklabs-gcp-01-e84785f988a0/locations/us-east1/reasoningEngines/8529621981169975296"


MEMORY_BANK_ID = "8529621981169975296"


_memory_service = VertexAiMemoryBankService(
    project="qwiklabs-gcp-01-e84785f988a0",
    location="us-east1",
    agent_engine_id=MEMORY_BANK_ID,
)


async def ensure_memory_service_callback(callback_context: CallbackContext):
    """Ensure memory service is attached to the invocation context on deployed runtime."""
    if hasattr(callback_context, "_invocation_context") and callback_context._invocation_context:
        if getattr(callback_context._invocation_context, "memory_service", None) is None:
            callback_context._invocation_context.memory_service = _memory_service
    return None


async def generate_memories_callback(callback_context: CallbackContext):
    """WRITE: Send session events to Memory Bank for extraction after each turn."""
    await callback_context.add_session_to_memory()
    return None


def memory_bank_service_builder():
    """Build Vertex AI Memory Bank service for deployed agent runtime."""
    return _memory_service


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description="You are a travel planning concierge assistant.",
    workflow_description=(
        "Analyze the user's travel request, discover destinations, search nearby places, "
        "view landmark information, check weather, convert currencies, and return structured "
        "UI cards when appropriate."
    ),
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects. "
        "IMPORTANT: Always remember and strictly respect all stated user allergies "
        "(food, dietary, medical, environmental) and personal preferences across all "
        "conversations when making recommendations or planning itineraries."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    code_executor=AgentEngineSandboxCodeExecutor(
        agent_engine_resource_name=_get_agent_engine_resource_name()
    ),
    before_agent_callback=ensure_memory_service_callback,
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
    tools=[
        PreloadMemoryTool(),
        generate_destination_image,
        generate_destination_video,
        get_destination_weather,
        convert_travel_currency,
        get_landmark_info,
        geocode_address,
        find_nearby_places,
        get_current_time,
        list_destinations,
        get_destination,
        add_destination,
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
