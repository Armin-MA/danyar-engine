import pytest
import json
from src.entities.domain_entities import SourceEntity
from src.mechanics.extract_atomic_claims import (
    AtomicClaimExtractor,
    extract_atomic_claims,
    ExtractionError,
)


class TestExtractAtomicClaims:
    @pytest.fixture
    def sample_source(self):
        return SourceEntity(
            id="src_001",
            title="اصول مدیریت بحران در استارتاپ‌ها",
            author="دانیار معتمد",
        )

    def test_happy_path_extraction(self, sample_source):
        mock_llm_response = json.dumps({
            "claims": [
                {
                    "statement": "در دوران بحران نقدینگی، مستندسازی غیرضروری باید متوقف شود.",
                    "type": "Actionable_Advice",
                    "confidence_score": 0.95,
                    "concepts": ["مستندسازی", "مدیریت بحران"],
                    "condition_category": "crisis",
                    "condition_description": "استارتاپ‌های نوپا در بحران شدید مالی"
                }
            ]
        })

        claims = extract_atomic_claims(
            source=sample_source,
            raw_text="متن تستی کتاب مدیریت بحران...",
            llm_invoker=lambda p: mock_llm_response,
        )

        assert len(claims) == 1
        claim = claims[0]
        assert "مستندسازی غیرضروری" in claim.statement
        assert claim.confidence_score == 0.95
        assert claim.source_id == "src_001"
        assert "مستندسازی" in claim.concept_ids
        assert len(claim.condition_ids) == 1

    def test_edge_case_empty_or_whitespace_text(self, sample_source):
        claims = extract_atomic_claims(
            source=sample_source,
            raw_text="   \n \t ",
            llm_invoker=lambda p: "{}",
        )
        assert claims == []

    def test_edge_case_zero_claims_returned(self, sample_source):
        mock_empty_claims = json.dumps({"claims": []})
        claims = extract_atomic_claims(
            source=sample_source,
            raw_text="یک پاراگراف بدون هیچ گزاره مهم.",
            llm_invoker=lambda p: mock_empty_claims,
        )
        assert claims == []

    def test_failure_unparseable_output_raises_extraction_error(self, sample_source):
        extractor = AtomicClaimExtractor(max_retries=1)

        with pytest.raises(ExtractionError, match="Failed to extract atomic claims"):
            extractor.extract_from_text(
                source=sample_source,
                raw_text="متن کتاب...",
                llm_invoker=lambda p: "متن کاملاً نامربوط بدون جی‌سان",
            )
