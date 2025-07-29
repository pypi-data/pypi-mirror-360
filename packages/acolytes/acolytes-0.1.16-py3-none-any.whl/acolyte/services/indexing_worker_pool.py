"""
Indexing Worker Pool - Parallel processing for indexing service.

Manages a pool of workers for parallel file indexing.
Separate from IndexingService to maintain single responsibility.
"""

import asyncio
from typing import List, Dict, Any, Optional, TYPE_CHECKING, Union, cast

from acolyte.core.logging import logger, PerformanceLogger
from acolyte.core.tracing import MetricsCollector
from acolyte.core.secure_config import Settings
from acolyte.models.chunk import Chunk

if TYPE_CHECKING:
    import weaviate
    from acolyte.services.indexing_service import IndexingService
    from acolyte.embeddings.unixcoder import UniXcoderEmbeddings


class IndexingWorkerPool:
    """
    Manages parallel workers for indexing operations.

    Features:
    - Configurable number of workers
    - Dedicated Weaviate client per worker (thread-safety)
    - Embeddings semaphore for GPU protection
    - Progress tracking and error collection
    """

    def __init__(
        self,
        indexing_service: 'IndexingService',
        num_workers: int = 4,
        embeddings_semaphore_size: int = 2,
    ):
        """
        Initialize the worker pool.

        Args:
            indexing_service: Parent indexing service for utilities
            num_workers: Number of parallel workers
            embeddings_semaphore_size: Max concurrent embedding operations
        """
        self.indexing_service = indexing_service
        self.num_workers = num_workers
        self.config = Settings()
        self.metrics = MetricsCollector()
        self.perf_logger = PerformanceLogger()

        # Worker components
        self._file_queue: asyncio.Queue = asyncio.Queue()
        self._worker_tasks: List[asyncio.Task] = []
        self._weaviate_clients: List[Optional['weaviate.Client']] = []
        self._embeddings_semaphore = asyncio.Semaphore(embeddings_semaphore_size)

        # Results tracking
        self._worker_results: Dict[int, Dict[str, Any]] = {}
        self._shutdown_event = asyncio.Event()
        self._initialized = False

        logger.info(
            "IndexingWorkerPool created",
            num_workers=num_workers,
            embeddings_semaphore=embeddings_semaphore_size,
        )

    async def initialize(self):
        """Initialize worker pool resources."""
        if self._initialized:
            return

        logger.info("Initializing worker pool")

        # Create Weaviate clients (one per worker for thread safety)
        await self._create_weaviate_clients()

        # Start worker tasks
        for i in range(self.num_workers):
            worker_task = asyncio.create_task(self._worker(i))
            self._worker_tasks.append(worker_task)

        self._initialized = True
        logger.info("Worker pool initialized", active_workers=len(self._worker_tasks))

    async def _create_weaviate_clients(self):
        """Create dedicated Weaviate client for each worker."""
        try:
            import weaviate
        except ImportError:
            logger.warning("Weaviate not available, workers will skip insertion")
            return

        weaviate_url = f"http://localhost:{self.config.get('ports.weaviate', 8080)}"

        for i in range(self.num_workers):
            try:
                client = weaviate.Client(weaviate_url)
                if client.is_ready():
                    self._weaviate_clients.append(client)
                    logger.debug(f"Created Weaviate client for worker {i}")
                else:
                    logger.warning(f"Weaviate client {i} not ready")
                    self._weaviate_clients.append(None)
            except Exception as e:
                logger.error(f"Failed to create Weaviate client {i}", error=str(e))
                self._weaviate_clients.append(None)

    async def process_files(
        self, files: List[str], batch_size: int = 10, trigger: str = "manual"
    ) -> Dict[str, Any]:
        """
        Process files using the worker pool.

        Args:
            files: List of file paths to process
            batch_size: Files per worker batch
            trigger: Indexing trigger type

        Returns:
            Aggregated results from all workers
        """
        if not self._initialized:
            await self.initialize()

        # Reset results
        self._worker_results.clear()

        # Queue file batches
        total_batches = 0
        for i in range(0, len(files), batch_size):
            batch = files[i : i + batch_size]
            await self._file_queue.put((batch, trigger))
            total_batches += 1

        logger.info(
            "Queued files for parallel processing",
            total_files=len(files),
            batches=total_batches,
            batch_size=batch_size,
        )

        # Wait for all batches to be processed
        await self._file_queue.join()

        # Aggregate results
        total_chunks = 0
        total_embeddings = 0
        all_errors = []

        for worker_id, result in self._worker_results.items():
            total_chunks += result.get("chunks_created", 0)
            total_embeddings += result.get("embeddings_created", 0)
            if result.get("errors"):
                all_errors.extend(result["errors"])

        return {
            "chunks_created": total_chunks,
            "embeddings_created": total_embeddings,
            "errors": all_errors,
            "workers_used": len(self._worker_results),
        }

    async def _worker(self, worker_id: int):
        """Individual worker process."""
        logger.info(f"Worker {worker_id} started")

        # Get dedicated Weaviate client
        weaviate_client = (
            self._weaviate_clients[worker_id] if worker_id < len(self._weaviate_clients) else None
        )

        # Create batch inserter if Weaviate available
        batch_inserter = None
        if weaviate_client:
            try:
                from acolyte.rag.collections import WeaviateBatchInserter

                batch_inserter = WeaviateBatchInserter(weaviate_client, self.config)
            except ImportError:
                logger.warning(f"Worker {worker_id}: Batch inserter not available")

        while not self._shutdown_event.is_set():
            try:
                # Get work with timeout to check shutdown
                try:
                    batch_data = await asyncio.wait_for(self._file_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue

                if batch_data is None:  # Shutdown signal
                    break

                file_batch, trigger = batch_data

                # Process the batch
                result = await self._process_file_batch(
                    worker_id, file_batch, trigger, batch_inserter
                )

                # Store result
                self._worker_results[worker_id] = result

                # Update metrics
                self.metrics.increment(f"indexing.worker_{worker_id}.batches_processed")

            except Exception as e:
                logger.error(f"Worker {worker_id} error", error=str(e))

            finally:
                self._file_queue.task_done()

        logger.info(f"Worker {worker_id} stopped")

    async def _process_file_batch(
        self, worker_id: int, files: List[str], trigger: str, batch_inserter: Optional[Any]
    ) -> Dict[str, Any]:
        """Process a batch of files."""
        chunks_created = 0
        embeddings_created = 0
        errors = []

        try:
            with self.perf_logger.measure(f"worker_{worker_id}_batch", files_count=len(files)):
                # Step 1: Chunk files
                chunks = await self.indexing_service._chunk_files(files)
                if not chunks:
                    return {
                        "chunks_created": 0,
                        "embeddings_created": 0,
                        "errors": [],
                        "files_processed": len(files),
                    }

                # Step 2: Enrich chunks
                enriched_tuples = await self._enrich_chunks(chunks, trigger)

                # Step 3: Generate embeddings (with semaphore)
                embeddings_list = await self._generate_embeddings(worker_id, enriched_tuples)
                embeddings_created = len([e for e in embeddings_list if e is not None])

                # Step 4: Insert to Weaviate
                if batch_inserter and embeddings_list:
                    chunks_created, insert_errors = await self._insert_to_weaviate(
                        enriched_tuples, embeddings_list, batch_inserter
                    )
                    errors.extend(insert_errors)

        except Exception as e:
            logger.error(f"Worker {worker_id} batch failed", error=str(e), files=files)
            errors.append(
                {
                    "worker_id": worker_id,
                    "files": files,
                    "error": str(e),
                    "error_type": type(e).__name__,
                }
            )

        return {
            "chunks_created": chunks_created,
            "embeddings_created": embeddings_created,
            "errors": errors,
            "files_processed": len(files),
        }

    async def _enrich_chunks(
        self, chunks: List[Chunk], trigger: str
    ) -> List[tuple[Chunk, Dict[str, Any]]]:
        """Enrich chunks with metadata."""
        if hasattr(self.indexing_service, 'enrichment') and self.indexing_service.enrichment:
            try:
                return await self.indexing_service.enrichment.enrich_chunks(chunks, trigger=trigger)
            except Exception as e:
                logger.error("Enrichment failed", error=str(e))

        # Fallback: empty metadata
        return [(chunk, {}) for chunk in chunks]

    async def _generate_embeddings(
        self, worker_id: int, enriched_tuples: List[tuple[Chunk, Dict[str, Any]]]
    ) -> List[Optional[Any]]:
        """Generate embeddings with GPU protection."""
        if not self.indexing_service._ensure_embeddings():
            return []

        chunks_content: list[Union[str, Chunk]] = [chunk.content for chunk, _ in enriched_tuples]
        embeddings_list = []

        try:
            # Use semaphore to limit GPU concurrency
            async with self._embeddings_semaphore:
                logger.debug(f"Worker {worker_id} acquired embeddings semaphore")

                max_tokens = self.config.get("embeddings.max_tokens_per_batch", 10000)
                assert (
                    self.indexing_service.embeddings is not None
                ), "Embeddings service must be initialized"
                embeddings_service = cast("UniXcoderEmbeddings", self.indexing_service.embeddings)
                embeddings_list = embeddings_service.encode_batch(
                    texts=chunks_content, max_tokens_per_batch=max_tokens
                )

                logger.debug(f"Worker {worker_id} generated embeddings", count=len(embeddings_list))

        except Exception as e:
            logger.error(f"Worker {worker_id} embeddings failed", error=str(e))
            # Return None for each chunk
            embeddings_list = [None] * len(chunks_content)

        return embeddings_list

    async def _insert_to_weaviate(
        self,
        enriched_tuples: List[tuple[Chunk, Dict[str, Any]]],
        embeddings_list: List[Optional[Any]],
        batch_inserter: Any,
    ) -> tuple[int, List[Dict[str, Any]]]:
        """Insert chunks to Weaviate."""
        weaviate_objects = []
        vectors_list = []

        for i, (chunk, metadata) in enumerate(enriched_tuples):
            obj = self.indexing_service._prepare_weaviate_object(chunk, metadata)
            weaviate_objects.append(obj)

            embedding = embeddings_list[i] if i < len(embeddings_list) else None
            if embedding:
                # Handle different embedding types
                from acolyte.embeddings.types import EmbeddingVector

                if isinstance(embedding, EmbeddingVector):
                    vector = embedding.to_weaviate()
                elif hasattr(embedding, "to_weaviate"):
                    vector = embedding.to_weaviate()
                else:
                    vector = list(embedding)
                vectors_list.append(vector)
            else:
                vectors_list.append(None)

        # Batch insert
        return await batch_inserter.batch_insert_with_fallback(
            data_objects=weaviate_objects, vectors=vectors_list, class_name="CodeChunk"
        )

    async def shutdown(self):
        """Gracefully shutdown the worker pool."""
        logger.info("Shutting down worker pool")

        # Signal shutdown
        self._shutdown_event.set()

        # Send shutdown signals to queue
        if self._file_queue:
            for _ in range(self.num_workers):
                await self._file_queue.put(None)

        # Wait for workers to finish
        if self._worker_tasks:
            await asyncio.gather(*self._worker_tasks, return_exceptions=True)

        # Cleanup
        self._worker_tasks.clear()
        self._weaviate_clients.clear()
        self._initialized = False

        logger.info("Worker pool shutdown complete")

    def get_stats(self) -> Dict[str, Any]:
        """Get worker pool statistics."""
        return {
            "num_workers": self.num_workers,
            "active_workers": len(self._worker_tasks),
            "queue_size": self._file_queue.qsize() if self._file_queue else 0,
            "results_collected": len(self._worker_results),
            "weaviate_clients": len([c for c in self._weaviate_clients if c]),
            "initialized": self._initialized,
        }
