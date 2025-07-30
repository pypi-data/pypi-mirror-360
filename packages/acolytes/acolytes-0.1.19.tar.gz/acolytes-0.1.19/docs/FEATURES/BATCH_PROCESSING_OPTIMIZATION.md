# 🚀 Best Practices: Batch Processing for Performance

## Overview

When working with multiple files or items that require enrichment, always prefer batch methods over individual queries. This can improve performance by 95%+ in most cases.

## EnrichmentService Batch Methods

### ❌ Anti-pattern: Individual Queries (Slow)

```python
# DON'T DO THIS - N individual queries
results = []
for file_path in file_paths:  # 50 files = 50 queries
    metadata = await enrichment_service.enrich_file(file_path)
    results.append(metadata)
```

### ✅ Best Practice: Batch Processing (Fast)

```python
# DO THIS - 1 batch call with parallel processing
all_metadata = await enrichment_service.enrich_files_batch(file_paths)

# Process results
for file_path, metadata in all_metadata.items():
    # Use metadata...
```

## Real-World Example: FatigueMonitor

The FatigueMonitor in the Dream module was optimized from making 120+ individual queries to just 5 batch calls:

### Before (Slow)
```python
for row in result.data:
    file_path = row["file_path"]
    git_metadata = await self._get_file_git_metadata(file_path)  # Individual query
    # Process...
```

### After (Fast)
```python
file_paths = [row["file_path"] for row in result.data]
all_metadata = await self.enrichment_service.enrich_files_batch(file_paths)  # Batch query
for file_path in file_paths:
    metadata = all_metadata.get(file_path, {})
    # Process...
```

## Performance Characteristics

- **Parallel Processing**: Uses `asyncio.gather()` internally
- **Configurable Batch Size**: Default 10 files per batch
- **Error Resilience**: Failures in one file don't affect others
- **Metrics Included**: Tracks batch processing time

## When to Use Batch Processing

Use batch methods when:
- Processing multiple files (>3)
- Analyzing collections (e.g., all files in a directory)
- Computing aggregate metrics (e.g., project-wide stability)
- Running periodic analyses (e.g., Dream system fatigue calculation)

## Available Batch Methods

### EnrichmentService
- `enrich_files_batch(file_paths)` - Enrich multiple files in parallel

### Future Batch Methods
Consider implementing batch methods for:
- EmbeddingService: `encode_batch()` for multiple texts
- ChunkingService: `chunk_files_batch()` for multiple files
- Any service that processes collections of items

## Implementation Guidelines

When implementing batch methods:

1. **Use asyncio.gather()** for parallel execution
2. **Implement batching** to avoid system overload
3. **Handle partial failures** gracefully
4. **Include metrics** for monitoring
5. **Document performance gains** in method docstrings

## Example Implementation Pattern

```python
async def process_items_batch(self, items: List[str]) -> Dict[str, Any]:
    """
    Process multiple items in batch for better performance.
    
    Performance: 95%+ improvement over individual processing.
    """
    results = {}
    batch_size = 10
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        
        # Process batch concurrently
        batch_results = await asyncio.gather(
            *[self.process_item(item) for item in batch],
            return_exceptions=True
        )
        
        # Collect results
        for item, result in zip(batch, batch_results):
            if isinstance(result, Exception):
                logger.error(f"Error processing {item}: {result}")
            else:
                results[item] = result
    
    return results
```

## Monitoring and Metrics

Always include metrics for batch operations:

```python
start_time = time.time()
results = await self.process_batch(items)
elapsed_ms = (time.time() - start_time) * 1000

self.metrics.gauge("batch_processing_time_ms", elapsed_ms)
self.metrics.gauge("batch_items_processed", len(items))
logger.info(f"Batch processed {len(items)} items in {elapsed_ms:.2f}ms")
```

---

**Remember**: A 95%+ performance improvement is worth the small additional complexity of batch processing!
