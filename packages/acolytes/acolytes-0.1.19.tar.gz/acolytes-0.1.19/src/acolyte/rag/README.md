# 🔍 RAG Module (Retrieval-Augmented Generation)

System for code indexing and search - The heart of ACOLYTE's knowledge.

## 📑 Documentation

- **[docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)** - Design principles and architectural decisions
- **[docs/STATUS.md](./docs/STATUS.md)** - Current implementation status
- **[docs/REFERENCE.md](./docs/REFERENCE.md)** - Complete API reference
- **[docs/WORKFLOWS.md](./docs/WORKFLOWS.md)** - Usage flows and examples
- **[docs/INTEGRATION.md](./docs/INTEGRATION.md)** - Integration with other modules

## 🔧 Main Components

### Core Systems

- **retrieval/** - Hybrid search implementation (70% semantic + 30% lexical)
- **compression/** - Contextual token optimization without LLM
- **chunking/** - Tree-sitter based intelligent code splitting
- **enrichment/** - Git metadata extraction and pattern analysis
- **graph/** - Neural relationship tracking for code connections
- **collections/** - Weaviate schema management

### Key Files

- `retrieval/hybrid_search.py` - Main search orchestration with graph expansion
- `chunking/factory.py` - Automatic language detection and chunker selection
- `compression/chunk_compressor.py` - Query-aware compression (<50ms)
- `enrichment/service.py` - Git metadata enrichment (reactive only)
- `graph/neural_graph.py` - Structural code relationship tracking

## ⚡ Quick Start

```python
from acolyte.rag.retrieval import HybridSearch
from acolyte.embeddings import EmbeddingService
from acolyte.core.logging import logger

# Initialize search
logger.info("Initializing HybridSearch")
search = HybridSearch(weaviate_client, embedding_service)

# Basic search
results = await search.search("authentication middleware")

# Search with compression for specific queries
results = await search.search_with_compression(
    query="login bug in user.py line 45",
    compression_ratio=0.5  # Aggressive compression
)

# Search with graph expansion for exploration
results = await search.search_with_graph_expansion(
    query="error handling patterns",
    expansion_depth=2  # Follow relationships 2 levels
)
```

## 📊 Key Features

- **Tree-sitter Chunking**: Real AST parsing for 31 languages with comprehensive metadata extraction
  - 27 languages with full metadata (structure, patterns, security, quality)
  - Automatic language detection via ChunkerFactory
  - Intelligent overlap and structure preservation
- **Hybrid Search**: Combines semantic embeddings with BM25 lexical search
- **Neural Graph**: Tracks imports, calls, and co-modification patterns
- **Smart Compression**: Reduces tokens by 60-80% without losing context
- **Git-Reactive**: Updates metadata on pull/commit, never auto-fetches
  - **NEW**: Batch enrichment methods for 95%+ performance improvement
  - Process 50+ files in parallel instead of sequential queries
- **18 ChunkTypes**: Precise semantic understanding of code structures
- **Comprehensive Testing**: 1000+ tests covering all submodules

## 🐛 Recent Fixes

- **Test Mocking**: Fixed WeaviateBaseError mock in collections tests
- **WeaviateConnectionError**: Added proper handling for connection errors
  - Import ConnectionError from weaviate.exceptions
  - Handle before generic WeaviateException
  - Updated all tests to use WeaviateBaseError imports
