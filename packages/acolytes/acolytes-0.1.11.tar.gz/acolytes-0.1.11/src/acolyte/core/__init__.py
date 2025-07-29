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
from acolyte.core.secure_config import Settings

# Important constants (no imports needed)
settings = Settings()
OLLAMA_MODEL = settings.get("model.name", "acolyte:latest")
DEFAULT_BIND_HOST = settings.get("ports.backend_host", "127.0.0.1")
DEFAULT_BIND_PORT = settings.get("ports.backend", 8000)
ID_LENGTH = 32  # Hex ID length

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
    """Lazy load heavy modules only when accessed."""
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
]

# Dummies para linters/type checkers (no rompen lazy loading)
DatabaseManager = None  # type: ignore
InsightStore = None  # type: ignore
FetchType = None  # type: ignore
QueryResult = None  # type: ignore
StoreResult = None  # type: ignore
get_db_manager = None  # type: ignore
AsyncLogger = None  # type: ignore
ConfigValidator = None  # type: ignore
SensitiveDataMasker = None  # type: ignore
PerformanceLogger = None  # type: ignore
logger = None  # type: ignore
EventType = None  # type: ignore
Event = None  # type: ignore
EventBus = None  # type: ignore
WebSocketManager = None  # type: ignore
OllamaClient = None  # type: ignore
ChunkingStrategy = None  # type: ignore
ChunkingConfig = None  # type: ignore
StrategyConfig = None  # type: ignore
ValidationResult = None  # type: ignore
TokenEncoder = None  # type: ignore
OllamaEncoder = None  # type: ignore
SmartTokenCounter = None  # type: ignore
TokenBudgetManager = None  # type: ignore
TokenCount = None  # type: ignore
ContextSplit = None  # type: ignore
TruncateStrategy = None  # type: ignore
tracer = None  # type: ignore
metrics = None  # type: ignore
LocalTracer = None  # type: ignore
MetricsCollector = None  # type: ignore
RuntimeStateManager = None  # type: ignore
get_runtime_state = None  # type: ignore
