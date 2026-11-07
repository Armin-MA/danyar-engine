"""
Unit tests for Pure Domain Entities in Danyar Engine.

Validates happy path instantiations, default parameters, immutability,
missing field errors (TypeError), edge cases, and serialization / deserialization.
"""

from dataclasses import FrozenInstanceError, asdict
from datetime import datetime, timezone
import pytest

from src.entities.domain_entities import (
    AuthorEntity,
    BaseDomainEntity,
    ClaimEntity,
    ConceptEntity,
    ConditionEntity,
    OutcomeEntity,
    SourceEntity,
    SynthesisResultEntity,
    UserNoteEntity,
)


class TestSourceEntity:
    """Test suite for SourceEntity."""

    def test_source_entity_instantiation_with_defaults(self):
        source = SourceEntity(id="src-001", title="Zero to One", author="Peter Thiel")
        assert source.id == "src-001"
        assert source.title == "Zero to One"
        assert source.author == "Peter Thiel"
        assert source.publication_year is None
        assert source.domain == "general"
        assert source.source_type == "book"

    def test_source_entity_full_instantiation(self):
        source = SourceEntity(
            id="src-002",
            title="The Lean Startup",
            author="Eric Ries",
            publication_year=2011,
            domain="entrepreneurship",
            source_type="audiobook",
        )
        assert source.publication_year == 2011
        assert source.domain == "entrepreneurship"
        assert source.source_type == "audiobook"

    def test_source_entity_immutability(self):
        source = SourceEntity(id="src-001", title="Title", author="Author")
        with pytest.raises((FrozenInstanceError, AttributeError)):
            source.title = "New Title"  # type: ignore[misc]

    def test_source_entity_missing_required_fields(self):
        with pytest.raises(TypeError):
            SourceEntity(id="src-001")  # type: ignore[call-arg]


class TestAuthorEntity:
    """Test suite for AuthorEntity."""

    def test_author_entity_instantiation_with_defaults(self):
        author = AuthorEntity(id="auth-001", name="Nassim Taleb")
        assert author.id == "auth-001"
        assert author.name == "Nassim Taleb"
        assert author.expertise_field == ""
        assert author.base_reputation == 7.0

    def test_author_entity_full_instantiation(self):
        author = AuthorEntity(
            id="auth-002",
            name="Daniel Kahneman",
            expertise_field="Behavioral Economics",
            base_reputation=9.5,
        )
        assert author.expertise_field == "Behavioral Economics"
        assert author.base_reputation == 9.5

    def test_author_entity_immutability(self):
        author = AuthorEntity(id="auth-001", name="Author")
        with pytest.raises((FrozenInstanceError, AttributeError)):
            author.name = "Changed"  # type: ignore[misc]

    def test_author_entity_missing_required_fields(self):
        with pytest.raises(TypeError):
            AuthorEntity(id="auth-001")  # type: ignore[call-arg]


class TestConceptEntity:
    """Test suite for ConceptEntity."""

    def test_concept_entity_instantiation_with_defaults(self):
        concept = ConceptEntity(id="cnc-001", name="Antifragility")
        assert concept.id == "cnc-001"
        assert concept.name == "Antifragility"
        assert concept.aliases == []
        assert concept.definition_summary == ""

    def test_concept_entity_full_instantiation(self):
        concept = ConceptEntity(
            id="cnc-002",
            name="Minimum Viable Product",
            aliases=["MVP", "کمینه محصول پذیرفتنی"],
            definition_summary="A version of a new product which allows a team to collect the maximum amount of validated learning with the least effort.",
        )
        assert concept.aliases == ["MVP", "کمینه محصول پذیرفتنی"]
        assert "validated learning" in concept.definition_summary

    def test_concept_entity_immutability(self):
        concept = ConceptEntity(id="cnc-001", name="Concept")
        with pytest.raises((FrozenInstanceError, AttributeError)):
            concept.name = "Changed Concept"  # type: ignore[misc]

    def test_concept_entity_missing_required_fields(self):
        with pytest.raises(TypeError):
            ConceptEntity()  # type: ignore[call-arg]


class TestConditionEntity:
    """Test suite for ConditionEntity."""

    def test_condition_entity_instantiation_with_defaults(self):
        condition = ConditionEntity(
            id="cnd-001",
            category="Market_Maturity",
            description="High market volatility with low regulatory barrier",
        )
        assert condition.id == "cnd-001"
        assert condition.category == "Market_Maturity"
        assert condition.description == "High market volatility with low regulatory barrier"
        assert condition.context_type == "general"

    def test_condition_entity_full_instantiation(self):
        condition = ConditionEntity(
            id="cnd-002",
            category="Team_Size",
            description="Early stage startup with under 10 members",
            context_type="organizational",
        )
        assert condition.context_type == "organizational"

    def test_condition_entity_immutability(self):
        condition = ConditionEntity(id="cnd-001", category="Cat", description="Desc")
        with pytest.raises((FrozenInstanceError, AttributeError)):
            condition.description = "New Desc"  # type: ignore[misc]

    def test_condition_entity_missing_required_fields(self):
        with pytest.raises(TypeError):
            ConditionEntity(id="cnd-001")  # type: ignore[call-arg]


class TestOutcomeEntity:
    """Test suite for OutcomeEntity."""

    def test_outcome_entity_instantiation_with_defaults(self):
        outcome = OutcomeEntity(id="out-001", metric="Customer Churn Rate")
        assert outcome.id == "out-001"
        assert outcome.metric == "Customer Churn Rate"
        assert outcome.impact_nature == "Positive"

    def test_outcome_entity_full_instantiation(self):
        outcome = OutcomeEntity(
            id="out-002",
            metric="Burn Rate",
            impact_nature="Negative",
        )
        assert outcome.impact_nature == "Negative"

    def test_outcome_entity_immutability(self):
        outcome = OutcomeEntity(id="out-001", metric="Metric")
        with pytest.raises((FrozenInstanceError, AttributeError)):
            outcome.metric = "New Metric"  # type: ignore[misc]

    def test_outcome_entity_missing_required_fields(self):
        with pytest.raises(TypeError):
            OutcomeEntity()  # type: ignore[call-arg]


class TestClaimEntity:
    """Test suite for ClaimEntity."""

    def test_claim_entity_happy_path(self):
        claim = ClaimEntity(
            id="clm-001",
            statement="Monopoly is the condition of every successful business.",
            claim_type="Strategic_Thesis",
            confidence_score=0.95,
        )
        assert claim.id == "clm-001"
        assert claim.statement == "Monopoly is the condition of every successful business."
        assert claim.claim_type == "Strategic_Thesis"
        assert claim.confidence_score == 0.95
        assert claim.source_id is None
        assert claim.concept_ids == []
        assert claim.condition_ids == []

    def test_claim_entity_with_defaults(self):
        claim = ClaimEntity(
            id="clm-002",
            statement="Launch early and iterate fast.",
        )
        assert claim.claim_type == "Actionable_Advice"
        assert claim.confidence_score == 1.0
        assert claim.source_id is None
        assert claim.concept_ids == []
        assert claim.condition_ids == []

    def test_claim_entity_full_instantiation(self):
        claim = ClaimEntity(
            id="clm-003",
            statement="Pivot when growth stalls after 3 iterations.",
            claim_type="Actionable_Advice",
            confidence_score=0.88,
            source_id="src-002",
            concept_ids=["cnc-001", "cnc-002"],
            condition_ids=["cnd-001"],
        )
        assert claim.source_id == "src-002"
        assert claim.concept_ids == ["cnc-001", "cnc-002"]
        assert claim.condition_ids == ["cnd-001"]

    def test_claim_entity_immutability(self):
        claim = ClaimEntity(id="clm-001", statement="Immutable claim")
        with pytest.raises((FrozenInstanceError, AttributeError)):
            claim.statement = "Modified claim"  # type: ignore[misc]

    def test_claim_entity_missing_required_fields(self):
        with pytest.raises(TypeError):
            ClaimEntity()  # type: ignore[call-arg]

        with pytest.raises(TypeError):
            ClaimEntity(id="clm-001")  # type: ignore[call-arg]


class TestSynthesisResultEntity:
    """Test suite for SynthesisResultEntity."""

    def test_synthesis_result_instantiation_with_defaults(self):
        synthesis = SynthesisResultEntity(
            source_claim_id="clm-001",
            target_claim_id="clm-002",
            relation_type="CONTRADICTS",
        )
        assert synthesis.source_claim_id == "clm-001"
        assert synthesis.target_claim_id == "clm-002"
        assert synthesis.relation_type == "CONTRADICTS"
        assert synthesis.strength == 1.0
        assert synthesis.resolution_hint == ""

    def test_synthesis_result_full_instantiation(self):
        synthesis = SynthesisResultEntity(
            source_claim_id="clm-001",
            target_claim_id="clm-002",
            relation_type="REFINES",
            strength=0.85,
            resolution_hint="Applies when market is saturated.",
        )
        assert synthesis.strength == 0.85
        assert synthesis.resolution_hint == "Applies when market is saturated."

    def test_synthesis_result_immutability(self):
        synthesis = SynthesisResultEntity(
            source_claim_id="clm-001",
            target_claim_id="clm-002",
            relation_type="SUPPORTS",
        )
        with pytest.raises((FrozenInstanceError, AttributeError)):
            synthesis.relation_type = "CONTRADICTS"  # type: ignore[misc]

    def test_synthesis_result_missing_required_fields(self):
        with pytest.raises(TypeError):
            SynthesisResultEntity(source_claim_id="clm-001")  # type: ignore[call-arg]


class TestUserNoteEntity:
    """Test suite for UserNoteEntity."""

    def test_user_note_instantiation_with_defaults(self):
        before = datetime.now(timezone.utc)
        note = UserNoteEntity(
            id="not-001",
            claim_id="clm-001",
            content="This advice seems counterintuitive in regulated markets.",
        )
        after = datetime.now(timezone.utc)

        assert note.id == "not-001"
        assert note.claim_id == "clm-001"
        assert note.content == "This advice seems counterintuitive in regulated markets."
        assert before <= note.created_at <= after
        assert note.sentiment == "Neutral"
        assert note.disputes is False
        assert note.tags == []

    def test_user_note_edge_case_optional_sentiment_and_tags(self):
        custom_dt = datetime(2026, 5, 1, 12, 0, 0, tzinfo=timezone.utc)
        note = UserNoteEntity(
            id="not-002",
            claim_id="clm-002",
            content="I strongly dispute this advice based on our fintech experience.",
            created_at=custom_dt,
            sentiment="Negative",
            disputes=True,
            tags=["dispute", "fintech", "compliance"],
        )
        assert note.created_at == custom_dt
        assert note.sentiment == "Negative"
        assert note.disputes is True
        assert note.tags == ["dispute", "fintech", "compliance"]

    def test_user_note_immutability(self):
        note = UserNoteEntity(id="not-001", claim_id="clm-001", content="Note text")
        with pytest.raises((FrozenInstanceError, AttributeError)):
            note.content = "Changed note text"  # type: ignore[misc]

    def test_user_note_missing_required_fields(self):
        with pytest.raises(TypeError):
            UserNoteEntity(id="not-001")  # type: ignore[call-arg]


class TestSerializationAndDeserialization:
    """Test suite for entity dictionary conversion and round-tripping."""

    def test_to_dict_and_asdict(self):
        claim = ClaimEntity(
            id="clm-100",
            statement="Test statement",
            claim_type="Fact",
            confidence_score=0.9,
            concept_ids=["cnc-1"],
            condition_ids=["cnd-1"],
        )
        d_method = claim.to_dict()
        d_func = asdict(claim)
        assert d_method == d_func
        assert d_method["id"] == "clm-100"
        assert d_method["statement"] == "Test statement"
        assert d_method["concept_ids"] == ["cnc-1"]

    def test_roundtrip_from_dict(self):
        claim = ClaimEntity(
            id="clm-200",
            statement="Roundtrip test",
            claim_type="Actionable_Advice",
            confidence_score=0.95,
        )
        claim_dict = claim.to_dict()
        recreated = ClaimEntity.from_dict(claim_dict)
        assert recreated == claim
        assert isinstance(recreated, ClaimEntity)

    def test_user_note_iso_dates_serialization_and_roundtrip(self):
        fixed_time = datetime(2026, 11, 7, 20, 0, 0, tzinfo=timezone.utc)
        note = UserNoteEntity(
            id="not-500",
            claim_id="clm-500",
            content="Serialized note",
            created_at=fixed_time,
            sentiment="Positive",
            tags=["learning", "insight"],
        )
        iso_dict = note.to_dict(iso_dates=True)
        assert isinstance(iso_dict["created_at"], str)
        assert "2026-11-07" in iso_dict["created_at"]

        # Recreate from iso string dict
        recreated = UserNoteEntity.from_dict(iso_dict)
        assert recreated == note
        assert isinstance(recreated.created_at, datetime)

    def test_from_dict_ignores_unknown_extra_keys(self):
        raw_data = {
            "id": "src-999",
            "title": "Extended Book",
            "author": "Some Author",
            "publication_year": 2025,
            "extra_db_metadata": "ignored_value",
            "neo4j_internal_id": 12345,
        }
        source = SourceEntity.from_dict(raw_data)
        assert source.id == "src-999"
        assert source.title == "Extended Book"
        assert not hasattr(source, "extra_db_metadata")
