# 🔄 RAG Module Workflows

## Complete Indexing Pipeline Flow

```mermaid
graph TD
    A[Project Files] --> B[ChunkerFactory.get_chunker]
    B --> C{Language Detected}
    C -->|Tree-sitter| D[Parse AST]
    C -->|Pattern Match| E[Regex Extraction]
    C -->|Unknown| F[Default Chunker]
    
    D --> G[Extract Chunks]
    E --> G
    F --> G
    
    G --> H[EnrichmentService]
    H --> I[Extract Git Metadata]
    H --> J[Detect Code Patterns]
    H --> K[Update Neural Graph]
    
    I --> L[EmbeddingService]
    J --> L
    K --> L
    
    L --> M[Generate 768-dim vectors]
    M --> N[Weaviate Storage]
    
    N --> O[CodeChunk Collection]
    N --> P[Document Collection]
```

## Hybrid Search Flow (70/30)

```mermaid
graph LR
    A[User Query] --> B[HybridSearch.search]
    
    B --> C[Semantic Search 70%]
    B --> D[Lexical Search 30%]
    
    C --> E[Query Embedding]
    E --> F[Weaviate near_vector]
    
    D --> G[Fuzzy Matching]
    G --> H[Weaviate BM25]
    
    F --> I[Semantic Results]
    H --> J[Lexical Results]
    
    I --> K[Score Normalization]
    J --> K
    
    K --> L[Combined Results]
    L --> M{Re-ranking Strategy}
    
    M -->|Type| N[Boost functions/classes]
    M -->|Recency| O[Boost recent files]
    M -->|Git| P[Stability/Activity scoring]
    
    N --> Q[Final Results]
    O --> Q
    P --> Q
```

## Search with Compression Flow

```mermaid
graph TD
    A[Query] --> B[QueryAnalyzer]
    B --> C{Query Type?}
    
    C -->|Specific| D[Extract Entities]
    C -->|General| E[No Compression]
    C -->|Generation| E
    
    D --> F[Calculate Relevance Scores]
    F --> G{Score Level?}
    
    G -->|High >0.8| H[Keep 90%]
    G -->|Medium 0.5-0.8| I[Keep 60%]
    G -->|Low <0.5| J[Keep 30%]
    
    H --> K[Apply Strategy by DocType]
    I --> K
    J --> K
    
    K --> L{Document Type?}
    L -->|CODE| M[Preserve signatures]
    L -->|MARKDOWN| N[Keep headers]
    L -->|CONFIG| O[Non-default values]
    L -->|DATA| P[Sample rows]
    
    M --> Q[Compressed Chunks]
    N --> Q
    O --> Q
    P --> Q
    
    Q --> R{Time Check}
    R -->|<45ms| S[Return compressed]
    R -->|>45ms| T[Early stop]
```

## Graph Expansion Search Flow

```mermaid
graph TB
    A[Search Query] --> B[Initial Search]
    B --> C[Seed Results]
    
    C --> D[NeuralGraph.find_related]
    D --> E{Expansion Depth}
    
    E -->|Level 1| F[Direct Relations]
    F --> G[IMPORTS/CALLS/EXTENDS]
    
    E -->|Level 2| H[Indirect Relations]
    H --> I[Relations of Relations]
    
    G --> J[Load Additional Chunks]
    I --> J
    
    J --> K[Combine All Results]
    K --> L[Re-rank by Relevance]
    
    L --> M{Filter by Strength}
    M -->|>0.7| N[Strong connections]
    M -->|0.3-0.7| O[Medium connections]
    M -->|<0.3| P[Weak - discard]
    
    N --> Q[Final Expanded Results]
    O --> Q
```

## Enrichment with Git Metadata Flow

```mermaid
graph LR
    A[Chunk] --> B[EnrichmentService]
    
    B --> C{Trigger Type}
    C -->|commit| D[Normal enrichment]
    C -->|pull| E[Invalidate cache + Full enrich]
    C -->|manual| D
    
    D --> F[Git blame analysis]
    E --> F
    
    F --> G[Extract contributors]
    F --> H[Calculate stability]
    F --> I[Detect conflicts]
    F --> J[Find co-modifications]
    
    G --> K[Metadata Object]
    H --> K
    I --> K
    J --> K
    
    K --> L[GraphBuilder.update]
    L --> M[Update SQLite graph]
    
    K --> N[Return enriched tuple]
    N --> O[(Chunk, Metadata)]
```

## Neural Graph Update Flow

```mermaid
graph TD
    A[Code Analysis] --> B{Entity Type}
    
    B -->|File| C[Add File Node]
    B -->|Function| D[Add Function Node]
    B -->|Class| E[Add Class Node]
    
    C --> F[Detect Relations]
    D --> F
    E --> F
    
    F --> G{Relation Type}
    G -->|Import| H[Add IMPORTS edge]
    G -->|Call| I[Add CALLS edge]
    G -->|Inheritance| J[Add EXTENDS edge]
    G -->|Git Pattern| K[Add CO_MODIFIED edge]
    
    H --> L[Set Initial Strength]
    I --> L
    J --> L
    K --> L
    
    L --> M{Edge Exists?}
    M -->|Yes| N[Strengthen Connection]
    M -->|No| O[Create New Edge]
    
    N --> P[Update Timestamp]
    O --> P
    
    P --> Q[Commit to SQLite]
```

## Complete Search Example Flow

```mermaid
graph TD
    A["Query: 'authentication middleware bug'"] --> B[analyze_query]
    
    B --> C{Query Analysis}
    C -->|Specific bug| D[Enable compression]
    C -->|Has 'bug'| E[Use debugging strategy]
    
    D --> F[HybridSearch]
    E --> F
    
    F --> G[70% Semantic + 30% Lexical]
    G --> H[Initial Results]
    
    H --> I{Enough results?}
    I -->|No| J[Graph Expansion]
    I -->|Yes| K[Skip expansion]
    
    J --> L[Find related code]
    L --> M[Expanded results]
    
    K --> N[Apply re-ranking]
    M --> N
    
    N --> O{Re-rank strategy}
    O -->|debugging| P[Prioritize unstable code]
    O -->|git_aware| Q[Balance all factors]
    
    P --> R[Compress chunks]
    Q --> R
    
    R --> S[Final results with context]
    S --> T["Return: auth.py, middleware.py, tests"]
```

## Chunking Decision Tree

```mermaid
graph TD
    A[File Input] --> B{File Extension}
    
    B -->|.py| C[PythonChunker]
    B -->|.js/.ts| D[TypeScriptChunker]
    B -->|.java| E[JavaChunker]
    B -->|.cs| F[CSharpChunker]
    B -->|.md| G[MarkdownChunker]
    B -->|Unknown| H[DefaultChunker]
    
    C --> I{Tree-sitter available?}
    D --> I
    E --> I
    
    I -->|Yes| J[Parse with tree-sitter]
    I -->|No| K[Use pattern matching]
    
    F --> K
    
    J --> L[Extract by AST nodes]
    K --> M[Extract by regex]
    
    L --> N[Apply size limits]
    M --> N
    
    N --> O{Chunk size}
    O -->|<1 line| P[Keep anyway]
    O -->|>max| Q[Split with overlap]
    O -->|OK| R[Valid chunk]
    
    P --> S[Add metadata]
    Q --> S
    R --> S
    
    S --> T[Assign ChunkType]
    T --> U[Return chunks]
```

## Performance Optimization Workflows

### Batch Processing Flow

```python
from acolyte.core.logging import logger
from acolyte.core.metrics import MetricsCollector

# Process files in optimized batches
async def batch_index_files(files: List[Path]):
    metrics = MetricsCollector()
    metrics.increment("rag.batch_indexing.started")
    # Group by language for better cache usage
    files_by_lang = group_by_language(files)
    
    for language, lang_files in files_by_lang.items():
        # Process in batches of 10-100
        for batch in batched(lang_files, size=50):
            tasks = []
            
            # Parallel chunking
            for file in batch:
                chunker = ChunkerFactory.get_chunker(file)
                tasks.append(chunker.chunk_file(file))
            
            chunks = await asyncio.gather(*tasks)
            
            # Batch enrichment
            all_chunks = list(chain.from_iterable(chunks))
            enriched = await enrichment.enrich_chunks(all_chunks)
            
            # Batch embedding generation
            contents = [c.content for c, _ in enriched]
            embeddings = await embedding_service.encode_batch(contents)
            
            # Batch insert to Weaviate
            await weaviate_batch_insert(enriched, embeddings)
```

### Cache Warming Flow

```python
from acolyte.core.logging import logger

# Pre-compute common searches
async def warm_search_cache():
    logger.info("Warming search cache")
    common_queries = [
        "authentication",
        "database connection",
        "error handling",
        "api endpoints"
    ]
    
    for query in common_queries:
        # Search without compression to cache full results
        results = await hybrid_search.search(
            query=query,
            limit=20
        )
        
        # Also cache compressed versions
        compressed = await hybrid_search.search_with_compression(
            query=query,
            compression_ratio=0.7
        )
```

### Git Hook Integration Flow

```mermaid
graph TD
    A[Git Operation] --> B{Hook Type}
    
    B -->|post-commit| C[Detect changed files]
    B -->|post-merge| D[Detect merged files]
    B -->|post-checkout| E[Detect branch diff]
    
    C --> F[HTTP POST to API]
    D --> F
    E --> F
    
    F --> G["/api/index/git-changes"]
    G --> H[IndexingService]
    
    H --> I{Trigger Type}
    I -->|commit| J[Normal indexing]
    I -->|pull| K[Full re-enrichment]
    
    J --> L[Process changes]
    K --> M[Invalidate caches]
    M --> L
    
    L --> N[Update Weaviate]
    N --> O[Notify via EventBus]
```

## Complete RAG Query Lifecycle

```python
from acolyte.core.logging import logger
from acolyte.core.metrics import MetricsCollector

async def complete_rag_lifecycle(query: str) -> List[Dict]:
    """Shows the complete flow from query to results."""
    metrics = MetricsCollector()
    
    # 1. Initialize services
    logger.info("Starting RAG lifecycle", query=query)
    search = HybridSearch(weaviate_client, embedding_service)
    compressor = ContextualCompressor()
    graph = NeuralGraph(db_path)
    
    # 2. Analyze query intent
    query_analysis = compressor.analyze_query(query)
    
    # 3. Determine search strategy
    if "bug" in query.lower() or "error" in query.lower():
        strategy = "debugging"
        use_compression = True
        expand_graph = True
    elif query_analysis.is_specific:
        strategy = "specific"
        use_compression = True
        expand_graph = False
    else:
        strategy = "exploratory"
        use_compression = False
        expand_graph = True
    
    # 4. Execute search
    if expand_graph:
        results = await search.search_with_graph_expansion(
            query=query,
            expansion_depth=2
        )
    else:
        results = await search.search(query=query)
    
    # 5. Apply compression if needed
    if use_compression:
        results = compressor.compress_chunks(
            chunks=results,
            query=query,
            target_ratio=0.5
        )
    
    # 6. Re-rank based on strategy
    if strategy == "debugging":
        results = SimpleReranker.rerank_for_debugging(results)
    else:
        results = SimpleReranker.rerank_git_aware(results)
    
    # 7. Format results
    return format_results_for_response(results)
```

## Performance Tips Summary

1. **Batch Operations**: Process 10-100 files at once
2. **Language Grouping**: Process similar files together  
3. **Parallel Processing**: Use asyncio.gather for I/O operations
4. **Cache Warming**: Pre-compute common queries
5. **Smart Compression**: Only for specific queries
6. **Graph Pruning**: Remove edges with strength < 0.1
7. **Incremental Updates**: Only re-index changed files
