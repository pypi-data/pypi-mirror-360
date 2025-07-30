from synalinks.src.knowledge_bases.database_adapters.database_adapter import (
    DatabaseAdapter,
)
from synalinks.src.knowledge_bases.database_adapters.neo4j_adapter import Neo4JAdapter


def get(index_name):
    if index_name.startswith("neo4j"):
        return Neo4JAdapter
    else:
        raise ValueError(f"No database adapter found for {index_name}")
