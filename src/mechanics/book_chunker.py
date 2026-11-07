"""Semantic Text Chunker for Danyar Engine.

Splits multi-page book extracts into overlapping semantic windows
suitable for LLM extraction and atomic claim formulation.
"""

from __future__ import annotations


def chunk_book_pages(
    pages: list[str],
    max_chars_per_chunk: int = 1500,
    overlap_chars: int = 200,
) -> list[str]:
    """Chunk extracted pages into overlapping semantic windows.

    Args:
        pages: List of extracted page text strings.
        max_chars_per_chunk: Target maximum character length for each chunk.
        overlap_chars: Number of overlapping characters preserved between chunks.

    Returns:
        List of cleaned chunk strings.

    Raises:
        ValueError: If max_chars_per_chunk <= overlap_chars.
    """
    if max_chars_per_chunk <= overlap_chars:
        raise ValueError(
            f"max_chars_per_chunk must be greater than overlap_chars ({max_chars_per_chunk} <= {overlap_chars})"
        )

    # Filter out empty or whitespace-only pages
    valid_pages = [p.strip() for p in pages if p and p.strip()]
    if not valid_pages:
        return []

    # Join pages with distinct double-newline breaks
    full_text = "\n\n".join(valid_pages)
    if len(full_text) <= max_chars_per_chunk:
        return [full_text]

    chunks: list[str] = []
    start = 0
    total_len = len(full_text)

    while start < total_len:
        end = start + max_chars_per_chunk
        if end >= total_len:
            chunk = full_text[start:].strip()
            if chunk:
                chunks.append(chunk)
            break

        # Attempt to split at a clean boundary (newline or period)
        split_point = -1
        # Search backwards within a 200 character window for a clean delimiter
        window_start = max(start + max_chars_per_chunk - 200, start)
        sub = full_text[window_start:end]

        for delim in ["\n\n", ".\n", ".\t", ". ", "\n"]:
            pos = sub.rfind(delim)
            if pos != -1:
                split_point = window_start + pos + len(delim)
                break

        if split_point == -1 or split_point <= start:
            split_point = end

        chunk = full_text[start:split_point].strip()
        if chunk:
            chunks.append(chunk)

        start = max(split_point - overlap_chars, start + 1)

    return chunks


__all__ = ["chunk_book_pages"]
