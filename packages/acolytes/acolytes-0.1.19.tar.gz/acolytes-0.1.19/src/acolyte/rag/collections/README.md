# 📚 Collections Module

Defines and manages the 5 Weaviate collections that constitute ACOLYTE's vector memory.

## 📑 Documentation

- **[Architecture](../../docs/ARCHITECTURE.md#decision-6-768-dimension-embeddings)** - Vector dimensions
- **[API Reference](../../docs/REFERENCE.md#collectionsmanagerpy)** - CollectionManager class
- **[Status](../../docs/STATUS.md#collections)** - Collection definitions
- **[Integration](../../docs/INTEGRATION.md#collection-schemas)** - Who uses which collection

## 🔧 Key Components

- `manager.py` - Collection lifecycle management
- `collection_names.py` - Enum preventing hardcoded strings
- `schemas.json` - Complete schema definitions for 5 collections

## ⚡ Quick Usage

```python
from acolyte.rag.collections import CollectionManager, CollectionName
from acolyte.core.logging import logger

logger.info("Creating Weaviate collections")
manager = CollectionManager(weaviate_client)
created = manager.create_all_collections()

# Use enum for type safety
info = manager.get_collection_info(CollectionName.CODE_CHUNK)
logger.info(f"Collection info retrieved: {info}")
```

## 📊 Key Features

- **5 Collections**: CodeChunk, Document, Conversation, Task, DreamInsight
- **vectorizer="none"**: All embeddings from UniXcoder (768 dims)
- **System constant**: 768 dimensions defined here, respected everywhere
- **HNSW indexing**: Optimized for cosine similarity searches

## 🐛 Recent Fixes

- **Connection Error Handling**: Added specific handling for `WeaviateConnectionError`
  - Import `ConnectionError` from `weaviate.exceptions`
  - Handle before generic `WeaviateException`
  - Return specific error message "No se puede conectar a Weaviate"
- **Test Updates**: All tests now use `WeaviateBaseError` instead of `WeaviateException`
