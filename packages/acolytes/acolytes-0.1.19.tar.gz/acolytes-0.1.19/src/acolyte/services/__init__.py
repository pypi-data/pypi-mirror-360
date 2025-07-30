"""
ACOLYTE Services module.

Business logic that coordinates internal components.
DOES NOT expose HTTP endpoints.
"""

# Lazy imports to avoid loading heavy modules
from acolyte.services.conversation_service import ConversationService
from acolyte.services.task_service import TaskService
from acolyte.services.chat_service import ChatService
from acolyte.services.git_service import GitService

# These services load heavy modules - import on demand
# from acolyte.services.indexing_service import IndexingService
# from acolyte.services.reindex_service import ReindexService


def __getattr__(name):
    """Lazy load heavy services."""
    if name == "IndexingService":
        from acolyte.services.indexing_service import IndexingService

        return IndexingService
    elif name == "ReindexService":
        from acolyte.services.reindex_service import ReindexService

        return ReindexService
    elif name == "IndexingWorkerPool":
        from acolyte.services.indexing_worker_pool import IndexingWorkerPool

        return IndexingWorkerPool
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "ConversationService",
    "TaskService",
    "ChatService",
    "IndexingService",
    "GitService",
    "ReindexService",
    "IndexingWorkerPool",
]
