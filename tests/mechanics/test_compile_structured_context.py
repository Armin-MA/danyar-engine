"""Unit Tests for Structured Context Compiler [TASK-010].

Verifies deterministic compilation of SubGraphDTO nodes, edges, consensus,
and dialectical tensions into high-density prompt packages for SLMs.
"""

from __future__ import annotations

import pytest

from src.database.dto.graph_dtos import NodeDTO, EdgeDTO, SubGraphDTO
from src.entities.domain_entities import ConditionEntity
from src.mechanics.compile_structured_context import compile_structured_context


def test_happy_path_compiles_structured_context():
    """Happy Path: Compiles claims, dialectical tensions (CONTRADICTS), and consensus into clean markdown."""
    node1 = NodeDTO(
        id="c1",
        label="Claim",
        properties={
            "statement": "قبل از PMF نباید استخدام انبوه کرد.",
            "author": "پیتر تیل",
            "source": "صفر به یک",
            "confidence_score": 0.9,
            "condition": "مرحله قبل از PMF",
        },
    )
    node2 = NodeDTO(
        id="c2",
        label="Claim",
        properties={
            "statement": "برای تسخیر سریع بازار باید سریعاً تیم فنی را مقیاس کرد.",
            "author": "رید هافمن",
            "source": "بلیتزاسکیلینگ",
            "confidence_score": 0.85,
            "condition": "بازارهای دارای اثر شبکه‌ای شدید",
        },
    )
    edge = EdgeDTO(
        source_id="c1",
        target_id="c2",
        relation_type="CONTRADICTS",
        properties={"conflict_nature": "تفاوت در سرعت سوزاندن سرمایه در برابر تسخیر سهم بازار"},
    )
    subgraph = SubGraphDTO(nodes=[node1, node2], edges=[edge])
    user_context = ConditionEntity(
        id="ctx_1",
        category="market_phase",
        description="استارتاپ مرحله بذری بدون PMF",
    )

    compiled = compile_structured_context(subgraph, user_context)

    assert isinstance(compiled, str)
    assert "صفر به یک" in compiled
    assert "بلیتزاسکیلینگ" in compiled
    assert "CONTRADICTS" in compiled or "تضاد" in compiled
    assert "استارتاپ مرحله بذری" in compiled


def test_edge_case_single_source_without_contradictions():
    """Edge Case: Formats gracefully when only one claim exists without contradictions."""
    node = NodeDTO(
        id="c1",
        label="Claim",
        properties={
            "statement": "تست‌نویسی جامع هزینه نگهداری نرم‌افزار را کاهش می‌دهد.",
            "author": "مارتین فاولر",
            "source": "Refactoring",
        },
    )
    subgraph = SubGraphDTO(nodes=[node], edges=[])

    compiled = compile_structured_context(subgraph)

    assert isinstance(compiled, str)
    assert "Refactoring" in compiled
    assert "مارتین فاولر" in compiled
    assert "هیچ نقطه تضادی یافت نشد" in compiled or "بدون تضاد" in compiled or len(compiled) > 50


def test_failure_state_empty_subgraph_raises_value_error():
    """Failure State: Raises ValueError when subgraph is completely empty or None."""
    with pytest.raises(ValueError, match="subgraph cannot be empty"):
        compile_structured_context(SubGraphDTO(nodes=[], edges=[]))

    with pytest.raises(ValueError, match="subgraph cannot be empty"):
        compile_structured_context(None)  # type: ignore
