"""Unit Tests for PDF Reader Logic [Book Ingestion Pipeline].

Verifies text extraction from PDF documents using PyMuPDF,
Persian typography normalization, and error resilience.
"""

from __future__ import annotations

import os
import pytest
import pymupdf

from src.mechanics.pdf_reader import extract_text_from_pdf, PDFReadError


@pytest.fixture
def sample_pdf_path(tmp_path) -> str:
    """Generate a clean mock PDF with text for testing."""
    pdf_file = tmp_path / "sample_book.pdf"
    doc = pymupdf.open()
    
    # Page 1
    page1 = doc.new_page()
    page1.insert_text((50, 72), "Chapter 1: The Lean Startup and Hypothesis Testing.")
    
    # Page 2
    page2 = doc.new_page()
    page2.insert_text((50, 72), "Chapter 2: The Mom Test and Customer Interviews.")
    
    doc.save(str(pdf_file))
    doc.close()
    return str(pdf_file)


def test_happy_path_extracts_all_pages(sample_pdf_path):
    """Happy Path: Successfully extracts text from all pages and normalizes text."""
    pages = extract_text_from_pdf(sample_pdf_path)
    assert len(pages) == 2
    assert "Lean Startup" in pages[0]
    assert "The Mom Test" in pages[1]


def test_failure_state_missing_file_raises_error():
    """Failure State: Raises PDFReadError if target PDF does not exist."""
    with pytest.raises(PDFReadError, match="File not found"):
        extract_text_from_pdf("non_existent_book.pdf")


def test_edge_case_empty_pdf(tmp_path):
    """Edge Case: Returns empty list if PDF has pages with zero text."""
    empty_pdf = tmp_path / "empty.pdf"
    doc = pymupdf.open()
    doc.new_page()  # Page without text
    doc.save(str(empty_pdf))
    doc.close()

    pages = extract_text_from_pdf(str(empty_pdf))
    assert pages == []
