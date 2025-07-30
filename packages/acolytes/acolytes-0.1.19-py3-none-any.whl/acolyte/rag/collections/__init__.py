"""
Collections module - Weaviate schema management for ACOLYTE.

Defines and manages the 5 main collections:
- Conversation: Conversation summaries
- CodeChunk: Code fragments with 18 ChunkTypes
- Document: Complete documents
- Task: Session grouping
- DreamInsight: Optimizer insights
"""

from typing import TYPE_CHECKING

# Direct imports for frequently used classes
from acolyte.rag.collections.manager import CollectionManager, get_collection_manager
from acolyte.rag.collections.collection_names import CollectionName

# Lazy imports for heavy classes
if TYPE_CHECKING:
    from acolyte.rag.collections.batch_inserter import WeaviateBatchInserter, BatchResult

__all__ = [
    "CollectionManager",
    "get_collection_manager",
    "CollectionName",
    "WeaviateBatchInserter",
    "BatchResult",
]


# Lazy loading for batch inserter (only loads when accessed)
def __getattr__(name):
    if name == "WeaviateBatchInserter":
        from acolyte.rag.collections.batch_inserter import WeaviateBatchInserter

        return WeaviateBatchInserter
    elif name == "BatchResult":
        from acolyte.rag.collections.batch_inserter import BatchResult

        return BatchResult
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
