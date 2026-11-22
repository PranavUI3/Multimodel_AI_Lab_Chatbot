"""
Test 5: Gemini provider handling.
Verifies Gemini provider capabilities, mock fallback, and response structure.
"""

import pytest
from app.providers.gemini_provider import GeminiProvider

@pytest.mark.asyncio
async def test_gemini_provider_execution():
    provider = GeminiProvider()
    assert provider.name == "gemini"
    assert "text" in provider.supported_modalities
    assert "image" in provider.supported_modalities
    assert "audio" in provider.supported_modalities
    assert "embedding" in provider.supported_modalities

    # Generate text response
    response = await provider.generate_text("Summarize quantum computing.")
    assert response is not None
    assert len(response) > 0

    # If unconfigured, clearly indicates mock mode
    if not provider.is_configured():
        assert "[Mock Mode" in response
