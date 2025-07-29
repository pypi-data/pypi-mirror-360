"""
Indexing Service - Indexing Pipeline.

Orchestrates the complete code indexing pipeline.
"""

from acolyte.core.utils.datetime_utils import utc_now, utc_now_iso
from acolyte.core.utils.file_types import FileTypeDetector, FileCategory
from pathlib import Path
from typing import List, Dict, Any, Optional, TYPE_CHECKING, cast, Union
import re
import asyncio

from acolyte.core.logging import logger, PerformanceLogger
from acolyte.core.tracing import MetricsCollector
from acolyte.core.exceptions import ExternalServiceError
from acolyte.core.secure_config import Settings
from acolyte.core.events import event_bus, ProgressEvent
from acolyte.core.runtime_state import get_runtime_state
from acolyte.models.chunk import Chunk, ChunkType
from acolyte.models.document import DocumentType

# from acolyte.embeddings.types import EmbeddingVector  # Import only when needed

# Conditional imports while modules are being developed
try:
    from acolyte.rag.enrichment.service import EnrichmentService

    ENRICHMENT_AVAILABLE = True
except ImportError:
    logger.warning("EnrichmentService not available yet")
    ENRICHMENT_AVAILABLE = False

# Embeddings will be imported lazily when needed
EMBEDDINGS_AVAILABLE = None  # Will check on first use

# Weaviate will be imported when needed
WEAVIATE_AVAILABLE = True

# AdaptiveChunker will be imported lazily when needed
ADAPTIVE_CHUNKER_AVAILABLE = None  # Will check on first use

if TYPE_CHECKING:
    from acolyte.embeddings.unixcoder import UniXcoderEmbeddings


class IndexingService:
    """
    Orchestrates complete indexing pipeline.

    PIPELINE:
    1. Chunking → splits files
    2. Enrichment → adds Git metadata (returns tuples)
    3. Embeddings → vectorizes
    4. Weaviate → stores everything

    TRIGGERS:
    - "manual": User requested
    - "commit": Post-commit hook
    - "pull": Post-merge (invalidates cache)
    - "checkout": Branch change
    - "fetch": Preparation
    """

    def __init__(self) -> None:
        self.metrics = MetricsCollector()
        self.perf_logger = PerformanceLogger()
        self.config = Settings()
        self._is_indexing = False

        # Initialize available services
        if ENRICHMENT_AVAILABLE:
            self.enrichment = EnrichmentService()
        else:
            self.enrichment = None

        # Embeddings will be loaded lazily
        self.embeddings: Optional["UniXcoderEmbeddings"] = None

        if WEAVIATE_AVAILABLE:
            self._init_weaviate()
        else:
            self.weaviate = None

        # Indexing configuration
        self.batch_size = self.config.get("indexing.batch_size", 20)
        self.max_file_size_mb = self.config.get("indexing.max_file_size_mb", 10)
        self.concurrent_workers = self.config.get("indexing.concurrent_workers", 4)
        self.enable_parallel = self.config.get("indexing.enable_parallel", False)

        # Ignored files cache
        self._ignore_patterns = []
        self._load_ignore_patterns()

        # Lock to prevent concurrent indexing
        self._indexing_lock: asyncio.Lock = asyncio.Lock()
        self._is_indexing = False

        # Lazy-loaded worker pool for parallel processing
        self._worker_pool = None

        # Runtime state for persistent progress
        self._runtime_state = get_runtime_state()

        # Checkpoint interval (save progress every N files)
        self.checkpoint_interval = self.config.get("indexing.checkpoint_interval", 50)

        # NOTE: Cache invalidation handling moved to ReindexService

        logger.info(
            "IndexingService initialized",
            enrichment=ENRICHMENT_AVAILABLE,
            embeddings="lazy",  # Will load on first use
            weaviate=WEAVIATE_AVAILABLE,
            parallel_enabled=self.enable_parallel,
            concurrent_workers=self.concurrent_workers if self.enable_parallel else "disabled",
        )

    def _ensure_embeddings(self):
        """Lazy load embeddings service when needed."""
        global EMBEDDINGS_AVAILABLE

        if self.embeddings is not None:
            return True

        if EMBEDDINGS_AVAILABLE is None:
            try:
                from acolyte.embeddings import get_embeddings

                EMBEDDINGS_AVAILABLE = True
                self.embeddings = get_embeddings()
                logger.info("Embeddings service loaded on demand")
            except ImportError:
                logger.warning("Embeddings service not available")
                EMBEDDINGS_AVAILABLE = False

        return self.embeddings is not None

    def _init_weaviate(self):
        """Initialize Weaviate client."""
        try:
            import weaviate  # type: ignore

            weaviate_url = f"http://localhost:{self.config.get('ports.weaviate', 8080)}"
            self.weaviate = weaviate.Client(weaviate_url)

            # Verify connection
            if not self.weaviate.is_ready():
                logger.warning("Weaviate not ready")
                self.weaviate = None

        except Exception as e:
            logger.error("Failed to connect to Weaviate", error=str(e))
            self.weaviate = None

    def _load_ignore_patterns(self):
        """Load patterns from .acolyteignore."""
        patterns_list = []
        ignore_config = self.config.get("ignore", {})
        for category, patterns in ignore_config.items():
            if isinstance(patterns, list):
                patterns_list.extend(patterns)
        self._ignore_patterns = [self._glob_to_regex(p) for p in patterns_list]
        logger.info("Loaded ignore patterns", patterns_count=len(self._ignore_patterns))

    def _glob_to_regex(self, pattern: str) -> re.Pattern:
        """Convert glob pattern to regex."""
        # Escape special regex characters
        pattern = pattern.replace(".", r"\.")
        pattern = pattern.replace("*", ".*")
        pattern = pattern.replace("?", ".")

        # Handle directories
        if pattern.endswith("/"):
            pattern = pattern + ".*"

        return re.compile(pattern)

    def _should_ignore(self, file_path: str) -> bool:
        """Check if a file should be ignored."""
        path_str = str(file_path)

        for pattern in self._ignore_patterns or []:
            if pattern.match(path_str):
                return True

        return False

    async def index_files(
        self,
        files: List[str],
        trigger: str = "manual",
        task_id: Optional[str] = None,
        resume_from: Optional[str] = None,
    ) -> Dict[str, Any]:
        # Atomic check-and-set to prevent race condition
        async with self._indexing_lock:
            if self._is_indexing:
                raise Exception("Indexing already in progress")
            self._is_indexing = True

        try:
            start_time = utc_now()

            # Validate trigger
            VALID_TRIGGERS = {"commit", "pull", "checkout", "fetch", "manual"}
            if trigger not in VALID_TRIGGERS:
                logger.warning("Unknown indexing trigger", trigger=trigger, fallback="manual")
                trigger = "manual"

            logger.info("Starting indexing", files_count=len(files), trigger=trigger)

            # Check for resumable progress
            if resume_from:
                progress = await self._load_progress(resume_from)
                if progress and progress.get("status") == "in_progress":
                    # Resume from saved progress
                    files_pending = progress.get("files_pending", [])
                    if files_pending:
                        logger.info(
                            "Resuming indexing from checkpoint",
                            task_id=resume_from,
                            total_files=progress.get("total_files", 0),
                            processed_files=progress.get("processed_files", 0),
                            pending_files=len(files_pending),
                        )
                        files = files_pending
                        # Restore counters
                        total_chunks = progress.get("chunks_created", 0)
                        total_embeddings = progress.get("embeddings_created", 0)
                        errors = progress.get("errors", [])
                        files_skipped = progress.get("files_skipped", 0)
                        resumed = True
                    else:
                        logger.warning("No pending files in saved progress", task_id=resume_from)
                        resumed = False
                else:
                    logger.info("No resumable progress found", task_id=resume_from)
                    resumed = False
            else:
                resumed = False

            # Filter files if not resuming
            if not resumed:
                with self.perf_logger.measure("indexing_filter_files", files_count=len(files)):
                    valid_files = await self._filter_files(files)
                files_skipped = len(files) - len(valid_files)  # Calculate skipped files
                total_chunks = 0
                total_embeddings = 0
                errors = []
            else:
                # When resuming, files are already filtered
                valid_files = files

            if not valid_files:
                return {
                    "status": "success",
                    "files_requested": len(files),
                    "files_processed": 0,
                    "reason": "All files filtered out",
                    "trigger": trigger,
                    "chunks_created": 0,
                    "embeddings_created": 0,
                    "duration_seconds": 0,
                    "errors": [],
                }

            # Decide whether to use parallel processing
            use_parallel = (
                self.enable_parallel
                and len(valid_files) >= self.config.get("indexing.min_files_for_parallel", 20)
                and self.concurrent_workers > 1
            )

            if use_parallel:
                # Use worker pool for parallel processing
                logger.info(
                    "Using parallel processing",
                    workers=self.concurrent_workers,
                    files=len(valid_files),
                )

                # Initialize worker pool if needed
                if self._worker_pool is None:
                    from acolyte.services.indexing_worker_pool import IndexingWorkerPool

                    embeddings_semaphore = self.config.get("indexing.embeddings_semaphore", 2)
                    self._worker_pool = IndexingWorkerPool(
                        indexing_service=self,
                        num_workers=self.concurrent_workers,
                        embeddings_semaphore_size=embeddings_semaphore,
                    )
                    await self._worker_pool.initialize()

                # Process files in parallel
                worker_batch_size = self.config.get("indexing.worker_batch_size", 10)
                pool_result = await self._worker_pool.process_files(
                    valid_files, batch_size=worker_batch_size, trigger=trigger
                )

                # Extract results
                total_chunks = pool_result["chunks_created"]
                total_embeddings = pool_result["embeddings_created"]
                errors = pool_result["errors"]

                # Notify final progress
                await self._notify_progress(
                    {
                        "total_files": len(valid_files),
                        "processed_files": len(valid_files),
                        "current_file": "Complete",
                        "percentage": 100,
                    },
                    task_id=task_id,
                    files_skipped=files_skipped,
                    chunks_created=total_chunks,
                    embeddings_generated=total_embeddings,
                    errors_count=len(errors),
                )

            else:
                # Use existing sequential processing
                logger.info(
                    "Using sequential processing",
                    reason=(
                        "parallel disabled or too few files"
                        if not self.enable_parallel
                        else "too few files"
                    ),
                    files=len(valid_files),
                )

                # Process in batches
                if not resumed:
                    total_chunks = 0
                    total_embeddings = 0
                    errors = []  # This will collect detailed errors from all batches

                for i in range(0, len(valid_files), self.batch_size):
                    batch = valid_files[i : i + self.batch_size]

                    try:
                        result = await self._process_batch(batch, trigger)
                        total_chunks += result["chunks_created"]
                        total_embeddings += result["embeddings_created"]

                        # Collect any errors from this batch
                        if result.get("errors"):
                            errors.extend(result["errors"])

                        # Notify progress with complete statistics
                        progress = {
                            "total_files": len(valid_files),
                            "processed_files": min(i + self.batch_size, len(valid_files)),
                            "current_file": batch[-1] if batch else "",
                            "percentage": (i + len(batch)) / len(valid_files) * 100,
                        }
                        await self._notify_progress(
                            progress,
                            task_id=task_id,
                            files_skipped=files_skipped,
                            chunks_created=total_chunks,
                            embeddings_generated=total_embeddings,
                            errors_count=len(errors),
                        )

                        # Save checkpoint periodically
                        if task_id and (i + len(batch)) % self.checkpoint_interval == 0:
                            checkpoint_data = {
                                "task_id": task_id,
                                "status": "in_progress",
                                "started_at": start_time.isoformat(),
                                "total_files": len(files),
                                "processed_files": i + len(batch),
                                "files_pending": valid_files[i + len(batch) :],
                                "files_skipped": files_skipped,
                                "chunks_created": total_chunks,
                                "embeddings_created": total_embeddings,
                                "errors": errors,
                                "last_checkpoint": utc_now_iso(),
                                "trigger": trigger,
                            }
                            await self._save_progress(task_id, checkpoint_data)
                            logger.debug(
                                "Checkpoint saved",
                                task_id=task_id,
                                processed=i + len(batch),
                                total=len(valid_files),
                            )

                    except Exception as e:
                        # Batch-level error (complete batch failed)
                        batch_error = {
                            "batch_index": i // self.batch_size,
                            "files": batch,
                            "error": str(e),
                            "error_type": type(e).__name__,
                        }
                        errors.append(batch_error)

                        logger.error(
                            "Batch processing failed",
                            batch_index=i // self.batch_size,
                            error=str(e),
                            files_in_batch=len(batch),
                        )

            # Calculate statistics
            duration = (utc_now() - start_time).total_seconds()

            result = {
                "status": "success" if not errors else "partial",
                "files_requested": len(files),
                "files_processed": len(valid_files),
                "chunks_created": total_chunks,
                "embeddings_created": total_embeddings,
                "trigger": trigger,
                "duration_seconds": duration,
                "errors": errors,
            }

            self.metrics.gauge("indexing.files_indexed", len(valid_files))
            self.metrics.gauge("indexing.chunks_created", total_chunks)
            self.metrics.increment(f"indexing.trigger.{trigger}")

            logger.info("Indexing complete", **result)

            # If there were errors, also log a summary
            if errors:
                error_summary = self._generate_error_summary(errors)
                logger.warning(
                    "Indexing completed with errors",
                    total_errors=len(errors),
                    error_summary=error_summary,
                )
                # Also include error summary in result
                result["error_summary"] = error_summary

            # Record timing
            elapsed_ms = (utc_now() - start_time).total_seconds() * 1000
            self.metrics.record("indexing.index_files_total_ms", elapsed_ms)

            # Clear progress if completed successfully
            if task_id and result["status"] in ["success", "partial"]:
                await self._clear_progress(task_id)
                logger.debug("Indexing progress cleared", task_id=task_id)

            return result
        finally:
            # Use lock to safely clear the flag
            async with self._indexing_lock:
                self._is_indexing = False

    async def _filter_files(self, files: List[str]) -> List[str]:
        """Filter valid files to index."""
        valid_files = []

        for file_path in files:
            path = Path(file_path).resolve()

            # Verify it exists
            if not path.exists():
                logger.debug(f"File not found: {file_path}")
                continue

            # Verify it's not a directory
            if path.is_dir():
                continue

            # Verify size
            size_mb = path.stat().st_size / (1024 * 1024)
            if size_mb > self.max_file_size_mb:
                logger.warning(
                    "File too large for indexing",
                    file=file_path,
                    size_mb=round(size_mb, 1),
                    limit_mb=self.max_file_size_mb,
                )
                continue

            # Verify ignore patterns
            if self._should_ignore(str(path)):
                logger.debug(f"File ignored by patterns: {file_path}")
                continue

            # Verify supported extension
            if not self._is_supported_file(path):
                logger.debug(f"Unsupported file type: {file_path}")
                continue

            valid_files.append(str(path))

        return valid_files

    def _is_supported_file(self, path: Path) -> bool:
        """Check if the file is of a supported type."""
        return FileTypeDetector.is_supported(path)

    async def _process_batch(self, files: List[str], trigger: str) -> Dict[str, Any]:
        """Process a batch of files."""
        chunks_created = 0
        embeddings_created = 0
        batch_errors = []  # Track errors with details

        # STEP 1: Chunking
        with self.perf_logger.measure("indexing_chunking", files_count=len(files)):
            chunks = await self._chunk_files(files)

        if not chunks:
            return {"chunks_created": 0, "embeddings_created": 0}

        # STEP 2: Enrichment - RETURNS TUPLES
        enriched_tuples = []
        with self.perf_logger.measure("indexing_enrichment", chunks_count=len(chunks)):
            if self.enrichment and ENRICHMENT_AVAILABLE:
                try:
                    enriched_tuples = await self.enrichment.enrich_chunks(
                        chunks, trigger=trigger  # EnrichmentService uses this for cache
                    )
                except Exception as e:
                    logger.error(
                        "Enrichment failed", chunks_count=len(chunks), trigger=trigger, error=str(e)
                    )
                    # Continue without enrichment
                    enriched_tuples = [(chunk, {}) for chunk in chunks]
            else:
                # Without enrichment, create empty tuples
                enriched_tuples = [(chunk, {}) for chunk in chunks]

        # STEP 3: Generate embeddings in batch (MUCH more efficient)
        from typing import Optional
        from acolyte.embeddings.types import EmbeddingVector

        embeddings_list: list[Optional[EmbeddingVector]] = []
        if self._ensure_embeddings() and self.embeddings is not None:
            # Extract all chunk contents for batch processing
            chunks_content = [chunk.content for chunk, _ in enriched_tuples]

            if chunks_content:
                try:
                    with self.perf_logger.measure(
                        "indexing_batch_embedding_generation", chunks_count=len(chunks_content)
                    ):
                        # Use batch processing with memory control
                        max_tokens = self.config.get("embeddings.max_tokens_per_batch", 10000)
                        embeddings_list = cast(
                            list[Optional[EmbeddingVector]],
                            self.embeddings.encode_batch(
                                texts=cast(list[Union[str, Chunk]], chunks_content),
                                max_tokens_per_batch=max_tokens,
                            ),
                        )
                    embeddings_created = len(embeddings_list)
                    logger.info(
                        "Batch embedding generation successful",
                        chunks_count=len(chunks_content),
                        embeddings_created=embeddings_created,
                    )
                except Exception as e:
                    logger.error(
                        "Batch embedding generation failed, falling back to individual",
                        error=str(e),
                        chunks_count=len(chunks_content),
                    )
                    # Fallback: process one by one if batch fails
                    for chunk_content in chunks_content:
                        try:
                            embedding = self.embeddings.encode(chunk_content)
                            embeddings_list.append(embedding)
                            embeddings_created += 1
                        except Exception as individual_error:
                            logger.error("Individual embedding failed", error=str(individual_error))
                            embeddings_list.append(None)  # Placeholder for failed

        # STEP 4: Prepare for batch insertion
        if self.weaviate and WEAVIATE_AVAILABLE:
            # Check if batch insertion is enabled
            use_batch = self.config.get("search.weaviate_batch_size", 100) > 1

            if use_batch:
                # Prepare data for batch insertion
                weaviate_objects = []
                vectors_list = []

                for i, (chunk, enrichment_metadata) in enumerate(enriched_tuples):
                    # Combine all info for Weaviate
                    weaviate_object = self._prepare_weaviate_object(chunk, enrichment_metadata)
                    weaviate_objects.append(weaviate_object)

                    # Get corresponding embedding (if any)
                    embedding = embeddings_list[i] if i < len(embeddings_list) else None

                    if embedding:
                        # Import EmbeddingVector only when needed
                        from acolyte.embeddings.types import EmbeddingVector

                        # Validate embedding type
                        if isinstance(embedding, EmbeddingVector):
                            vector = embedding.to_weaviate()
                        elif hasattr(embedding, "to_weaviate"):
                            vector = embedding.to_weaviate()
                        else:
                            # Assume it's a list or array
                            vector = list(embedding)
                        vectors_list.append(vector)
                    else:
                        vectors_list.append(None)

                # Use batch inserter
                try:
                    with self.perf_logger.measure(
                        "indexing_weaviate_batch_insert", chunks_count=len(weaviate_objects)
                    ):
                        # Lazy initialize batch inserter if needed
                        if not hasattr(self, "batch_inserter"):
                            from acolyte.rag.collections import WeaviateBatchInserter

                            self.batch_inserter = WeaviateBatchInserter(self.weaviate, self.config)
                            # Note: batch_inserter handles thread safety internally with a lock

                        # Perform batch insertion with fallback
                        successful, errors = await self.batch_inserter.batch_insert_with_fallback(
                            data_objects=weaviate_objects,
                            vectors=vectors_list,
                            class_name="CodeChunk",
                        )

                        chunks_created = successful
                        batch_errors.extend(errors)

                        logger.info(
                            "Batch insertion completed",
                            successful=successful,
                            failed=len(errors),
                            batch_size=len(weaviate_objects),
                        )

                except Exception as e:
                    logger.error(
                        "Batch insertion failed completely",
                        error=str(e),
                        chunks_count=len(weaviate_objects),
                    )
                    # Add all chunks as errors
                    for chunk, _ in enriched_tuples:
                        file_path = getattr(chunk.metadata, "file_path", "unknown")
                        chunk_type = getattr(chunk.metadata, "chunk_type", "unknown")
                        error_detail = {
                            "file": file_path,
                            "chunk_type": chunk_type,
                            "error": "Batch insertion failed",
                            "error_type": "BatchInsertionError",
                        }
                        batch_errors.append(error_detail)
            else:
                # Fallback to individual insertion (original code)
                for i, (chunk, enrichment_metadata) in enumerate(enriched_tuples):
                    try:
                        # Get corresponding embedding (if any)
                        embedding = embeddings_list[i] if i < len(embeddings_list) else None

                        # Combine all info for Weaviate
                        weaviate_object = self._prepare_weaviate_object(chunk, enrichment_metadata)

                        # Save with vector
                        with self.perf_logger.measure("indexing_weaviate_insert"):
                            if embedding:
                                # Import EmbeddingVector only when needed
                                from acolyte.embeddings.types import EmbeddingVector

                                # Validate embedding type
                                if isinstance(embedding, EmbeddingVector):
                                    vector = embedding.to_weaviate()
                                elif hasattr(embedding, "to_weaviate"):
                                    vector = embedding.to_weaviate()
                                else:
                                    # Assume it's a list or array
                                    vector = list(embedding)
                                await self._index_to_weaviate(weaviate_object, vector)
                            else:
                                # Save without vector - Weaviate will generate if configured
                                await self._index_to_weaviate(weaviate_object, None)

                        chunks_created += 1

                    except Exception as e:
                        file_path = getattr(chunk.metadata, "file_path", "unknown")
                        chunk_type = getattr(chunk.metadata, "chunk_type", "unknown")
                        error_detail = {
                            "file": file_path,
                            "chunk_type": chunk_type,
                            "error": str(e),
                            "error_type": type(e).__name__,
                        }
                        batch_errors.append(error_detail)

                        logger.error(
                            "Failed to process chunk",
                            file_path=file_path,
                            chunk_type=chunk_type,
                            error=str(e),
                            error_type=type(e).__name__,
                        )
                        continue

        return {
            "chunks_created": chunks_created,
            "embeddings_created": embeddings_created,
            "errors": batch_errors,
        }

    async def _chunk_files(self, files: List[str]) -> List[Chunk]:
        """
        Divide files into chunks with intelligent ChunkType detection.

        Uses AdaptiveChunker from RAG when available for:
        - AST analysis in Python
        - Complexity detection
        - Intelligent overlap that preserves context
        - Respect for natural code boundaries

        Fallback to simple implementation if AdaptiveChunker is not available.
        """
        chunks = []

        # Lazy check and import AdaptiveChunker
        global ADAPTIVE_CHUNKER_AVAILABLE
        if ADAPTIVE_CHUNKER_AVAILABLE is None:
            try:
                from acolyte.rag.chunking.adaptive import AdaptiveChunker

                ADAPTIVE_CHUNKER_AVAILABLE = True
            except ImportError:
                logger.warning("AdaptiveChunker not available yet")
                ADAPTIVE_CHUNKER_AVAILABLE = False

        # Use AdaptiveChunker if available
        if ADAPTIVE_CHUNKER_AVAILABLE:
            from acolyte.rag.chunking.adaptive import AdaptiveChunker

            chunker = AdaptiveChunker()

            for file_path in files:
                try:
                    path = Path(file_path)
                    content = path.read_text(encoding="utf-8", errors="ignore")

                    if not content.strip():
                        continue

                    # Use AdaptiveChunker for intelligent chunking (asynchronous)
                    # Assuming the signature is chunk(content: str, file_path: str)
                    file_chunks = await chunker.chunk(content, str(file_path))
                    chunks.extend(file_chunks)

                    logger.debug(
                        "Chunked file with AdaptiveChunker",
                        file_path=file_path,
                        chunks_created=len(file_chunks),
                    )

                except Exception as e:
                    logger.error(
                        "Failed to chunk file with AdaptiveChunker",
                        file_path=file_path,
                        error=str(e),
                    )
                    continue

        else:
            # Fallback: Use DefaultChunker when AdaptiveChunker is not available
            logger.info("Using DefaultChunker fallback (AdaptiveChunker not available)")

            from acolyte.rag.chunking.languages.default import DefaultChunker

            for file_path in files:
                try:
                    path = Path(file_path)
                    content = path.read_text(encoding="utf-8", errors="ignore")

                    if not content.strip():
                        continue

                    # Detect language for DefaultChunker
                    language = self._detect_language(path)

                    # Create DefaultChunker for this language
                    default_chunker = DefaultChunker(language)

                    # Use DefaultChunker's smart chunking
                    file_chunks = await default_chunker.chunk(content, str(file_path))
                    chunks.extend(file_chunks)

                    logger.debug(
                        "Chunked file with DefaultChunker",
                        file_path=file_path,
                        chunks_created=len(file_chunks),
                        language=language,
                    )

                except Exception as e:
                    logger.error("Failed to chunk file", file_path=file_path, error=str(e))
                    continue

        return chunks

    def _detect_chunk_type(self, content: str, file_extension: str) -> ChunkType:
        """
        Detect chunk type based on its content and extension.

        Uses patterns to identify the 18 ChunkType types.
        """
        content_lower = content.lower()

        # Patterns to detect types
        # NAMESPACE (check before CLASS to avoid false positives)
        if re.search(r"^\s*namespace\s+\w+", content, re.MULTILINE):
            return ChunkType.NAMESPACE

        # INTERFACE (check before CLASS)
        if re.search(r"^\s*interface\s+\w+", content, re.MULTILINE):
            return ChunkType.INTERFACE

        # CLASS (check after more specific patterns)
        if re.search(r"^\s*(class|struct)\s+\w+", content, re.MULTILINE):
            return ChunkType.CLASS

        # CONSTRUCTOR
        if re.search(r"def\s+__init__\s*\(", content) or re.search(r"constructor\s*\(", content):
            return ChunkType.CONSTRUCTOR

        # FUNCTION
        if re.search(r"\b(def|function|func|fn)\s+\w+\s*\(", content) or re.search(
            r"const\s+\w+\s*=\s*\(.*?\)\s*=>", content
        ):
            return ChunkType.FUNCTION

        # METHOD
        if re.search(r"^\s{4,}(def|function|func)\s+\w+\s*\(", content, re.MULTILINE):
            return ChunkType.METHOD

        # PROPERTY
        if (
            re.search(r"@property", content)
            or re.search(r"get\s+\w+\s*\(\s*\)", content)
            or re.search(r"set\s+\w+\s*\(", content)
        ):
            return ChunkType.PROPERTY

        # IMPORTS (check before MODULE - short import sections)
        if (
            re.search(r"^(import|from|require|use|include)", content, re.MULTILINE)
            and content.count("\n") < 20
        ):  # Short import section
            return ChunkType.IMPORTS

        # MODULE
        if file_extension in [".py", ".js", ".ts"] and re.search(
            r"^\s*(import|from|export|module)", content, re.MULTILINE
        ):
            return ChunkType.MODULE

        # CONSTANTS
        if re.search(r"^[A-Z_]+\s*=", content, re.MULTILINE) or re.search(
            r"^\s*const\s+[A-Z_]+", content, re.MULTILINE
        ):
            return ChunkType.CONSTANTS

        # TYPES
        if (
            re.search(r"^\s*(type|typedef|interface)\s+", content, re.MULTILINE)
            or file_extension in [".ts", ".tsx"]
            and "type " in content
        ):
            return ChunkType.TYPES

        # TESTS
        if (
            re.search(r"(test_|test\(|describe\(|it\(|@Test)", content)
            or "unittest" in content
            or "pytest" in content
        ):
            return ChunkType.TESTS

        # README
        if file_extension in [".md", ".rst"] and "readme" in content_lower:
            return ChunkType.README

        # DOCSTRING
        if (
            content.strip().startswith('"""')
            or content.strip().startswith("'''")
            or re.search(r"/\*\*[\s\S]*?\*/", content)
        ):
            return ChunkType.DOCSTRING

        # COMMENT
        if (
            content.strip().startswith("#")
            or content.strip().startswith("//")
            or content.strip().startswith("/*")
        ):
            return ChunkType.COMMENT

        # SUMMARY (for documentation files)
        if file_extension in [".md", ".rst", ".txt"] and len(content) < 500:
            return ChunkType.SUMMARY

        # Default
        return ChunkType.UNKNOWN

    def _infer_document_type(self, path: Path) -> DocumentType:
        """Infer document type by extension."""
        # Get file category from FileTypeDetector
        category = FileTypeDetector.get_category(path)

        # Map FileCategory to DocumentType
        category_to_doc_type = {
            FileCategory.CODE: DocumentType.CODE,
            FileCategory.DOCUMENTATION: DocumentType.MARKDOWN,
            FileCategory.CONFIGURATION: DocumentType.CONFIG,
            FileCategory.DATA: DocumentType.DATA,
            FileCategory.OTHER: DocumentType.OTHER,
        }

        return category_to_doc_type.get(category, DocumentType.OTHER)

    def _detect_language(self, path: Path) -> str:
        """Detect language by extension."""
        return FileTypeDetector.get_language(path)

    def _prepare_weaviate_object(
        self, chunk: Chunk, enrichment_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare object for Weaviate combining chunk and metadata."""
        # Chunk fields
        # Handle chunk_type carefully - can be None or ChunkType
        chunk_type = getattr(chunk.metadata, "chunk_type", ChunkType.UNKNOWN)
        if isinstance(chunk_type, ChunkType):
            chunk_type_str = chunk_type.value.upper()
        else:
            chunk_type_str = ChunkType.UNKNOWN.value.upper()

        weaviate_obj = {
            "content": chunk.content,
            "file_path": getattr(chunk.metadata, "file_path", ""),
            "chunk_type": chunk_type_str,
            "language": getattr(chunk.metadata, "language", "unknown"),
            "start_line": getattr(chunk.metadata, "start_line", 0),
            "end_line": getattr(chunk.metadata, "end_line", 0),
        }

        # Enriched metadata (flatten)
        git_metadata = enrichment_metadata.get("git", {})
        if git_metadata:
            weaviate_obj.update(
                {
                    "git_last_author": git_metadata.get("last_author"),
                    "git_last_modified": git_metadata.get("last_modified"),
                    "git_stability_score": git_metadata.get("stability_score", 0),
                    "git_commit_hash": git_metadata.get("commit_hash"),
                }
            )

        pattern_metadata = enrichment_metadata.get("patterns", {})
        if pattern_metadata:
            weaviate_obj.update(
                {
                    "pattern_is_test": pattern_metadata.get("is_test_code", False),
                    "pattern_has_todo": pattern_metadata.get("has_todo", False),
                    "pattern_complexity": pattern_metadata.get("complexity", "medium"),
                }
            )

        # Indexing timestamp
        weaviate_obj["indexed_at"] = utc_now_iso()

        return weaviate_obj

    async def _index_to_weaviate(self, data_object: Dict[str, Any], vector: Any) -> None:
        """Index object in Weaviate with optional vector."""
        if not self.weaviate:
            return

        try:
            if vector is not None:
                # Import EmbeddingVector only when needed
                from acolyte.embeddings.types import EmbeddingVector

                # Handle different vector types
                if isinstance(vector, EmbeddingVector):
                    vector_list = vector.to_weaviate()
                elif hasattr(vector, "to_weaviate"):
                    vector_list = vector.to_weaviate()
                else:
                    vector_list = list(vector)

                self.weaviate.data_object.create(
                    class_name="CodeChunk", data_object=data_object, vector=vector_list
                )
            else:
                # Create without vector - Weaviate may generate if configured
                self.weaviate.data_object.create(class_name="CodeChunk", data_object=data_object)
        except Exception as e:
            logger.error("Failed to index to Weaviate", class_name="CodeChunk", error=str(e))
            raise ExternalServiceError(f"Failed to index to Weaviate: {str(e)}") from e

    async def _notify_progress(
        self,
        progress: Dict[str, Any],
        task_id: Optional[str] = None,
        files_skipped: int = 0,
        chunks_created: int = 0,
        embeddings_generated: int = 0,
        errors_count: int = 0,
    ):
        """
        Notify indexing progress via EventBus.

        Publishes ProgressEvent that can be consumed by:
        - WebSocketManager to update UI in real time
        - Other services that need to monitor indexing
        - Metrics system for tracking

        The event includes:
        - current/total for percentage
        - message with current file
        - task_id dedicated for precise WebSocket filtering
        - operation identifying the indexing type
        - Complete indexing statistics

        Args:
            progress: Object with progress information
            task_id: Optional task ID for WebSocket filtering
            files_skipped: Number of files skipped by filters
            chunks_created: Total chunks created so far
            embeddings_generated: Total embeddings generated
            errors_count: Number of errors found
        """
        try:
            # Create progress event with complete statistics
            progress_event = ProgressEvent(
                source="indexing_service",
                operation="indexing_files",
                current=progress["processed_files"],
                total=progress["total_files"],
                message=f"Processing: {progress['current_file']}",
                task_id=task_id,
                files_skipped=files_skipped,
                chunks_created=chunks_created,
                embeddings_generated=embeddings_generated,
                errors=errors_count,
                current_file=progress["current_file"],
            )

            # Publish event
            await event_bus.publish(progress_event)

            # Log only at significant intervals (every 10% or every 10 files)
            if (
                progress["processed_files"] % 10 == 0
                or progress["processed_files"] == progress["total_files"]
                or int(progress.get("percentage", 0)) % 10 == 0
            ):
                logger.info(
                    "Indexing progress",
                    processed=progress["processed_files"],
                    total=progress["total_files"],
                    percentage=f"{progress.get('percentage', 0):.1f}%",
                    current_file=progress["current_file"],
                    task_id=task_id,
                )

        except Exception as e:
            # Don't fail indexing due to notification errors
            logger.warning("Failed to notify progress", error=str(e))

    # ============================================================================
    # ADDITIONAL METHODS FOR API
    # ============================================================================

    async def estimate_files(
        self,
        root: Path,
        patterns: List[str],
        exclude_patterns: List[str],
        respect_gitignore: bool = True,
        respect_acolyteignore: bool = True,
    ) -> int:
        """
        Estimate how many files would be indexed.

        PURPOSE: Dashboard UX - show estimated time before indexing.

        Args:
            root: Project root directory
            patterns: File patterns to include (*.py, *.js, etc.)
            exclude_patterns: Patterns to exclude
            respect_gitignore: Whether to respect .gitignore
            respect_acolyteignore: Whether to respect .acolyteignore

        Returns:
            Estimated number of files that would be indexed
        """
        try:
            start_time = utc_now()
            logger.info(
                "Estimating files for indexing", root=str(root), patterns_count=len(patterns)
            )

            # Collect files matching patterns
            candidate_files = []

            for pattern in patterns:
                if pattern.startswith("*."):
                    # Extension pattern: *.py -> **/*.py
                    ext = pattern[2:]
                    matches = list(root.rglob(f"*.{ext}"))
                    candidate_files.extend([str(f) for f in matches])
                else:
                    # Direct pattern
                    matches = list(root.rglob(pattern))
                    candidate_files.extend([str(f) for f in matches])

            # Remove duplicates
            candidate_files = list(set(candidate_files))

            # Apply filters (same logic as _filter_files but without detailed logs)
            estimated_count = 0

            for file_path in candidate_files:
                path = Path(file_path)

                # Verify it exists and is not a directory
                if not path.exists() or path.is_dir():
                    continue

                # Verify size
                try:
                    size_mb = path.stat().st_size / (1024 * 1024)
                    if size_mb > self.max_file_size_mb:
                        continue
                except OSError:
                    continue

                # Verify ignore patterns
                if self._should_ignore(str(path)):
                    continue

                # Verify supported extension
                if not self._is_supported_file(path):
                    continue

                estimated_count += 1

            logger.info(
                "File estimation completed",
                candidates=len(candidate_files),
                estimated=estimated_count,
                filter_rate=f"{(1 - estimated_count/max(len(candidate_files), 1))*100:.1f}%",
            )

            self.metrics.gauge("indexing.estimated_files", estimated_count)

            # Record timing
            elapsed_ms = (utc_now() - start_time).total_seconds() * 1000
            self.metrics.record("indexing.estimate_files_ms", elapsed_ms)

            return estimated_count

        except Exception as e:
            logger.error("Failed to estimate files", error=str(e))
            # Return conservative estimate in case of error
            return 100

    async def remove_file(self, file_path: str) -> bool:
        """
        Remove a file from the search index.

        PURPOSE: Keep index clean when files are removed from the project.

        Args:
            file_path: Path of the file to remove from index

        Returns:
            True if successfully removed, False otherwise
        """
        try:
            start_time = utc_now()
            logger.info("Removing file from index", file_path=file_path)

            if not self.weaviate or not WEAVIATE_AVAILABLE:
                logger.warning("Weaviate not available for file removal")
                return False

            # Find objects in Weaviate that correspond to this file
            try:
                # Query to find chunks for this file
                where_filter = {
                    "path": ["file_path"],
                    "operator": "Equal",
                    "valueText": file_path,
                }

                result = (
                    self.weaviate.query.get("CodeChunk", ["file_path"])
                    .with_where(where_filter)
                    .with_additional(["id"])
                    .do()
                )
                from typing import cast, List, Dict, Any

                chunks_to_delete = cast(
                    List[Dict[str, Any]], result.get("data", {}).get("Get", {}).get("CodeChunk", [])
                )
                logger.info("[UNTESTED PATH] Weaviate remove_file path executed")
                if chunks_to_delete:
                    deleted_count = 0
                    for chunk_data in chunks_to_delete:
                        chunk_id = chunk_data.get("_additional", {}).get("id")
                        if chunk_id:
                            try:
                                self.weaviate.data_object.delete(chunk_id, class_name="CodeChunk")
                                deleted_count += 1
                            except Exception as e:
                                logger.warning(
                                    "Failed to delete chunk", chunk_id=chunk_id, error=str(e)
                                )
                    logger.info(
                        "File removal completed",
                        file_path=file_path,
                        chunks_deleted=deleted_count,
                    )
                    self.metrics.increment("indexing.files_removed")
                    self.metrics.increment("indexing.chunks_removed", deleted_count)
                    elapsed_ms = (utc_now() - start_time).total_seconds() * 1000
                    self.metrics.record("indexing.remove_file_ms", elapsed_ms)
                    return deleted_count > 0
                else:
                    logger.info("No chunks found for file", file_path=file_path)
                    elapsed_ms = (utc_now() - start_time).total_seconds() * 1000
                    self.metrics.record("indexing.remove_file_ms", elapsed_ms)
                    return True

            except Exception as e:
                logger.error(
                    "Failed to query/delete from Weaviate", file_path=file_path, error=str(e)
                )
                return False

        except Exception as e:
            logger.error("Failed to remove file", file_path=file_path, error=str(e))
            return False

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get indexing statistics for the dashboard.

        PURPOSE: Show metrics in the web dashboard.

        Returns:
            Dict with indexing statistics:
            - total_files: Unique indexed files
            - total_chunks: Total chunks in Weaviate
            - languages: Distribution by language
            - chunk_types: Distribution by chunk type
            - last_indexed: Last indexing timestamp
            - index_size_estimate: Index size estimate
        """
        try:
            start_time = utc_now()
            logger.info("Getting indexing statistics")

            stats = {
                "total_files": 0,
                "total_chunks": 0,
                "languages": {},
                "chunk_types": {},
                "last_indexed": None,
                "index_size_estimate_mb": 0.0,
                "weaviate_available": WEAVIATE_AVAILABLE and self.weaviate is not None,
            }

            if not self.weaviate or not WEAVIATE_AVAILABLE:
                logger.warning("Weaviate not available for stats")
                return stats

            try:
                # Get total chunk count
                count_result = self.weaviate.query.aggregate("CodeChunk").with_meta_count().do()

                if "data" in count_result and "Aggregate" in count_result["data"]:
                    aggregate_data = count_result["data"]["Aggregate"].get("CodeChunk", [{}])[0]
                    stats["total_chunks"] = aggregate_data.get("meta", {}).get("count", 0)

                # Get distribution by language
                lang_result = (
                    self.weaviate.query.aggregate("CodeChunk")
                    .with_group_by_filter(["language"])
                    .with_meta_count()
                    .do()
                )
                from typing import cast, List, Dict, Any

                lang_groups = cast(
                    List[Dict[str, Any]],
                    lang_result.get("data", {}).get("Aggregate", {}).get("CodeChunk", []),
                )
                for group in lang_groups:
                    if "groupedBy" in group and "value" in group["groupedBy"]:
                        language = group["groupedBy"]["value"]
                        count = group.get("meta", {}).get("count", 0)
                        if language and count > 0:
                            stats["languages"][language] = count

                # Get distribution by chunk type
                type_result = (
                    self.weaviate.query.aggregate("CodeChunk")
                    .with_group_by_filter(["chunk_type"])
                    .with_meta_count()
                    .do()
                )
                type_groups = cast(
                    List[Dict[str, Any]],
                    type_result.get("data", {}).get("Aggregate", {}).get("CodeChunk", []),
                )
                for group in type_groups:
                    if "groupedBy" in group and "value" in group["groupedBy"]:
                        chunk_type = group["groupedBy"]["value"]
                        count = group.get("meta", {}).get("count", 0)
                        if chunk_type and count > 0:
                            stats["chunk_types"][chunk_type] = count

                # Get unique files (approximated by unique file_path)
                # Note: Weaviate doesn't have native DISTINCT, so we estimate
                if stats["total_chunks"] > 0:
                    # Estimation based on average chunks per file
                    avg_chunks_per_file = 10  # Conservative value
                    stats["total_files"] = max(1, stats["total_chunks"] // avg_chunks_per_file)

                # Get last indexing (from metrics if available)
                # For now, use current timestamp as placeholder
                stats["last_indexed"] = utc_now_iso()

                # Estimate index size (approximated)
                # Each chunk ~2KB average (content + metadata + vector)
                stats["index_size_estimate_mb"] = round((stats["total_chunks"] * 2) / 1024, 2)

                logger.info(
                    "Indexing stats retrieved",
                    total_chunks=stats["total_chunks"],
                    languages=len(stats["languages"]),
                    types=len(stats["chunk_types"]),
                )

                self.metrics.gauge("indexing.indexed_chunks_total", stats["total_chunks"])
                self.metrics.gauge("indexing.indexed_files_estimated", stats["total_files"])

            except Exception as e:
                logger.error("Failed to query Weaviate for stats", error=str(e))
                # Return partial stats instead of failing completely

            # Record timing
            elapsed_ms = (utc_now() - start_time).total_seconds() * 1000
            self.metrics.record("indexing.get_stats_ms", elapsed_ms)

            return stats

        except Exception as e:
            logger.error("Failed to get indexing stats", error=str(e))
            return {
                "total_files": 0,
                "total_chunks": 0,
                "languages": {},
                "chunk_types": {},
                "last_indexed": None,
                "index_size_estimate_mb": 0.0,
                "error": str(e),
            }

    async def rename_file(self, old_path: str, new_path: str) -> bool:
        """
        Update references of a renamed file in the index.

        PURPOSE: Preserve history when files are moved/renamed.

        Args:
            old_path: Previous file path
            new_path: New file path

        Returns:
            True if successfully updated, False otherwise
        """
        try:
            start_time = utc_now()
            logger.info("Renaming file in index", old_path=old_path, new_path=new_path)

            if not self.weaviate or not WEAVIATE_AVAILABLE:
                logger.warning("Weaviate not available for file renaming")
                return False

            # Find objects in Weaviate that correspond to the old file
            try:
                where_filter = {
                    "path": ["file_path"],
                    "operator": "Equal",
                    "valueText": old_path,
                }

                result = (
                    self.weaviate.query.get("CodeChunk", ["file_path"])
                    .with_where(where_filter)
                    .with_additional(["id"])
                    .do()
                )
                from typing import cast, List, Dict, Any

                chunks_to_update = cast(
                    List[Dict[str, Any]], result.get("data", {}).get("Get", {}).get("CodeChunk", [])
                )
                logger.info("[UNTESTED PATH] Weaviate rename_file path executed")
                if chunks_to_update:
                    updated_count = 0
                    for chunk_data in chunks_to_update:
                        chunk_id = chunk_data.get("_additional", {}).get("id")
                        if chunk_id:
                            try:
                                self.weaviate.data_object.update(
                                    data_object={"file_path": new_path},
                                    class_name="CodeChunk",
                                    uuid=chunk_id,
                                )
                                updated_count += 1
                            except Exception as e:
                                logger.warning(
                                    "Failed to update chunk", chunk_id=chunk_id, error=str(e)
                                )
                    logger.info(
                        "File rename completed",
                        old_path=old_path,
                        new_path=new_path,
                        chunks_updated=updated_count,
                    )
                    self.metrics.increment("indexing.files_renamed")
                    self.metrics.increment("indexing.chunks_updated", updated_count)
                    elapsed_ms = (utc_now() - start_time).total_seconds() * 1000
                    self.metrics.record("indexing.rename_file_ms", elapsed_ms)
                    return updated_count > 0
                else:
                    logger.info("No chunks found for old file path", old_path=old_path)
                    return True

            except Exception as e:
                logger.error(
                    "Failed to query/update Weaviate",
                    old_path=old_path,
                    new_path=new_path,
                    error=str(e),
                )
                return False

        except Exception as e:
            logger.error(
                "Failed to rename file", old_path=old_path, new_path=new_path, error=str(e)
            )
            return False

    def is_supported_file(self, path: Path) -> bool:
        """Check if the file is of a supported type (public method)."""
        return self._is_supported_file(path)

    def should_ignore(self, file_path: str) -> bool:
        """Check if a file should be ignored (public method)."""
        return self._should_ignore(file_path)

    def _generate_error_summary(self, errors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a human-readable summary of indexing errors."""
        summary = {"total_errors": len(errors), "by_type": {}, "by_file": {}, "sample_errors": []}

        # Categorize errors
        for error in errors:
            # By error type
            error_type = error.get("error_type", "Unknown")
            if error_type not in summary["by_type"]:
                summary["by_type"][error_type] = 0
            summary["by_type"][error_type] += 1

            # By file (if it's a file-level error)
            if "file" in error:
                file_path = error["file"]
                if file_path not in summary["by_file"]:
                    summary["by_file"][file_path] = []
                summary["by_file"][file_path].append(
                    {"error": error.get("error", "Unknown error"), "type": error_type}
                )

        # Include sample of first 5 errors for debugging
        summary["sample_errors"] = errors[:5]

        return summary

    @property
    def is_indexing(self):
        """Indica si el servicio está indexando actualmente."""
        return self._is_indexing

    async def _save_progress(self, task_id: str, progress_data: Dict[str, Any]):
        """Save indexing progress to runtime_state."""
        try:
            key = f"indexing_progress_{task_id}"
            success = await self._runtime_state.set_json(key, progress_data)
            if not success:
                logger.warning("Failed to save indexing progress", task_id=task_id)
        except Exception as e:
            # Not critical - indexing can continue without checkpoint
            logger.warning("Error saving indexing progress", task_id=task_id, error=str(e))

    async def _load_progress(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Load saved indexing progress."""
        try:
            key = f"indexing_progress_{task_id}"
            return await self._runtime_state.get_json(key)
        except Exception as e:
            logger.warning("Error loading indexing progress", task_id=task_id, error=str(e))
            return None

    async def _clear_progress(self, task_id: str):
        """Clear saved indexing progress."""
        try:
            key = f"indexing_progress_{task_id}"
            await self._runtime_state.delete(key)
        except Exception as e:
            logger.warning("Error clearing indexing progress", task_id=task_id, error=str(e))

    async def list_resumable_tasks(self) -> List[Dict[str, Any]]:
        """List all resumable indexing tasks."""
        try:
            keys = await self._runtime_state.list_keys("indexing_progress_")
            tasks = []

            for key in keys:
                task_id = key.replace("indexing_progress_", "")
                progress = await self._runtime_state.get_json(key)
                if progress and progress.get("status") == "in_progress":
                    tasks.append(
                        {
                            "task_id": task_id,
                            "started_at": progress.get("started_at"),
                            "total_files": progress.get("total_files", 0),
                            "processed_files": progress.get("processed_files", 0),
                            "pending_files": len(progress.get("files_pending", [])),
                            "last_checkpoint": progress.get("last_checkpoint"),
                        }
                    )

            return tasks
        except Exception as e:
            logger.error("Error listing resumable tasks", error=str(e))
            return []

    async def shutdown(self):
        """Gracefully shutdown the indexing service and cleanup resources."""
        logger.info("Shutting down IndexingService")

        # Shutdown worker pool if exists
        if self._worker_pool:
            try:
                await self._worker_pool.shutdown()
                self._worker_pool = None
                logger.info("Worker pool shutdown complete")
            except Exception as e:
                logger.error("Error shutting down worker pool", error=str(e))

        # Wait for any ongoing indexing to complete
        if self._is_indexing:
            logger.info("Waiting for ongoing indexing to complete...")
            # Give it max 30 seconds to complete
            for _ in range(30):
                if not self._is_indexing:
                    break
                await asyncio.sleep(1)

            if self._is_indexing:
                logger.warning("Indexing still in progress after 30s, forcing shutdown")

        logger.info("IndexingService shutdown complete")
