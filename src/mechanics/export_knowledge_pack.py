"""Dialectical Knowledge Pack Exporter for Danyar Engine.

Compiles knowledge graph claims, boundary conditions, consensus, and dialectical tensions
into a standalone, high-density markdown knowledge package formatted specifically for
consumption by external LLMs (Claude, ChatGPT, Gemini).
"""

from __future__ import annotations

import os
from typing import Any
from src.contracts.engine_contracts import IGraphRepository
from src.database.dto.graph_dtos import SubGraphDTO, NodeDTO, EdgeDTO


SYSTEM_PROMPT_TEMPLATE = """# بسته دانش دیالکتیکی دانیار (Danyar Epistemic Knowledge Pack)

## دستورالعمل و پرامپت راهنما برای مدل زبانی (System Prompt for LLM):
شما به عنوان «مشاور هوشمند دیالکتیکی دانیار» عمل می‌کنید. اطلاعات زیر، پایگاه دانش ساختاریافته استخراج‌شده از کتب و مراجع معتبر است که شامل گزاره‌ها، شروط مرزی و تضادهای فکری میان اندیشمندان مختلف است.

هنگام پاسخ‌دهی به پرسش‌های کاربر، اکیداً قوانین زیر را رعایت فرمایید:
۱. **پاسخ ۳ بخشی دیالکتیکی:** پاسخ خود را به سه بخش شفاف تقسیم کنید:
   - بخش اول: «اجماع بزرگان» (مواردی که صاحب‌نظران بر آن اتفاق نظر دارند).
   - بخش دوم: «نقاط تضاد و تقابل دیدگاه‌ها» (جنگ فکری و تضادهای بنیادین میان مکاتب مختلف).
   - بخش سوم: «نسخه اختصاصی شما» (تحلیل وضعیت خاص کاربر بر مبنای شروط مرزی).
۲. **قیدگذاری مرزی (Boundary Conditions):** هرگز حکم کلی یا نسخه مطلق صادر نکنید؛ همواره بیان کنید که هر دیدگاه در چه شرایطی (اندازه تیم، مرحله بازار، نقدینگی) معتبر است.
۳. **استناد دقیق:** به نویسندگان و عنوان کتاب‌های مندرج در این سند به صورت صریح استناد کنید.
"""


def format_knowledge_pack_markdown(subgraph: SubGraphDTO) -> str:
    """Compile SubGraphDTO into high-density Markdown documentation for external LLMs.

    Args:
        subgraph: Graph containing nodes and dialectical edges.

    Returns:
        Structured markdown text ready to be uploaded or injected into Claude/ChatGPT/Gemini.
    """
    node_map: dict[str, NodeDTO] = {node.id: node for node in subgraph.nodes}

    # Group edges by relation type
    contradictions: list[EdgeDTO] = []
    consensus: list[EdgeDTO] = []
    refinements: list[EdgeDTO] = []

    for edge in subgraph.edges:
        r_type = edge.relation_type.upper().strip()
        if r_type == "CONTRADICTS":
            contradictions.append(edge)
        elif r_type == "SUPPORTS":
            consensus.append(edge)
        elif r_type == "REFINES":
            refinements.append(edge)

    lines: list[str] = [SYSTEM_PROMPT_TEMPLATE.strip(), ""]

    # 1. Dialectical Contradictions Matrix
    lines.append("---")
    lines.append("## ۱. ماتریس تضادهای فکری و تقابل دیدگاه‌ها (Dialectical Tensions Matrix)")
    if contradictions:
        for idx, edge in enumerate(contradictions, 1):
            src_node = node_map.get(edge.source_id)
            tgt_node = node_map.get(edge.target_id)

            src_stmt = src_node.properties.get("statement", edge.source_id) if src_node else edge.source_id
            src_author = src_node.properties.get("author", "نویسنده الف") if src_node else "ناشناس"
            src_source = src_node.properties.get("source", "") if src_node else ""
            src_cond = src_node.properties.get("condition", "شرایط عمومی") if src_node else ""

            tgt_stmt = tgt_node.properties.get("statement", edge.target_id) if tgt_node else edge.target_id
            tgt_author = tgt_node.properties.get("author", "نویسنده ب") if tgt_node else "ناشناس"
            tgt_source = tgt_node.properties.get("source", "") if tgt_node else ""
            tgt_cond = tgt_node.properties.get("condition", "شرایط عمومی") if tgt_node else ""

            nature = edge.properties.get("conflict_nature", "اختلاف در مبانی استراتژیک یا اولویت‌بندی اهداف")

            lines.append(f"### [تضاد #{idx}] تقابل «{src_author}» در برابر «{tgt_author}»")
            lines.append(f"- **دیدگاه اول ({src_author} در {src_source}):** «{src_stmt}»")
            lines.append(f"  - *شرط کاربست دیدگاه اول:* {src_cond}")
            lines.append(f"- **دیدگاه دوم ({tgt_author} در {tgt_source}):** «{tgt_stmt}»")
            lines.append(f"  - *شرط کاربست دیدگاه دوم:* {tgt_cond}")
            lines.append(f"- **ماهیت و ریشه تضاد:** {nature}")
            lines.append("")
    else:
        lines.append("- در این مجموعه داده، تضاد فکری صریحی ثبت نشده است.")
        lines.append("")

    # 2. Consensus & Synergies
    lines.append("---")
    lines.append("## ۲. نقاط اجماع و همگرایی دیدگاه‌ها (Consensus & Synergies)")
    if consensus:
        for edge in consensus:
            src_node = node_map.get(edge.source_id)
            tgt_node = node_map.get(edge.target_id)
            src_desc = src_node.properties.get("statement", edge.source_id) if src_node else edge.source_id
            tgt_desc = tgt_node.properties.get("statement", edge.target_id) if tgt_node else edge.target_id
            lines.append(f"- **تایید متقابل:** «{src_desc}» هم‌راستا و تاییدکننده «{tgt_desc}» است.")
    else:
        lines.append("- پیوند تایید صریح مستقلی ثبت نشده است.")
    lines.append("")

    # 3. Refinements
    if refinements:
        lines.append("---")
        lines.append("## ۳. تدقیق‌ها و قیود مشروط‌کننده (Nuance & Refinements)")
        for edge in refinements:
            src_node = node_map.get(edge.source_id)
            tgt_node = node_map.get(edge.target_id)
            src_desc = src_node.properties.get("statement", edge.source_id) if src_node else edge.source_id
            tgt_desc = tgt_node.properties.get("statement", edge.target_id) if tgt_node else edge.target_id
            hint = edge.properties.get("resolution_hint", "")
            lines.append(f"- **تدقیق:** «{src_desc}» قید و شرطی بر «{tgt_desc}» است. ({hint})")
        lines.append("")

    # 4. Atomic Claims by Author / Book
    lines.append("---")
    lines.append("## ۴. فهرست گزاره‌های اتمیک و شروط کاربست به تفکیک منابع")
    claims = [n for n in subgraph.nodes if n.label.lower() == "claim"]
    if claims:
        # Group claims by author/source
        grouped: dict[str, list[NodeDTO]] = {}
        for c in claims:
            author = c.properties.get("author", "سایر صاحب‌نظران")
            source = c.properties.get("source", "منابع عمومی")
            key = f"«{source}» اثر {author}"
            grouped.setdefault(key, []).append(c)

        for src_title, src_claims in grouped.items():
            lines.append(f"### منبع: {src_title}")
            for c in src_claims:
                stmt = c.properties.get("statement", c.id)
                cond = c.properties.get("condition", "")
                cond_part = f" *(شرط: {cond})*" if cond else ""
                lines.append(f"- **[شناسه: {c.id}]** «{stmt}»{cond_part}")
            lines.append("")
    else:
        for n in subgraph.nodes:
            lines.append(f"- **[{n.label}: {n.id}]** {n.properties}")

    return "\n".join(lines).strip()


def export_knowledge_pack(
    graph_repo: IGraphRepository,
    output_path: str = "danyar_knowledge_pack.md",
    limit: int = 500,
) -> dict[str, Any]:
    """Retrieve active graph from repository and write knowledge package to markdown file.

    Args:
        graph_repo: Source graph repository.
        output_path: File path to save the generated markdown pack.
        limit: Maximum number of nodes to pull.

    Returns:
        Dictionary containing summary statistics.
    """
    if hasattr(graph_repo, "fetch_full_graph"):
        subgraph = graph_repo.fetch_full_graph(limit=limit)
    else:
        subgraph = graph_repo.fetch_related_subgraph([])

    markdown_content = format_knowledge_pack_markdown(subgraph)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    claims_count = sum(1 for n in subgraph.nodes if n.label.lower() == "claim")
    tensions_count = sum(1 for e in subgraph.edges if e.relation_type.upper() == "CONTRADICTS")
    supports_count = sum(1 for e in subgraph.edges if e.relation_type.upper() == "SUPPORTS")

    return {
        "output_path": output_path,
        "nodes_count": len(subgraph.nodes),
        "claims_count": claims_count,
        "tensions_count": tensions_count,
        "supports_count": supports_count,
    }


__all__ = [
    "export_knowledge_pack",
    "format_knowledge_pack_markdown",
    "SYSTEM_PROMPT_TEMPLATE",
]
