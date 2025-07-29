"""Type stubs for indexing_service module."""

# mypy: disable-error-code="type-arg"

from pathlib import Path
from typing import List, Dict, Any, Optional, Pattern, TypedDict
import asyncio
from acolyte.core.logging import PerformanceLogger
from acolyte.core.tracing import MetricsCollector
from acolyte.core.secure_config import Settings
from acolyte.models.chunk import Chunk, ChunkType
from acolyte.models.document import DocumentType
from acolyte.rag.enrichment.service import EnrichmentService

ENRICHMENT_AVAILABLE: bool
EMBEDDINGS_AVAILABLE: bool
WEAVIATE_AVAILABLE: bool
ADAPTIVE_CHUNKER_AVAILABLE: bool

# Weaviate response types
class WeaviateMeta(TypedDict):
    count: int

class WeaviateGroupedBy(TypedDict):
    value: str

class WeaviateGroup(TypedDict):
    groupedBy: WeaviateGroupedBy
    meta: WeaviateMeta

class WeaviateAggregate(TypedDict):
    CodeChunk: List[WeaviateGroup]

class WeaviateData(TypedDict):
    Aggregate: WeaviateAggregate

class WeaviateResponse(TypedDict):
    data: WeaviateData

# Embeddings types
class EmbeddingService:
    def encode(self, content: str) -> List[float]: ...

# Stats types
class IndexingStats(TypedDict):
    total_files: int
    total_chunks: int
    languages: Dict[str, int]
    chunk_types: Dict[str, int]
    last_indexed: Optional[str]
    index_size_estimate_mb: float
    weaviate_available: bool
    error: Optional[str]

class IndexingService:
    metrics: MetricsCollector
    perf_logger: PerformanceLogger
    config: Settings
    _is_indexing: bool
    enrichment: Optional[EnrichmentService]
    embeddings: Optional[EmbeddingService]
    weaviate: Optional[Any]  # Weaviate client
    batch_size: int
    max_file_size_mb: int
    concurrent_workers: int
    _ignore_patterns: List[Pattern[str]]
    _indexing_lock: asyncio.Lock

    def __init__(self) -> None: ...
    def _ensure_embeddings(self) -> bool: ...
    def _init_weaviate(self) -> None: ...
    def _load_ignore_patterns(self) -> None: ...
    def _glob_to_regex(self, pattern: str) -> Pattern[str]: ...
    def _should_ignore(self, file_path: str) -> bool: ...
    async def index_files(
        self, files: List[str], trigger: str = "manual", task_id: Optional[str] = None
    ) -> Dict[str, Any]: ...
    async def _filter_files(self, files: List[str]) -> List[str]: ...
    def _is_supported_file(self, path: Path) -> bool: ...
    async def _process_batch(self, files: List[str], trigger: str) -> Dict[str, Any]: ...
    async def _chunk_files(self, files: List[str]) -> List[Chunk]: ...
    def _detect_chunk_type(self, content: str, file_extension: str) -> ChunkType: ...
    def _infer_document_type(self, path: Path) -> DocumentType: ...
    def _detect_language(self, path: Path) -> str: ...
    def _prepare_weaviate_object(
        self, chunk: Chunk, enrichment_metadata: Dict[str, Any]
    ) -> Dict[str, Any]: ...
    async def _index_to_weaviate(self, data_object: Dict[str, Any], vector: Any) -> None: ...
    async def _notify_progress(
        self,
        progress: Dict[str, Any],
        task_id: Optional[str] = None,
        files_skipped: int = 0,
        chunks_created: int = 0,
        embeddings_generated: int = 0,
        errors_count: int = 0,
    ) -> None: ...
    async def estimate_files(
        self,
        root: Path,
        patterns: List[str],
        exclude_patterns: List[str],
        respect_gitignore: bool = True,
        respect_acolyteignore: bool = True,
    ) -> int: ...
    async def remove_file(self, file_path: str) -> bool: ...
    async def get_stats(self) -> IndexingStats: ...
    async def rename_file(self, old_path: str, new_path: str) -> bool: ...
    def is_supported_file(self, path: Path) -> bool: ...
    def should_ignore(self, file_path: str) -> bool: ...
    def _generate_error_summary(self, errors: List[Dict[str, Any]]) -> Dict[str, Any]: ...
    @property
    def is_indexing(self) -> bool: ...
