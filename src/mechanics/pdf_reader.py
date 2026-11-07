"""PDF Document Reader & Text Extractor for Danyar Engine.

Extracts page-by-page text from PDF files using PyMuPDF and normalizes
typography through Danyar's Persian text normalization pipeline.
"""

from __future__ import annotations

import os
import pymupdf

from src.utils.text_normalizer import normalize_persian_text


class PDFReadError(Exception):
    """Raised when opening or parsing a PDF document fails."""
    pass


def extract_text_from_pdf(pdf_path: str) -> list[str]:
    """Extract and normalize text content from all pages of a PDF document.

    Args:
        pdf_path: Absolute or relative file path to the PDF document.

    Returns:
        List of cleaned, normalized text strings for each page containing content.

    Raises:
        PDFReadError: If file not found, unreadable, or password protected.
    """
    if not os.path.isfile(pdf_path):
        raise PDFReadError(f"File not found: '{pdf_path}'")

    try:
        doc = pymupdf.open(pdf_path)
    except Exception as e:
        raise PDFReadError(f"Failed to open PDF document '{pdf_path}': {e}") from e

    cleaned_pages: list[str] = []
    try:
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            if text and text.strip():
                normalized = normalize_persian_text(text.strip())
                cleaned_pages.append(normalized)
    except Exception as e:
        raise PDFReadError(f"Error reading pages from '{pdf_path}': {e}") from e
    finally:
        doc.close()

    return cleaned_pages


__all__ = ["extract_text_from_pdf", "PDFReadError"]
