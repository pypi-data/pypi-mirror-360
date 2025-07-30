"""
Acolyte Core module.

Exports the fundamental system components using lazy loading for heavy modules.
"""

from acolyte.core.id_generator import IDGenerator, generate_id, is_valid_id
from acolyte.core.exceptions import (
    # Python exceptions
    AcolyteError,
    DatabaseError,
    VectorStaleError,
    ConfigurationError,
    ValidationError,
    NotFoundError,
    ExternalServiceError,
    VersionIncompatibilityError,
    # HTTP response models
    ErrorType,
    ErrorDetail,
    ErrorResponse,
    # Helper functions
    validation_error,
    not_found_error,
    internal_error,
    external_service_error,
    configuration_error,
    from_exception,
)
from typing import TYPE_CHECKING, Any

# Remove direct import and singleton creation
# Settings will be loaded lazily like other modules

# Constants that don't require Settings
ID_LENGTH = 32  # Hex ID length

# Settings-dependent constants will be loaded lazily
_lazy_constants: dict[str, Any] = {
    "OLLAMA_MODEL": None,
    "DEFAULT_BIND_HOST": None,
    "DEFAULT_BIND_PORT": None,
    "settings": None,
}

# Lazy loading for heavy modules
_lazy_modules = {
    # Configuration (yaml is heavy)
    "Settings": "acolyte.core.secure_config",
    "ConfigValidator": "acolyte.core.secure_config",
    # Database (sqlite3 is heavy)
    "DatabaseManager": "acolyte.core.database",
    "InsightStore": "acolyte.core.database",
    "FetchType": "acolyte.core.database",
    "QueryResult": "acolyte.core.database",
    "StoreResult": "acolyte.core.database",
    "get_db_manager": "acolyte.core.database",
    # Logging (loguru is heavy)
    "AsyncLogger": "acolyte.core.logging",
    "SensitiveDataMasker": "acolyte.core.logging",
    "PerformanceLogger": "acolyte.core.logging",
    "logger": "acolyte.core.logging",
    # Events
    "EventType": "acolyte.core.events",
    "Event": "acolyte.core.events",
    "EventBus": "acolyte.core.events",
    "WebSocketManager": "acolyte.core.events",
    # LLM (httpx is heavy)
    "OllamaClient": "acolyte.core.ollama",
    # Chunking
    "ChunkingStrategy": "acolyte.core.chunking_config",
    "ChunkingConfig": "acolyte.core.chunking_config",
    "StrategyConfig": "acolyte.core.chunking_config",
    "ValidationResult": "acolyte.core.chunking_config",
    # Tokens
    "TokenEncoder": "acolyte.core.token_counter",
    "OllamaEncoder": "acolyte.core.token_counter",
    "SmartTokenCounter": "acolyte.core.token_counter",
    "TokenBudgetManager": "acolyte.core.token_counter",
    "TokenCount": "acolyte.core.token_counter",
    "ContextSplit": "acolyte.core.token_counter",
    "TruncateStrategy": "acolyte.core.token_counter",
    # Tracing
    "tracer": "acolyte.core.tracing",
    "metrics": "acolyte.core.tracing",
    "LocalTracer": "acolyte.core.tracing",
    "MetricsCollector": "acolyte.core.tracing",
    # Runtime state
    "RuntimeStateManager": "acolyte.core.runtime_state",
    "get_runtime_state": "acolyte.core.runtime_state",
}

# Cache for loaded modules
_module_cache = {}


def __getattr__(name):  # type: ignore
    """Lazy load heavy modules and settings-dependent constants only when accessed."""
    # Check for lazy constants first
    if name in _lazy_constants:
        if _lazy_constants[name] is None:
            # Load settings lazily
            from acolyte.core.secure_config import Settings

            if _lazy_constants["settings"] is None:
                _lazy_constants["settings"] = Settings()

            settings = _lazy_constants["settings"]

            # Load the specific constant
            if name == "OLLAMA_MODEL":
                _lazy_constants[name] = settings.get("model.name", "acolyte:latest")
            elif name == "DEFAULT_BIND_HOST":
                _lazy_constants[name] = settings.get("ports.backend_host", "127.0.0.1")
            elif name == "DEFAULT_BIND_PORT":
                _lazy_constants[name] = settings.get("ports.backend", 8000)
            elif name == "settings":
                pass  # Already loaded above

        # Cache it in globals for next access
        value = _lazy_constants[name]
        globals()[name] = value
        return value

    # Original lazy module loading
    if name in _lazy_modules:
        module_path = _lazy_modules[name]

        # Check cache first
        if module_path not in _module_cache:
            import importlib

            _module_cache[module_path] = importlib.import_module(module_path)

        module = _module_cache[module_path]

        # Get the attribute from the module
        parts = name.split('.')
        obj = module
        for part in parts:
            obj = getattr(obj, part)

        # Cache it in globals for next access
        globals()[name] = obj
        return obj

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# Public exports list
__all__ = [
    # Configuration
    "Settings",
    "ConfigValidator",
    # Database
    "DatabaseManager",
    "InsightStore",
    "FetchType",
    "QueryResult",
    "StoreResult",
    "get_db_manager",
    # Exceptions (already imported)
    "AcolyteError",
    "DatabaseError",
    "VectorStaleError",
    "ConfigurationError",
    "ValidationError",
    "NotFoundError",
    "ExternalServiceError",
    "VersionIncompatibilityError",
    # HTTP error models
    "ErrorType",
    "ErrorDetail",
    "ErrorResponse",
    # Error helper functions
    "validation_error",
    "not_found_error",
    "internal_error",
    "external_service_error",
    "configuration_error",
    "from_exception",
    # Logging
    "AsyncLogger",
    "SensitiveDataMasker",
    "PerformanceLogger",
    "logger",
    # Eventos
    "EventType",
    "Event",
    "EventBus",
    "WebSocketManager",
    # LLM
    "OllamaClient",
    # Chunking
    "ChunkingStrategy",
    "ChunkingConfig",
    "StrategyConfig",
    "ValidationResult",
    # Tokens
    "TokenEncoder",
    "OllamaEncoder",
    "SmartTokenCounter",
    "TokenBudgetManager",
    "TokenCount",
    "ContextSplit",
    "TruncateStrategy",
    # Tracing
    "tracer",
    "metrics",
    "LocalTracer",
    "MetricsCollector",
    # Runtime state
    "RuntimeStateManager",
    "get_runtime_state",
    # Generador de IDs (already imported)
    "IDGenerator",
    "generate_id",
    "is_valid_id",
    # Constants
    "OLLAMA_MODEL",
    "DEFAULT_BIND_HOST",
    "DEFAULT_BIND_PORT",
    "ID_LENGTH",
    "settings",
]

if TYPE_CHECKING:
    Settings: type = None  # type: ignore
    DatabaseManager: type = None  # type: ignore
    InsightStore: type = None  # type: ignore
    FetchType: type = None  # type: ignore
    QueryResult: type = None  # type: ignore
    StoreResult: type = None  # type: ignore
    get_db_manager: type = None  # type: ignore
    AsyncLogger: type = None  # type: ignore
    ConfigValidator: type = None  # type: ignore
    SensitiveDataMasker: type = None  # type: ignore
    PerformanceLogger: type = None  # type: ignore
    logger: type = None  # type: ignore
    EventType: type = None  # type: ignore
    Event: type = None  # type: ignore
    EventBus: type = None  # type: ignore
    WebSocketManager: type = None  # type: ignore
    OllamaClient: type = None  # type: ignore
    ChunkingStrategy: type = None  # type: ignore
    ChunkingConfig: type = None  # type: ignore
    StrategyConfig: type = None  # type: ignore
    ValidationResult: type = None  # type: ignore
    TokenEncoder: type = None  # type: ignore
    OllamaEncoder: type = None  # type: ignore
    SmartTokenCounter: type = None  # type: ignore
    TokenBudgetManager: type = None  # type: ignore
    TokenCount: type = None  # type: ignore
    ContextSplit: type = None  # type: ignore
    TruncateStrategy: type = None  # type: ignore
    tracer: type = None  # type: ignore
    metrics: type = None  # type: ignore
    LocalTracer: type = None  # type: ignore
    MetricsCollector: type = None  # type: ignore
    RuntimeStateManager: type = None  # type: ignore
    get_runtime_state: type = None  # type: ignore
    OLLAMA_MODEL: type = None  # type: ignore
    DEFAULT_BIND_HOST: type = None  # type: ignore
    DEFAULT_BIND_PORT: type = None  # type: ignore
    settings: type = None  # type: ignore

# Assign VersionIncompatibilityError to the global namespace
VersionIncompatibilityError = VersionIncompatibilityError
