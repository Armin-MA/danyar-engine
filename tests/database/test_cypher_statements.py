"""Unit Tests for Parameterized Cypher Statements [TASK-012].

Verifies syntax cleanliness, parameterization standards ($param),
and Cypher injection defense protocols.
"""

from __future__ import annotations

import re
import pytest

from src.database.queries.cypher_statements import (
    MERGE_CLAIM_INGEST,
    MERGE_DIALECTICAL_EDGE,
    TRAVERSE_SUBGRAPH_BY_CONCEPTS,
    ATTACH_USER_NOTE,
    FETCH_NOTES_FOR_CLAIM,
    FETCH_FULL_GRAPH,
    build_concept_traversal_query,
    verify_parameterized_query,
)


def test_happy_path_parameterized_merge_claim_and_source():
    """Happy Path: MERGE_CLAIM_INGEST contains parameterized $placeholders and MERGE semantics."""
    assert "MERGE (a:Author" in MERGE_CLAIM_INGEST
    assert "MERGE (s:Source" in MERGE_CLAIM_INGEST
    assert "MERGE (c:Claim" in MERGE_CLAIM_INGEST
    assert "$claim_id" in MERGE_CLAIM_INGEST
    assert "$statement" in MERGE_CLAIM_INGEST
    assert "$author_name" in MERGE_CLAIM_INGEST
    assert "$source_title" in MERGE_CLAIM_INGEST

    # Verify no raw string formatting placeholders like %s or {var}
    assert not re.search(r"\{[a-zA-Z_0-9]+\}", MERGE_CLAIM_INGEST)


def test_happy_path_dialectical_relationship_merge():
    """Happy Path: MERGE_DIALECTICAL_EDGE merges SUPPORTS, CONTRADICTS, or REFINES safely."""
    assert "$source_claim_id" in MERGE_DIALECTICAL_EDGE
    assert "$target_claim_id" in MERGE_DIALECTICAL_EDGE
    assert "$strength" in MERGE_DIALECTICAL_EDGE
    assert "$conflict_nature" in MERGE_DIALECTICAL_EDGE


def test_happy_path_user_note_attachment():
    """Happy Path: ATTACH_USER_NOTE connects UserNote to target Claim via ANNOTATES edge."""
    assert "$claim_id" in ATTACH_USER_NOTE
    assert "$note_id" in ATTACH_USER_NOTE
    assert "$content" in ATTACH_USER_NOTE
    assert "[:ANNOTATES]" in ATTACH_USER_NOTE


def test_edge_case_traversal_query_with_safe_hop_builder():
    """Edge Case: Traversal query handles bounded depth without raw SQL/Cypher injection."""
    query = build_concept_traversal_query(max_depth=2)
    assert "$concept_names" in query
    assert "*1..2" in query

    # Depth must be strictly bounded between 1 and 3
    with pytest.raises(ValueError, match="max_depth must be between 1 and 3"):
        build_concept_traversal_query(max_depth=10)


def test_failure_state_prohibits_unparameterized_raw_interpolation():
    """Failure State: verify_parameterized_query detects raw concatenation or unescaped strings."""
    unsafe_query = "MATCH (c:Claim) WHERE c.id = '123' OR '1'='1' RETURN c"
    with pytest.raises(ValueError, match="Unparameterized raw literal detected"):
        verify_parameterized_query(unsafe_query)

    safe_query = "MATCH (c:Claim {id: $claim_id}) RETURN c"
    # Should not raise
    verify_parameterized_query(safe_query)
