import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.video_tool import generate_destination_video, PROJECT_ID, BUCKET_NAME

@pytest.mark.asyncio
async def test_generate_destination_video_mocked():
    tool_context = MagicMock()
    tool_context.save_artifact = AsyncMock()

    mock_client = MagicMock()
    mock_interaction = MagicMock()
    mock_video_part = MagicMock()
    mock_video_part.data = "dGVzdF92aWRlb19ieXRlcw==" # base64 for test_video_bytes
    mock_video_part.mime_type = "video/mp4"
    mock_interaction.output_video = mock_video_part
    mock_client.interactions.create.return_value = mock_interaction

    mock_storage_client = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_storage_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    with patch("app.video_tool.genai.Client", return_value=mock_client), \
         patch("app.video_tool.storage.Client", return_value=mock_storage_client):
        
        url = await generate_destination_video("A short video of Mount Fuji", tool_context)
        
        assert url.startswith(f"https://storage.googleapis.com/{BUCKET_NAME}/videos/")
        assert tool_context.save_artifact.called
        assert mock_blob.upload_from_string.called
