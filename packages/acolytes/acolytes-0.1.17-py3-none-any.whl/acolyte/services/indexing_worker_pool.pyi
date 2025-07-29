from typing import Any, Dict, List
import asyncio

class IndexingWorkerPool:
    indexing_service: Any
    num_workers: int
    config: Any
    metrics: Any
    perf_logger: Any
    _file_queue: asyncio.Queue
    _worker_tasks: List[asyncio.Task]
    _weaviate_clients: List[Any]
    _embeddings_semaphore: asyncio.Semaphore
    _worker_results: Dict[int, Dict[str, Any]]
    _shutdown_event: asyncio.Event
    _initialized: bool

    def __init__(
        self, indexing_service: Any, num_workers: int = ..., embeddings_semaphore_size: int = ...
    ) -> None: ...
    async def initialize(self) -> None: ...
    async def process_files(
        self, files: List[str], batch_size: int = ..., trigger: str = ...
    ) -> Dict[str, Any]: ...
    async def shutdown(self) -> None: ...
    def get_stats(self) -> Dict[str, Any]: ...
