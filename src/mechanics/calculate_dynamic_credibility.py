"""Dynamic Credibility Calculator for Danyar Engine.

Implements ICredibilityCalculator to deterministically evaluate claim weights
conditioned on author reputation, situational user context (FitScore), and human feedback.
"""

from __future__ import annotations

import re
from src.contracts.engine_contracts import ICredibilityCalculator
from src.entities.domain_entities import ClaimEntity, ConditionEntity, AuthorEntity


class DynamicCredibilityCalculator(ICredibilityCalculator):
    """Calculates context-aware credibility scores for claims."""

    def compute_fit_score(
        self,
        claim: ClaimEntity,
        user_context: ConditionEntity | None,
        human_modifier: float = 1.0,
        author: AuthorEntity | None = None,
        claim_condition: ConditionEntity | None = None,
    ) -> float:
        """Compute normalized credibility score in range [0.0, 1.0].

        Formula:
            EffectiveScore = (BaseReputation / 10.0) * ConfidenceScore * FitScore * (HumanModifier / 1.0)
            Capped strictly to [0.0, 1.0].

        Args:
            claim: Target claim entity.
            user_context: Current situational context of the user (or None).
            human_modifier: Human dispute/validation multiplier (0.0 to 10.0, default 1.0).
            author: Author entity associated with the claim (optional, default reputation 7.0).
            claim_condition: The condition entity associated with the claim (optional).

        Raises:
            ValueError: If human_modifier is < 0.0 or > 10.0.
        """
        if human_modifier < 0.0 or human_modifier > 10.0:
            raise ValueError(
                f"human_modifier must be within [0.0, 10.0], got {human_modifier}"
            )

        # 1. Base reputation and confidence
        base_rep = author.base_reputation if author is not None else 7.0
        if base_rep < 0.0 or base_rep > 10.0:
            raise ValueError(f"author base_reputation must be within [0.0, 10.0], got {base_rep}")

        norm_author_weight = base_rep / 10.0
        confidence = max(0.0, min(1.0, claim.confidence_score))

        # 2. Context Fit Score calculation
        fit_score = self._calculate_context_fit(user_context, claim_condition)

        # 3. Final synthesis
        raw_score = norm_author_weight * confidence * fit_score * human_modifier
        return round(max(0.0, min(1.0, raw_score)), 4)

    def _calculate_context_fit(
        self,
        user_context: ConditionEntity | None,
        claim_condition: ConditionEntity | None,
    ) -> float:
        """Evaluate alignment between claim condition and current user context."""
        # If no user context or no claim condition, fallback to neutral baseline 1.0
        if user_context is None or claim_condition is None:
            return 1.0

        if not user_context.description.strip() or not claim_condition.description.strip():
            return 1.0

        # Opposing / mutually exclusive category check
        opposing_pairs = {
            ("crisis", "growth"),
            ("growth", "crisis"),
            ("startup", "enterprise"),
            ("enterprise", "startup"),
            ("downturn", "boom"),
            ("boom", "downturn"),
        }

        u_cat = user_context.category.strip().lower()
        c_cat = claim_condition.category.strip().lower()

        if (u_cat, c_cat) in opposing_pairs:
            return 0.25

        # Category match gives strong foundation
        score = 0.5
        if u_cat and c_cat and u_cat == c_cat:
            score += 0.3

        # Token overlap in description
        def tokenize(text: str) -> set[str]:
            return set(re.findall(r"\w+", text.lower()))

        u_tokens = tokenize(user_context.description)
        c_tokens = tokenize(claim_condition.description)

        if u_tokens and c_tokens:
            intersection = u_tokens.intersection(c_tokens)
            overlap_ratio = len(intersection) / min(len(u_tokens), len(c_tokens))
            score += overlap_ratio * 0.2

        return min(1.0, score)


# Pure functional alias
def calculate_dynamic_credibility(
    claim: ClaimEntity,
    user_context: ConditionEntity | None = None,
    human_modifier: float = 1.0,
    author: AuthorEntity | None = None,
    claim_condition: ConditionEntity | None = None,
) -> float:
    """Convenience functional interface for calculate_dynamic_credibility."""
    calculator = DynamicCredibilityCalculator()
    return calculator.compute_fit_score(
        claim=claim,
        user_context=user_context,
        human_modifier=human_modifier,
        author=author,
        claim_condition=claim_condition,
    )


__all__ = ["DynamicCredibilityCalculator", "calculate_dynamic_credibility"]
