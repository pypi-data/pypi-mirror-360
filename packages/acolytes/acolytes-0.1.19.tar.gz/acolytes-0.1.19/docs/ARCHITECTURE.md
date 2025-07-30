# ACOLYTE Architecture

## 🏗️ System Overview

ACOLYTE follows a clean, modular architecture designed for local, single-user operation.

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   User Project  │     │   ACOLYTE CLI   │     │  ACOLYTE API    │
│ .acolyte.project│────▶│    Commands     │────▶│   FastAPI       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                          │
                        ┌─────────────────────────────────┴───────────┐
                        │                                             │
                        ▼                                             ▼
                ┌─────────────────┐                         ┌─────────────────┐
                │     Weaviate     │                         │     Ollama      │
                │ Vector Database  │                         │   LLM Server    │
                └─────────────────┘                         └─────────────────┘
                        │                                             │
                        └─────────────────┬───────────────────────────┘
                                          ▼
                                ┌─────────────────┐
                                │     SQLite      │
                                │ Metadata & History│
                                └─────────────────┘
```

## 📁 Project Structure

```
acolyte/
├── src/acolyte/              # Source code
│   ├── api/                  # HTTP API endpoints
│   │   ├── openai.py        # OpenAI-compatible endpoints
│   │   ├── health.py        # Health checks
│   │   ├── dream.py         # Dream analysis endpoints
│   │   └── index.py         # Indexing endpoints
│   ├── core/                # Core infrastructure
│   │   ├── database.py      # Database management
│   │   ├── logging.py       # Async logging
│   │   ├── exceptions.py    # Error hierarchy
│   │   └── config.py        # Configuration
│   ├── services/            # Business logic (6 services)
│   │   ├── chat_service.py  # Chat orchestration
│   │   ├── conversation_service.py
│   │   ├── task_service.py
│   │   ├── git_service.py
│   │   ├── indexing_service.py
│   │   └── reindex_service.py
│   ├── models/              # Pydantic schemas
│   ├── embeddings/          # Vector embeddings
│   ├── semantic/            # NLP processing
│   ├── rag/                 # Retrieval & search
│   └── dream/               # Deep analysis
├── scripts/                 # Installation & utilities
├── tests/                   # Test suite
└── docs/                    # Documentation
```

## 🔑 Key Components

### 1. API Layer (`/api`)

FastAPI-based REST API providing:
- OpenAI-compatible chat endpoints
- Health monitoring
- WebSocket support
- Indexing triggers

### 2. Core Layer (`/core`)

Foundation services:
- **DatabaseManager**: Thread-safe SQLite operations
- **AsyncLogger**: Zero-latency logging
- **Settings**: Configuration management
- **Exceptions**: Typed error handling

### 3. Services Layer (`/services`)

Business logic orchestration:
- **ChatService**: Main chat orchestration
- **ConversationService**: History management
- **TaskService**: Task grouping
- **GitService**: Git integration
- **IndexingService**: File indexing
- **ReindexService**: Automatic reindexing

### 4. RAG System (`/rag`)

Retrieval Augmented Generation:
- **ChunkingService**: 31 language parsers
- **HybridSearch**: 70% semantic + 30% lexical
- **CompressionService**: Token optimization
- **EnrichmentService**: Git metadata

### 5. Semantic Layer (`/semantic`)

NLP processing:
- **Summarizer**: Conversation summaries
- **PromptBuilder**: Dynamic prompts
- **TaskDetector**: Task identification
- **DecisionDetector**: Technical decisions

### 6. Dream System (`/dream`)

Deep analysis engine:
- **DreamOrchestrator**: Analysis coordination
- **FatigueMonitor**: Code health metrics
- **Analyzers**: Bug, security, performance
- **NeuralGraph**: Dependency analysis

## 🗄️ Data Storage

### SQLite Database

Primary metadata storage:
```sql
conversations      -- Chat history
tasks             -- Task grouping
task_sessions     -- Many-to-many
technical_decisions -- Architectural decisions
dream_state       -- Analysis state
dream_insights    -- Findings
```

### Weaviate Vector DB

Semantic search:
```
CodeChunk collection:
- content: str
- embedding: vector[768]
- file_path: str
- language: str
- chunk_type: str
- metadata: dict
```

### File System

```
~/.acolyte/
├── projects/
│   └── {project_id}/
│       ├── config.yaml      # Project config
│       ├── data/
│       │   ├── acolyte.db   # SQLite
│       │   └── logs/        # Logs
│       └── infra/
│           ├── docker-compose.yml
│           ├── weaviate/    # Vector data
│           └── ollama/      # Models
└── global/
    └── models/              # Shared models
```

## 🔄 Data Flow

### Chat Request Flow

1. **API receives request** → `/v1/chat/completions`
2. **ChatService orchestrates**:
   - Load conversation context
   - Detect task/intent
   - Search relevant code (RAG)
   - Build dynamic prompt
   - Generate response (Ollama)
   - Summarize & store
   - Detect decisions
3. **Response sent** with streaming support

### Indexing Flow

1. **Git hook detects changes**
2. **Sends to** `/api/index/git-changes`
3. **IndexingService processes**:
   - Parse files with tree-sitter
   - Chunk into semantic units
   - Generate embeddings
   - Enrich with Git metadata
   - Store in Weaviate
4. **Cache invalidated** if needed

## 🎯 Design Principles

### 1. Local-First

- No cloud dependencies
- No authentication needed
- All data on user's machine
- Works offline

### 2. Simplicity

- Mono-user design
- No multi-tenancy
- Singletons allowed
- Direct instantiation

### 3. Performance

- Async everywhere
- Lazy loading
- Smart caching
- Batch operations

### 4. Privacy

- No telemetry
- No external calls
- No data leaves machine
- No usage tracking

## 🚀 Deployment

### Docker Services

Three containers:
1. **Weaviate** - Vector database
2. **Ollama** - LLM server
3. **Backend** - ACOLYTE API

### Resource Limits

- 50% of system RAM
- 50% of CPU cores
- GPU auto-detection
- Configurable per project

## 🔧 Extension Points

### Adding Languages

1. Create chunker in `/rag/chunking/languages/`
2. Implement `BaseChunker` interface
3. Register in `ChunkerFactory`
4. Add tests

### Adding Analyzers

1. Create analyzer in `/dream/analyzers/`
2. Implement `BaseAnalyzer` interface
3. Register in `DreamOrchestrator`
4. Add tests

### Adding Services

1. Create service in `/services/`
2. Follow existing patterns
3. Add to API if needed
4. Add tests

## 🔐 Security

- Localhost only (127.0.0.1)
- Path validation
- No shell execution
- Sanitized inputs
- Secure file handling
