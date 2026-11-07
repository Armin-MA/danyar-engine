"""Socratic Advisory Presenter for Danyar Engine.

Formats structured dialectical synthesis outputs into warm, professional Persian prose
with distinct analytical sections (اجماع بزرگان، نقاط تضاد، نسخه اختصاصی شما) and
markdown footnote citations.
"""

from __future__ import annotations

from typing import Any
from src.entities.domain_entities import SourceEntity


POLITE_FALLBACK_MESSAGE = (
    "درود و احترام. در حال حاضر اطلاعات ساختاریافته کافی برای ارائه تحلیل جامع در دسترس نیست. "
    "لطفاً پرسش یا سناریوی تصمیم‌گیری خود را با شرح جزئیات بیشتری مطرح فرمایید تا بررسی دقیق صورت پذیرد."
)


class SocraticPresenter:
    """Presenter formatting dialectical reasoning outputs for the UI/Chat interface."""

    @staticmethod
    def format_advisory_response(
        payload: dict[str, Any] | None,
        citations: list[SourceEntity] | None = None,
    ) -> str:
        """Format raw advisory dictionary into standard Persian dialectical response.

        Args:
            payload: Dictionary containing 'consensus', 'contradictions', 'tailored_advice'.
            citations: List of SourceEntity instances cited in the response.

        Returns:
            Rich markdown Persian string.
        """
        if not payload:
            return POLITE_FALLBACK_MESSAGE

        lines: list[str] = [
            "### تحلیل و مشاوره دیالکتیکی دانیار",
            "",
        ]

        # 1. Consensus Section
        consensus = payload.get("consensus")
        if consensus:
            lines.append("#### ۱. اجماع بزرگان و نقاط همگرایی")
            if isinstance(consensus, list):
                for item in consensus:
                    lines.append(f"- {item}")
            else:
                lines.append(f"{consensus}")
            lines.append("")

        # 2. Dialectical Contradictions Section
        contradictions = payload.get("contradictions") or payload.get("tensions")
        if contradictions:
            lines.append("#### ۲. نقاط تضاد و تقابل دیدگاه‌ها")
            if isinstance(contradictions, list):
                for idx, c in enumerate(contradictions, 1):
                    if isinstance(c, dict):
                        pa = c.get("perspective_a", "")
                        pb = c.get("perspective_b", "")
                        nature = c.get("tension_nature", "")
                        lines.append(f"**تضاد #{idx}:**")
                        if pa:
                            lines.append(f"- *دیدگاه اول:* {pa}")
                        if pb:
                            lines.append(f"- *دیدگاه مقابل:* {pb}")
                        if nature:
                            lines.append(f"- *ماهیت تضاد:* {nature}")
                    else:
                        lines.append(f"- {c}")
            else:
                lines.append(f"{contradictions}")
            lines.append("")

        # 3. Tailored Prescription Section
        tailored = payload.get("tailored_advice") or payload.get("recommendation")
        if tailored:
            lines.append("#### ۳. نسخه اختصاصی شما (تحلیل وضعیت کنونی)")
            if isinstance(tailored, list):
                for t in tailored:
                    lines.append(f"- {t}")
            else:
                lines.append(f"{tailored}")
            lines.append("")

        # 4. Citations and Footnotes
        if citations:
            lines.append("---")
            lines.append("#### منابع و مراجع مستند")
            for idx, src in enumerate(citations, 1):
                year_part = f" ({src.publication_year})" if src.publication_year else ""
                lines.append(f"[^{idx}]: **«{src.title}»** اثر {src.author}{year_part}")

        return "\n".join(lines).strip()


def format_socratic_advice(
    payload: dict[str, Any] | None,
    citations: list[SourceEntity] | None = None,
) -> str:
    """Helper functional wrapper for SocraticPresenter.format_advisory_response."""
    return SocraticPresenter.format_advisory_response(payload, citations)


__all__ = ["SocraticPresenter", "format_socratic_advice"]
