import pytest
import json
from src.entities.domain_entities import ClaimEntity
from src.mechanics.evaluate_dialectical_conflict import (
    DialecticalConflictEvaluator,
    evaluate_dialectical_conflict,
    SynthesisError,
)


class TestEvaluateDialecticalConflict:
    @pytest.fixture
    def new_claim(self):
        return ClaimEntity(
            id="claim_new",
            statement="در شرایط بحران نقدینگی، مستندسازی تفصیلی سرعت بقا را از بین می‌برد و باید موقتاً لغو شود.",
            confidence_score=0.9,
        )

    @pytest.fixture
    def existing_claims(self):
        return [
            ClaimEntity(
                id="claim_exist_1",
                statement="مستندسازی دقیق فرآیندها ضامن پایداری و مقیاس‌پذیری سازمان است.",
                confidence_score=0.95,
            ),
            ClaimEntity(
                id="claim_exist_2",
                statement="سرعت یادگیری تیمی به حفظ مستندات مکتوب بستگی دارد.",
                confidence_score=0.8,
            ),
        ]

    def test_happy_path_detects_contradiction(self, new_claim, existing_claims):
        mock_response = json.dumps({
            "relationships": [
                {
                    "target_claim_id": "claim_exist_1",
                    "relation_type": "CONTRADICTS",
                    "strength": 0.9,
                    "conflict_nature": "تفاوت شرایط بحران در برابر مقیاس‌پذیری",
                    "resolution_hint": "در بحران مستندسازی سبک صوتی جایگزین شود"
                },
                {
                    "target_claim_id": "claim_exist_2",
                    "relation_type": "REFINES",
                    "strength": 0.7,
                    "conflict_nature": "مشروط کردن گزاره",
                    "resolution_hint": "یادگیری سریع‌تر با ارتباط مستقیم در بحران"
                }
            ]
        })

        results = evaluate_dialectical_conflict(
            new_claim=new_claim,
            existing_claims=existing_claims,
            llm_invoker=lambda p: mock_response,
        )

        assert len(results) == 2
        rel1 = next(r for r in results if r.target_claim_id == "claim_exist_1")
        assert rel1.relation_type == "CONTRADICTS"
        assert rel1.strength == 0.9
        assert "مستندسازی سبک" in rel1.resolution_hint

    def test_edge_case_supports_consensus(self, new_claim):
        supporting_claim = ClaimEntity(
            id="claim_support",
            statement="تیم‌های بسیار کوچک باید کارهای اداری و مستندسازی را به حداقل برسانند.",
        )
        mock_response = json.dumps({
            "relationships": [
                {
                    "target_claim_id": "claim_support",
                    "relation_type": "SUPPORTS",
                    "strength": 0.95,
                    "conflict_nature": "اجماع دیدگاه",
                    "resolution_hint": "تأیید هر دو نویسنده بر اولویت سرعت در تیم‌های کوچک"
                }
            ]
        })

        results = evaluate_dialectical_conflict(
            new_claim=new_claim,
            existing_claims=[supporting_claim],
            llm_invoker=lambda p: mock_response,
        )

        assert len(results) == 1
        assert results[0].relation_type == "SUPPORTS"
        assert results[0].strength == 0.95

    def test_edge_case_empty_existing_claims_returns_empty_safely(self, new_claim):
        results = evaluate_dialectical_conflict(
            new_claim=new_claim,
            existing_claims=[],
            llm_invoker=lambda p: "{}",
        )
        assert results == []

    def test_failure_invalid_relation_taxonomy_raises_synthesis_error(self, new_claim, existing_claims):
        mock_invalid_response = json.dumps({
            "relationships": [
                {
                    "target_claim_id": "claim_exist_1",
                    "relation_type": "UNKNOWN_RELATION_TYPE",
                    "strength": 0.5,
                }
            ]
        })

        with pytest.raises(SynthesisError, match="Invalid relation taxonomy"):
            evaluate_dialectical_conflict(
                new_claim=new_claim,
                existing_claims=existing_claims,
                llm_invoker=lambda p: mock_invalid_response,
            )
