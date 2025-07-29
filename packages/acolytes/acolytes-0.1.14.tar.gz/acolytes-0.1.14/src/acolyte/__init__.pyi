"""Stub file for acolyte package to help with type checking and IDE support."""

from typing import Any

# Version info
__version__: str
__version_info__: tuple[int, int, int]
__author__: str
__license__: str

# Core components
from acolyte.core import (
    logger as logger,
    Settings as Settings,
    get_db_manager as get_db_manager,
    generate_id as generate_id,
    AcolyteError as AcolyteError,
    ValidationError as ValidationError,
    ConfigurationError as ConfigurationError,
    NotFoundError as NotFoundError,
    ExternalServiceError as ExternalServiceError,
)

# Services
from acolyte.services import (
    ChatService as ChatService,
    ConversationService as ConversationService,
    TaskService as TaskService,
    GitService as GitService,
    IndexingService as IndexingService,
    ReindexService as ReindexService,
)

# Models
from acolyte.models import (
    Role as Role,
    Message as Message,
    ChatRequest as ChatRequest,
    ChatResponse as ChatResponse,
    Choice as Choice,
    Usage as Usage,
    Conversation as Conversation,
    TaskCheckpoint as TaskCheckpoint,
    TechnicalDecision as TechnicalDecision,
    ChunkType as ChunkType,
    ChunkMetadata as ChunkMetadata,
    Chunk as Chunk,
    DreamState as DreamState,
    DreamInsight as DreamInsight,
    OptimizationStatus as OptimizationStatus,
)

# RAG components
from acolyte.rag import HybridSearch as HybridSearch
from acolyte.rag.chunking import ChunkerFactory as ChunkerFactory

# Semantic components
from acolyte.semantic import (
    Summarizer as Summarizer,
    PromptBuilder as PromptBuilder,
    QueryAnalyzer as QueryAnalyzer,
    TaskDetector as TaskDetector,
    DecisionDetector as DecisionDetector,
    ReferenceResolver as ReferenceResolver,
)

# Dream system
from acolyte.dream import create_dream_orchestrator as create_dream_orchestrator

# Functions
def get_app() -> Any: ...
def create_app() -> Any: ...
def get_config() -> Settings: ...
def check_version() -> dict[str, str]: ...
def is_ready() -> bool: ...

__all__: list[str]
