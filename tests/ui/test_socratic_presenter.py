"""Unit Tests for Socratic Advisory Presenter [TASK-015].

Verifies formatting of structured SLM advisory outputs into Persian prose with
standard dialectical sections (اجماع بزرگان، نقاط تضاد، نسخه اختصاصی شما),
citation footnotes, and fallback behavior.
"""

from __future__ import annotations

import pytest

from src.entities.domain_entities import SourceEntity
from src.ui.presenters.socratic_presenter import SocraticPresenter, format_socratic_advice


def test_happy_path_renders_structured_persian_sections():
    """Happy Path: Renders structured sections: اجماع بزرگان، نقاط تضاد، نسخه اختصاصی شما."""
    payload = {
        "consensus": "همگی بر اهمیت شفافیت در ارتباطات درون‌تیمی توافق دارند.",
        "contradictions": [
            {
                "perspective_a": "پیتر تیل: مقیاس‌دهی زودهنگام قاتل استارتاپ‌ها است.",
                "perspective_b": "رید هافمن: در بازارهای شبکه‌ای، سرعت سوزاندن سرمایه بر بهره‌وری ارجحیت دارد.",
                "tension_nature": "تفاوت بنیادین در ارزیابی ریسک شکست بازار در برابر ریسک جا ماندن",
            }
        ],
        "tailored_advice": "با توجه به وضعیت قبل از PMF شما، نسخه بهینه این است که ابتدا تطابق محصول با بازار اثبات شود سپس تیم فنی توسعه یابد.",
    }
    citations = [
        SourceEntity(id="src_1", title="صفر به یک", author="پیتر تیل", publication_year=2014),
        SourceEntity(id="src_2", title="بلیتزاسکیلینگ", author="رید هافمن", publication_year=2018),
    ]

    result = SocraticPresenter.format_advisory_response(payload, citations)

    assert "اجماع بزرگان" in result
    assert "نقاط تضاد" in result
    assert "نسخه اختصاصی شما" in result
    assert "صفر به یک" in result
    assert "بلیتزاسکیلینگ" in result
    assert "[^1]" in result or "[1]" in result or "منابع" in result


def test_edge_case_links_citations_with_markdown_footnotes():
    """Edge Case: Properly links citations to source nodes with markdown footnotes."""
    payload = {
        "tailored_advice": "تمرکز روی ارزش پیشنهادی واحد داشته باشید.",
    }
    citations = [
        SourceEntity(id="src_1", title="اصول رهبری", author="ری دالیو", publication_year=2017),
    ]

    result = format_socratic_advice(payload, citations)

    assert "ری دالیو" in result
    assert "اصول رهبری" in result
    assert "منابع و مراجع" in result or "ارجاعات" in result


def test_failure_state_empty_payload_returns_polite_fallback():
    """Failure State: Returns polite fallback message when payload is None or empty."""
    res_none = format_socratic_advice(None)
    assert isinstance(res_none, str)
    assert "احترام" in res_none or "اطلاعات" in res_none or len(res_none) > 20

    res_empty = format_socratic_advice({})
    assert isinstance(res_empty, str)
    assert "احترام" in res_empty or "اطلاعات" in res_empty


def test_empty_citations_handled_gracefully():
    """Gracefully formats advice when citations list is empty or None."""
    payload = {
        "consensus": "توافق کلی وجود دارد.",
        "tailored_advice": "اقدام مستقیم توصیه می‌شود.",
    }
    result = format_socratic_advice(payload, citations=[])

    assert "اجماع بزرگان" in result
    assert "نسخه اختصاصی شما" in result
    # Should not produce broken citation markers
    assert "[^1]" not in result
