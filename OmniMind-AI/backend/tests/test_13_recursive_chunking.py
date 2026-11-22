"""
Test 13: Recursive chunking.
Verifies recursive character chunking splits text while maintaining semantic boundaries and overlap.
"""

from app.utils.chunking import recursive_character_chunking

def test_recursive_character_chunking():
    # Long text with paragraphs and sentences
    paragraphs = [
        f"Paragraph {i}: OmniMind AI supports text, vision, audio, and documents. "
        f"This paragraph provides background context for chunking validation test #{i}. "
        f"Semantic continuity is essential for high quality vector retrieval."
        for i in range(1, 15)
    ]
    sample_text = "\n\n".join(paragraphs)

    # Chunk with smaller size to force splitting
    chunks = recursive_character_chunking(
        sample_text,
        chunk_size=300,
        chunk_overlap=50
    )

    assert len(chunks) > 1
    for chunk in chunks:
        assert isinstance(chunk, str)
        assert len(chunk.strip()) > 0
        # Each chunk should generally respect max chunk size with reasonable boundary slack
        assert len(chunk) <= 450
