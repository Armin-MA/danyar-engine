"""Neo4j Annotation Repository for Danyar Engine.

Implements IAnnotationRepository to attach and query human user notes,
dispute annotations, and credibility feedback directly on Claim nodes.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import neo4j
from neo4j import GraphDatabase, Driver

from src.config.neo4j_config import Neo4jConfig
from src.contracts.engine_contracts import IAnnotationRepository
from src.database.dto.graph_dtos import UserNoteDTO
from src.entities.domain_entities import UserNoteEntity
from src.database.queries.cypher_statements import (
    ATTACH_USER_NOTE,
    FETCH_NOTES_FOR_CLAIM,
)


class DatabaseError(Exception):
    """Base exception for annotation database errors."""
    pass


class EntityNotFoundError(DatabaseError):
    """Raised when the target entity (e.g. Claim) does not exist in Neo4j."""
    pass


CHECK_CLAIM_EXISTS = "MATCH (c:Claim {id: $claim_id}) RETURN c.id AS id"
MERGE_DISPUTE_EDGE = "MATCH (n:UserNote {id: $note_id}), (c:Claim {id: $claim_id}) MERGE (n)-[:DISPUTES]->(c)"


class Neo4jAnnotationRepository(IAnnotationRepository):
    """Repository handling human notes and dispute annotations in Neo4j."""

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
                raise DatabaseError(f"Failed to initialize Neo4j driver for annotations: {e}") from e

    def _get_session(self):
        try:
            return self._driver.session(database=self.config.database)
        except Exception as e:
            raise DatabaseError(f"Failed to acquire session: {e}") from e

    def add_user_note(self, note_dto: UserNoteDTO) -> UserNoteEntity:
        """Attach a user note or dispute annotation to a target claim.

        Args:
            note_dto: UserNoteDTO holding note id, target claim_id, content, and dispute_type.

        Returns:
            Instantiated UserNoteEntity.

        Raises:
            EntityNotFoundError: If target claim does not exist.
            DatabaseError: If write query fails.
        """
        now = datetime.now(timezone.utc)
        now_iso = note_dto.created_at or now.isoformat()
        is_dispute = note_dto.dispute_type.strip().lower() == "dispute"

        with self._get_session() as session:
            # 1. Verify target claim exists
            def _check_claim(tx):
                res = tx.run(CHECK_CLAIM_EXISTS, claim_id=note_dto.claim_id)
                return list(res)

            claim_records = session.execute_read(_check_claim)
            if not claim_records:
                raise EntityNotFoundError(f"Claim with id '{note_dto.claim_id}' not found.")

            # 2. Persist UserNote and ANNOTATES edge
            def _create_note(tx):
                tx.run(
                    ATTACH_USER_NOTE,
                    claim_id=note_dto.claim_id,
                    note_id=note_dto.id,
                    content=note_dto.content,
                    dispute_type=note_dto.dispute_type,
                    credibility_impact=note_dto.credibility_impact,
                    created_at=now_iso,
                )
                if is_dispute:
                    tx.run(MERGE_DISPUTE_EDGE, note_id=note_dto.id, claim_id=note_dto.claim_id)

            try:
                session.execute_write(_create_note)
            except Exception as e:
                raise DatabaseError(f"Failed to attach note to claim: {e}") from e

        return UserNoteEntity(
            id=note_dto.id,
            claim_id=note_dto.claim_id,
            content=note_dto.content,
            created_at=now if not note_dto.created_at else datetime.fromisoformat(now_iso),
            sentiment=note_dto.dispute_type,
            disputes=is_dispute,
        )

    def fetch_notes_for_claim(self, claim_id: str) -> list[UserNoteEntity]:
        """Retrieve all human feedback notes and annotations for a claim.

        Args:
            claim_id: Unique identifier of target claim.

        Returns:
            List of UserNoteEntity instances.
        """
        with self._get_session() as session:
            def _read_notes(tx):
                res = tx.run(FETCH_NOTES_FOR_CLAIM, claim_id=claim_id)
                return list(res)

            try:
                records = session.execute_read(_read_notes)
            except Exception as e:
                raise DatabaseError(f"Failed to fetch notes for claim '{claim_id}': {e}") from e

        notes: list[UserNoteEntity] = []
        for r in records:
            data = dict(r)
            dispute_type = data.get("dispute_type", "")
            is_dispute = str(dispute_type).strip().lower() == "dispute"
            created_at_val = data.get("created_at")
            if isinstance(created_at_val, str):
                created_dt = datetime.fromisoformat(created_at_val)
            elif isinstance(created_at_val, datetime):
                created_dt = created_at_val
            else:
                created_dt = datetime.now(timezone.utc)

            notes.append(
                UserNoteEntity(
                    id=str(data.get("id")),
                    claim_id=str(data.get("claim_id", claim_id)),
                    content=str(data.get("content", "")),
                    created_at=created_dt,
                    sentiment=str(dispute_type),
                    disputes=is_dispute,
                )
            )

        return notes


__all__ = ["Neo4jAnnotationRepository", "DatabaseError", "EntityNotFoundError"]
