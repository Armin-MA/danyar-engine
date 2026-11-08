"""Unit Tests for Knowledge Pack Exporter [TASK: Export for LLMs].

Verifies generation of high-density markdown knowledge packs formatted
specifically for consumption by external LLMs (Claude, ChatGPT, Gemini).
"""

from __future__ import annotations

import os
import pytest

from src.database.dto.graph_dtos import NodeDTO, EdgeDTO, SubGraphDTO
from src.database.repositories.in_memory_graph_repository import InMemoryGraphRepository
from src.mechanics.export_knowledge_pack import export_knowledge_pack, format_knowledge_pack_markdown


def test_happy_path_formats_knowledge_pack_markdown():
    """Happy Path: Generates markdown with system instructions, tensions, consensus, and citations."""
    subgraph = SubGraphDTO(
        nodes=[
            NodeDTO(
                id="c1",
                label="Claim",
                properties={
                    "statement": "استخدام زیاد قبل از PMF سرمایه را هدر می‌دهد.",
                    "author": "پیتر تیل",
                    "source": "صفر به یک",
                    "condition": "مراحل آغازین استارتاپ",
                },
            ),
            NodeDTO(
                id="c2",
                label="Claim",
                properties={
                    "statement": "در بازارهای برنده-تمام، مقیاس‌دهی سریع بر بهره‌وری اولویت دارد.",
                    "author": "رید هافمن",
                    "source": "بلیتزاسکیلینگ",
                    "condition": "بازار با اثر شبکه‌ای شدید",
                },
            ),
        ],
        edges=[
            EdgeDTO(
                source_id="c1",
                target_id="c2",
                relation_type="CONTRADICTS",
                properties={
                    "conflict_nature": "تضاد در اولویت‌بندی بقای سرمایه در برابر سرعت تسخیر سهم بازار"
                },
            )
        ],
    )

    content = format_knowledge_pack_markdown(subgraph)

    assert "بسته دانش دیالکتیکی دانیار" in content
    assert "دستورالعمل و پرامپت راهنما برای مدل زبانی" in content
    assert "پیتر تیل" in content
    assert "رید هافمن" in content
    assert "صفر به یک" in content
    assert "بلیتزاسکیلینگ" in content
    assert "تضاد در اولویت‌بندی بقای سرمایه" in content
    assert "CONTRADICTS" in content or "تضادهای فکری" in content


def test_export_knowledge_pack_writes_file(tmp_path):
    """Verify export_knowledge_pack writes output to specified destination file."""
    repo = InMemoryGraphRepository()
    out_file = tmp_path / "danyar_knowledge_pack.md"

    summary = export_knowledge_pack(graph_repo=repo, output_path=str(out_file))

    assert os.path.isfile(str(out_file))
    assert summary["nodes_count"] >= 4
    assert summary["tensions_count"] >= 1

    with open(str(out_file), "r", encoding="utf-8") as f:
        text = f.read()

    assert len(text) > 200
    assert "دانیار" in text
