"""Type stubs for Weaviate Batch Inserter.

Provides type hints for the batch insertion module.
"""

from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import threading
from acolyte.core.secure_config import Settings
from acolyte.core.tracing import MetricsCollector
from acolyte.core.logging import PerformanceLogger

@dataclass
class BatchResult:
    successful: int = 0
    failed: int = 0
    errors: Optional[List[Dict[str, Any]]] = None

    def __post_init__(self) -> None: ...
    @property
    def total(self) -> int: ...

class WeaviateBatchInserter:
    client: Any  # weaviate.Client
    config: Settings
    metrics: MetricsCollector
    perf_logger: PerformanceLogger
    batch_size: int
    num_workers: int
    dynamic_batching: bool
    timeout_retries: int
    connection_error_retries: int
    _batch_lock: threading.Lock  # Thread safety lock

    def __init__(self, weaviate_client: Any, config: Optional[Settings] = None) -> None: ...
    async def batch_insert(
        self,
        data_objects: List[Dict[str, Any]],
        vectors: List[Optional[List[float]]],
        class_name: str = "CodeChunk",
    ) -> Tuple[int, List[Dict[str, Any]]]: ...
    def _sync_batch_insert(
        self,
        data_objects: List[Dict[str, Any]],
        vectors: List[Optional[List[float]]],
        class_name: str,
    ) -> BatchResult: ...
    async def batch_insert_with_fallback(
        self,
        data_objects: List[Dict[str, Any]],
        vectors: List[Optional[List[float]]],
        class_name: str = "CodeChunk",
        fallback_to_individual: bool = True,
    ) -> Tuple[int, List[Dict[str, Any]]]: ...
    def validate_objects(
        self, data_objects: List[Dict[str, Any]], class_name: str = "CodeChunk"
    ) -> List[str]: ...
