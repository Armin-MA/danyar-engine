"""Socratic Diagnostic Formulator for Danyar Engine.

Implements ISocraticAdvisor to analyze user inquiries against dialectical boundary conditions,
verifying whether situational context is sufficient or formulating targeted clarifying questions.
"""

from __future__ import annotations

import json
from typing import Callable
from pydantic import BaseModel, Field

from src.contracts.engine_contracts import ISocraticAdvisor
from src.entities.domain_entities import ConditionEntity
from src.utils.schema_validator import validate_json_schema, SchemaValidationError
from src.utils.text_normalizer import normalize_persian_text


class SocraticResponseSchema(BaseModel):
    """Schema for validating LLM-generated Socratic inquiries."""

    is_sufficient: bool = Field(..., description="Whether user query has sufficient context.")
    questions: list[str] = Field(
        default_factory=list,
        description="Up to 2 targeted Persian clarifying questions if context is lacking.",
    )


SOCRATIC_DIAGNOSTIC_PROMPT = """شما مشاور خردمند سقراطی در موتور دانشی دانیار هستید.
کاربر یک پرسش مطرح کرده است و برای پاسخ‌دهی دقیق، شرایط مرزی زیر از پایگاه دانش استخراج شده است:

شرایط مرزی مرتبط:
{conditions_text}

پرسش کاربر:
"{user_query}"

وظیفه:
1. ارزیابی کنید آیا کاربر اطلاعات کافی درباره این شرایط مرزی در سوال خود ارائه کرده است یا خیر.
2. اگر اطلاعات کافی است، is_sufficient=true و لیست سوالات خالی برگردانید.
3. اگر اطلاعات ناکافی است، حداکثر ۲ سوال کوتاه، دقیق و تشخیصی (به زبان فارسی معیار) طرح کنید.

فرمت پاسخ صرفاً JSON باشد:
{{
  "is_sufficient": false,
  "questions": [
    "سوال تشخیصی اول",
    "سوال تشخیصی دوم"
  ]
}}
"""

DEFAULT_FALLBACK_QUESTION = "لطفاً شرایط، محدودیت‌ها و زمینه دقیق وضعیت فعلی خود را بیشتر توضیح دهید."

CATEGORY_QUESTIONS: dict[str, str] = {
    "company_size": "اندازه و تعداد اعضای تیم شما در حال حاضر چقدر است؟",
    "market_phase": "محصول و کسب‌وکار شما در چه مرحله‌ای از بازار (قبل از PMF، رشد اولیه یا مقیاس‌پذیری) قرار دارد؟",
    "runway": "میزان نقدینگی و ران‌وی مالی در دسترس شما چقدر است؟",
    "business_model": "مدل کسب‌وکار و درآمدی شما (مثلاً B2B یا B2C) چیست؟",
    "risk_tolerance": "سطح ریسک‌پذیری سازمان و محدودیت‌های زمانی شما چگونه تعریف شده است؟",
}

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "company_size": ["نفر", "پرسنل", "کارمند", "همکار", "تعداد", "اندازه"],
    "market_phase": ["pmf", "فاز", "مرحله", "رشد", "بازار", "بحران"],
    "runway": ["ران‌وی", "runway", "مالی", "نقدینگی", "بودجه", "سرمایه", "ماه"],
    "business_model": ["b2b", "b2c", "مدل درآمد", "فروش سازمانی", "مارکت‌پلیس"],
    "risk_tolerance": ["ریسک", "تحمل ریسک", "محدودیت زمانی", "بقا"],
}


class SocraticAdvisor(ISocraticAdvisor):
    """Diagnoses situational context sufficiency and formulates Socratic inquiries."""

    def __init__(self, llm_caller: Callable[[str], str] | None = None) -> None:
        self.llm_caller = llm_caller

    def assess_context_sufficiency(
        self, user_query: str, matched_conditions: list[ConditionEntity]
    ) -> tuple[bool, list[str]]:
        """Assess if user_query specifies required situational parameters.

        Args:
            user_query: The natural language question from the user.
            matched_conditions: Boundary conditions associated with candidate claims.

        Returns:
            tuple[bool, list[str]]: (is_sufficient, diagnostic_questions capped at 2).
        """
        # 1. No conditions to satisfy -> automatically sufficient
        if not matched_conditions:
            return True, []

        # 2. Check for malformed condition list entries
        for cond in matched_conditions:
            if not isinstance(cond, ConditionEntity):
                return False, [DEFAULT_FALLBACK_QUESTION]
            if not hasattr(cond, "category") or not hasattr(cond, "description"):
                return False, [DEFAULT_FALLBACK_QUESTION]

        # 3. LLM-based evaluation if caller provided
        if self.llm_caller is not None:
            try:
                cond_bullets = "\n".join(
                    f"- دسته: {c.category} | توضیحات: {c.description}" for c in matched_conditions
                )
                prompt = SOCRATIC_DIAGNOSTIC_PROMPT.format(
                    conditions_text=cond_bullets, user_query=user_query
                )
                raw_response = self.llm_caller(prompt)
                validated = validate_json_schema(raw_response, SocraticResponseSchema)
                return validated.is_sufficient, validated.questions[:2]
            except (SchemaValidationError, json.JSONDecodeError, Exception):
                pass  # Fall back to deterministic heuristic

        # 4. Deterministic Heuristic Evaluation
        normalized_query = normalize_persian_text(user_query).lower()
        missing_questions: list[str] = []
        handled_categories: set[str] = set()

        for cond in matched_conditions:
            cat = cond.category.lower().strip()
            if cat in handled_categories:
                continue

            keywords = CATEGORY_KEYWORDS.get(cat, [])
            desc_words = [
                w.strip().lower()
                for w in cond.description.split()
                if len(w.strip()) > 3 and not w.strip().isdigit()
            ]

            # Check if query satisfies this condition's keywords or description
            keyword_match = any(kw.lower() in normalized_query for kw in keywords)
            desc_match = any(dw in normalized_query for dw in desc_words)

            if not (keyword_match or desc_match):
                question = CATEGORY_QUESTIONS.get(
                    cat,
                    f"وضعیت و شرایط شما از نظر {cond.description or cond.category} چگونه است؟",
                )
                missing_questions.append(question)
                handled_categories.add(cat)

            if len(missing_questions) >= 2:
                break

        if not missing_questions:
            return True, []

        return False, missing_questions[:2]


def formulate_socratic_inquiry(
    user_query: str,
    matched_conditions: list[ConditionEntity],
    llm_caller: Callable[[str], str] | None = None,
) -> tuple[bool, list[str]]:
    """Helper functional wrapper around SocraticAdvisor."""
    advisor = SocraticAdvisor(llm_caller=llm_caller)
    return advisor.assess_context_sufficiency(user_query, matched_conditions)


__all__ = ["SocraticAdvisor", "formulate_socratic_inquiry"]
