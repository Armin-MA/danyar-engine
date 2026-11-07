"""Unit Tests for Socratic Diagnostic Formulator [TASK-009].

Verifies deterministic assessment of user query context sufficiency against
matched boundary conditions, generation of clarifying inquiries, and error resilience.
"""

from __future__ import annotations

import json
import pytest

from src.entities.domain_entities import ConditionEntity
from src.contracts.engine_contracts import ISocraticAdvisor
from src.mechanics.formulate_socratic_inquiry import (
    SocraticAdvisor,
    formulate_socratic_inquiry,
)


def test_socratic_advisor_implements_interface():
    """Verify SocraticAdvisor conforms to ISocraticAdvisor ABC."""
    advisor = SocraticAdvisor()
    assert isinstance(advisor, ISocraticAdvisor)


def test_happy_path_generates_two_clarifying_questions():
    """Happy Path: Generates 2 diagnostic questions when query lacks company size and market phase."""
    advisor = SocraticAdvisor()
    user_query = "آیا باید به سرعت تیم فنی را توسعه دهیم؟"
    matched_conditions = [
        ConditionEntity(
            id="cond_1",
            category="company_size",
            description="سازمان با بیش از ۵۰ پرسنل فنی",
        ),
        ConditionEntity(
            id="cond_2",
            category="market_phase",
            description="مرحله پس از تطابق محصول با بازار (Post-PMF)",
        ),
    ]

    is_sufficient, questions = advisor.assess_context_sufficiency(user_query, matched_conditions)

    assert is_sufficient is False
    assert len(questions) == 2
    # Questions should be non-empty Persian strings
    assert all(isinstance(q, str) and len(q.strip()) > 5 for q in questions)


def test_edge_case_query_with_explicit_constraints():
    """Edge Case: Returns is_sufficient=True when query already explicitly specifies constraints."""
    advisor = SocraticAdvisor()
    user_query = "ما یک تیم استارتاپی ۱۰ نفره در مرحله پس از PMF هستیم؛ آیا باید تیم فنی را توسعه دهیم؟"
    matched_conditions = [
        ConditionEntity(
            id="cond_1",
            category="company_size",
            description="تیم ۱۰ نفره",
        ),
        ConditionEntity(
            id="cond_2",
            category="market_phase",
            description="مرحله پس از PMF",
        ),
    ]

    is_sufficient, questions = advisor.assess_context_sufficiency(user_query, matched_conditions)

    assert is_sufficient is True
    assert questions == []


def test_edge_case_empty_matched_conditions():
    """When no boundary conditions match, query is treated as sufficient."""
    advisor = SocraticAdvisor()
    user_query = "تعریف تفکر دیالکتیکی چیست؟"
    is_sufficient, questions = advisor.assess_context_sufficiency(user_query, [])

    assert is_sufficient is True
    assert questions == []


def test_failure_state_malformed_conditions():
    """Failure State: Returns graceful default question if condition list contains malformed entries."""
    advisor = SocraticAdvisor()
    user_query = "چگونه بهره‌وری را افزایش دهیم؟"
    malformed_conditions = [
        {"invalid": "data"},  # Not a ConditionEntity
        None,
    ]

    is_sufficient, questions = advisor.assess_context_sufficiency(user_query, malformed_conditions)  # type: ignore

    assert is_sufficient is False
    assert len(questions) >= 1
    assert any("شرایط" in q or "زمینه" in q or "وضعیت" in q for q in questions)


def test_llm_caller_integration():
    """Verify LLM-driven diagnostic formulation when llm_caller is provided."""
    mock_payload = {
        "is_sufficient": False,
        "questions": [
            "میزان نقدینگی در دسترس تیم چقدر است؟",
            "آیا به ثبات محصول در بازار رسیده‌اید؟",
            "سوال سوم که باید فیلتر شود",
        ],
    }

    def mock_llm(prompt: str) -> str:
        return json.dumps(mock_payload)

    advisor = SocraticAdvisor(llm_caller=mock_llm)
    user_query = "باید استخدام کنیم؟"
    conditions = [
        ConditionEntity(id="c1", category="runway", description="ران‌وی مالی"),
    ]

    is_sufficient, questions = advisor.assess_context_sufficiency(user_query, conditions)

    assert is_sufficient is False
    # Max 2 questions assertion
    assert len(questions) == 2
    assert questions[0] == "میزان نقدینگی در دسترس تیم چقدر است؟"
    assert questions[1] == "آیا به ثبات محصول در بازار رسیده‌اید؟"


def test_standalone_formulate_socratic_inquiry_helper():
    """Verify standalone function helper behaves identically."""
    user_query = "بهترین استراتژی قیمت‌گذاری چیست؟"
    conditions = [
        ConditionEntity(id="c1", category="business_model", description="مدل B2B"),
    ]
    is_sufficient, questions = formulate_socratic_inquiry(user_query, conditions)
    assert isinstance(is_sufficient, bool)
    assert isinstance(questions, list)
    assert len(questions) <= 2
