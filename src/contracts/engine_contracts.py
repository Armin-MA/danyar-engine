"""Abstract Layer Contracts for Danyar Engine.

Defines pure abstract interfaces (ABCs) enforcing strict Inversion of Control (IoC).
ZERO runtime business logic or database drivers permitted in this layer.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from src.entities.domain_entities import (
    SourceEntity,
    ClaimEntity,
    ConditionEntity,
    SynthesisResultEntity,
    UserNoteEntity,
)


class IExtractionPipeline(ABC):
    """Contract for extracting structured, atomic claims from raw text sources."""

    @abstractmethod
    def extract_from_text(self, source: SourceEntity, raw_text: str) -> list[ClaimEntity]:
        """Convert unstructured text into normalized atomic ClaimEntity instances."""
        pass


class IDialecticalSynthesizer(ABC):
    """Contract for dialectical reasoning and conflict/consensus evaluation."""

    @abstractmethod
    def analyze_relationship(
        self, new_claim: ClaimEntity, existing_claims: list[ClaimEntity]
    ) -> list[SynthesisResultEntity]:
        """Classify logical relations (SUPPORTS, CONTRADICTS, REFINES) between claims."""
        pass


class ICredibilityCalculator(ABC):
    """Contract for computing context-aware dynamic credibility scores."""

    @abstractmethod
    def compute_fit_score(
        self, claim: ClaimEntity, user_context: ConditionEntity, human_modifier: float = 1.0
    ) -> float:
        """Compute normalized credibility score based on author reputation, context fit, and human feedback."""
        pass


class ISocraticAdvisor(ABC):
    """Contract for diagnostic inquiry formulation and advisory synthesis."""

    @abstractmethod
    def assess_context_sufficiency(
        self, user_query: str, matched_conditions: list[ConditionEntity]
    ) -> tuple[bool, list[str]]:
        """Assess if query provides sufficient context; if not, return targeted diagnostic questions."""
        pass


class IGraphRepository(ABC):
    """Contract for persisting and querying graph clusters in Neo4j."""

    @abstractmethod
    def save_claim_cluster(self, dto: Any) -> bool:
        """Atomically persist a cluster of claims, concepts, and relationships in Neo4j."""
        pass

    @abstractmethod
    def fetch_related_subgraph(self, concept_names: list[str]) -> Any:
        """Fetch active subgraph matching the requested canonical concepts."""
        pass


class IAnnotationRepository(ABC):
    """Contract for human user notes and dispute annotations."""

    @abstractmethod
    def add_user_note(self, note_dto: Any) -> UserNoteEntity:
        """Attach a user note or dispute annotation to a target claim in Neo4j."""
        pass

    @abstractmethod
    def fetch_notes_for_claim(self, claim_id: str) -> list[UserNoteEntity]:
        """Retrieve all human feedback notes and annotations associated with a claim."""
        pass


__all__ = [
    "IExtractionPipeline",
    "IDialecticalSynthesizer",
    "ICredibilityCalculator",
    "ISocraticAdvisor",
    "IGraphRepository",
    "IAnnotationRepository",
]
