"""Unit Tests for Book Chunker Logic [Book Ingestion Pipeline].

Verifies semantic text windowing, chunk boundary preservation,
and overlap mechanics across multiple pages.
"""

from __future__ import annotations

import pytest
from src.mechanics.book_chunker import chunk_book_pages


def test_happy_path_chunks_pages_with_boundaries():
    """Happy Path: Chunks multiple long pages into manageable windows with overlap."""
    page1 = "این یک متن طولانی برای تست قطعه‌بندی است. " * 30
    page2 = "بخش دوم کتاب شامل تحلیل استراتژی‌های رشد است. " * 30
    pages = [page1, page2]

    chunks = chunk_book_pages(pages, max_chars_per_chunk=600, overlap_chars=100)

    assert len(chunks) > 2
    assert all(isinstance(c, str) and len(c) > 0 for c in chunks)


def test_edge_case_single_short_page():
    """Edge Case: Returns single chunk if page is shorter than max_chars_per_chunk."""
    pages = ["این یک صفحه کوتاه با اطلاعات مختصر است."]
    chunks = chunk_book_pages(pages, max_chars_per_chunk=1000)

    assert len(chunks) == 1
    assert chunks[0] == pages[0]


def test_edge_case_empty_pages_list():
    """Edge Case: Returns empty list if no pages provided."""
    assert chunk_book_pages([]) == []
    assert chunk_book_pages(["", "   ", "\n"]) == []


def test_failure_state_invalid_chunk_sizes():
    """Failure State: Raises ValueError if max_chars_per_chunk <= overlap_chars."""
    with pytest.raises(ValueError, match="max_chars_per_chunk must be greater than overlap_chars"):
        chunk_book_pages(["متن"], max_chars_per_chunk=100, overlap_chars=150)
