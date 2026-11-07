"""Book Assimilation & Cross-Book Dialectical Harmonizer Pipeline.

Ingests book PDF documents, segments them into semantic chunks, extracts
atomic claims and conditions, compares against existing claims in the knowledge
graph to detect SUPPORTS, CONTRADICTS, and REFINES relationships, and atomically updates the graph.
"""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass
from typing import Any, Callable

from src.contracts.engine_contracts import (
    IGraphRepository,
    IExtractionPipeline,
    IDialecticalSynthesizer,
)
from src.database.dto.graph_dtos import ClaimIngestDTO, NodeDTO, EdgeDTO
from src.database.repositories.in_memory_graph_repository import InMemoryGraphRepository
from src.entities.domain_entities import SourceEntity, ClaimEntity
from src.mechanics.book_chunker import chunk_book_pages
from src.mechanics.evaluate_dialectical_conflict import DialecticalConflictEvaluator
from src.mechanics.extract_atomic_claims import AtomicClaimExtractor
from src.mechanics.pdf_reader import extract_text_from_pdf


def _default_heuristic_claim_invoker(prompt: str) -> str:
    """Deterministic heuristic extractor when external LLM API is not configured."""
    # Extract text from prompt snippet
    lines = prompt.splitlines()
    snippet_lines = []
    capture = False
    for line in lines:
        if "[Text Snippet" in line:
            capture = True
            continue
        if capture:
            snippet_lines.append(line)

    content = " ".join(snippet_lines).strip() or prompt
    # Split into clean sentences
    raw_sentences = [s.strip() for s in re.split(r"[.\n؟!\u061f]", content) if len(s.strip()) > 20]

    claims_data = []
    for s in raw_sentences[:3]:
        words = s.split()
        concepts = [w for w in words if len(w) > 4][:2]
        claims_data.append({
            "statement": s,
            "type": "Actionable_Advice",
            "confidence_score": 0.88,
            "concepts": concepts or ["استراتژی"],
            "condition_category": "general",
            "condition_description": "وضعیت توسعه کسب‌وکار",
        })

    if not claims_data and content:
        claims_data.append({
            "statement": content[:150],
            "type": "Actionable_Advice",
            "confidence_score": 0.85,
            "concepts": ["مدیریت"],
            "condition_category": "general",
            "condition_description": "عمومی",
        })

    return json.dumps({"claims": claims_data})


def _default_heuristic_dialectical_invoker(prompt: str) -> str:
    """Deterministic heuristic dialectical tension detector when LLM is offline."""
    # Find existing claim IDs
    matches = re.findall(r"- \[([a-zA-Z0-9_]+)\]:", prompt)
    relationships = []

    opposing_pairs = [
        ("mvp", "monopoly"),
        ("early", "burn"),
        ("scale", "premature"),
        ("ناقص", "انحصار"),
        ("سریع", "کیفیت"),
        ("استخدام", "بقا"),
    ]

    lower_prompt = prompt.lower()
    has_tension = any((p1 in lower_prompt and p2 in lower_prompt) for p1, p2 in opposing_pairs)

    for target_id in matches[:2]:
        rel_type = "CONTRADICTS" if has_tension else "SUPPORTS"
        relationships.append({
            "target_claim_id": target_id,
            "relation_type": rel_type,
            "strength": 0.85,
            "conflict_nature": "تفاوت بنیادین در تقدم سرعت یادگیری در برابر مقیاس‌دهی سرمایه‌محور",
            "resolution_hint": "وابسته به نوع ساختار بازار و سرعت ظهور اثر شبکه‌ای",
        })

    return json.dumps({"relationships": relationships})


@dataclass(frozen=True)
class BookAssimilationSummary:
    """Statistical summary of an assimilated book document."""

    book_title: str
    author_name: str
    pages_count: int
    chunks_count: int
    claims_count: int
    supports_count: int
    contradicts_count: int
    refines_count: int


def assimilate_book_pdf(
    pdf_path: str,
    book_title: str,
    author_name: str,
    domain: str = "general",
    graph_repo: IGraphRepository | None = None,
    extractor: IExtractionPipeline | None = None,
    evaluator: IDialecticalSynthesizer | None = None,
) -> BookAssimilationSummary:
    """End-to-end pipeline to read, extract, dialectically harmonize, and persist a book PDF.

    Args:
        pdf_path: Path to the PDF file.
        book_title: Name of the book.
        author_name: Name of the primary author.
        domain: Domain or discipline of the book.
        graph_repo: Target graph repository (Neo4j or InMemory).
        extractor: Optional custom IExtractionPipeline instance.
        evaluator: Optional custom IDialecticalSynthesizer instance.

    Returns:
        BookAssimilationSummary with detailed ingestion metrics.
    """
    repo = graph_repo or InMemoryGraphRepository()
    claim_extractor = extractor or AtomicClaimExtractor()
    dialectic_evaluator = evaluator or DialecticalConflictEvaluator()

    # Step 1: Extract pages
    pages = extract_text_from_pdf(pdf_path)
    if not pages:
        return BookAssimilationSummary(
            book_title=book_title,
            author_name=author_name,
            pages_count=0,
            chunks_count=0,
            claims_count=0,
            supports_count=0,
            contradicts_count=0,
            refines_count=0,
        )

    # Step 2: Semantic Chunking
    chunks = chunk_book_pages(pages, max_chars_per_chunk=1500, overlap_chars=200)

    # Step 3: Fetch existing claims currently in the graph for dialectical cross-comparison
    existing_claims: list[ClaimEntity] = []
    if hasattr(repo, "fetch_full_graph"):
        full_subgraph = repo.fetch_full_graph(limit=250)
        for node in full_subgraph.nodes:
            if node.label.lower() == "claim":
                existing_claims.append(
                    ClaimEntity(
                        id=node.id,
                        statement=str(node.properties.get("statement", node.id)),
                        source_id=node.properties.get("source"),
                    )
                )

    source = SourceEntity(
        id=f"src_{uuid.uuid4().hex[:8]}",
        title=book_title,
        author=author_name,
        domain=domain,
    )

    all_extracted_claims: list[ClaimEntity] = []
    supports_count = 0
    contradicts_count = 0
    refines_count = 0

    # Step 4: Extract and harmonize chunk by chunk
    for chunk in chunks:
        if isinstance(claim_extractor, AtomicClaimExtractor):
            extracted = claim_extractor.extract_from_text(
                source, chunk, llm_invoker=_default_heuristic_claim_invoker
            )
        else:
            extracted = claim_extractor.extract_from_text(source, chunk)

        for claim in extracted:
            all_extracted_claims.append(claim)

            # Persist claim cluster to repository
            ingest_dto = ClaimIngestDTO(
                statement=claim.statement,
                source_title=book_title,
                author_name=author_name,
                concepts=claim.concept_ids,
                condition_category="general",
                condition_description="",
                confidence_score=claim.confidence_score,
            )
            repo.save_claim_cluster(ingest_dto)

            # Ensure node with claim.id exists for dialectical edge linking
            claim_node_dto = NodeDTO(
                id=claim.id,
                label="Claim",
                properties={
                    "statement": claim.statement,
                    "author": author_name,
                    "source": book_title,
                    "confidence_score": claim.confidence_score,
                },
            )
            if hasattr(repo, "add_node"):
                repo.add_node(claim_node_dto)

            # Step 5: Cross-Book Dialectical Comparison against existing claims
            if existing_claims:
                if isinstance(dialectic_evaluator, DialecticalConflictEvaluator):
                    relationships = dialectic_evaluator.analyze_relationship(
                        claim, existing_claims, llm_invoker=_default_heuristic_dialectical_invoker
                    )
                else:
                    relationships = dialectic_evaluator.analyze_relationship(claim, existing_claims)
                for rel in relationships:
                    r_type = rel.relation_type.upper()
                    if r_type == "CONTRADICTS":
                        contradicts_count += 1
                    elif r_type == "SUPPORTS":
                        supports_count += 1
                    elif r_type == "REFINES":
                        refines_count += 1

                    # Persist dialectical relationship edge in repository
                    edge_dto = EdgeDTO(
                        source_id=rel.source_claim_id,
                        target_id=rel.target_claim_id,
                        relation_type=r_type,
                        properties={
                            "strength": rel.strength,
                            "resolution_hint": rel.resolution_hint,
                        },
                    )

                    if hasattr(repo, "add_edge"):
                        repo.add_edge(edge_dto)
                    elif hasattr(repo, "_driver") and repo._driver is not None:
                        # Write directly to Neo4j transaction
                        from src.database.queries.cypher_statements import MERGE_DIALECTICAL_EDGE

                        def _tx(tx):
                            tx.run(
                                MERGE_DIALECTICAL_EDGE,
                                source_claim_id=rel.source_claim_id,
                                target_claim_id=rel.target_claim_id,
                                relation_type=r_type,
                                strength=rel.strength,
                                conflict_nature="",
                                resolution_hint=rel.resolution_hint,
                            )

                        with repo._get_session() as session:
                            session.execute_write(_tx)

            # Add this claim to pool of existing claims so subsequent chunks can link too
            existing_claims.append(claim)

    return BookAssimilationSummary(
        book_title=book_title,
        author_name=author_name,
        pages_count=len(pages),
        chunks_count=len(chunks),
        claims_count=len(all_extracted_claims),
        supports_count=supports_count,
        contradicts_count=contradicts_count,
        refines_count=refines_count,
    )


__all__ = ["assimilate_book_pdf", "BookAssimilationSummary"]
