"""Parameterized Cypher Statements for Danyar Engine.

Contains pure, parameterized Cypher statements for graph ingestion,
dialectical edge linking, subgraph traversal, and user note annotation.
Prohibits string concatenation or unsanitized dynamic formatting to eliminate Cypher injection.
"""

from __future__ import annotations

import re


MERGE_CLAIM_INGEST = """
MERGE (a:Author {name: $author_name})
ON CREATE SET a.id = $author_id, a.base_reputation = $base_reputation, a.created_at = $created_at

MERGE (s:Source {title: $source_title})
ON CREATE SET s.id = $source_id, s.domain = $domain, s.source_type = $source_type, s.created_at = $created_at

MERGE (a)-[:AUTHORED]->(s)

MERGE (c:Claim {id: $claim_id})
SET c.statement = $statement,
    c.claim_type = $claim_type,
    c.confidence_score = $confidence_score,
    c.created_at = $created_at

MERGE (s)-[:CONTAINS]->(c)

WITH c
FOREACH (cname IN $concepts |
    MERGE (cp:Concept {name: cname})
    ON CREATE SET cp.id = randomUUID(), cp.created_at = $created_at
    MERGE (c)-[:MENTIONS]->(cp)
)

FOREACH (cond IN CASE WHEN $has_condition THEN [1] ELSE [] END |
    MERGE (cd:Condition {category: $condition_category, description: $condition_description})
    ON CREATE SET cd.id = $condition_id, cd.created_at = $created_at
    MERGE (c)-[:CONDITIONED_ON]->(cd)
)

RETURN c.id AS claim_id
""".strip()


MERGE_DIALECTICAL_EDGE = """
MATCH (src:Claim {id: $source_claim_id})
MATCH (tgt:Claim {id: $target_claim_id})

FOREACH (_ IN CASE WHEN $relation_type = 'SUPPORTS' THEN [1] ELSE [] END |
    MERGE (src)-[r:SUPPORTS]->(tgt)
    SET r.strength = $strength, r.conflict_nature = $conflict_nature, r.resolution_hint = $resolution_hint
)

FOREACH (_ IN CASE WHEN $relation_type = 'CONTRADICTS' THEN [1] ELSE [] END |
    MERGE (src)-[r:CONTRADICTS]->(tgt)
    SET r.strength = $strength, r.conflict_nature = $conflict_nature, r.resolution_hint = $resolution_hint
)

FOREACH (_ IN CASE WHEN $relation_type = 'REFINES' THEN [1] ELSE [] END |
    MERGE (src)-[r:REFINES]->(tgt)
    SET r.strength = $strength, r.conflict_nature = $conflict_nature, r.resolution_hint = $resolution_hint
)

RETURN src.id AS source_id, tgt.id AS target_id
""".strip()


ATTACH_USER_NOTE = """
MATCH (c:Claim {id: $claim_id})
CREATE (n:UserNote {
    id: $note_id,
    content: $content,
    dispute_type: $dispute_type,
    credibility_impact: $credibility_impact,
    created_at: $created_at
})
CREATE (n)-[:ANNOTATES]->(c)
RETURN n.id AS note_id
""".strip()


FETCH_NOTES_FOR_CLAIM = """
MATCH (n:UserNote)-[:ANNOTATES]->(c:Claim {id: $claim_id})
RETURN n.id AS id, c.id AS claim_id, n.content AS content,
       n.dispute_type AS dispute_type, n.credibility_impact AS credibility_impact,
       n.created_at AS created_at
ORDER BY n.created_at DESC
""".strip()


FETCH_FULL_GRAPH = """
MATCH (n)
OPTIONAL MATCH (n)-[r]->(m)
RETURN n, r, m
LIMIT $limit
""".strip()


TRAVERSE_SUBGRAPH_BY_CONCEPTS = """
MATCH (cp:Concept) WHERE cp.name IN $concept_names
MATCH path = (cp)<-[:MENTIONS]-(c:Claim)-[*0..1]-(neighbor)
RETURN path
""".strip()


def build_concept_traversal_query(max_depth: int = 1) -> str:
    """Build bounded traversal query for concepts.

    Args:
        max_depth: Maximum relationship traversal hops (must be 1, 2, or 3).

    Returns:
        Parameterized Cypher query string.

    Raises:
        ValueError: If max_depth is not between 1 and 3.
    """
    if not (1 <= max_depth <= 3):
        raise ValueError(f"max_depth must be between 1 and 3, got {max_depth}")

    return f"""
MATCH (cp:Concept) WHERE cp.name IN $concept_names
MATCH path = (cp)<-[:MENTIONS]-(c:Claim)-[*1..{max_depth}]-(neighbor)
RETURN path
""".strip()


def verify_parameterized_query(query: str) -> None:
    """Assert query does not contain raw string literal injection or unparameterized values.

    Args:
        query: Cypher statement to audit.

    Raises:
        ValueError: If dangerous unparameterized string literals or potential injection patterns detected.
    """
    # Detect raw string literal comparisons like = 'abc' or '1'='1'
    literal_pattern = re.compile(r"=\s*'[^']*'|'[^']+'\s*=\s*'[^']+'")
    if literal_pattern.search(query):
        raise ValueError("Unparameterized raw literal detected in Cypher query! Use $parameters.")


__all__ = [
    "MERGE_CLAIM_INGEST",
    "MERGE_DIALECTICAL_EDGE",
    "ATTACH_USER_NOTE",
    "FETCH_NOTES_FOR_CLAIM",
    "FETCH_FULL_GRAPH",
    "TRAVERSE_SUBGRAPH_BY_CONCEPTS",
    "build_concept_traversal_query",
    "verify_parameterized_query",
]
