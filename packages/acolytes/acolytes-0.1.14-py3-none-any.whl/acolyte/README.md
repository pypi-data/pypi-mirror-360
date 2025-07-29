# ACOLYTE Python Package

This is the core Python package for ACOLYTE - Your Local AI Programming Assistant.

## Package Structure

```
acolyte/
├── api/         # FastAPI endpoints and WebSocket handlers
├── core/        # Core infrastructure (logging, database, exceptions)
├── dream/       # Deep analysis and optimization system
├── embeddings/  # Vector embedding generation
├── models/      # Pydantic models and schemas
├── rag/         # Retrieval Augmented Generation system
├── semantic/    # Natural language processing
├── services/    # Business logic services
└── cli.py       # Command-line interface
```

## Key Components

- **CLI**: Main entry point for the `acolyte` command
- **API**: OpenAI-compatible REST API
- **Services**: Core business logic (chat, indexing, git, etc.)
- **RAG**: Code search and retrieval system
- **Dream**: Autonomous code analysis system

## Installation

This package is installed as part of the ACOLYTE system:

```bash
pip install git+https://github.com/unmasSk/acolyte.git
```

## Development

For development work:

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy src/acolyte
```

## License

See LICENSE file in the project root.
