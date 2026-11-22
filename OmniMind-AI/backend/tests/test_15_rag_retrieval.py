"""
Test 15: RAG retrieval.
Verifies cosine similarity ranking correctly retrieves the top-matching chunk.
"""

from app.utils.similarity import cosine_similarity, find_top_k_chunks

def test_rag_cosine_retrieval():
    # Synthetic vectors
    query_vec = [1.0, 0.0, 0.0, 0.0]

    chunk_target = {
        "id": 1,
        "chunk_index": 0,
        "chunk_text": "Target chunk with matching directional embedding.",
        "embedding": [0.98, 0.05, 0.0, 0.0]
    }
    chunk_unrelated = {
        "id": 2,
        "chunk_index": 1,
        "chunk_text": "Unrelated chunk with orthogonal embedding.",
        "embedding": [0.0, 1.0, 0.0, 0.0]
    }

    chunks = [chunk_unrelated, chunk_target]

    top_results = find_top_k_chunks(
        query_vector=query_vec,
        chunks=chunks,
        top_k=2,
        min_similarity=0.1
    )

    assert len(top_results) > 0
    # Top chunk must be chunk_target
    assert top_results[0]["id"] == 1
    assert top_results[0]["score"] > 0.90
