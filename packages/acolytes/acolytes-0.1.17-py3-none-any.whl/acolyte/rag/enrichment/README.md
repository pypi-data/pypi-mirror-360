# 🏷️ Enrichment Module

Enriches code chunks with comprehensive Git metadata, providing context about code evolution and contributors.

## 📑 Documentation

- **[Architecture](../../docs/ARCHITECTURE.md#decision-5-git-metadata-enrichment)** - Git-reactive design
- **[API Reference](../../docs/REFERENCE.md#enrichmentservicepy)** - EnrichmentService class
- **[Workflows](../../docs/WORKFLOWS.md#enrichment-with-git-metadata-flow)** - Enrichment flow
- **[Integration](../../docs/INTEGRATION.md#git-service-integration)** - Git hooks and triggers

## 🔧 Key Components

- `service.py` - Main enrichment coordinator with all Git metrics
- `processors/graph_builder.py` - Automatic neural graph updates

## ⚡ Quick Usage

### Standard Chunk Enrichment

```python
from acolyte.rag.enrichment import EnrichmentService
from acolyte.core.logging import logger

enrichment = EnrichmentService(repo_path=".")
enriched_tuples = await enrichment.enrich_chunks(
    chunks,
    trigger="pull"  # Invalidates cache
)

# Returns tuples with rich metadata
for chunk, metadata in enriched_tuples:
    logger.info(f"Stability: {metadata['git']['stability_score']}")
```

### 🚀 Batch File Enrichment

**NEW**: For scenarios where you need metadata for many files without chunks (e.g., FatigueMonitor analysis), use the batch methods:

```python
# Single file (convenience method)
metadata = await enrichment.enrich_file("src/main.py")
logger.info(f"Stability score: {metadata['git_metadata']['stability_score']}")

# Batch processing - MUCH faster for multiple files
file_paths = ["src/main.py", "src/utils.py", "src/config.py", ...]
all_metadata = await enrichment.enrich_files_batch(file_paths)

# Process results
for file_path, metadata in all_metadata.items():
    git_data = metadata["git_metadata"]
    logger.info(f"{file_path}: stability={git_data.get('stability_score', 0.5)}")
```

**Performance characteristics**:
- Processes files in parallel with `asyncio.gather()`
- Batches of 10 files to avoid system overload
- Reduces N individual queries to 1 batch call
- Used by FatigueMonitor for 95%+ performance improvement

## 📊 Key Features

- **13 Git metrics**: stability, volatility, contributors, conflicts
- **Reactive only**: Never auto-fetches, responds to user Git operations
- **Graph updates**: Automatically maintains code relationships
- **Cache-aware**: Different behavior for commit/pull/manual triggers
- **Batch processing**: New `enrich_files_batch()` method for 95%+ performance improvement
- **Parallel execution**: Processes files concurrently with configurable batch size
