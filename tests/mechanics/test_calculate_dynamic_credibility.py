import pytest
from src.entities.domain_entities import ClaimEntity, ConditionEntity, AuthorEntity
from src.mechanics.calculate_dynamic_credibility import (
    DynamicCredibilityCalculator,
    calculate_dynamic_credibility,
)


class TestDynamicCredibilityCalculator:
    @pytest.fixture
    def sample_claim(self):
        return ClaimEntity(
            id="claim_001",
            statement="در دوران بحران باید فرآیندهای سنگین متوقف شوند",
            confidence_score=0.9,
        )

    @pytest.fixture
    def crisis_author(self):
        return AuthorEntity(
            id="auth_001",
            name="دکتر تست",
            base_reputation=8.5,
        )

    def test_happy_path_context_match_increases_fit_score(self, sample_claim, crisis_author):
        user_context = ConditionEntity(
            id="cond_user",
            category="crisis",
            description="استارتاپ در شرایط بحران نقدینگی شدید",
        )
        claim_condition = ConditionEntity(
            id="cond_claim",
            category="crisis",
            description="شرایط بحران مالی در سازمان‌های کوچک",
        )

        score = calculate_dynamic_credibility(
            claim=sample_claim,
            user_context=user_context,
            author=crisis_author,
            claim_condition=claim_condition,
        )

        # Base rep: 0.85 * 0.9 * fit_score(~0.9+) > 0.65
        assert 0.60 <= score <= 1.0

    def test_opposing_context_drops_fit_score(self, sample_claim, crisis_author):
        user_context = ConditionEntity(
            id="cond_user",
            category="growth",
            description="شرکت با رشد سریع و مقیاس‌پذیری بالا",
        )
        claim_condition = ConditionEntity(
            id="cond_claim",
            category="crisis",
            description="شرایط بحران مالی",
        )

        score = calculate_dynamic_credibility(
            claim=sample_claim,
            user_context=user_context,
            author=crisis_author,
            claim_condition=claim_condition,
        )

        # Fit score should drop to ~0.25, significantly reducing final score
        assert score < 0.30

    def test_edge_case_none_context_uses_neutral_baseline(self, sample_claim, crisis_author):
        score = calculate_dynamic_credibility(
            claim=sample_claim,
            user_context=None,
            author=crisis_author,
        )

        # Base rep (0.85) * conf (0.9) * 1.0 = 0.765
        assert pytest.approx(score, 0.01) == 0.765

    def test_human_modifier_scaling(self, sample_claim, crisis_author):
        # Neutral score
        base_score = calculate_dynamic_credibility(
            claim=sample_claim,
            user_context=None,
            author=crisis_author,
            human_modifier=1.0,
        )

        # User disputes / downvotes (modifier 0.5)
        disputed_score = calculate_dynamic_credibility(
            claim=sample_claim,
            user_context=None,
            author=crisis_author,
            human_modifier=0.5,
        )

        assert pytest.approx(disputed_score, 0.01) == base_score * 0.5

    def test_failure_invalid_modifier_raises_value_error(self, sample_claim):
        calculator = DynamicCredibilityCalculator()
        with pytest.raises(ValueError, match="human_modifier must be within"):
            calculator.compute_fit_score(sample_claim, None, human_modifier=-0.5)

        with pytest.raises(ValueError, match="human_modifier must be within"):
            calculator.compute_fit_score(sample_claim, None, human_modifier=11.0)
