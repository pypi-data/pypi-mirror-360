"""
Test lazy loading of heavy modules in ACOLYTE.

This test ensures that heavy dependencies (torch, transformers, tree-sitter, etc.)
are NOT loaded until they are actually needed, keeping startup time fast.

CRITICAL: This test must pass to ensure ACOLYTE starts quickly.
"""

import sys
import time
import pytest
from pathlib import Path
from typing import List, Set
from unittest.mock import patch

# Heavy modules that should NOT be loaded on import
HEAVY_MODULES = [
    'torch',
    'transformers',
    'tree_sitter',
    'tree_sitter_languages',
    'weaviate',
    'ollama',
    'sentence_transformers',
    'unixcoder',
]

# Maximum acceptable import time in seconds
MAX_IMPORT_TIME = 0.5


def get_loaded_modules() -> Set[str]:
    """Get set of currently loaded module names."""
    return set(sys.modules.keys())


def check_heavy_modules() -> List[str]:
    """Check which heavy modules are currently loaded."""
    return [m for m in HEAVY_MODULES if m in sys.modules]


class TestLazyLoading:
    """Test that ACOLYTE uses lazy loading effectively."""

    def setup_method(self):
        """Clear ACOLYTE modules before each test."""
        # Clear all acolyte modules to test fresh imports
        modules_to_clear = [m for m in sys.modules if m.startswith('acolyte')]
        for module in modules_to_clear:
            del sys.modules[module]

    def test_basic_import_time(self):
        """Test that basic ACOLYTE import is fast."""
        start = time.time()
        import acolyte

        elapsed = time.time() - start

        assert (
            elapsed < MAX_IMPORT_TIME
        ), f"Import took {elapsed:.3f}s, exceeds limit of {MAX_IMPORT_TIME}s"

        # Check no heavy modules loaded
        heavy_loaded = check_heavy_modules()
        assert not heavy_loaded, f"Heavy modules loaded on import: {heavy_loaded}"

    def test_core_modules_lightweight(self):
        """Test that core modules don't load heavy dependencies."""
        from acolyte.core import Settings, generate_id
        from acolyte.core.logging import logger
        from acolyte.core.database import get_db_manager
        from acolyte.core.exceptions import AcolyteError

        heavy_loaded = check_heavy_modules()
        assert not heavy_loaded, f"Core modules loaded heavy deps: {heavy_loaded}"

    def test_models_lightweight(self):
        """Test that model classes don't load heavy dependencies."""
        from acolyte.models import Chunk, ChunkType, ChunkMetadata
        from acolyte.models.conversation import Message
        from acolyte.models.task_checkpoint import TaskCheckpoint

        heavy_loaded = check_heavy_modules()
        assert not heavy_loaded, f"Models loaded heavy deps: {heavy_loaded}"

    def test_services_import_lazy(self):
        """Test that importing services doesn't load heavy dependencies."""
        from acolyte.services import ChatService, ConversationService, TaskService, GitService

        heavy_loaded = check_heavy_modules()
        assert not heavy_loaded, f"Services import loaded heavy deps: {heavy_loaded}"

    def test_indexing_service_lazy(self):
        """Test that IndexingService doesn't load embeddings until used."""
        from acolyte.services import IndexingService

        heavy_loaded = check_heavy_modules()
        # Should not load torch/transformers
        assert 'torch' not in heavy_loaded, "IndexingService loaded torch"
        assert 'transformers' not in heavy_loaded, "IndexingService loaded transformers"

    def test_rag_modules_lazy(self):
        """Test that RAG modules are lazy."""
        from acolyte.rag import HybridSearch, ContextualCompressor
        from acolyte.rag.retrieval import SearchFilters, ScoredChunk

        heavy_loaded = check_heavy_modules()
        assert not heavy_loaded, f"RAG modules loaded heavy deps: {heavy_loaded}"

    def test_semantic_modules_lazy(self):
        """Test that semantic modules are lazy."""
        from acolyte.semantic import (
            Summarizer,
            TaskDetector,
            PromptBuilder,
            QueryAnalyzer,
            DecisionDetector,
        )

        heavy_loaded = check_heavy_modules()
        assert not heavy_loaded, f"Semantic modules loaded heavy deps: {heavy_loaded}"

    def test_dream_module_lazy(self):
        """Test that dream module is lazy."""
        from acolyte.dream import DreamOrchestrator, DreamState, create_dream_orchestrator

        heavy_loaded = check_heavy_modules()
        assert not heavy_loaded, f"Dream module loaded heavy deps: {heavy_loaded}"

    def test_embeddings_lazy_until_used(self):
        """Test that embeddings module delays loading until get_embeddings() is called."""
        # Import should not load models
        from acolyte.embeddings import EmbeddingVector, get_embeddings

        heavy_loaded = check_heavy_modules()
        assert 'torch' not in heavy_loaded, "Embeddings import loaded torch"
        assert 'transformers' not in heavy_loaded, "Embeddings import loaded transformers"

        # Only when get_embeddings() is called should models load
        # We mock it to avoid actually downloading models in tests
        with patch('acolyte.embeddings.unixcoder.UniXcoderEmbeddings') as mock_embedder:
            embedder = get_embeddings()
            assert mock_embedder.called or embedder is not None

    def test_chunking_lazy_until_used(self):
        """Test that chunking delays tree-sitter loading."""
        # Import should not load tree-sitter
        from acolyte.rag.chunking import ChunkerFactory

        heavy_loaded = check_heavy_modules()
        assert 'tree_sitter' not in heavy_loaded, "Import loaded tree_sitter"
        assert 'tree_sitter_languages' not in heavy_loaded, "Import loaded tree_sitter_languages"

        # Only when instantiated should it load
        factory = ChunkerFactory()
        heavy_loaded = check_heavy_modules()
        assert 'tree_sitter' in heavy_loaded, "ChunkerFactory didn't load tree_sitter"

    def test_cli_lightweight(self):
        """Test that CLI doesn't load heavy modules for help."""
        from acolyte.cli import cli

        heavy_loaded = check_heavy_modules()
        assert not heavy_loaded, f"CLI loaded heavy deps: {heavy_loaded}"

    def test_api_lightweight(self):
        """Test that API module is lightweight."""
        from acolyte.api import app

        heavy_loaded = check_heavy_modules()
        assert not heavy_loaded, f"API loaded heavy deps: {heavy_loaded}"

    def test_comprehensive_import_time(self):
        """Test that importing all common modules stays fast."""
        start = time.time()

        # Import everything a typical user might import
        import acolyte
        from acolyte import (
            ChatService,
            ConversationService,
            TaskService,
            HybridSearch,
            Settings,
            generate_id,
        )
        from acolyte.models import Chunk, Message
        from acolyte.semantic import Summarizer, PromptBuilder

        elapsed = time.time() - start

        assert elapsed < 1.0, f"Comprehensive import took {elapsed:.3f}s, should be < 1.0s"

        # These imports should not trigger heavy loads
        heavy_loaded = check_heavy_modules()
        expected_heavy = []  # None should be loaded

        unexpected = [m for m in heavy_loaded if m not in expected_heavy]
        assert not unexpected, f"Unexpected heavy modules loaded: {unexpected}"


@pytest.mark.benchmark
class TestLazyLoadingPerformance:
    """Performance benchmarks for lazy loading."""

    def test_import_performance(self, benchmark):
        """Benchmark ACOLYTE import time."""

        def import_acolyte():
            # Clear module first
            if 'acolyte' in sys.modules:
                del sys.modules['acolyte']
            import acolyte

            return acolyte

        result = benchmark(import_acolyte)
        assert result is not None

        # Check benchmark stats
        assert (
            benchmark.stats['mean'] < 0.1
        ), f"Mean import time {benchmark.stats['mean']:.3f}s exceeds 0.1s"
