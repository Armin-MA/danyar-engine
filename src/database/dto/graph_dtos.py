"""Graph Data Transfer Objects (DTOs) for Danyar Engine.

Cross-boundary data transfer schemas for transferring graph elements between
Neo4j repository, reasoning mechanics, and UI presentation layers.
Strictly decoupled from concrete database drivers.
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class NodeDTO(BaseModel):
    """Represents a graph node crossing architectural boundaries."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(..., min_length=1, description="Unique node identifier")
    label: str = Field(..., min_length=1, description="Primary node label (Claim, Concept, Condition, etc.)")
    properties: dict[str, Any] = Field(default_factory=dict, description="Node property key-value map")


class EdgeDTO(BaseModel):
    """Represents a directed graph relationship crossing architectural boundaries."""

    model_config = ConfigDict(frozen=True)

    source_id: str = Field(..., min_length=1, description="Source node identifier")
    target_id: str = Field(..., min_length=1, description="Target node identifier")
    relation_type: str = Field(
        ...,
        min_length=1,
        description="Relationship type (SUPPORTS, CONTRADICTS, REFINES, MENTIONS, CONDITIONED_ON, etc.)",
    )
    properties: dict[str, Any] = Field(default_factory=dict, description="Edge property key-value map")


class SubGraphDTO(BaseModel):
    """Encapsulates a connected subgraph containing nodes and directed edges."""

    model_config = ConfigDict(frozen=True)

    nodes: list[NodeDTO] = Field(default_factory=list, description="List of nodes in the subgraph")
    edges: list[EdgeDTO] = Field(default_factory=list, description="List of relationships in the subgraph")

    def is_empty(self) -> bool:
        """Return True if subgraph contains no nodes and no edges."""
        return len(self.nodes) == 0 and len(self.edges) == 0


class ClaimIngestDTO(BaseModel):
    """Encapsulates payload required to atomically ingest a claim into Neo4j."""

    model_config = ConfigDict(frozen=True)

    statement: str = Field(..., min_length=1, description="Atomic, self-contained proposition statement")
    source_title: str = Field(..., min_length=1, description="Title of the source book, article, or interview")
    author_name: str = Field(..., min_length=1, description="Name of the author or domain expert")
    concepts: list[str] = Field(default_factory=list, description="Canonical concept names mentioned")
    condition_category: str = Field(default="general", description="Boundary condition category")
    condition_description: str = Field(default="", description="Detailed boundary condition statement")
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Extraction confidence score")
    claim_type: str = Field(default="Actionable_Advice", description="Claim classification")


class UserNoteDTO(BaseModel):
    """Encapsulates a user annotation, dispute, or validation attached to a claim."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(..., min_length=1, description="Unique note identifier")
    claim_id: str = Field(..., min_length=1, description="Target claim being annotated")
    content: str = Field(..., min_length=1, description="Markdown/text note content")
    dispute_type: str = Field(default="Dispute", description="Dispute, Endorsement, or Nuance")
    credibility_impact: float = Field(
        default=-0.2, ge=-1.0, le=1.0, description="Delta modifier applied to claim credibility"
    )
    created_at: str | None = Field(default=None, description="ISO timestamp of note creation")


class NodeNeighborDTO(BaseModel):
    """Encapsulates a central node and its 1-hop neighborhood for localized inspection."""

    model_config = ConfigDict(frozen=True)

    center_node: NodeDTO = Field(..., description="Focus node of inquiry")
    neighbors: list[NodeDTO] = Field(default_factory=list, description="Directly adjacent nodes")
    incident_edges: list[EdgeDTO] = Field(default_factory=list, description="Connecting relationships")


__all__ = [
    "NodeDTO",
    "EdgeDTO",
    "SubGraphDTO",
    "ClaimIngestDTO",
    "UserNoteDTO",
    "NodeNeighborDTO",
]
