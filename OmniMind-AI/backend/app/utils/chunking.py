"""
Recursive character text chunking utility.
Splits text progressively by paragraphs, lines, sentences, and words to maintain semantic coherence.
"""

from typing import List


def recursive_character_chunking(
    text: str,
    chunk_size: int = 800,
    chunk_overlap: int = 150,
    separators: List[str] = None
) -> List[str]:
    """
    Splits content recursively using separators: ['\n\n', '\n', '. ', ' ', ''].
    Preserves context overlap between adjacent chunks.
    """
    if not text or not text.strip():
        return []

    if separators is None:
        separators = ["\n\n", "\n", ". ", " ", ""]

    def _split_text(current_text: str, current_separators: List[str]) -> List[str]:
        final_chunks: List[str] = []
        separator = current_separators[-1]
        new_separators: List[str] = []

        for i, sep in enumerate(current_separators):
            if sep == "":
                separator = sep
                break
            if sep in current_text:
                separator = sep
                new_separators = current_separators[i + 1:]
                break

        splits = current_text.split(separator) if separator else list(current_text)
        good_splits: List[str] = []

        for s in splits:
            if s.strip():
                good_splits.append(s)

        current_doc: List[str] = []
        total_len = 0

        for piece in good_splits:
            piece_len = len(piece) + (len(separator) if separator else 0)
            if total_len + piece_len > chunk_size and current_doc:
                doc_text = separator.join(current_doc).strip()
                if doc_text:
                    if len(doc_text) > chunk_size and new_separators:
                        # Recursively break down large piece
                        sub_chunks = _split_text(doc_text, new_separators)
                        final_chunks.extend(sub_chunks)
                    else:
                        final_chunks.append(doc_text)

                # Overlap logic: keep end of current_doc for next chunk
                overlap_doc: List[str] = []
                overlap_len = 0
                for item in reversed(current_doc):
                    if overlap_len + len(item) <= chunk_overlap:
                        overlap_doc.insert(0, item)
                        overlap_len += len(item)
                    else:
                        break
                current_doc = overlap_doc
                total_len = overlap_len

            current_doc.append(piece)
            total_len += piece_len

        if current_doc:
            doc_text = separator.join(current_doc).strip()
            if doc_text:
                if len(doc_text) > chunk_size and new_separators:
                    sub_chunks = _split_text(doc_text, new_separators)
                    final_chunks.extend(sub_chunks)
                else:
                    final_chunks.append(doc_text)

        return final_chunks

    raw_chunks = _split_text(text.strip(), separators)
    # Deduplicate and ensure non-empty
    cleaned_chunks = [c.strip() for c in raw_chunks if len(c.strip()) > 10]
    return cleaned_chunks if cleaned_chunks else ([text.strip()] if text.strip() else [])
