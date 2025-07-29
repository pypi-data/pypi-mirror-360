# 🗜️ Compression Module

Contextual token optimization without LLM calls. Reduces tokens by 60-80% for specific queries while maintaining <50ms latency.

## 📑 Documentation

- **[Architecture](../../docs/ARCHITECTURE.md#decision-4-no-llm-for-compression)** - Why heuristic approach
- **[API Reference](../../docs/REFERENCE.md#compressionchunk_compressorpy)** - ContextualCompressor class
- **[Workflows](../../docs/WORKFLOWS.md#search-with-compression-flow)** - Compression decision flow
- **[Integration](../../docs/INTEGRATION.md#embedding-service-integration)** - ChatService integration

## 🔧 Key Components

- `chunk_compressor.py` - Main compression orchestrator
- `contextual.py` - Query analysis and relevance scoring
- `strategies.py` - Document type specific strategies

## ⚡ Quick Usage

```python
from acolyte.rag.compression import ContextualCompressor
from acolyte.core.logging import logger

compressor = ContextualCompressor()

# Analyze and compress
if compressor.should_compress(query, chunks, token_budget):
    logger.info("Compressing chunks for specific query")
    compressed = compressor.compress_chunks(
        chunks, 
        query="error in auth.py line 23",
        token_budget=5000
    )
```

## 📊 Key Features

- **Query-aware**: Different strategies for specific vs general queries
- **Document-type aware**: CODE vs MARKDOWN vs CONFIG strategies
- **Deterministic**: Same input = same output always
- **Early stopping**: Guarantees <50ms by stopping at 45ms
