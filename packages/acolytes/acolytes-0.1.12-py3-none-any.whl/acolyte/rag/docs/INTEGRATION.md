# 🔗 RAG Module Integration

## Module Dependencies

### What RAG Uses

```
Core ─────────► Models ─────────► RAG
  │                │                │
  ├─ id_generator  ├─ chunk.py     └─ All submodules
  ├─ exceptions    ├─ metadata.py
  ├─ logging       └─ git_metadata.py
  └─ config
```

### Who Uses RAG

```
RAG ◄───────── Services ◄───────── API
                  │                  │
                  ├─ ChatService     ├─ /v1/chat/completions
                  ├─ ConversationService
                  └─ IndexingService └─ /api/index/*
```

## Service Integration Points

### ChatService Integration
```python
from acolyte.core.logging import logger

# ChatService uses RAG for context retrieval
class ChatService:
    async def _retrieve_context(self, query: str):
        # Uses HybridSearch with compression
        results = await self.rag.search_with_compression(
            query=query,
            compression_ratio=0.7,
            limit=10
        )
        return self._format_context(results)
```

### ConversationService Integration
```python
from acolyte.core.logging import logger

# ConversationService stores and searches conversation summaries
class ConversationService:
    async def search_similar_conversations(self, query: str):
        # Uses hybrid search on Conversation collection
        return await self.hybrid_search.search(
            query=query,
            collection="Conversation",
            limit=5
        )
```

### IndexingService Integration
```python
from acolyte.core.logging import logger
from acolyte.core.metrics import MetricsCollector

# IndexingService orchestrates the RAG pipeline
class IndexingService:
    async def index_files(self, files: List[Path], trigger: str):
        # 1. Chunking
        chunks = await self.chunker_factory.chunk_files(files)
        
        # 2. Enrichment
        enriched = await self.enrichment_service.enrich_chunks(
            chunks, trigger=trigger
        )
        
        # 3. Embeddings (separate module)
        embeddings = await self.embedding_service.encode_batch(...)
        
        # 4. Store in Weaviate
        await self.weaviate_client.batch.create(...)
```

## Weaviate Integration Requirements

### Client Configuration
```python
import weaviate
from acolyte.core.secure_config import Settings
from acolyte.core.logging import logger

class WeaviateClient:
    def __init__(self):
        config = Settings()
        logger.info("Initializing Weaviate client")
        self.client = weaviate.Client(
            url=config.get("weaviate.url", "http://localhost:8080"),
            timeout_config=(5, 30)  # connection, read timeout
        )
```

### Required Collections (5 total)
- **CodeChunk**: Code fragments with 18 ChunkTypes
- **Document**: Complete files (README, docs)
- **Conversation**: Chat summaries (~90% reduction)
- **Task**: Task checkpoints grouping sessions
- **DreamInsight**: Optimization patterns

### Weaviate Schema Requirements
```json
{
  "class": "CodeChunk",
  "properties": [
    { "name": "content", "dataType": ["text"] },
    { "name": "file_path", "dataType": ["string"] },
    { "name": "chunk_type", "dataType": ["string"] },
    { "name": "start_line", "dataType": ["int"] },
    { "name": "end_line", "dataType": ["int"] }
  ],
  "vectorizer": "none",
  "moduleConfig": {
    "text2vec-transformers": { "skip": true }
  }
}
```

### BM25 Configuration
```json
"moduleConfig": {
  "bm25": {
    "enabled": true,
    "k1": 1.2,
    "b": 0.75
  }
}
```

## Embedding Service Integration

### Bidirectional Dependency
```python
# RAG needs embeddings for search
query_embedding = await embedding_service.encode(query)

# Embeddings uses RAG collections for schema
vector_dims = collections.get_vector_dimensions("CodeChunk")
```

### Required Interface
```python
from acolyte.embeddings import get_embeddings
from acolyte.core.logging import logger

class UniXcoderEmbeddings:
    def encode(self, text: str, context: RichCodeContext = None) -> np.ndarray:
        """Generate 768-dim embedding"""
    
    def encode_batch(self, texts: List[str], batch_size: int = 32) -> List[np.ndarray]:
        """Batch encoding for efficiency"""
```

## Git Service Integration

### Event-Based Updates
```python
from acolyte.core.logging import logger

# GitService publishes events
logger.info("Publishing git.pull event")
await event_bus.publish("git.pull", {"files": changed_files})

# IndexingService subscribes and triggers RAG
@event_bus.subscribe("git.pull")
async def handle_git_pull(event):
    await indexing_service.reindex_files(
        event.data["files"],
        trigger="pull"
    )
```

## Collection Schemas

### Shared Collections
RAG defines and manages these Weaviate collections used system-wide:

1. **CodeChunk** - Primary code storage
2. **Document** - Full file storage  
3. **Conversation** - Chat summaries
4. **Task** - Task checkpoints (TODO)
5. **DreamInsight** - Optimization insights (TODO)

### Schema Coordination
```python
# Collections define schema
VECTOR_DIMENSIONS = 768  # System constant

# Embeddings respects it
assert embedding_model.output_dim == VECTOR_DIMENSIONS

# RAG validates on storage
if len(embedding) != VECTOR_DIMENSIONS:
    raise ValidationError()
```

## Cache Coordination

### EventBus Integration
```python
from acolyte.core.logging import logger

# Git operations invalidate RAG caches
@event_bus.subscribe("git.pull")
async def invalidate_caches(event):
    logger.info("Invalidating RAG caches after git pull")
    enrichment_cache.clear()
    search_cache.clear()
    compression_cache.clear()
```

### Unified Cache Settings
All RAG components use:
- Max size: 1000 entries
- TTL: 3600 seconds
- LRU eviction policy

## API Endpoints Using RAG

### Direct Endpoints
```
POST /api/index/file      → IndexingService → RAG pipeline
POST /api/index/git-changes → IndexingService → RAG enrichment
GET  /api/search          → RAG HybridSearch directly
```

### Indirect Usage
```
POST /v1/chat/completions → ChatService → RAG search
POST /api/tasks/create    → TaskService → RAG for context
```

## Configuration Flow

### .acolyte Configuration
```yaml
# RAG reads these settings
rag:
  hybrid_search:
    semantic_weight: 0.7
  compression:
    enabled: true
  chunking:
    sizes:
      python: 150

# Services inherit RAG config
services:
  chat:
    rag_config: ${rag}  # Reference RAG settings
```

## Initialization Flow

### Docker Compose for Weaviate
```yaml
services:
  weaviate:
    image: semitechnologies/weaviate:latest
    ports:
      - "8080:8080"
    environment:
      QUERY_DEFAULTS_LIMIT: 25
      AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: "true"
      PERSISTENCE_DATA_PATH: "/var/lib/weaviate"
```

### Startup Sequence
```python
from acolyte.core.logging import logger

# 1. Initialize Weaviate
logger.info("Starting ACOLYTE initialization")
weaviate_client = WeaviateClient()
weaviate_client.ensure_schema()

# 2. Initialize Embeddings
embedder = get_embeddings()

# 3. Initialize HybridSearch
hybrid_search = HybridSearch(
    weaviate_client=weaviate_client.client,
    enable_compression=True
)

# 4. Index initial project
indexing_service = IndexingService()
await indexing_service.index_project()
```

## Error Propagation

### Exception Hierarchy
```python
# RAG throws specific exceptions
ChunkingError → IndexingError → ServiceError → API 400
SearchError → RetrievalError → ServiceError → API 500
```

### Error Context
```python
from acolyte.core.logging import logger

try:
    await rag.search(query)
except SearchError as e:
    logger.error("RAG search failed", error=str(e))
    # Services add context
    raise ServiceError(
        f"Context retrieval failed: {e}",
        original_error=e,
        query=query
    )
```

## Performance Contracts

### Latency Guarantees
- Chunking: <100ms per file
- Search: <200ms total
- Compression: <50ms analysis
- Graph expansion: +50ms per depth level

### Throughput Limits
- Batch size: 100 chunks for Weaviate
- Concurrent searches: 10 max
- File processing: 10 parallel

## Extension Points

### Adding New Search Strategies
1. Implement in `rag/retrieval/strategies/`
2. Register in HybridSearch
3. Services automatically use it

### Custom Enrichment
1. Add processor to `rag/enrichment/processors/`
2. Hook into EnrichmentService
3. Metadata available in all searches

### Language Support
1. Add chunker to `rag/chunking/languages/`
2. Register in ChunkerFactory
3. IndexingService handles automatically

## Integration Checklist

- [ ] Weaviate running and accessible
- [ ] Schemas created in Weaviate  
- [ ] EmbeddingService available
- [ ] Model Chunk with all fields
- [ ] WeaviateClient configured
- [ ] ConversationService updated
- [ ] Configuration in .acolyte
- [ ] Integration tests passing
