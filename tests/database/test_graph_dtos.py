"""Unit Tests for Graph Data Transfer Objects [TASK-011].

Verifies validation, instantiation, serialization, and error handling
for cross-boundary graph data transfer objects.
"""

from __future__ import annotations

import json
import pytest
from pydantic import ValidationError

from src.database.dto.graph_dtos import (
    NodeDTO,
    EdgeDTO,
    SubGraphDTO,
    ClaimIngestDTO,
    UserNoteDTO,
    NodeNeighborDTO,
)


def test_happy_path_subgraph_instantiation():
    """Happy Path: Instantiates SubGraphDTO with valid nodes and edges."""
    node1 = NodeDTO(id="claim_1", label="Claim", properties={"statement": "تست گزاره"})
    node2 = NodeDTO(id="concept_1", label="Concept", properties={"name": "رشد"})
    edge = EdgeDTO(source_id="claim_1", target_id="concept_1", relation_type="MENTIONS")

    subgraph = SubGraphDTO(nodes=[node1, node2], edges=[edge])

    assert len(subgraph.nodes) == 2
    assert len(subgraph.edges) == 1
    assert subgraph.nodes[0].id == "claim_1"
    assert subgraph.edges[0].relation_type == "MENTIONS"
    assert not subgraph.is_empty()


def test_edge_case_subgraph_json_serialization():
    """Edge Case: Serializes cleanly to JSON dictionary for API responses."""
    node = NodeDTO(id="c1", label="Claim", properties={"statement": "گزاره الف"})
    edge = EdgeDTO(source_id="c1", target_id="c2", relation_type="CONTRADICTS")
    subgraph = SubGraphDTO(nodes=[node], edges=[edge])

    data = subgraph.model_dump()
    assert isinstance(data, dict)
    assert "nodes" in data and "edges" in data

    # Ensure JSON serializable without error
    json_str = json.dumps(data, ensure_ascii=False)
    assert "گزاره الف" in json_str
    assert "CONTRADICTS" in json_str


def test_failure_state_missing_node_id():
    """Failure State: Raises ValidationError when required node id is missing."""
    with pytest.raises(ValidationError):
        # Missing 'id'
        NodeDTO(label="Claim", properties={})  # type: ignore


def test_claim_ingest_dto_validation():
    """Verifies ClaimIngestDTO validates statement, source, and concepts."""
    ingest_dto = ClaimIngestDTO(
        statement="توسعه تیم فنی قبل از PMF پرریسک است.",
        source_title="کتاب صفر به یک",
        author_name="پیتر تیل",
        concepts=["PMF", "توسعه تیم"],
        condition_category="market_phase",
        condition_description="مرحله قبل از PMF",
    )
    assert ingest_dto.statement.startswith("توسعه تیم")
    assert ingest_dto.author_name == "پیتر تیل"


def test_user_note_dto_validation():
    """Verifies UserNoteDTO instantiates and supports dispute properties."""
    note = UserNoteDTO(
        id="note_1",
        claim_id="claim_100",
        content="در صنعت پتروشیمی این گزاره صادق نیست.",
        dispute_type="Empirical_Counterexample",
        credibility_impact=-0.3,
    )
    assert note.dispute_type == "Empirical_Counterexample"
    assert note.credibility_impact == -0.3


def test_node_neighbor_dto():
    """Verifies NodeNeighborDTO holds target node and 1-hop graph neighbors."""
    center = NodeDTO(id="center", label="Claim", properties={})
    nbr = NodeDTO(id="nbr1", label="Condition", properties={})
    edge = EdgeDTO(source_id="center", target_id="nbr1", relation_type="CONDITIONED_ON")

    dto = NodeNeighborDTO(center_node=center, neighbors=[nbr], incident_edges=[edge])
    assert dto.center_node.id == "center"
    assert len(dto.neighbors) == 1
    assert len(dto.incident_edges) == 1
