"""
Pure Domain Entities for Danyar Engine.

This module defines the foundational, immutable domain data models for the
epistemological knowledge graph and reasoning engine. Entities are defined
using frozen dataclasses with zero external database or UI dependencies.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from datetime import datetime, timezone
from typing import Any, TypeVar

T = TypeVar("T", bound="BaseDomainEntity")


def _get_default_timestamp() -> datetime:
    """Generate default UTC timestamp."""
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class BaseDomainEntity:
    """Base class for all immutable domain entities in Danyar Engine."""

    def to_dict(self, iso_dates: bool = False) -> dict[str, Any]:
        """
        Serialize domain entity to a dictionary.

        Args:
            iso_dates: If True, convert datetime fields to ISO 8601 string representation.

        Returns:
            Dictionary containing entity attributes.
        """
        data = asdict(self)
        if iso_dates:
            for k, v in data.items():
                if isinstance(v, datetime):
                    data[k] = v.isoformat()
        return data

    @classmethod
    def from_dict(cls: type[T], data: dict[str, Any]) -> T:
        """
        Instantiate entity from dictionary representation.

        Safely handles ISO datetime strings for created_at and ignores
        unrecognized extra keys for robust data migration/deserialization.

        Args:
            data: Dictionary containing entity field values.

        Returns:
            Instantiated domain entity.
        """
        valid_fields = {f.name for f in fields(cls)}
        clean_data = {k: v for k, v in data.items() if k in valid_fields}

        if "created_at" in clean_data and isinstance(clean_data["created_at"], str):
            clean_data["created_at"] = datetime.fromisoformat(clean_data["created_at"])

        return cls(**clean_data)


@dataclass(frozen=True)
class SourceEntity(BaseDomainEntity):
    """
    Represents an authoritative knowledge source (e.g., book, paper, interview).
    """

    id: str
    title: str
    author: str
    publication_year: int | None = None
    domain: str = "general"
    source_type: str = "book"


@dataclass(frozen=True)
class AuthorEntity(BaseDomainEntity):
    """
    Represents an author or domain expert associated with claims.
    """

    id: str
    name: str
    expertise_field: str = ""
    base_reputation: float = 7.0


@dataclass(frozen=True)
class ConceptEntity(BaseDomainEntity):
    """
    Represents a canonical epistemological concept or theme.
    """

    id: str
    name: str
    aliases: list[str] = field(default_factory=list)
    definition_summary: str = ""


@dataclass(frozen=True)
class ConditionEntity(BaseDomainEntity):
    """
    Represents a contextual boundary condition under which a claim holds true.
    """

    id: str
    category: str
    description: str
    context_type: str = "general"


@dataclass(frozen=True)
class OutcomeEntity(BaseDomainEntity):
    """
    Represents the expected result or metric impact asserted by a claim.
    """

    id: str
    metric: str
    impact_nature: str = "Positive"


@dataclass(frozen=True)
class ClaimEntity(BaseDomainEntity):
    """
    Represents an atomic, actionable advice or factual assertion extracted from sources.
    """

    id: str
    statement: str
    claim_type: str = "Actionable_Advice"
    confidence_score: float = 1.0
    source_id: str | None = None
    concept_ids: list[str] = field(default_factory=list)
    condition_ids: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SynthesisResultEntity(BaseDomainEntity):
    """
    Represents a dialectical relationship detected between two claims
    (e.g., SUPPORTS, CONTRADICTS, REFINES).
    """

    source_claim_id: str
    target_claim_id: str
    relation_type: str
    strength: float = 1.0
    resolution_hint: str = ""


@dataclass(frozen=True)
class UserNoteEntity(BaseDomainEntity):
    """
    Represents a user-generated reflection, dispute, or annotation on a claim.
    """

    id: str
    claim_id: str
    content: str
    created_at: datetime = field(default_factory=_get_default_timestamp)
    sentiment: str = "Neutral"
    disputes: bool = False
    tags: list[str] = field(default_factory=list)
