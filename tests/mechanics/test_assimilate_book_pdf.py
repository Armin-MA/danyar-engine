"""Unit Tests for Book Assimilation & Cross-Book Harmonizer Pipeline.

Verifies end-to-end processing of a book PDF: text extraction,
atomic claim extraction, cross-book conflict detection, and graph persistence.
"""

from __future__ import annotations

import pymupdf
import pytest
from unittest.mock import MagicMock

from src.database.repositories.in_memory_graph_repository import InMemoryGraphRepository
from src.entities.domain_entities import ClaimEntity, SynthesisResultEntity
from src.mechanics.assimilate_book_pdf import (
    assimilate_book_pdf,
    BookAssimilationSummary,
)


@pytest.fixture
def mock_book_pdf(tmp_path) -> str:
    """Create a sample PDF file representing a book chapter."""
    pdf_path = tmp_path / "zero_to_one.pdf"
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 72), "Chapter 1: The Challenge of the Future. Competition is for losers. Build a monopoly.")
    doc.save(str(pdf_path))
    doc.close()
    return str(pdf_path)


def test_happy_path_assimilates_book_and_links_tensions(mock_book_pdf):
    """Happy Path: Ingests PDF book, extracts claims, harmonizes against existing claims, and updates graph."""
    repo = InMemoryGraphRepository()
    
    # Mock extractor that returns 1 claim
    mock_extractor = MagicMock()
    mock_claim = ClaimEntity(
        id="new_claim_1",
        statement="ساخت محصول با مزیت ۱۰ برابری بر رقابت در قیمت ارجحیت دارد.",
        source_id="src_peter",
    )
    mock_extractor.extract_from_text.return_value = [mock_claim]

    # Mock evaluator that detects a contradiction with an existing claim
    mock_evaluator = MagicMock()
    mock_synthesis = SynthesisResultEntity(
        source_claim_id="new_claim_1",
        target_claim_id="c2",
        relation_type="CONTRADICTS",
        strength=0.9,
        resolution_hint="تضاد در انحصار کیفی در برابر مقیاس‌دهی با سوزاندن سرمایه",
    )
    mock_evaluator.analyze_relationship.return_value = [mock_synthesis]

    summary = assimilate_book_pdf(
        pdf_path=mock_book_pdf,
        book_title="صفر به یک",
        author_name="پیتر تیل",
        domain="استارتاپ",
        graph_repo=repo,
        extractor=mock_extractor,
        evaluator=mock_evaluator,
    )

    assert isinstance(summary, BookAssimilationSummary)
    assert summary.book_title == "صفر به یک"
    assert summary.claims_count >= 1
    assert summary.contradicts_count == 1

    # Verify graph now contains the new relationship
    subgraph = repo.fetch_full_graph()
    contradictions = [e for e in subgraph.edges if e.relation_type == "CONTRADICTS"]
    assert any(e.source_id == "new_claim_1" or e.target_id == "new_claim_1" for e in contradictions)


def test_edge_case_empty_book(tmp_path):
    """Edge Case: Handles empty PDF gracefully with 0 claims extracted."""
    empty_pdf = tmp_path / "blank.pdf"
    doc = pymupdf.open()
    doc.new_page()
    doc.save(str(empty_pdf))
    doc.close()

    repo = InMemoryGraphRepository()
    summary = assimilate_book_pdf(
        pdf_path=str(empty_pdf),
        book_title="کتاب خالی",
        author_name="ناشناس",
        graph_repo=repo,
    )

    assert summary.claims_count == 0
    assert summary.pages_count == 0
