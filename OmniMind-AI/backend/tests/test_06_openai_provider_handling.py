"""
Test 6: OpenAI provider handling.
Verifies OpenAI provider capabilities, text generation, and audio mock handling.
"""

import pytest
from app.providers.openai_provider import OpenAIProvider

@pytest.mark.asyncio
async def test_openai_provider_execution():
    provider = OpenAIProvider()
    assert provider.name == "openai"
    assert "text" in provider.supported_modalities
    assert "audio" in provider.supported_modalities

    # Generate text response
    response = await provider.generate_text("Explain photosynthesis.")
    assert response is not None
    assert len(response) > 0

    if not provider.is_configured():
        assert "[Mock Mode" in response
