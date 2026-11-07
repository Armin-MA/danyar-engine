"""Unit Tests for InMemory Graph & Annotation Repository.

Verifies zero-dependency fallback repository providing seeded dialectical graph data
and user note storage when Neo4j is offline.
"""

from __future__ import annotations

import pytest

from src.contracts.engine_contracts import IGraphRepository, IAnnotationRepository
from src.database.dto.graph_dtos import ClaimIngestDTO, UserNoteDTO, SubGraphDTO
from src.database.repositories.in_memory_graph_repository import InMemoryGraphRepository


def test_in_memory_repository_implements_interfaces():
    """Verify InMemoryGraphRepository satisfies both IGraphRepository and IAnnotationRepository."""
    repo = InMemoryGraphRepository()
    assert isinstance(repo, IGraphRepository)
    assert isinstance(repo, IAnnotationRepository)


def test_fetch_full_graph_returns_seeded_dialectical_tensions():
    """Verify repository initializes with rich dialectical seed data."""
    repo = InMemoryGraphRepository()
    subgraph = repo.fetch_full_graph(limit=50)

    assert isinstance(subgraph, SubGraphDTO)
    assert len(subgraph.nodes) >= 4
    assert len(subgraph.edges) >= 2

    # Check for presence of CONTRADICTS edges
    contradictions = [e for e in subgraph.edges if e.relation_type == "CONTRADICTS"]
    assert len(contradictions) >= 1


def test_save_and_fetch_claim_cluster():
    """Verify in-memory ingestion persists claims and connects concepts."""
    repo = InMemoryGraphRepository()
    dto = ClaimIngestDTO(
        statement="گزاره تست درون‌حافظه‌ای",
        source_title="منبع تست",
        author_name="نویسنده تست",
        concepts=["مفهوم تست"],
        condition_category="test_cat",
        condition_description="شرایط تست",
    )

    success = repo.save_claim_cluster(dto)
    assert success is True

    subgraph = repo.fetch_related_subgraph(["مفهوم تست"])
    assert any(n.properties.get("statement") == "گزاره تست درون‌حافظه‌ای" for n in subgraph.nodes)


def test_add_and_fetch_user_notes():
    """Verify attaching user notes and retrieving them by claim_id."""
    repo = InMemoryGraphRepository()
    note_dto = UserNoteDTO(
        id="mem_note_1",
        claim_id="c1",
        content="تجربه بومی در اکوسیستم ایران تاییدکننده این گزاره است.",
        dispute_type="Endorsement",
    )

    created_entity = repo.add_user_note(note_dto)
    assert created_entity.id == "mem_note_1"

    notes = repo.fetch_notes_for_claim("c1")
    assert len(notes) >= 1
    assert notes[0].content.startswith("تجربه بومی")
