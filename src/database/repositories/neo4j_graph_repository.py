"""Neo4j Graph Repository Implementation for Danyar Engine.

Implements IGraphRepository using the official neo4j Python driver.
Handles connection pooling, transactional writes, and subgraph deserialization
into validated SubGraphDTO instances.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any
import neo4j
from neo4j import GraphDatabase, Driver

from src.config.neo4j_config import Neo4jConfig
from src.contracts.engine_contracts import IGraphRepository
from src.database.dto.graph_dtos import (
    ClaimIngestDTO,
    SubGraphDTO,
    NodeDTO,
    EdgeDTO,
)
from src.database.queries.cypher_statements import (
    MERGE_CLAIM_INGEST,
    TRAVERSE_SUBGRAPH_BY_CONCEPTS,
    FETCH_FULL_GRAPH,
)


class DatabaseError(Exception):
    """Base exception for Neo4j database errors."""
    pass


class DatabaseConnectionError(DatabaseError):
    """Raised when establishing connection or acquiring a session fails."""
    pass


class Neo4jGraphRepository(IGraphRepository):
    """Repository handling persistence and queries for the Neo4j knowledge graph."""

    def __init__(
        self,
        driver: Driver | None = None,
        config: Neo4jConfig | None = None,
    ) -> None:
        self.config = config or Neo4jConfig()
        if driver is not None:
            self._driver = driver
        else:
            try:
                self._driver = GraphDatabase.driver(
                    self.config.uri,
                    auth=(self.config.username, self.config.password),
                )
            except Exception as e:
                raise DatabaseConnectionError(f"Failed to initialize Neo4j driver: {e}") from e

    def close(self) -> None:
        """Close driver connection pool cleanly."""
        if self._driver is not None:
            self._driver.close()

    def _get_session(self):
        try:
            return self._driver.session(database=self.config.database)
        except Exception as e:
            raise DatabaseConnectionError(f"Failed to acquire Neo4j session: {e}") from e

    def save_claim_cluster(self, dto: ClaimIngestDTO) -> bool:
        """Atomically persist a cluster of claims, author, source, concepts, and conditions.

        Args:
            dto: ClaimIngestDTO holding parsed claim parameters.

        Returns:
            True if write succeeded.

        Raises:
            DatabaseConnectionError: If connection cannot be established.
            DatabaseError: If transaction fails or constraint violated.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        claim_id = f"claim_{uuid.uuid4().hex[:12]}"
        has_condition = bool(dto.condition_category and dto.condition_category != "general")

        params: dict[str, Any] = {
            "author_id": f"auth_{uuid.uuid4().hex[:8]}",
            "author_name": dto.author_name,
            "base_reputation": 7.0,
            "source_id": f"src_{uuid.uuid4().hex[:8]}",
            "source_title": dto.source_title,
            "domain": "business",
            "source_type": "book",
            "claim_id": claim_id,
            "statement": dto.statement,
            "claim_type": dto.claim_type,
            "confidence_score": dto.confidence_score,
            "concepts": dto.concepts,
            "has_condition": has_condition,
            "condition_id": f"cond_{uuid.uuid4().hex[:8]}",
            "condition_category": dto.condition_category,
            "condition_description": dto.condition_description,
            "created_at": now_iso,
        }

        def _tx_work(tx):
            result = tx.run(MERGE_CLAIM_INGEST, **params)
            return list(result)

        try:
            with self._get_session() as session:
                session.execute_write(_tx_work)
                return True
        except DatabaseConnectionError:
            raise
        except Exception as e:
            raise DatabaseError(f"Write transaction failed: {e}") from e

    def fetch_related_subgraph(self, concept_names: list[str]) -> SubGraphDTO:
        """Fetch active subgraph matching the requested canonical concepts.

        Args:
            concept_names: List of concept keywords to seed graph traversal.

        Returns:
            SubGraphDTO containing parsed NodeDTO and EdgeDTO elements.
        """
        def _tx_read(tx):
            result = tx.run(TRAVERSE_SUBGRAPH_BY_CONCEPTS, concept_names=concept_names)
            return list(result)

        try:
            with self._get_session() as session:
                records = session.execute_read(_tx_read)
        except DatabaseConnectionError:
            raise
        except Exception as e:
            raise DatabaseError(f"Read query failed: {e}") from e

        return self._records_to_subgraph(records)

    def fetch_full_graph(self, limit: int = 150) -> SubGraphDTO:
        """Fetch full active graph up to limit for dashboard visualization."""
        def _tx_read(tx):
            result = tx.run(FETCH_FULL_GRAPH, limit=limit)
            return list(result)

        try:
            with self._get_session() as session:
                records = session.execute_read(_tx_read)
        except DatabaseConnectionError:
            raise
        except Exception as e:
            raise DatabaseError(f"Full graph fetch failed: {e}") from e

        return self._records_to_subgraph(records)

    def _records_to_subgraph(self, records: list[Any]) -> SubGraphDTO:
        """Helper to parse Neo4j records/paths into SubGraphDTO."""
        node_map: dict[str, NodeDTO] = {}
        edge_set: set[tuple[str, str, str]] = set()
        edges: list[EdgeDTO] = []

        def _process_node(raw_node: Any) -> None:
            if raw_node is None:
                return
            nid = str(getattr(raw_node, "id", getattr(raw_node, "element_id", "")))
            if not nid:
                return
            labels = list(getattr(raw_node, "labels", ["Node"]))
            lbl = labels[0] if labels else "Node"
            props = dict(raw_node.items()) if hasattr(raw_node, "items") else {}
            if nid not in node_map:
                node_map[nid] = NodeDTO(id=nid, label=lbl, properties=props)

        def _process_rel(raw_rel: Any) -> None:
            if raw_rel is None:
                return
            src = str(getattr(raw_rel, "start_node", None) or getattr(raw_rel, "start", ""))
            tgt = str(getattr(raw_rel, "end_node", None) or getattr(raw_rel, "end", ""))
            rel_type = str(getattr(raw_rel, "type", "RELATED_TO"))
            key = (src, tgt, rel_type)
            if key not in edge_set:
                edge_set.add(key)
                props = dict(raw_rel.items()) if hasattr(raw_rel, "items") else {}
                edges.append(EdgeDTO(source_id=src, target_id=tgt, relation_type=rel_type, properties=props))

        for record in records:
            # Check for path object
            if hasattr(record, "values"):
                items = record.values()
            elif isinstance(record, dict):
                items = record.values()
            else:
                items = [record]

            for item in items:
                # Handle path objects
                if hasattr(item, "nodes") and hasattr(item, "relationships"):
                    for n in item.nodes:
                        _process_node(n)
                    for r in item.relationships:
                        _process_rel(r)
                elif isinstance(item, list):
                    for sub in item:
                        if hasattr(sub, "labels"):
                            _process_node(sub)
                        elif hasattr(sub, "type"):
                            _process_rel(sub)
                elif hasattr(item, "labels"):
                    _process_node(item)
                elif hasattr(item, "type"):
                    _process_rel(item)

        return SubGraphDTO(nodes=list(node_map.values()), edges=edges)


__all__ = ["Neo4jGraphRepository", "DatabaseError", "DatabaseConnectionError"]
