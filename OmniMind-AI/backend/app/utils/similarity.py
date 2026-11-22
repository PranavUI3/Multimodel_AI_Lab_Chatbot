"""
Vector similarity and ranking utilities.
Calculates cosine similarity in pure Python with numpy.
"""

from typing import Any, Dict, List, Tuple
import numpy as np


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Computes cosine similarity between two vector embeddings."""
    a = np.array(vec_a, dtype=np.float32)
    b = np.array(vec_b, dtype=np.float32)

    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    dot = np.dot(a, b)
    score = float(dot / (norm_a * norm_b))
    # Bound to [-1.0, 1.0] to prevent floating point anomalies
    return max(-1.0, min(1.0, score))


def find_top_k_chunks(
    query_vector: List[float],
    chunks: List[Dict[str, Any]],
    top_k: int = 4,
    min_similarity: float = 0.20
) -> List[Dict[str, Any]]:
    """
    Ranks document chunks by cosine similarity to query_vector.
    Each chunk dict must contain 'embedding' (as List[float] or JSON string).
    Returns top_k chunks sorted by score descending.
    """
    if not query_vector or not chunks:
        return []

    scored_chunks = []
    for chunk in chunks:
        emb = chunk.get("embedding")
        if isinstance(emb, str):
            import json
            try:
                emb = json.loads(emb)
            except Exception:
                continue

        if not emb or not isinstance(emb, list):
            continue

        score = cosine_similarity(query_vector, emb)
        scored_chunk = dict(chunk)
        scored_chunk["score"] = round(score, 4)
        scored_chunks.append(scored_chunk)

    # Sort descending by similarity score
    scored_chunks.sort(key=lambda x: x["score"], reverse=True)

    # Filter by minimum threshold
    filtered = [c for c in scored_chunks if c["score"] >= min_similarity]

    # Return top_k (or top 1 if none reached threshold but list is non-empty)
    return filtered[:top_k] if filtered else (scored_chunks[:1] if scored_chunks else [])
