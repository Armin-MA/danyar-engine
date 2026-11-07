"""Unit Tests for System IoC Container & Bootstrap Orchestrator [TASK-018].

Verifies complete wiring of contracts to concrete layers, IoC dependency injection,
health check verification, and graceful shutdown.
"""

from __future__ import annotations

from unittest.mock import MagicMock
import pytest
from fastapi import FastAPI

from src.config.app_config import AppConfig
from src.contracts.engine_contracts import (
    IGraphRepository,
    IAnnotationRepository,
    ISocraticAdvisor,
    ICredibilityCalculator,
)
from src.core.orchestrator import DanyarContainer, BootError, bootstrap_system


def test_happy_path_bootstraps_system_and_bindings():
    """Happy Path: Bootstraps system cleanly and verifies all repository & service bindings."""
    mock_graph_repo = MagicMock(spec=IGraphRepository)
    mock_annotation_repo = MagicMock(spec=IAnnotationRepository)
    mock_advisor = MagicMock(spec=ISocraticAdvisor)

    container = DanyarContainer(
        graph_repo=mock_graph_repo,
        annotation_repo=mock_annotation_repo,
        advisor=mock_advisor,
        verify_health=False,
    )

    assert container.graph_repo is mock_graph_repo
    assert container.annotation_repo is mock_annotation_repo
    assert container.advisor is mock_advisor
    assert isinstance(container.credibility_calc, ICredibilityCalculator)

    app = container.get_app()
    assert isinstance(app, FastAPI)
    assert app.title == "Danyar Engine API"


def test_edge_case_graceful_shutdown():
    """Edge Case: Provides graceful shutdown hook closing connection pools."""
    mock_graph_repo = MagicMock(spec=IGraphRepository)
    mock_annotation_repo = MagicMock(spec=IAnnotationRepository)

    container = DanyarContainer(
        graph_repo=mock_graph_repo,
        annotation_repo=mock_annotation_repo,
        verify_health=False,
    )
    container.shutdown()

    # If repository has close() method, verify it was invoked
    if hasattr(mock_graph_repo, "close"):
        mock_graph_repo.close.assert_called_once()


def test_failure_state_raises_boot_error_on_unreachable_db():
    """Failure State: Raises BootError with clear diagnosis when Neo4j health check fails."""
    mock_graph_repo = MagicMock(spec=IGraphRepository)
    mock_graph_repo.fetch_related_subgraph.side_effect = Exception("ConnectionRefusedError: bolt://localhost:7687")

    with pytest.raises(BootError, match="Health check failed"):
        DanyarContainer(
            graph_repo=mock_graph_repo,
            verify_health=True,
        )


def test_bootstrap_system_helper():
    """Verifies bootstrap_system functional helper returns runnable FastAPI application."""
    mock_graph_repo = MagicMock(spec=IGraphRepository)
    app = bootstrap_system(graph_repo=mock_graph_repo, verify_health=False)
    assert isinstance(app, FastAPI)
