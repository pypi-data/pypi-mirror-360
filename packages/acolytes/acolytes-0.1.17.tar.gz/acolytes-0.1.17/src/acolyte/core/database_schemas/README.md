# 🗄️ Database Module

Dual persistence system: SQLite for relational data + Weaviate for vector search.

## 📁 Structure

```
database/
├── __init__.py         # Main exports
├── schemas.sql         # Complete SQLite schema (includes neural graph)
└── README.md           # This file

# Note: Initialization script moved to /scripts/init_database.py
```

## 🎯 Responsibilities

1. **Define SQLite schemas** with all tables
2. **Connection with initialization script** (now in `/scripts/init_database.py`)
3. **Connection management** (implemented in parent's `database.py`)
4. **Future migrations** if schema changes

## 📊 SQLite Tables

### Conversation and Task Tables

| Table                 | Purpose             | Features                                                                                                          |
| --------------------- | ------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `conversations`       | Chat messages       | - 32-char hex IDs<br>- UNIQUE session_id for FK<br>- Includes summaries and tokens                                |
| `tasks`               | Session grouping    | - 6 types: IMPLEMENTATION, DEBUGGING, etc.<br>- 3 states: PLANNING, IN_PROGRESS, COMPLETED<br>- Progress tracking |
| `task_sessions`       | M:N relationship    | - Connects tasks with sessions<br>- Association timestamp                                                         |
| `technical_decisions` | Important decisions | - 4 types: ARCHITECTURE, LIBRARY, PATTERN, SECURITY<br>- Impact level 1-5                                         |

### Dream System Tables

| Table            | Purpose         | Features                                                                          |
| ---------------- | --------------- | --------------------------------------------------------------------------------- |
| `dream_state`    | Optimizer state | - **Singleton** (only 1 row)<br>- Fatigue 0-10<br>- Performance metrics           |
| `dream_insights` | Discoveries     | - 5 types: PATTERN, CONNECTION, etc.<br>- Confidence 0.0-1.0<br>- Code references |

### 🆕 Neural Graph Tables (Decision #21)

| Table                | Purpose       | Features                                                                                                              |
| -------------------- | ------------- | --------------------------------------------------------------------------------------------------------------------- |
| `code_graph_nodes`   | Graph nodes   | - 4 types: FILE, FUNCTION, CLASS, MODULE<br>- Unique path per type<br>- JSON metadata                                 |
| `code_graph_edges`   | Relationships | - 7 types: IMPORTS, CALLS, EXTENDS, etc.<br>- Strength 0.0-1.0<br>- Discovered by: GIT_ACTIVITY, DREAM_ANALYSIS, etc. |
| `code_graph_metrics` | Graph metrics | - **Singleton** (only 1 row)<br>- Global statistics<br>- Detected clusters                                            |

### Useful Views

- `task_summary` - Task summary with counts
- `node_connectivity` - Neural graph connectivity analysis

## 🎨 Weaviate Collections

Defined in `/rag/collections/schemas.json`:

1. **Conversation** - Conversation embeddings
2. **CodeChunk** - Code embeddings
3. **Document** - Document embeddings
4. **Task** - Task embeddings
5. **DreamInsight** - Insight embeddings

All with `vectorizer="none"` (external embeddings with UniXcoder).

## 🚀 Initialization Script

### Usage

```bash
# From project root
python scripts/init_database.py

# Or with Poetry
poetry run python scripts/init_database.py
```

### What it does

1. **Creates directory** `.acolyte/` if not exists
2. **Initializes SQLite**:
   - Executes complete `schemas.sql`
   - Creates tables, indexes, triggers and views
   - Inserts initial rows in singletons
   - Verifies integrity
3. **Initializes Weaviate**:
   - Connects to `http://localhost:8080` (configurable)
   - Creates 5 collections if not exist
   - Configures optimized HNSW indexes
4. **Verifies installation**:
   - Counts SQLite tables (expects ≥9)
   - Counts Weaviate collections (expects ≥5)

### Requirements

- Weaviate must be running:
  ```bash
  docker-compose up -d weaviate
  ```
- Python packages: `weaviate-client`, `loguru`

### Expected output

```
=== Starting ACOLYTE database installation ===
✅ SQLite initialized correctly with 12 tables
✅ Weaviate initialized: 5 collections created, 0 already existed

=== Verifying installation ===
SQLite: ✅ (12 tables)
Weaviate: ✅ (5 collections)

✅ Databases initialized successfully!
SQLite: .acolyte/acolyte.db
Weaviate: http://localhost:8080
```

## ⚙️ Conventions and Rules

### IDs in SQLite ✅ CENTRALIZED SYSTEM

**🔄 PARADIGM CHANGE**: NO longer use `secrets` directly, use centralized IDGenerator:

```python
# ❌ BEFORE - Each file generated different IDs
import secrets
import uuid
id_secrets = secrets.token_hex(16)  # Some files
id_uuid = str(uuid.uuid4())         # Other files
# Result: Incompatibility between Python and SQLite

# ✅ NOW - Unified system
from acolyte.core.id_generator import generate_id
id = generate_id()  # Always SQLite-compatible hex32
```

**Benefits of the change**:

- ✅ **Single format**: All IDs are hex32 (32 characters without dashes)
- ✅ **Compatibility**: Works perfectly with SQLite as PRIMARY KEY
- ✅ **Consistency**: All modules use the same system
- ✅ **Validation**: `is_valid_id()` to verify valid IDs
- ✅ **Conversion**: Functions to migrate existing IDs

**Database files now using IDGenerator**:

- `core/database.py`: Lines 225 and 384 updated
- `models/base.py`: IdentifiableMixin uses `generate_id()`
- All services: Use the new centralized system

### Enums in UPPERCASE

```python
# Python must convert to uppercase
task_type = TaskType.IMPLEMENTATION  # In Python
# Saved as 'IMPLEMENTATION' in SQLite
```

### Automatic Triggers

- `updated_at` updates automatically
- `dream_state` and `code_graph_metrics` only allow 1 row

### Foreign Keys

- Enabled with `PRAGMA foreign_keys = ON`
- CASCADE on DELETE to maintain integrity

## 🔗 Integration with Other Modules

### ✅ With Core (centralized IDGenerator)

- **ALL modules** now use `generate_id()` for consistent IDs
- **Eliminated duplication**: No more `secrets.token_hex()` in individual files
- **Database**: Schemas expect hex32 IDs without dashes
- **Migrations**: Conversion functions for existing IDs

### With Services

- `ConversationService` reads/writes `conversations` (centralized IDs)
- `TaskService` manages `tasks` and `task_sessions` (centralized IDs)
- `DreamService` updates `dream_state` and `dream_insights` (centralized IDs)

### With RAG

- RAG doesn't touch SQLite directly
- Only interacts with Weaviate for embeddings
- **Exception**: Neural graph in `/rag/graph/` DOES use SQLite

### With API

- API doesn't access DBs directly
- Always through Services

## 🚧 TODO

- [ ] Migration system for schema changes
- [ ] Automatic SQLite backup
- [ ] Old data cleanup (>365 days)
- [ ] DB usage metrics

## ❌ What this module does NOT do

- **NO** complex ORM (uses direct SQL)
- **NO** elaborate connection pooling (single-user)
- **NO** replication (it's local)
- **NO** partitioning (small datasets)

---

**NOTE**: This module defines schemas and provides installation tools. Data access logic is in Services.
