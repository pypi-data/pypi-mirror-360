# 🔍 Retrieval Module

Hybrid search implementation combining 70% semantic + 30% lexical search for optimal code retrieval.

## 📑 Documentation

- **[Architecture](../docs/ARCHITECTURE.md#decision-2-hybrid-search-weights-7030)** - Why 70/30 split
- **[API Reference](../docs/REFERENCE.md#retrievalhybrid_searchpy)** - HybridSearch class
- **[Workflows](../docs/WORKFLOWS.md#hybrid-search-flow-7030)** - Search flow diagram
- **[Integration](../docs/INTEGRATION.md#service-integration-points)** - How services use it

## 🔧 Key Components

- `hybrid_search.py` - Main search orchestration with graph expansion
- `rerank.py` - Multi-strategy re-ranking (type, recency, git-aware)
- `fuzzy_matcher.py` - Normalizes naming conventions (snake_case ↔ camelCase)
- `cache.py` - LRU cache with TTL and invalidation

## ⚡ Quick Usage

```python
from acolyte.rag.retrieval import HybridSearch
from acolyte.core.logging import logger

search = HybridSearch(weaviate_client, embedding_service)
logger.info("Performing hybrid search")
results = await search.search("authentication middleware")

# With compression for specific queries
results = await search.search_with_compression(
    "bug in auth.py line 45", 
    compression_ratio=0.5
)

# With graph expansion
results = await search.search_with_graph_expansion(
    "error handling", 
    expansion_depth=2
)
```

## 📊 Key Features

- **Fuzzy Matching**: `getUserData` ≈ `get_user_data` ≈ `GetUserData`
- **Graph Expansion**: Finds structurally related code beyond text matches
- **Git-Aware Ranking**: Prioritizes stable/active code based on Git metadata
- **<200ms latency**: Optimized for single-user performance
