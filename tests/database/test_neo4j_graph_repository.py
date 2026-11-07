"""Unit Tests for Neo4j Graph Repository [TASK-013].

Verifies session management, transactional execution of parameterized Cypher statements,
subgraph reconstruction into SubGraphDTO, and exception resilience using mocked Neo4j driver.
"""

from __future__ import annotations

from unittest.mock import MagicMock
import pytest

from src.contracts.engine_contracts import IGraphRepository
from src.database.dto.graph_dtos import ClaimIngestDTO, SubGraphDTO
from src.database.repositories.neo4j_graph_repository import (
    Neo4jGraphRepository,
    DatabaseError,
    DatabaseConnectionError,
)


def test_repository_implements_interface():
    """Verify Neo4jGraphRepository implements IGraphRepository ABC."""
    mock_driver = MagicMock()
    repo = Neo4jGraphRepository(driver=mock_driver)
    assert isinstance(repo, IGraphRepository)


def test_happy_path_save_claim_cluster():
    """Happy Path: Saves claim cluster and relationships atomically in a managed write transaction."""
    mock_driver = MagicMock()
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__.return_value = mock_session
    mock_session.execute_write.return_value = [{"claim_id": "claim_test_1"}]

    repo = Neo4jGraphRepository(driver=mock_driver)
    ingest_dto = ClaimIngestDTO(
        statement="استفاده از TDD باگ‌های کد را تا ۷۰٪ کاهش می‌دهد.",
        source_title="مهندسی نرم‌افزار تمیز",
        author_name="مارتین فاولر",
        concepts=["TDD", "کیفیت کد"],
        condition_category="software_development",
        condition_description="پروژه‌های با پیچیدگی متوسط به بالا",
    )

    success = repo.save_claim_cluster(ingest_dto)

    assert success is True
    assert mock_session.execute_write.called


def test_happy_path_fetch_related_subgraph():
    """Happy Path: Fetches related subgraph and parses records into validated SubGraphDTO."""
    mock_driver = MagicMock()
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__.return_value = mock_session

    # Mock Neo4j Record representing path or nodes/edges
    mock_node = MagicMock()
    mock_node.id = "claim_1"
    mock_node.element_id = "claim_1"
    mock_node.labels = ["Claim"]
    mock_node.items.return_value = [("statement", "گزاره اول")]

    mock_record = {
        "nodes": [mock_node],
        "relationships": [],
    }
    mock_session.execute_read.return_value = [mock_record]

    repo = Neo4jGraphRepository(driver=mock_driver)
    subgraph = repo.fetch_related_subgraph(["TDD"])

    assert isinstance(subgraph, SubGraphDTO)
    assert len(subgraph.nodes) >= 1
    assert subgraph.nodes[0].id == "claim_1"


def test_failure_state_raises_database_error_on_transaction_exception():
    """Failure State: Raises DatabaseError when Neo4j write transaction raises an exception."""
    mock_driver = MagicMock()
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__.return_value = mock_session
    mock_session.execute_write.side_effect = RuntimeError("Neo.ClientError.Schema.ConstraintValidationFailed")

    repo = Neo4jGraphRepository(driver=mock_driver)
    ingest_dto = ClaimIngestDTO(
        statement="گزاره خطا",
        source_title="منبع",
        author_name="نویسنده",
    )

    with pytest.raises(DatabaseError, match="ConstraintValidationFailed"):
        repo.save_claim_cluster(ingest_dto)


def test_failure_state_raises_connection_error_when_session_fails():
    """Failure State: Raises DatabaseConnectionError when driver cannot establish session."""
    mock_driver = MagicMock()
    mock_driver.session.side_effect = Exception("ServiceUnavailable: Connection refused")

    repo = Neo4jGraphRepository(driver=mock_driver)
    with pytest.raises(DatabaseConnectionError, match="Connection refused"):
        repo.fetch_related_subgraph(["any"])
