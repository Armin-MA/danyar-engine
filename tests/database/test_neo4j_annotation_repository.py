"""Unit Tests for Neo4j Annotation Repository [TASK-014].

Verifies user note attachment, dispute edge generation, retrieval,
and EntityNotFoundError when referencing invalid claims.
"""

from __future__ import annotations

from unittest.mock import MagicMock
import pytest

from src.contracts.engine_contracts import IAnnotationRepository
from src.database.dto.graph_dtos import UserNoteDTO
from src.entities.domain_entities import UserNoteEntity
from src.database.repositories.neo4j_annotation_repository import (
    Neo4jAnnotationRepository,
    EntityNotFoundError,
)


def test_annotation_repository_implements_interface():
    """Verify Neo4jAnnotationRepository implements IAnnotationRepository ABC."""
    mock_driver = MagicMock()
    repo = Neo4jAnnotationRepository(driver=mock_driver)
    assert isinstance(repo, IAnnotationRepository)


def test_happy_path_attach_user_note():
    """Happy Path: Attaches (:UserNote)-[:ANNOTATES]->(:Claim) successfully."""
    mock_driver = MagicMock()
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__.return_value = mock_session

    # Step 1: Claim existence check returns claim
    # Step 2: Note insertion returns created note id
    mock_session.execute_read.return_value = [{"id": "claim_123"}]
    mock_session.execute_write.return_value = [{"note_id": "note_001"}]

    repo = Neo4jAnnotationRepository(driver=mock_driver)
    note_dto = UserNoteDTO(
        id="note_001",
        claim_id="claim_123",
        content="تجربه شخصی من در اسکیل‌آپ این توصیه را تایید می‌کند.",
        dispute_type="Endorsement",
        credibility_impact=0.1,
    )

    created_entity = repo.add_user_note(note_dto)

    assert isinstance(created_entity, UserNoteEntity)
    assert created_entity.id == "note_001"
    assert created_entity.claim_id == "claim_123"
    assert created_entity.disputes is False


def test_edge_case_attach_dispute_note():
    """Edge Case: Creates dispute annotation with disputes=True when dispute_type is Dispute."""
    mock_driver = MagicMock()
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__.return_value = mock_session

    mock_session.execute_read.return_value = [{"id": "claim_999"}]
    mock_session.execute_write.return_value = [{"note_id": "note_dispute_1"}]

    repo = Neo4jAnnotationRepository(driver=mock_driver)
    note_dto = UserNoteDTO(
        id="note_dispute_1",
        claim_id="claim_999",
        content="در بازارهای سنتی این استراتژی منجر به شکست می‌شود.",
        dispute_type="Dispute",
        credibility_impact=-0.3,
    )

    created_entity = repo.add_user_note(note_dto)

    assert created_entity.disputes is True
    assert created_entity.id == "note_dispute_1"


def test_failure_state_target_claim_not_found():
    """Failure State: Raises EntityNotFoundError when targeting non-existent claim id."""
    mock_driver = MagicMock()
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__.return_value = mock_session

    # Return empty list from existence check
    mock_session.execute_read.return_value = []

    repo = Neo4jAnnotationRepository(driver=mock_driver)
    note_dto = UserNoteDTO(
        id="note_err",
        claim_id="missing_claim",
        content="این ادعا وجود ندارد.",
    )

    with pytest.raises(EntityNotFoundError, match="Claim with id 'missing_claim' not found"):
        repo.add_user_note(note_dto)


def test_fetch_notes_for_claim():
    """Verifies fetching list of UserNoteEntity for an existing claim."""
    mock_driver = MagicMock()
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__.return_value = mock_session

    mock_records = [
        {
            "id": "note_1",
            "claim_id": "c1",
            "content": "یادداشت اول",
            "dispute_type": "Dispute",
            "credibility_impact": -0.2,
            "created_at": "2026-11-07T12:00:00+00:00",
        }
    ]
    mock_session.execute_read.return_value = mock_records

    repo = Neo4jAnnotationRepository(driver=mock_driver)
    notes = repo.fetch_notes_for_claim("c1")

    assert len(notes) == 1
    assert notes[0].id == "note_1"
    assert notes[0].disputes is True
