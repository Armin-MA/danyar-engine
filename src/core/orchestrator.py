"""System IoC Container & Bootstrap Orchestrator for Danyar Engine.

Wires abstract contracts to concrete implementations across database,
mechanics, and presentation layers with dependency injection, health checking,
and graceful shutdown.
"""

from __future__ import annotations

from typing import Any
from fastapi import FastAPI

from src.config.app_config import AppConfig
from src.contracts.engine_contracts import (
    IGraphRepository,
    IAnnotationRepository,
    ISocraticAdvisor,
    ICredibilityCalculator,
    IExtractionPipeline,
    IDialecticalSynthesizer,
)
from src.database.repositories.neo4j_graph_repository import Neo4jGraphRepository
from src.database.repositories.neo4j_annotation_repository import Neo4jAnnotationRepository
from src.mechanics.calculate_dynamic_credibility import DynamicCredibilityCalculator
from src.mechanics.extract_atomic_claims import AtomicClaimExtractor
from src.mechanics.evaluate_dialectical_conflict import DialecticalConflictEvaluator
from src.mechanics.formulate_socratic_inquiry import SocraticAdvisor
from src.ui.api.routes import create_app


class BootError(Exception):
    """Raised when system bootstrapping, wiring, or health check fails."""
    pass


class DanyarContainer:
    """Dependency Injection (IoC) Container orchestrating the Danyar Engine."""

    def __init__(
        self,
        config: AppConfig | None = None,
        graph_repo: IGraphRepository | None = None,
        annotation_repo: IAnnotationRepository | None = None,
        advisor: ISocraticAdvisor | None = None,
        credibility_calc: ICredibilityCalculator | None = None,
        extraction_pipeline: IExtractionPipeline | None = None,
        dialectical_synthesizer: IDialecticalSynthesizer | None = None,
        verify_health: bool = False,
    ) -> None:
        self.config = config or AppConfig()

        # 1. Database Repositories
        self.graph_repo = graph_repo or Neo4jGraphRepository(config=self.config.neo4j)
        self.annotation_repo = annotation_repo or Neo4jAnnotationRepository(config=self.config.neo4j)

        # 2. Epistemological Mechanics
        self.credibility_calc = credibility_calc or DynamicCredibilityCalculator()
        self.extraction_pipeline = extraction_pipeline or AtomicClaimExtractor()
        self.dialectical_synthesizer = dialectical_synthesizer or DialecticalConflictEvaluator()
        self.advisor = advisor or SocraticAdvisor()

        # 3. Health check verification
        if verify_health:
            self._verify_health()

        # 4. FastAPI Presentation Layer
        self.app = create_app(
            graph_repo=self.graph_repo,
            annotation_repo=self.annotation_repo,
            advisor=self.advisor,
        )

    def _verify_health(self) -> None:
        """Probe dependencies to assert system operational status."""
        try:
            # Query graph repository to verify Neo4j connection
            self.graph_repo.fetch_related_subgraph(["__health_check__"])
        except Exception as e:
            raise BootError(f"Health check failed during system bootstrapping: {e}") from e

    def get_app(self) -> FastAPI:
        """Retrieve configured FastAPI application instance."""
        return self.app

    def shutdown(self) -> None:
        """Gracefully release database pools and resource handlers."""
        if hasattr(self.graph_repo, "close") and callable(self.graph_repo.close):
            self.graph_repo.close()


def bootstrap_system(
    config: AppConfig | None = None,
    graph_repo: IGraphRepository | None = None,
    annotation_repo: IAnnotationRepository | None = None,
    advisor: ISocraticAdvisor | None = None,
    verify_health: bool = False,
) -> FastAPI:
    """Bootstrap complete Danyar Engine and return runnable FastAPI app."""
    container = DanyarContainer(
        config=config,
        graph_repo=graph_repo,
        annotation_repo=annotation_repo,
        advisor=advisor,
        verify_health=verify_health,
    )
    return container.get_app()


__all__ = ["DanyarContainer", "BootError", "bootstrap_system"]
