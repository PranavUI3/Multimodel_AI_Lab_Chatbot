"""
Test 7: Hugging Face provider handling.
Verifies Hugging Face supports text and rejects incompatible modalities (e.g. image, audio) with HTTP 400.
"""

import pytest
from fastapi import HTTPException
from app.providers.huggingface_provider import HuggingFaceProvider

@pytest.mark.asyncio
async def test_huggingface_provider_execution():
    provider = HuggingFaceProvider()
    assert provider.name == "huggingface"
    assert "text" in provider.supported_modalities

    # Text generation works
    response = await provider.generate_text("Explain gravity.")
    assert response is not None
    assert len(response) > 0

    # Incompatible modalities raise 400
    with pytest.raises(HTTPException) as exc_img:
        await provider.analyze_image(b"fake_image", "image/png")
    assert exc_img.value.status_code == 400
    assert "does not support" in exc_img.value.detail or "image" in exc_img.value.detail

    with pytest.raises(HTTPException) as exc_aud:
        await provider.process_audio(b"fake_audio", "audio/mp3")
    assert exc_aud.value.status_code == 400
