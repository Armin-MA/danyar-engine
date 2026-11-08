"""Unit Tests for LLM Knowledge Digest Exporter.

Verifies compilation of Neo4j dialectical graph into high-density Markdown/JSON
digest files optimized for ingestion into Claude, ChatGPT, or Gemini.
"""

from __future__ import annotations

import os
import pytest

from src.database.repositories.in_memory_graph_repository import InMemoryGraphRepository
from src.mechanics.export_llm_digest import export_dialectical_digest


def test_happy_path_exports_digest_file(tmp_path):
    """Happy Path: Generates a structured markdown file ready for upload to Claude/ChatGPT."""
    repo = InMemoryGraphRepository()
    output_file = tmp_path / "danyar_digest.md"

    res_path = export_dialectical_digest(graph_repo=repo, output_path=str(output_file))

    assert os.path.isfile(res_path)
    with open(res_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Verify key sections
    assert "ماتریس تضادهای دیالکتیکی" in content or "Dialectical Tensions" in content
    assert "راهنمای هوش مصنوعی" in content or "System Prompt" in content
    assert "پیتر تیل" in content or "رید هافمن" in content
    assert "CONTRADICTS" in content or "تضاد" in content


def test_edge_case_empty_graph(tmp_path):
    """Edge Case: Generates clean template when graph has no nodes."""
    from unittest.mock import MagicMock
    from src.database.dto.graph_dtos import SubGraphDTO

    mock_repo = MagicMock()
    mock_repo.fetch_full_graph.return_value = SubGraphDTO(nodes=[], edges=[])

    output_file = tmp_path / "empty_digest.md"
    res_path = export_dialectical_digest(graph_repo=mock_repo, output_path=str(output_file))

    assert os.path.isfile(res_path)
    with open(res_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "دانیار" in content
