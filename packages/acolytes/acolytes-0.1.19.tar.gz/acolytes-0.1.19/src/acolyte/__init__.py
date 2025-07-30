"""
ACOLYTE - Your Private AI Programming Assistant with Infinite Memory.

Local and private AI copilot powered by Qwen-2.5-Coder through Ollama.
"""

from typing import Any

# Version is lightweight, keep it
from acolyte._version import __version__, __version_info__

__author__ = "Bextia"
__license__ = "BSL"

# Lazy loading implementation to avoid heavy imports
_lazy_imports = {
    # Core - these are already lazy-loaded in core.__init__
    "logger": "acolyte.core",
    "Settings": "acolyte.core",
    "get_db_manager": "acolyte.core",
    "generate_id": "acolyte.core",
    "AcolyteError": "acolyte.core",
    "ValidationError": "acolyte.core",
    "ConfigurationError": "acolyte.core",
    "NotFoundError": "acolyte.core",
    "ExternalServiceError": "acolyte.core",
    # Services - HEAVY, especially ChatService
    "ChatService": "acolyte.services",
    "ConversationService": "acolyte.services",
    "TaskService": "acolyte.services",
    "GitService": "acolyte.services",
    "IndexingService": "acolyte.services",
    "ReindexService": "acolyte.services",
    # Models - relatively lightweight
    "Role": "acolyte.models",
    "Message": "acolyte.models",
    "ChatRequest": "acolyte.models",
    "ChatResponse": "acolyte.models",
    "Choice": "acolyte.models",
    "Usage": "acolyte.models",
    "Conversation": "acolyte.models",
    "TaskCheckpoint": "acolyte.models",
    "TechnicalDecision": "acolyte.models",
    "ChunkType": "acolyte.models",
    "ChunkMetadata": "acolyte.models",
    "Chunk": "acolyte.models",
    "DreamState": "acolyte.models",
    "DreamInsight": "acolyte.models",
    "OptimizationStatus": "acolyte.models",
    # RAG components
    "HybridSearch": "acolyte.rag",
    "ChunkerFactory": "acolyte.rag.chunking",
    # Semantic components
    "Summarizer": "acolyte.semantic",
    "PromptBuilder": "acolyte.semantic",
    "QueryAnalyzer": "acolyte.semantic",
    "TaskDetector": "acolyte.semantic",
    "DecisionDetector": "acolyte.semantic",
    "ReferenceResolver": "acolyte.semantic",
    # Dream system
    "create_dream_orchestrator": "acolyte.dream",
}

# Cache for loaded attributes
_import_cache: dict[str, Any] = {}


def __getattr__(name):  # type: ignore
    """Lazy load modules only when accessed."""
    if name in _lazy_imports:
        # Check cache first
        if name in _import_cache:
            return _import_cache[name]

        # Import the module
        module_path = _lazy_imports[name]

        # Import module
        import importlib

        module = importlib.import_module(module_path)

        # Get the specific attribute
        try:
            attr = getattr(module, name)
        except AttributeError:
            # If not found, it might be a submodule import
            if '.' in name:
                # For nested imports like rag.chunking
                submodule = importlib.import_module(f"{module_path}.{name.split('.')[-1]}")
                attr = submodule
            else:
                raise

        # Cache it
        _import_cache[name] = attr
        return attr

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# Lazy import function for API
def get_app():
    """
    Get the ACOLYTE FastAPI application (lazy import).

    This function imports the API only when needed, preventing
    initialization logs from appearing during CLI help commands.
    """
    from acolyte.api import app

    return app


# Package metadata
__all__ = [
    # Version info
    "__version__",
    "__version_info__",
    "__author__",
    "__license__",
    # Core
    "logger",
    "Settings",
    "get_db_manager",
    "generate_id",
    # Exceptions
    "AcolyteError",
    "ValidationError",
    "ConfigurationError",
    "NotFoundError",
    "ExternalServiceError",
    # API - Use get_app() instead of direct import
    "get_app",
    # Services
    "ChatService",
    "ConversationService",
    "TaskService",
    "GitService",
    "IndexingService",
    "ReindexService",
    # Models
    "Role",
    "Message",
    "ChatRequest",
    "ChatResponse",
    "Choice",
    "Usage",
    "Conversation",
    "TaskCheckpoint",
    "TechnicalDecision",
    "ChunkType",
    "ChunkMetadata",
    "Chunk",
    "DreamState",
    "DreamInsight",
    "OptimizationStatus",
    # RAG
    "HybridSearch",
    "ChunkerFactory",
    # Semantic
    "Summarizer",
    "PromptBuilder",
    "QueryAnalyzer",
    "TaskDetector",
    "DecisionDetector",
    "ReferenceResolver",
    # Dream
    "create_dream_orchestrator",
]


# Convenience function for quick setup
def create_app():
    """
    Create and return the ACOLYTE FastAPI application.

    Example:
        >>> app = create_app()
        >>> # Use with uvicorn
        >>> import uvicorn
        >>> uvicorn.run(app, host="127.0.0.1", port=8000)

    Returns:
        FastAPI: Configured application instance
    """
    return get_app()


# Quick access to configuration
def get_config():
    """
    Get the current ACOLYTE configuration.

    Example:
        >>> config = get_config()
        >>> print(config.get("model.name"))
        'qwen2.5-coder:3b'

    Returns:
        Settings: Configuration instance
    """
    # Import Settings only when needed
    from acolyte.core import Settings

    return Settings()


# Version check
def check_version():
    """
    Check ACOLYTE version and dependencies.

    Example:
        >>> info = check_version()
        >>> print(f"ACOLYTE {info['acolyte']} on Python {info['python']}")

    Returns:
        dict: Version information including:
            - acolyte: ACOLYTE version
            - python: Python version
            - platform: OS platform
            - torch: PyTorch version (if installed)
            - weaviate: Weaviate client version (if installed)
    """
    import sys
    import platform

    try:
        import torch

        torch_version = torch.__version__
    except ImportError:
        torch_version = "Not installed"

    try:
        import weaviate

        weaviate_version = weaviate.__version__
    except ImportError:
        weaviate_version = "Not installed"

    return {
        "acolyte": __version__,
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": platform.platform(),
        "torch": torch_version,
        "weaviate": weaviate_version,
    }


def is_ready():
    """
    Check if ACOLYTE is ready to use.

    Example:
        >>> if is_ready():
        >>>     print("ACOLYTE is ready!")
        >>> else:
        >>>     print("ACOLYTE needs configuration")

    Returns:
        bool: True if ACOLYTE is properly configured and ready
    """
    try:
        # Import only when needed
        from acolyte.core import get_db_manager, Settings

        # Check database
        db = get_db_manager()
        # Verify database is accessible by checking the connection path exists
        _ = db.db_path

        # Check configuration
        config = Settings()
        # Verify configuration is valid by accessing a required setting
        model_name = config.get("model.name")
        return model_name is not None
    except Exception:
        return False
