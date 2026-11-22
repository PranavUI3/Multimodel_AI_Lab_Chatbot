"""
Test 14: Embedding generation with mocked API.
Verifies embedding generation produces normalized numerical float vectors.
"""

import math
import pytest
from app.providers.gemini_provider import GeminiProvider, _generate_deterministic_mock_embedding

@pytest.mark.asyncio
async def test_embedding_generation():
    provider = GeminiProvider()
    text = "OmniMind AI multimodal embedding test text."

    embedding = await provider.get_embedding(text)

    assert isinstance(embedding, list)
    assert len(embedding) >= 128
    assert all(isinstance(val, float) for val in embedding)

    # Verify vector is unit normalized (norm ≈ 1.0)
    norm = math.sqrt(sum(x * x for x in embedding))
    assert abs(norm - 1.0) < 0.05
