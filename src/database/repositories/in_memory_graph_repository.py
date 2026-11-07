"""In-Memory Graph & Annotation Repository for Danyar Engine.

Provides zero-dependency in-memory graph persistence and seeded dialectical knowledge.
Used for instant local execution, testing, and offline fallback when Neo4j is not running.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from src.contracts.engine_contracts import IGraphRepository, IAnnotationRepository
from src.database.dto.graph_dtos import (
    NodeDTO,
    EdgeDTO,
    SubGraphDTO,
    ClaimIngestDTO,
    UserNoteDTO,
)
from src.entities.domain_entities import UserNoteEntity


class InMemoryGraphRepository(IGraphRepository, IAnnotationRepository):
    """In-memory repository implementing both graph and annotation contracts."""

    def __init__(self) -> None:
        self._nodes: dict[str, NodeDTO] = {}
        self._edges: list[EdgeDTO] = []
        self._notes: dict[str, list[UserNoteEntity]] = {}  # claim_id -> list of notes
        self._seed_default_data()

    def _seed_default_data(self) -> None:
        """Seed rich dialectical knowledge nodes and contradictory tension edges."""
        # 1. Claims
        c1 = NodeDTO(
            id="c1",
            label="Claim",
            properties={
                "statement": "قبل از دستیابی به تطابق محصول با بازار (PMF)، توسعه سریع و استخدام انبوه تیم فنی بزرگ‌ترین خطای استراتژیک است.",
                "author": "پیتر تیل",
                "source": "کتاب صفر به یک",
                "confidence_score": 0.95,
                "condition": "استارتاپ‌های مراحل بذری و رشد اولیه",
            },
        )
        c2 = NodeDTO(
            id="c2",
            label="Claim",
            properties={
                "statement": "در بازارهایی با اثر شبکه‌ای قوی، سرعت سوزاندن سرمایه و مقیاس‌دهی فوق‌سریع تیم (Blitzscaling) بر بهره‌وری ارجحیت دارد.",
                "author": "رید هافمن",
                "source": "کتاب بلیتزاسکیلینگ",
                "confidence_score": 0.90,
                "condition": "بازارهای دارای برنده تمام یا اثر شبکه‌ای شدید",
            },
        )
        c3 = NodeDTO(
            id="c3",
            label="Claim",
            properties={
                "statement": "شفافیت مطلق و گزارش بی‌تعارف خطاهای درون‌سازمانی، تنها راه تضمین تصمیم‌گیری عقلانی و پایداری بلندمدت است.",
                "author": "ری دالیو",
                "source": "کتاب اصول رهبری",
                "confidence_score": 0.88,
                "condition": "فرهنگ‌های سازمانی مبتنی بر شایسته‌سالاری ایده",
            },
        )
        c4 = NodeDTO(
            id="c4",
            label="Claim",
            properties={
                "statement": "شفافیت بدون امنیت روانی، به اضطراب مفرط، ریاکاری سازمانی و سرکوب خلاقیت تیم می‌انجامد.",
                "author": "ایمی ادموندسون",
                "source": "سازمان بدون ترس",
                "confidence_score": 0.92,
                "condition": "تیم‌های نیازمند نوآوری و یادگیری مستمر",
            },
        )

        # 2. Concepts
        cp1 = NodeDTO(id="cp_pmf", label="Concept", properties={"name": "PMF"})
        cp2 = NodeDTO(id="cp_scale", label="Concept", properties={"name": "توسعه تیم"})
        cp3 = NodeDTO(id="cp_network", label="Concept", properties={"name": "اثر شبکه‌ای"})
        cp4 = NodeDTO(id="cp_transparency", label="Concept", properties={"name": "شفافیت"})
        cp5 = NodeDTO(id="cp_safety", label="Concept", properties={"name": "امنیت روانی"})

        # 3. Conditions
        cd1 = NodeDTO(id="cd_early", label="Condition", properties={"category": "market_phase", "description": "قبل از PMF"})
        cd2 = NodeDTO(id="cd_network", label="Condition", properties={"category": "market_type", "description": "اثر شبکه‌ای شدید"})

        for n in [c1, c2, c3, c4, cp1, cp2, cp3, cp4, cp5, cd1, cd2]:
            self._nodes[n.id] = n

        # 4. Dialectical Tensions & Relationships
        self._edges.extend([
            EdgeDTO(
                source_id="c1",
                target_id="c2",
                relation_type="CONTRADICTS",
                properties={"conflict_nature": "تقابل میان بقای سرمایه و محافظه‌کاری در برابر تسخیر سریع سهم بازار"},
            ),
            EdgeDTO(
                source_id="c3",
                target_id="c4",
                relation_type="CONTRADICTS",
                properties={"conflict_nature": "تضاد در تقدم شفافیت محض یا امنیت روانی اعضای تیم"},
            ),
            EdgeDTO(source_id="c1", target_id="cp_pmf", relation_type="MENTIONS", properties={}),
            EdgeDTO(source_id="c1", target_id="cp_scale", relation_type="MENTIONS", properties={}),
            EdgeDTO(source_id="c2", target_id="cp_network", relation_type="MENTIONS", properties={}),
            EdgeDTO(source_id="c2", target_id="cp_scale", relation_type="MENTIONS", properties={}),
            EdgeDTO(source_id="c3", target_id="cp_transparency", relation_type="MENTIONS", properties={}),
            EdgeDTO(source_id="c4", target_id="cp_safety", relation_type="MENTIONS", properties={}),
            EdgeDTO(source_id="c1", target_id="cd_early", relation_type="CONDITIONED_ON", properties={}),
            EdgeDTO(source_id="c2", target_id="cd_network", relation_type="CONDITIONED_ON", properties={}),
        ])

    def fetch_full_graph(self, limit: int = 150) -> SubGraphDTO:
        """Fetch all active in-memory nodes and edges up to limit."""
        nodes = list(self._nodes.values())[:limit]
        node_ids = {n.id for n in nodes}
        edges = [e for e in self._edges if e.source_id in node_ids and e.target_id in node_ids]
        return SubGraphDTO(nodes=nodes, edges=edges)

    def fetch_related_subgraph(self, concept_names: list[str]) -> SubGraphDTO:
        """Fetch claims, concepts, and relationships matching concept keywords."""
        if not concept_names:
            return self.fetch_full_graph(limit=30)

        norm_keywords = [k.lower().strip() for k in concept_names if k.strip()]
        matched_node_ids: set[str] = set()

        for nid, node in self._nodes.items():
            text_repr = f"{node.label} {node.id} {str(node.properties)}".lower()
            if any(kw in text_repr for kw in norm_keywords):
                matched_node_ids.add(nid)

        # Include 1-hop connected neighbors
        neighbor_ids: set[str] = set(matched_node_ids)
        for e in self._edges:
            if e.source_id in matched_node_ids:
                neighbor_ids.add(e.target_id)
            if e.target_id in matched_node_ids:
                neighbor_ids.add(e.source_id)

        matched_nodes = [self._nodes[nid] for nid in neighbor_ids if nid in self._nodes]
        matched_edges = [
            e for e in self._edges if e.source_id in neighbor_ids and e.target_id in neighbor_ids
        ]
        return SubGraphDTO(nodes=matched_nodes, edges=matched_edges)

    def save_claim_cluster(self, dto: ClaimIngestDTO) -> bool:
        """Persist a new claim cluster into memory."""
        cid = f"claim_{uuid.uuid4().hex[:8]}"
        claim_node = NodeDTO(
            id=cid,
            label="Claim",
            properties={
                "statement": dto.statement,
                "author": dto.author_name,
                "source": dto.source_title,
                "confidence_score": dto.confidence_score,
                "condition": dto.condition_description,
            },
        )
        self._nodes[cid] = claim_node

        for cname in dto.concepts:
            cpid = f"cp_{uuid.uuid4().hex[:6]}"
            self._nodes[cpid] = NodeDTO(id=cpid, label="Concept", properties={"name": cname})
            self._edges.append(EdgeDTO(source_id=cid, target_id=cpid, relation_type="MENTIONS", properties={}))

        return True

    def add_user_note(self, note_dto: UserNoteDTO) -> UserNoteEntity:
        """Attach a user note or dispute to a target claim in memory."""
        now = datetime.now(timezone.utc)
        is_dispute = note_dto.dispute_type.strip().lower() == "dispute"

        entity = UserNoteEntity(
            id=note_dto.id,
            claim_id=note_dto.claim_id,
            content=note_dto.content,
            created_at=now,
            sentiment=note_dto.dispute_type,
            disputes=is_dispute,
        )

        if note_dto.claim_id not in self._notes:
            self._notes[note_dto.claim_id] = []
        self._notes[note_dto.claim_id].append(entity)

        # Also add as a node in the graph for visual inspection
        self._nodes[note_dto.id] = NodeDTO(
            id=note_dto.id,
            label="UserNote",
            properties={
                "content": note_dto.content,
                "dispute_type": note_dto.dispute_type,
                "claim_id": note_dto.claim_id,
            },
        )
        rel_type = "DISPUTES" if is_dispute else "ANNOTATES"
        self._edges.append(EdgeDTO(source_id=note_dto.id, target_id=note_dto.claim_id, relation_type=rel_type, properties={}))

        return entity

    def fetch_notes_for_claim(self, claim_id: str) -> list[UserNoteEntity]:
        """Retrieve notes attached to a claim."""
        return self._notes.get(claim_id, [])

    def close(self) -> None:
        """No-op cleanup for in-memory store."""
        pass


__all__ = ["InMemoryGraphRepository"]
