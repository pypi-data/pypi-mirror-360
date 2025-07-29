"""
Re-ranking with Cross-Encoder to improve accuracy.

Cross-Encoders process (query, document) pairs directly
to produce more accurate relevance scores than embeddings.
"""

from typing import List, Tuple, Optional, TYPE_CHECKING
from collections import OrderedDict
import time
import threading
import hashlib

from acolyte.core.exceptions import ExternalServiceError
from acolyte.embeddings.types import RerankerMetricsSummary, MetricsProvider
from acolyte.models.chunk import Chunk

if TYPE_CHECKING:
    import torch
    from acolyte.core.secure_config import Settings


class CrossEncoderReranker:
    """Re-ranker using cross-encoder to improve accuracy.

    Cross-Encoders are different from traditional embedding models:
    - They do not generate embeddings
    - They process (query, document) pairs directly
    - They produce a more accurate relevance score
    - They are slower but more accurate for re-ranking

    Typical flow:
    1. Initial search with embeddings (fast, 100+ results)
    2. Re-ranking with CrossEncoder (slow but accurate, top 10-20)
    """

    def __init__(self, model_name: Optional[str] = None, metrics: Optional[MetricsProvider] = None):
        """Initializes the re-ranker with lazy loading.

        Args:
            model_name: Hugging Face model to use. If None, it is read from
                        configuration. Defaults to ms-marco-MiniLM-L-6-v2.
            metrics: Optional metrics provider. If not provided,
                     uses the module singleton if enabled.
        """
        # Store params for lazy initialization
        self._model_name_override = model_name
        self._metrics_override = metrics

        # Lazy loaded attributes
        self._config = None
        self._metrics = None
        self._model_name = None

        # Model state
        self._model = None
        self._tokenizer = None
        self._device = None
        self._device_lock = threading.Lock()

        # Cache for query-candidate pairs (using OrderedDict for LRU O(1))
        self._pair_cache: OrderedDict[str, float] = OrderedDict()
        self._cache_max_size = 5000  # Smaller than embeddings because it's more specific

        # Will be loaded from config when needed
        self._batch_size = None

    @property
    def config(self) -> 'Settings':
        """Lazy load config."""
        if self._config is None:
            from acolyte.core.secure_config import Settings

            self._config = Settings()
        return self._config

    @property
    def model_name(self) -> str:
        """Lazy load model name."""
        if self._model_name is None:
            if self._model_name_override is not None:
                self._model_name = self._model_name_override
            else:
                self._model_name = self.config.get(
                    "embeddings.reranker_model", "cross-encoder/ms-marco-MiniLM-L-6-v2"
                )
        return self._model_name

    @property
    def metrics(self) -> Optional[MetricsProvider]:
        """Lazy load metrics."""
        if self._metrics is None:
            if self._metrics_override is not None:
                self._metrics = self._metrics_override
            else:
                from acolyte.embeddings import get_embeddings_metrics

                self._metrics = get_embeddings_metrics()
        return self._metrics

    @property
    def batch_size(self) -> int:
        """Lazy load batch size."""
        if self._batch_size is None:
            self._batch_size = self.config.get("embeddings.reranker_batch_size", 32)
        return self._batch_size

    @property
    def torch(self):
        """Lazy load torch module."""
        if not hasattr(self, '_torch'):
            try:
                import torch

                self._torch = torch
            except ImportError:
                error = ExternalServiceError(
                    "PyTorch is required for reranker",
                    context={"module": "torch"},
                )
                error.add_suggestion("pip install torch")
                error.add_suggestion("pip install acolyte[ml]")
                raise error
        return self._torch

    @property
    def transformers(self):
        """Lazy load transformers module."""
        if not hasattr(self, '_transformers'):
            try:
                import transformers

                self._transformers = transformers
            except ImportError:
                error = ExternalServiceError(
                    "Transformers is required for reranker",
                    context={"module": "transformers"},
                )
                error.add_suggestion("pip install transformers")
                error.add_suggestion("pip install acolyte[ml]")
                raise error
        return self._transformers

    @property
    def device(self) -> 'torch.device':
        """Uses the same device as the embeddings model with thread safety."""
        if self._device is None:
            with self._device_lock:
                # Double-check locking pattern
                if self._device is None:
                    torch_module = self.torch  # Lazy load here
                    device_config = self.config.get("embeddings.device", "auto")

                    if device_config == "auto":
                        self._device = torch_module.device(
                            "cuda" if torch_module.cuda.is_available() else "cpu"
                        )
                    else:
                        self._device = torch_module.device(device_config)

        return self._device

    def _load_model(self):
        """Loads the CrossEncoder model when needed.

        Uses AutoModelForSequenceClassification which is the correct type
        for ranking cross-encoders.
        """
        if self._model is not None:
            return

        # Lazy import logger
        from acolyte.core.logging import logger

        logger.info("Loading CrossEncoder", model_name=self.model_name)
        start_time = time.time()

        try:
            # Lazy load transformers
            AutoTokenizer = self.transformers.AutoTokenizer
            AutoModelForSequenceClassification = (
                self.transformers.AutoModelForSequenceClassification
            )

            # Load tokenizer and model
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self._model = AutoModelForSequenceClassification.from_pretrained(self.model_name)

            # Move to appropriate device
            self._model.to(self.device)
            self._model.eval()

            load_time = (time.time() - start_time) * 1000
            logger.info("CrossEncoder loaded", load_time_ms=load_time)
            if self.metrics:
                self.metrics.record_operation("crossencoder_load", load_time)

        except Exception as e:
            error = ExternalServiceError(
                f"Error loading CrossEncoder {self.model_name}",
                context={"model": self.model_name, "device": str(self.device), "error": str(e)},
            )
            error.add_suggestion("Check model name")
            error.add_suggestion("Check internet connection")
            error.add_suggestion("Try a smaller model: cross-encoder/ms-marco-TinyBERT-L-2-v2")
            logger.error("Error loading CrossEncoder", error=error.to_dict())
            raise error

    def _generate_cache_key(self, query: str, candidate: str) -> str:
        """Generates a unique key for the query-candidate pair."""
        # Include length to reduce collisions
        key = f"{len(query)}:{query[:500]}||{len(candidate)}:{candidate[:500]}"
        return hashlib.sha256(key.encode()).hexdigest()[:16]  # SHA256 more secure

    def _score_pairs(self, pairs: List[List[str]]) -> List[float]:
        """Calculates scores for a list of [query, candidate] pairs.

        Args:
            pairs: List of [query, candidate] to evaluate

        Returns:
            List of relevance scores (typically 0-1)
        """
        if not pairs:
            return []

        # Ensure model and tokenizer are loaded
        self._load_model()
        if self._tokenizer is None:
            raise ExternalServiceError("Tokenizer not initialized in CrossEncoderReranker")
        if self._model is None:
            raise ExternalServiceError("Model not initialized in CrossEncoderReranker")

        # Tokenize all pairs
        inputs = self._tokenizer(
            pairs, padding=True, truncation=True, max_length=512, return_tensors="pt"
        ).to(self.device)

        # Get torch via property
        torch_module = self.torch

        # Get scores
        with torch_module.no_grad():
            outputs = self._model(**inputs)
            # Cross-encoders typically have a single output (score)
            if outputs.logits.shape[-1] == 1:
                # Regression model (direct score)
                scores = outputs.logits.squeeze(-1).cpu().numpy()
            else:
                # Classification model (needs softmax)
                # Take the probability of the "relevant" class (typically index 1)
                scores = torch_module.softmax(outputs.logits, dim=-1)[:, 1].cpu().numpy()

        return scores.tolist()

    def rerank(
        self, query: str, candidates: List[str], top_k: int = 10, return_scores: bool = True
    ) -> List[Tuple[str, float]]:
        """Re-ranks candidates by relevance to the query.

        This is the main method that significantly improves the accuracy
        of search results at the cost of higher latency.

        Args:
            query: User query
            candidates: List of candidates to re-rank (ideally 20-100)
            top_k: Number of top results to return
            return_scores: Whether to include scores in the result

        Returns:
            List of tuples (candidate, score) sorted by descending relevance

        Example:
            >>> reranker = CrossEncoderReranker()
            >>> candidates = ["def login(user)", "class User", "def logout()"]
            >>> results = reranker.rerank("user authentication", candidates, top_k=2)
            >>> # results = [("def login(user)", 0.92), ("def logout()", 0.75)]
        """
        if not candidates:
            return []

        start_time = time.time()

        # Limit candidates to avoid OOM
        max_candidates = 100
        if len(candidates) > max_candidates:
            # Lazy import logger
            from acolyte.core.logging import logger

            logger.warning(
                "Slow re-ranking",
                candidate_count=len(candidates),
                warning_message=f"Too many candidates ({len(candidates)}), processing only the first {max_candidates}",
            )
            candidates = candidates[:max_candidates]

        # Load model if needed
        self._load_model()

        # Separate candidates into cached and non-cached
        pairs_to_score = []
        pair_indices = []
        scores = [0.0] * len(candidates)

        for i, candidate in enumerate(candidates):
            cache_key = self._generate_cache_key(query, candidate)

            if cache_key in self._pair_cache:
                scores[i] = self._pair_cache[cache_key]
                # Move to end for LRU (most recently used)
                self._pair_cache.move_to_end(cache_key)
                if self.metrics:
                    self.metrics.record_cache_hit()
            else:
                pairs_to_score.append([query, candidate])
                pair_indices.append(i)
                if self.metrics:
                    self.metrics.record_cache_miss()

        # Calculate scores for non-cached
        if pairs_to_score:
            # Process in batches if many
            batch_size = self.batch_size
            new_scores = []

            for i in range(0, len(pairs_to_score), batch_size):
                batch = pairs_to_score[i : i + batch_size]
                batch_scores = self._score_pairs(batch)
                new_scores.extend(batch_scores)

            # Update scores and cache
            for idx, score in zip(pair_indices, new_scores):
                scores[idx] = score

                # Update cache
                cache_key = self._generate_cache_key(query, candidates[idx])

                # LRU eviction O(1) - remove only as needed to make space
                if (
                    len(self._pair_cache) >= self._cache_max_size
                    and cache_key not in self._pair_cache
                ):
                    # Remove least recently used
                    self._pair_cache.popitem(last=False)

                self._pair_cache[cache_key] = score
                # Move to end for LRU (most recently used)
                if cache_key in self._pair_cache:
                    self._pair_cache.move_to_end(cache_key)

        # Combine candidates with scores
        results = list(zip(candidates, scores))

        # Sort by descending score
        results.sort(key=lambda x: x[1], reverse=True)

        # Take only top_k
        results = results[:top_k]

        # Metrics
        latency = (time.time() - start_time) * 1000
        if self.metrics:
            self.metrics.record_operation("crossencoder_rerank", latency)

        # Log if it was very slow
        if latency > 1000:  # > 1 second
            # Lazy import logger
            from acolyte.core.logging import logger

            logger.warning("Slow re-ranking", latency_ms=latency, candidate_count=len(candidates))

        if not return_scores:
            return [(candidate, 0.0) for candidate, _ in results]

        return results

    def rerank_chunks(
        self, query: str, chunks: List[Chunk], top_k: int = 10
    ) -> List[Tuple[Chunk, float]]:
        """Re-ranks Chunks keeping the complete object.

        Convenient version that works directly with Chunk objects.

        Args:
            query: User query
            chunks: List of Chunks to re-rank
            top_k: Number of top results

        Returns:
            List of tuples (Chunk, score) sorted by relevance
        """
        if not chunks:
            return []

        # Extract content from chunks
        contents = [chunk.content for chunk in chunks]

        # Re-rank contents
        reranked_contents = self.rerank(query, contents, top_k=len(chunks))

        # Create mapping from content to all chunks with that content
        content_to_chunks = {}
        for chunk in chunks:
            if chunk.content not in content_to_chunks:
                content_to_chunks[chunk.content] = []
            content_to_chunks[chunk.content].append(chunk)

        # Rebuild with original chunks preserving order
        results = []
        seen_chunks = set()
        for content, score in reranked_contents:
            if content in content_to_chunks:
                # Add all chunks with this content that we haven't seen yet
                for chunk in content_to_chunks[content]:
                    if chunk not in seen_chunks:
                        results.append((chunk, score))
                        seen_chunks.add(chunk)

        return results[:top_k]

    def get_metrics_summary(self) -> RerankerMetricsSummary:
        """Returns metrics summary of the re-ranker.

        Returns:
            RerankerMetricsSummary with information about the re-ranker's state
        """
        base_info = {
            "model_loaded": self._model is not None,
            "cache_size": len(self._pair_cache),
            "device": str(self.device) if self._device else "not_set",
            "metrics_enabled": self.metrics is not None,
        }

        if self.metrics:
            if hasattr(self.metrics, "_cache_hits") and hasattr(self.metrics, "_cache_misses"):
                total_ops = self.metrics._cache_hits + self.metrics._cache_misses  # type: ignore[attr-defined]
            else:
                total_ops = 0
            base_info.update(
                {
                    "cache_hit_rate": self.metrics.get_cache_hit_rate(),
                    "total_rerank_operations": total_ops,
                }
            )

        from typing import cast

        return cast(RerankerMetricsSummary, base_info)
