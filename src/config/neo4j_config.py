from dataclasses import dataclass


@dataclass(frozen=True)
class Neo4jConfig:
    """Configuration data structure for Neo4j database connection."""

    uri: str = "bolt://localhost:7687"
    username: str = "neo4j"
    password: str = ""
    database: str = "neo4j"
