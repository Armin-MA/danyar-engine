"""LLM Knowledge Digest Exporter for Danyar Engine.

Exports the Neo4j dialectical graph into a high-density, structured Markdown
knowledge package specifically designed to be uploaded or attached into Claude,
ChatGPT, or Gemini as an authoritative external knowledge base.
"""

from __future__ import annotations

import os
from typing import Any
from src.contracts.engine_contracts import IGraphRepository
from src.database.dto.graph_dtos import SubGraphDTO, NodeDTO, EdgeDTO


EXTERNAL_AI_SYSTEM_PROMPT = """# راهنمای هوش مصنوعی و دستورالعمل سیستم (System Prompt for Claude / ChatGPT / Gemini):
شما به یک «پایگاه دانش دیالکتیکی» از معتبرترین کتاب‌ها و متفکران حوزه استراتژی و مدیریت دسترسی دارید.
وظایف شما هنگام پاسخ به پرسش کاربر:
۱. از ارائه پاسخ‌های کلی، تک‌بعدی یا کلیشه‌ای اکیداً خودداری کنید.
۲. ابتدا شرایط و زمینه کاربر را ارزیابی کرده و مشخص کنید کدام قید یا شرط مرزی بر وضعیت او حاکم است.
۳. در پاسخ خود، حتماً «نقاط تضاد فکری» میان صاحب‌نظران مرتبط را تشریح کنید (مثلاً نشان دهید نظر فلانی با نظر بهمانی در چه موردی و به چه دلیل در تقابل است).
۴. در پایان، بر مبنای شرایط اختصاصی کاربر، یک نسخه سنتز‌شده و شخصی‌سازی‌شده پیشنهاد دهید و منابع و نام نویسندگان را به صراحت ذکر فرمایید.
"""


def export_dialectical_digest(
    graph_repo: IGraphRepository,
    output_path: str = "exports/danyar_knowledge_digest.md",
) -> str:
    """Export the entire active knowledge graph into an LLM-ready markdown document.

    Args:
        graph_repo: Source repository holding the graph.
        output_path: Destination file path for the exported markdown file.

    Returns:
        Absolute or relative path to the generated export file.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    if hasattr(graph_repo, "fetch_full_graph"):
        subgraph: SubGraphDTO = graph_repo.fetch_full_graph(limit=1000)
    else:
        subgraph = graph_repo.fetch_related_subgraph([])

    node_map: dict[str, NodeDTO] = {n.id: n for n in subgraph.nodes}

    # Group edges by dialectical category
    tensions: list[EdgeDTO] = []
    consensus: list[EdgeDTO] = []
    refinements: list[EdgeDTO] = []

    for edge in subgraph.edges:
        rtype = edge.relation_type.upper().strip()
        if rtype == "CONTRADICTS":
            tensions.append(edge)
        elif rtype == "SUPPORTS":
            consensus.append(edge)
        elif rtype == "REFINES":
            refinements.append(edge)

    lines: list[str] = [
        "# پایگاه دانش دیالکتیکی دانیار (Danyar Epistemic Knowledge Base)",
        "این سند حاوی استخراج ساختاریافته گزاره‌ها، شروط مرزی و تقابل‌های فکری نویسندگان مختلف است.",
        "",
        "---",
        "",
        EXTERNAL_AI_SYSTEM_PROMPT,
        "",
        "---",
        "",
        "## بخش اول: ماتریس تضادهای دیالکتیکی (Dialectical Tensions & Conflicts)",
        "نقاطی که صاحب‌نظران مختلف دیدگاه‌های متقابل یا ناسازگار مطرح کرده‌اند:",
        "",
    ]

    if tensions:
        for idx, edge in enumerate(tensions, 1):
            src = node_map.get(edge.source_id)
            tgt = node_map.get(edge.target_id)
            src_stmt = src.properties.get("statement", edge.source_id) if src else edge.source_id
            src_author = src.properties.get("author", "ناشناس") if src else "ناشناس"
            src_source = src.properties.get("source", "") if src else ""

            tgt_stmt = tgt.properties.get("statement", edge.target_id) if tgt else edge.target_id
            tgt_author = tgt.properties.get("author", "ناشناس") if tgt else "ناشناس"
            tgt_source = tgt.properties.get("source", "") if tgt else ""

            conflict_nature = edge.properties.get("conflict_nature") or edge.properties.get("resolution_hint", "")

            lines.append(f"### تضاد #{idx}: تقابل دیدگاه {src_author} و {tgt_author}")
            lines.append(f"- **دیدگاه الف ({src_author} - {src_source}):** «{src_stmt}»")
            lines.append(f"- **دیدگاه ب ({tgt_author} - {tgt_source}):** «{tgt_stmt}»")
            if conflict_nature:
                lines.append(f"- **ریشه و ماهیت تضاد:** {conflict_nature}")
            lines.append("")
    else:
        lines.append("- هنوز نقطه تضادی ثبت نشده است.\n")

    lines.append("## بخش دوم: نقاط اجماع و تایید (Consensus & Mutual Support)")
    if consensus:
        for edge in consensus:
            src = node_map.get(edge.source_id)
            tgt = node_map.get(edge.target_id)
            src_stmt = src.properties.get("statement", edge.source_id) if src else edge.source_id
            tgt_stmt = tgt.properties.get("statement", edge.target_id) if tgt else edge.target_id
            src_author = src.properties.get("author", "") if src else ""
            tgt_author = tgt.properties.get("author", "") if tgt else ""
            lines.append(f"- **همگرایی:** نظر {src_author} («{src_stmt}») تاییدکننده دیدگاه {tgt_author} («{tgt_stmt}») است.")
        lines.append("")
    else:
        lines.append("- نقطه تایید صریحی ثبت نشده است.\n")

    lines.append("## بخش سوم: فهرست کامل گزاره‌های دانشی به تفکیک منابع و شروط مرزی")
    claim_nodes = [n for n in subgraph.nodes if n.label.lower() == "claim"]
    if claim_nodes:
        for node in claim_nodes:
            stmt = node.properties.get("statement", node.id)
            author = node.properties.get("author", "نامشخص")
            source = node.properties.get("source", "نامشخص")
            cond = node.properties.get("condition", "")
            lines.append(f"- **[{author} | {source}]** «{stmt}»")
            if cond:
                lines.append(f"  - *شرط کاربست:* {cond}")
    else:
        lines.append("- گزاره‌ای در مخزن وجود ندارد.")

    full_text = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_text)

    return output_path


__all__ = ["export_dialectical_digest", "EXTERNAL_AI_SYSTEM_PROMPT"]
