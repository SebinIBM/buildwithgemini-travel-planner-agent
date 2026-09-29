"""Video generation tool using gemini-omni-flash-preview and GCS upload."""

import base64
import uuid
from google import genai
from google.cloud import storage
from google.genai import types
from google.adk.tools import ToolContext

PROJECT_ID = "qwiklabs-gcp-01-e84785f988a0"
BUCKET_NAME = "qwiklabs-gcp-01-e84785f988a0-static-assets-bucket"


async def generate_destination_video(prompt: str, tool_context: ToolContext) -> str:
    """Generate a short video for a travel destination or attraction item using Google's Omni model (gemini-omni-flash-preview) in the global region, save as artifact, and upload to public Cloud Storage.

    Args:
        prompt: Detailed description of the video to generate (e.g. 'A scenic 5-second video of Tokyo Shibuya Crossing at night').
        tool_context: ADK ToolContext injected by the agent framework.

    Returns:
        The public HTTPS URL of the generated video stored in Google Cloud Storage.
    """
    try:
        # Initialize GenAI Client in global region with Vertex AI
        client = genai.Client(
            vertexai=True, location="global", project=PROJECT_ID
        )

        interaction = client.interactions.create(
            model="gemini-omni-flash-preview",
            input=prompt,
        )

        video_bytes = None
        mime_type = "video/mp4"

        if hasattr(interaction, "output_video") and interaction.output_video:
            raw_data = interaction.output_video.data
            if isinstance(raw_data, str):
                video_bytes = base64.b64decode(raw_data)
            else:
                video_bytes = raw_data
            if hasattr(interaction.output_video, "mime_type") and interaction.output_video.mime_type:
                mime_type = interaction.output_video.mime_type

        if not video_bytes and hasattr(interaction, "candidates") and interaction.candidates:
            for candidate in interaction.candidates:
                if hasattr(candidate, "content") and candidate.content and hasattr(candidate.content, "parts"):
                    for part in candidate.content.parts:
                        if hasattr(part, "inline_data") and part.inline_data:
                            raw_data = part.inline_data.data
                            video_bytes = base64.b64decode(raw_data) if isinstance(raw_data, str) else raw_data
                            if hasattr(part.inline_data, "mime_type") and part.inline_data.mime_type:
                                mime_type = part.inline_data.mime_type
                            break
                if video_bytes:
                    break

        if not video_bytes:
            return f"Failed to generate video bytes for prompt: '{prompt}'."

        unique_id = uuid.uuid4().hex[:8]
        filename = f"destination_video_{unique_id}.mp4"

        # 1. Save artifact in ADK Playground
        artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
        await tool_context.save_artifact(filename=filename, artifact=artifact_part)

        # 2. Upload video bytes directly to GCS without writing local files
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"videos/{filename}")
        blob.upload_from_string(video_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/videos/{filename}"
        return public_url
    except Exception as e:
        return f"Error generating video for '{prompt}': {e}"
