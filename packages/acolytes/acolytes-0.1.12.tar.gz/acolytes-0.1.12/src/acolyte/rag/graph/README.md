# 🧠 Neural Graph Module

Maintains structural code relationships as a memory associative network, tracking imports, calls, and co-modification patterns.

## 📑 Documentation

- **[Architecture](../docs/ARCHITECTURE.md#decision-3-neural-graph-over-clustering)** - Why graph over clustering
- **[API Reference](../docs/REFERENCE.md#graphneural_graphpy)** - NeuralGraph class
- **[Workflows](../docs/WORKFLOWS.md#neural-graph-update-flow)** - Graph update flow
- **[Integration](../docs/INTEGRATION.md#embedding-service-integration)** - Dream and search usage

## 🔧 Key Components

- `neural_graph.py` - Graph persistence and BFS queries in SQLite
- `relations_manager.py` - Relationship detection and strength management
- `pattern_detector.py` - Pattern discovery algorithms

## ⚡ Quick Usage

```python
from acolyte.rag.graph import NeuralGraph
from acolyte.core.logging import logger

graph = NeuralGraph(db_path)

# Find related code
logger.info("Finding related nodes")
related = await graph.find_related_nodes(
    "auth.py:login",
    max_depth=2,
    edge_types=["CALLS", "IMPORTS"]
)

# Strengthen connections through use
await graph.strengthen_connection("auth.py", "jwt.py")
```

## 📊 Key Features

- **Structural relationships**: IMPORTS, CALLS, EXTENDS, CO_MODIFIED
- **Edge weights**: 0.0-1.0 strength that evolves with use
- **O(1) lookups**: Pre-computed vs O(n²) clustering per query
- **Dual storage**: SQLite for structure, Weaviate for patterns (future)
