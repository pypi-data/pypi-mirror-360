# 🔪 Chunking Module

Intelligent code splitting using tree-sitter AST parsing for 31 languages, with pattern matching fallback.

## 📑 Documentation

- **[Architecture](../docs/ARCHITECTURE.md#decision-1-tree-sitter-for-all-chunking)** - Tree-sitter design
- **[API Reference](../docs/REFERENCE.md#chunkingbasepy)** - BaseChunker and factory
- **[Workflows](../docs/WORKFLOWS.md#chunking-decision-tree)** - Language detection flow
- **[Status](../docs/STATUS.md#chunking)** - Supported languages list

## 🔧 Key Components

- `factory.py` - Automatic language detection and chunker selection
- `base.py` - Tree-sitter integration base class
- `adaptive.py` - Dynamic chunk size adjustment
- `languages/` - 31 language-specific chunkers

## ⚡ Quick Usage

```python
from acolyte.rag.chunking import ChunkerFactory
from acolyte.core.logging import logger

logger.info("Getting chunker for auth.py")
chunker = ChunkerFactory.get_chunker("auth.py")
chunks = await chunker.chunk_file("auth.py")

# Each chunk has rich metadata
for chunk in chunks:
    logger.info(f"{chunk.chunk_type}: {chunk.metadata.name}")
```

## 📊 Key Features

- **31 languages**: Python, JS/TS, Java, Go, Rust, C/C++, etc.
- **Real AST parsing**: Tree-sitter for most languages
- **Smart boundaries**: Respects function/class boundaries
- **Min 1 line chunks**: Never loses small but important code
- **Enhanced fallback**: Pattern detection for unknown languages with metadata extraction
