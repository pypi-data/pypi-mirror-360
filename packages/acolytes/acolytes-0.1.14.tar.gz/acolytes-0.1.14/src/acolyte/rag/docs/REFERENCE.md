# 📚 RAG Module API Reference

## retrieval/hybrid_search.py

### HybridSearch
Main search implementation combining semantic and lexical search.

```python
from acolyte.core.logging import logger
from acolyte.core.metrics import MetricsCollector

class HybridSearch:
    def __init__(
        self,
        weaviate_client: Any,
        embedding_service: EmbeddingService,
        semantic_weight: float = 0.7,
        lexical_weight: float = 0.3,
        fuzzy_threshold: float = 0.85
    )
    
    async def search(
        self,
        query: str,
        collection: str = "CodeChunk",
        limit: int = 20,
        where: Optional[dict] = None,
        additional_fields: Optional[List[str]] = None,
        boost_recent: bool = True,
        file_limit: int = 5
    ) -> List[SearchResult]
    
    async def search_with_compression(
        self,
        query: str,
        collection: str = "CodeChunk", 
        limit: int = 20,
        compression_ratio: float = 0.7,
        **search_kwargs
    ) -> List[SearchResult]
    
    async def search_with_graph_expansion(
        self,
        query: str,
        max_results: int = 10,
        expansion_depth: int = 2
    ) -> List[SearchResult]
```

### SearchResult
```python
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class SearchResult:
    id: str
    content: str
    score: float
    metadata: Dict[str, Any]
    distance: Optional[float] = None
    certainty: Optional[float] = None
    chunk_type: Optional[str] = None
    language: Optional[str] = None
```

## retrieval/rerank.py

### SimpleReranker
Re-ranks search results using multiple strategies.

```python
from acolyte.core.logging import logger

class SimpleReranker:
    @staticmethod
    def rerank_by_type(
        results: List[SearchResult],
        query: str,
        boost_weights: Optional[Dict[str, float]] = None
    ) -> List[SearchResult]
    
    @staticmethod
    def rerank_by_recency(
        results: List[SearchResult],
        decay_factor: float = 0.1,
        max_age_days: int = 365
    ) -> List[SearchResult]
    
    @staticmethod
    def diversity_rerank(
        results: List[SearchResult],
        soft_max_per_file: int = 3,
        min_score_threshold: float = 0.5
    ) -> List[SearchResult]
```

## compression/chunk_compressor.py

### ContextualCompressor
Token optimization without LLM calls.

```python
from acolyte.core.logging import logger
from acolyte.core.metrics import MetricsCollector

class ContextualCompressor:
    def __init__(
        self,
        token_counter: Optional[SmartTokenCounter] = None,
        cache_size: int = 1000,
        cache_ttl: int = 3600
    )
    
    def compress_chunks(
        self,
        chunks: List[Dict[str, Any]],
        query: str,
        target_ratio: float = 0.7,
        preserve_structure: bool = True
    ) -> List[Dict[str, Any]]
    
    def analyze_query(self, query: str) -> QueryAnalysis
    
    def score_chunk_relevance(
        self,
        chunk: Dict[str, Any],
        query_analysis: QueryAnalysis
    ) -> float
```

## chunking/base.py

### BaseChunker
Foundation for all language chunkers with tree-sitter.

```python
from abc import ABC, abstractmethod
from acolyte.core.logging import logger
from acolyte.core.id_generator import generate_id

class BaseChunker(ABC):
    def __init__(
        self,
        language: str,
        chunk_size: int = 100,
        overlap: int = 20,
        min_chunk_size: int = 10
    )
    
    async def chunk_file(
        self,
        file_path: Path,
        content: Optional[str] = None
    ) -> List[Chunk]
    
    def _parse_with_tree_sitter(
        self,
        content: str
    ) -> Optional[tree_sitter.Tree]
    
    @abstractmethod
    def _extract_chunks_from_tree(
        self,
        tree: tree_sitter.Tree,
        content: str
    ) -> List[Tuple[str, int, int, str]]
```

### Chunk
```python
from dataclasses import dataclass
from acolyte.core.id_generator import generate_id

@dataclass
class Chunk:
    id: str  # Use generate_id()
    content: str
    start_line: int
    end_line: int
    chunk_type: ChunkType
    metadata: ChunkMetadata
    embedding: Optional[List[float]] = None
```

## chunking/factory.py

### ChunkerFactory
Automatic language detection and chunker selection.

```python
from acolyte.core.logging import logger

class ChunkerFactory:
    @staticmethod
    def get_chunker(
        file_path: Path,
        language_override: Optional[str] = None
    ) -> BaseChunker
    
    @staticmethod
    def detect_language(file_path: Path) -> str
    
    @staticmethod
    def register_chunker(
        language: str,
        chunker_class: Type[BaseChunker]
    ) -> None
```

## enrichment/service.py

### EnrichmentService
Git metadata extraction and enrichment.

```python
from acolyte.core.logging import logger
from acolyte.core.metrics import MetricsCollector
from acolyte.core.utils.datetime_utils import utc_now, utc_now_iso

class EnrichmentService:
    def __init__(
        self,
        repo_path: str,
        cache_ttl: int = 3600,
        enable_advanced_metrics: bool = True
    )
    
    async def enrich_chunks(
        self,
        chunks: List[Chunk],
        trigger: str = "manual"
    ) -> List[Tuple[Chunk, Dict[str, Any]]]
    
    def extract_git_metadata(
        self,
        file_path: str,
        start_line: int,
        end_line: int
    ) -> GitMetadata
    
    def analyze_code_patterns(
        self,
        chunk: Chunk
    ) -> Dict[str, Any]
```

### GitMetadata
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Any

@dataclass
class GitMetadata:
    author: str
    last_modified: datetime  # Use utc_now()
    commit_hash: str
    commit_message: str
    commits_last_30_days: int
    stability_score: float
    file_age_days: int
    is_actively_developed: bool
    contributors: Dict[str, Dict[str, Any]]
    co_modified_with: List[str]
    code_volatility_index: float
    modification_pattern: str
    commit_types: Dict[str, int]
```

## graph/neural_graph.py

### NeuralGraph
Structural relationship tracking.

```python
from acolyte.core.logging import logger
from acolyte.core.metrics import MetricsCollector

class NeuralGraph:
    def __init__(self, db_path: str)
    
    async def add_node(
        self,
        node_id: str,
        node_type: str,
        metadata: Dict[str, Any]
    ) -> None
    
    async def add_edge(
        self,
        source_id: str,
        target_id: str,
        edge_type: str,
        weight: float = 1.0
    ) -> None
    
    async def find_related_nodes(
        self,
        node_id: str,
        max_depth: int = 2,
        edge_types: Optional[List[str]] = None
    ) -> List[Tuple[str, float]]
    
    async def strengthen_connection(
        self,
        source_id: str,
        target_id: str,
        increment: float = 0.1
    ) -> None
```

## collections/manager.py

### CollectionManager
Weaviate collection lifecycle management.

```python
from acolyte.core.logging import logger

class CollectionManager:
    def __init__(self, client: Any)
    
    async def ensure_collections(self) -> Dict[str, bool]
    
    async def get_collection_info(
        self,
        collection_name: CollectionName
    ) -> Optional[Dict[str, Any]]
    
    async def update_collection_schema(
        self,
        collection_name: CollectionName,
        properties: List[Dict[str, Any]]
    ) -> bool
```

## Configuration

### .acolyte Configuration
```yaml
rag:
  hybrid_search:
    semantic_weight: 0.7
    lexical_weight: 0.3
    fuzzy_threshold: 0.85
    
  compression:
    enabled: true
    target_ratio: 0.7
    cache_size: 1000
    
  chunking:
    default_size: 100
    overlap: 20
    min_size: 10
    
  enrichment:
    enable_advanced_metrics: true
    cache_ttl: 3600
    
  graph:
    max_expansion_depth: 2
    connection_decay: 0.1
```

## Exceptions

All exceptions inherit from `AcolyteException`:

```python
class ChunkingError(AcolyteException): pass
class EnrichmentError(AcolyteException): pass  
class SearchError(AcolyteException): pass
class CompressionError(AcolyteException): pass
class GraphError(AcolyteException): pass
```
