import pytest
from src.contracts.engine_contracts import (
    IExtractionPipeline,
    IDialecticalSynthesizer,
    ICredibilityCalculator,
    ISocraticAdvisor,
    IGraphRepository,
    IAnnotationRepository,
)
from src.entities.domain_entities import (
    SourceEntity,
    ClaimEntity,
    ConditionEntity,
    SynthesisResultEntity,
    UserNoteEntity,
)


class TestEngineContracts:
    def test_direct_instantiation_raises_type_error(self):
        contracts = [
            IExtractionPipeline,
            IDialecticalSynthesizer,
            ICredibilityCalculator,
            ISocraticAdvisor,
            IGraphRepository,
            IAnnotationRepository,
        ]
        for contract in contracts:
            with pytest.raises(TypeError):
                contract()  # type: ignore

    def test_complete_subclass_instantiates_successfully(self):
        class DummyExtraction(IExtractionPipeline):
            def extract_from_text(self, source: SourceEntity, raw_text: str) -> list[ClaimEntity]:
                return []

        class DummyDialectic(IDialecticalSynthesizer):
            def analyze_relationship(
                self, new_claim: ClaimEntity, existing_claims: list[ClaimEntity]
            ) -> list[SynthesisResultEntity]:
                return []

        class DummyCredibility(ICredibilityCalculator):
            def compute_fit_score(
                self, claim: ClaimEntity, user_context: ConditionEntity, human_modifier: float = 1.0
            ) -> float:
                return 1.0

        class DummyAdvisor(ISocraticAdvisor):
            def assess_context_sufficiency(
                self, user_query: str, matched_conditions: list[ConditionEntity]
            ) -> tuple[bool, list[str]]:
                return True, []

        class DummyGraphRepo(IGraphRepository):
            def save_claim_cluster(self, dto: object) -> bool:
                return True

            def fetch_related_subgraph(self, concept_names: list[str]) -> object:
                return {}

        class DummyAnnotationRepo(IAnnotationRepository):
            def add_user_note(self, note_dto: object) -> UserNoteEntity:
                return UserNoteEntity(id="n1", claim_id="c1", content="test")

            def fetch_notes_for_claim(self, claim_id: str) -> list[UserNoteEntity]:
                return []

        # All dummy implementations must instantiate without TypeError
        assert isinstance(DummyExtraction(), IExtractionPipeline)
        assert isinstance(DummyDialectic(), IDialecticalSynthesizer)
        assert isinstance(DummyCredibility(), ICredibilityCalculator)
        assert isinstance(DummyAdvisor(), ISocraticAdvisor)
        assert isinstance(DummyGraphRepo(), IGraphRepository)
        assert isinstance(DummyAnnotationRepo(), IAnnotationRepository)
