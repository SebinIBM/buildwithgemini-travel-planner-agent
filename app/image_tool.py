"""Image generation tool using gemini-3.1-flash-lite-image and GCS upload."""

import uuid
from google import genai
from google.cloud import storage
from google.genai import types
from google.genai.types import GenerateContentConfig, Modality
from google.adk.tools import ToolContext

PROJECT_ID = "qwiklabs-gcp-01-e84785f988a0"
BUCKET_NAME = "qwiklabs-gcp-01-e84785f988a0-static-assets-bucket"


async def generate_destination_image(prompt: str, tool_context: ToolContext) -> str:
    """Generate an image for a travel destination or attraction and upload it to public Cloud Storage.

    Args:
        prompt: Detailed description of the image to generate (e.g. 'A photo of Kyoto bamboo grove at sunrise').
        tool_context: ADK ToolContext injected by the agent framework.

    Returns:
        The public HTTPS URL of the generated image stored in Google Cloud Storage.
    """
    try:
        # Initialize GenAI Client in global region with Vertex AI
        client = genai.Client(
            vertexai=True, location="global", project=PROJECT_ID
        )

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt,
            config=GenerateContentConfig(
                response_modalities=[Modality.TEXT, Modality.IMAGE]
            ),
        )

        image_bytes = None
        mime_type = "image/jpeg"

        if response.candidates:
            for candidate in response.candidates:
                for part in candidate.content.parts:
                    if part.inline_data:
                        image_bytes = part.inline_data.data
                        if part.inline_data.mime_type:
                            mime_type = part.inline_data.mime_type
                        break
                if image_bytes:
                    break

        if not image_bytes:
            return f"Failed to generate image bytes for prompt: '{prompt}'."

        unique_id = uuid.uuid4().hex[:8]
        filename = f"destination_{unique_id}.jpg"

        # 1. Save artifact in ADK Playground
        artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        await tool_context.save_artifact(filename=filename, artifact=artifact_part)

        # 2. Upload image bytes directly to GCS without writing local files
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"images/{filename}")
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/images/{filename}"
        return public_url
    except Exception as e:
        return f"Error generating image for '{prompt}': {e}"
