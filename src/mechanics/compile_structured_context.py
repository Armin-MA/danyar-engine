"""Structured Context Compiler for Danyar Engine.

Compiles sub-graph claims, boundary conditions, and dialectical tensions into a
high-density, structured markdown prompt context for Small Language Models (SLMs).
"""

from __future__ import annotations

from typing import Any
from src.database.dto.graph_dtos import SubGraphDTO, NodeDTO, EdgeDTO
from src.entities.domain_entities import ConditionEntity


def compile_structured_context(
    subgraph: SubGraphDTO,
    user_context: ConditionEntity | None = None,
) -> str:
    """Compile graph nodes, relationships, and user context into structured markdown context.

    Args:
        subgraph: Connected subgraph retrieved from Neo4j knowledge graph.
        user_context: Situational boundary conditions of the user inquiry (optional).

    Returns:
        High-density structured markdown prompt context.

    Raises:
        ValueError: If subgraph is None or contains zero nodes and edges.
    """
    if subgraph is None or (not subgraph.nodes and not subgraph.edges):
        raise ValueError("subgraph cannot be empty or null")

    # Index nodes by ID for relationship resolution
    node_map: dict[str, NodeDTO] = {node.id: node for node in subgraph.nodes}

    # Group edges by relation type
    tensions: list[EdgeDTO] = []
    consensus: list[EdgeDTO] = []
    refinements: list[EdgeDTO] = []
    other_edges: list[EdgeDTO] = []

    for edge in subgraph.edges:
        rel = edge.relation_type.upper().strip()
        if rel == "CONTRADICTS":
            tensions.append(edge)
        elif rel == "SUPPORTS":
            consensus.append(edge)
        elif rel == "REFINES":
            refinements.append(edge)
        else:
            other_edges.append(edge)

    lines: list[str] = [
        "# بسته بافت ساختاریافته پایگاه دانش دانیار (Dialectical Knowledge Context)",
        "",
        "## ۱. گزاره‌های دانشی (Claims & Propositions)",
    ]

    claims_found = False
    for node in subgraph.nodes:
        if node.label.lower() in {"claim", "node"}:
            claims_found = True
            stmt = node.properties.get("statement", node.properties.get("text", node.id))
            author = node.properties.get("author", "ناشناس")
            source = node.properties.get("source", "نامشخص")
            conf = node.properties.get("confidence_score")
            cond = node.properties.get("condition", "")

            meta_parts: list[str] = [f"نویسنده: {author}", f"منبع: {source}"]
            if conf is not None:
                meta_parts.append(f"ضریب اطمینان: {conf}")

            lines.append(f"- **[شناسه: {node.id}]** «{stmt}» ({' | '.join(meta_parts)})")
            if cond:
                lines.append(f"  - *شرط کاربست:* {cond}")

    if not claims_found:
        for node in subgraph.nodes:
            lines.append(f"- **[{node.label}: {node.id}]** {node.properties}")

    lines.append("")
    lines.append("## ۲. نقاط تضاد و تقابل‌های دیالکتیکی (Dialectical Tensions)")
    if tensions:
        for edge in tensions:
            src_node = node_map.get(edge.source_id)
            tgt_node = node_map.get(edge.target_id)
            src_desc = src_node.properties.get("statement", edge.source_id) if src_node else edge.source_id
            tgt_desc = tgt_node.properties.get("statement", edge.target_id) if tgt_node else edge.target_id
            conflict_nature = edge.properties.get("conflict_nature", "")

            lines.append(f"- **[CONTRADICTS]**")
            lines.append(f"  - موضع الف ({edge.source_id}): «{src_desc}»")
            lines.append(f"  - موضع ب ({edge.target_id}): «{tgt_desc}»")
            if conflict_nature:
                lines.append(f"  - ماهیت تضاد: {conflict_nature}")
    else:
        lines.append("- در این زیرگراف، هیچ نقطه تضادی یافت نشد (اتفاق نظر یا تک‌نظری دانشی).")

    lines.append("")
    lines.append("## ۳. نقاط اجماع و هم‌افزایی (Consensus & Support)")
    if consensus:
        for edge in consensus:
            src_node = node_map.get(edge.source_id)
            tgt_node = node_map.get(edge.target_id)
            src_desc = src_node.properties.get("statement", edge.source_id) if src_node else edge.source_id
            tgt_desc = tgt_node.properties.get("statement", edge.target_id) if tgt_node else edge.target_id
            lines.append(f"- **[SUPPORTS]** «{src_desc}» تاییدکننده «{tgt_desc}» است.")
    else:
        lines.append("- پیوند تایید مستقیم ثبتی وجود ندارد.")

    if refinements:
        lines.append("")
        lines.append("## ۴. تدقیق‌ها و قیود ظریف (Refinements)")
        for edge in refinements:
            src_node = node_map.get(edge.source_id)
            tgt_node = node_map.get(edge.target_id)
            src_desc = src_node.properties.get("statement", edge.source_id) if src_node else edge.source_id
            tgt_desc = tgt_node.properties.get("statement", edge.target_id) if tgt_node else edge.target_id
            hint = edge.properties.get("resolution_hint", "")
            lines.append(f"- **[REFINES]** «{src_desc}» مشروط‌کننده «{tgt_desc}» است. ({hint})")

    lines.append("")
    lines.append("## ۵. انطباق با زمینه وضعیت کاربر (User Context Alignment)")
    if user_context is not None:
        lines.append(f"- **دسته بافت کاربر:** {user_context.category}")
        lines.append(f"- **شرح شرایط کاربر:** {user_context.description}")
        lines.append("- **دستور دیالکتیکی:** توصیه‌ها را منحصراً متناسب با شرایط فوق غربال و اولویت‌بندی کنید.")
    else:
        lines.append("- شرایط مرزی اختصاصی از جانب کاربر تصریح نشده است (توصیه عمومی همراه با قید شروط).")

    return "\n".join(lines)


__all__ = ["compile_structured_context"]
