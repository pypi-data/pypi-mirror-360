# ACOLYTE Lazy Loading

## Overview

ACOLYTE uses lazy loading to ensure fast startup times by deferring the import of heavy dependencies (torch, transformers, tree-sitter, etc.) until they are actually needed.

## Performance Impact

- **Before lazy loading**: ~6 seconds to import
- **After lazy loading**: ~0.01 seconds to import (**600x faster!**)

## How It Works

### 1. Module-level lazy loading

Heavy modules are imported inside functions/methods rather than at module level:

```python
# ❌ Bad - loads immediately
from acolyte.embeddings.unixcoder import UniXcoderEmbeddings

# ✅ Good - loads only when needed
def get_embeddings():
    from acolyte.embeddings.unixcoder import UniXcoderEmbeddings
    return UniXcoderEmbeddings()
```

### 2. `__getattr__` lazy loading

Modules use `__getattr__` to load attributes on demand:

```python
def __getattr__(name):
    if name == "IndexingService":
        from acolyte.services.indexing_service import IndexingService
        return IndexingService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
```

### 3. Property-based lazy loading

Classes use properties to defer initialization:

```python
class ChatService:
    def __init__(self):
        self._dream_orchestrator = None  # Don't load yet
    
    @property
    def dream_orchestrator(self):
        if self._dream_orchestrator is None:
            from acolyte.dream import create_dream_orchestrator
            self._dream_orchestrator = create_dream_orchestrator()
        return self._dream_orchestrator
```

## Heavy Dependencies

These modules are loaded only when needed:

| Module | Size | Used By | Loaded When |
|--------|------|---------|-------------|
| `torch` | ~2GB | embeddings | `get_embeddings()` called |
| `transformers` | ~500MB | embeddings | `get_embeddings()` called |
| `tree_sitter` | ~50MB | chunking | `ChunkerFactory()` instantiated |
| `tree_sitter_languages` | ~100MB | chunking | `ChunkerFactory()` instantiated |
| `weaviate` | ~10MB | search | Weaviate operations performed |
| `ollama` | ~5MB | LLM | Ollama operations performed |

## Testing Lazy Loading

### Quick Test

```bash
# Run the simple test script
python claude_test_all_modules.py
```

### Unit Tests

```bash
# Run pytest tests
poetry run pytest tests/test_lazy_loading.py -v
```

### Integration Test

```bash
# Run comprehensive integration test
poetry run python tests/integration/test_lazy_loading_integration.py

# Save results to JSON
poetry run python tests/integration/test_lazy_loading_integration.py --save
```

### Manual Check

```python
# Quick Python check
import time
start = time.time()
import acolyte
print(f"Import time: {time.time() - start:.3f}s")
# Should be < 0.1s
```

## Guidelines for Maintaining Lazy Loading

### DO:

1. **Import heavy modules inside functions**
   ```python
   def process():
       from heavy_module import HeavyClass  # ✅
   ```

2. **Use TYPE_CHECKING for type hints**
   ```python
   from typing import TYPE_CHECKING
   if TYPE_CHECKING:
       from heavy_module import HeavyClass
   ```

3. **Test imports regularly**
   - Run `test_lazy_loading.py` after changes
   - Check that import time stays < 0.1s

### DON'T:

1. **Import at module level**
   ```python
   from heavy_module import HeavyClass  # ❌
   ```

2. **Import in `__init__.py` unnecessarily**
   ```python
   # __init__.py
   from .heavy_module import *  # ❌
   ```

3. **Create module-level instances**
   ```python
   embedder = UniXcoderEmbeddings()  # ❌ At module level
   ```

## Common Issues

### Issue: Import time increases

**Solution**: Run the test to identify which module is loading heavy dependencies:
```bash
python tests/integration/test_lazy_loading_integration.py
```

### Issue: Type checking errors

**Solution**: Use `TYPE_CHECKING` imports:
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from heavy_module import HeavyClass

def process() -> 'HeavyClass':
    from heavy_module import HeavyClass
    return HeavyClass()
```

### Issue: Circular imports

**Solution**: Move imports inside functions or use string annotations:
```python
from __future__ import annotations  # Enable string annotations
```

## CI/CD Integration

Add to your CI pipeline:

```yaml
# GitHub Actions example
- name: Test Lazy Loading
  run: |
    poetry run pytest tests/test_lazy_loading.py
    poetry run python tests/integration/test_lazy_loading_integration.py
```

## Monitoring

To monitor import performance over time:

1. Run integration test with `--save` flag
2. Track `total_time` in the JSON output
3. Alert if import time exceeds threshold (e.g., 1.0s)

## Future Improvements

1. **Automatic detection**: Pre-commit hook to detect heavy imports
2. **Import profiler**: Tool to visualize import dependencies
3. **Lazy loading linter**: Custom pylint rules for lazy loading
