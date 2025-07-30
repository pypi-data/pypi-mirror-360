# 🏗️ RAG Module Architecture

## Design Principles

1. **Tree-sitter Based Chunking**: Real AST parsing for all languages - not fragile regex
2. **Hybrid Search (70/30)**: 70% semantic embeddings + 30% BM25 lexical search
3. **Neural Graph Expansion**: Structural code relationships complement semantic search
4. **Contextual Compression**: Optimize tokens without additional LLM calls
5. **Git-Reactive Enrichment**: Reacts to user actions, never auto-fetches

## Architectural Decisions

### Decision #1: Tree-sitter for All Chunking
**Why**: GitHub uses tree-sitter. Real AST parsing handles incomplete code better than regex.
**Implementation**: `tree-sitter-languages` provides pre-compiled parsers for 31 languages.

### Decision #2: Hybrid Search Weights (70/30)
**Why**: Pure semantic misses exact matches; pure lexical misses conceptual similarity.
**Implementation**: Weaviate BM25 for lexical, UniXcoder embeddings for semantic.

### Decision #3: Neural Graph over Clustering
**Why**: Pre-computed relationships are O(1) vs O(n²) clustering per query.
**Implementation**: SQLite stores structural relationships, updated incrementally.

### Decision #4: No LLM for Compression
**Why**: <50ms latency requirement, no external dependencies.
**Implementation**: Heuristic relevance scoring based on query analysis.

### Decision #5: Git Metadata Enrichment
**Why**: Code stability and contributor patterns improve search ranking.
**Implementation**: GitPython extracts comprehensive metadata reactively.

### Decision #6: 768-Dimension Embeddings
**Why**: UniXcoder standard, good balance of accuracy vs storage.
**Implementation**: Constant defined in Collections, respected system-wide.

### Decision #7: 18 Official ChunkTypes
**Why**: Precise semantic understanding improves search accuracy.
**Implementation**: Defined in `/models/chunk.py`, used for re-ranking.

### Decision #8: No Auto-Indexing
**Why**: User control principle - only index when explicitly triggered.
**Implementation**: Git hooks send triggers, but user must enable them.

## Module Structure

```
rag/
├── retrieval/      # Search implementation
├── compression/    # Token optimization  
├── chunking/       # AST-based splitting
├── enrichment/     # Git metadata extraction
├── graph/          # Neural relationship tracking
└── collections/    # Weaviate schema management
```

## Data Flow Architecture

```
Files → Chunking (AST) → Enrichment (Git) → Embeddings → Weaviate
                ↓                    ↓
            ChunkTypes           Metadata
                ↓                    ↓
            Re-ranking      Graph Relations
```

## Key Design Patterns

### Composable Pipeline
Each component can work independently:
- Chunking without enrichment
- Search without compression
- Graph without embeddings

### Lazy Loading
- Tree-sitter parsers loaded on-demand
- Git operations only when metadata requested
- Graph expansion optional

### Cache Coordination
- Unified cache: 1000 entries, 3600s TTL
- EventBus invalidation on git operations
- LRU eviction policy

## Performance Targets

- Chunking: <100ms per file
- Search: <200ms for hybrid query
- Compression: <50ms analysis
- Indexing: <1s for 100 chunks

## Extension Points

### Adding Languages
1. Install tree-sitter grammar
2. Create language chunker inheriting BaseChunker
3. Register in ChunkerFactory
4. Define node types to extract

### Custom Search Strategies
- Implement SearchStrategy interface
- Register in HybridSearch
- Configure weights in .acolyte

### Metadata Processors
- Add processor to enrichment/processors/
- Hook into EnrichmentService pipeline
- Results stored with chunks
