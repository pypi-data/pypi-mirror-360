# 📋 CENTRALIZATION IMPLEMENTATION - GUÍA ESTRICTA

> ⚠️ **IMPERATIVO**: Esta timeline es OBLIGATORIA. No saltar pasos. No cambiar orden.

## 🎯 REGLAS DE ORO

1. **UN ARCHIVO A LA VEZ**: Nunca trabajar en múltiples archivos simultáneamente
2. **TEST ANTES DE CONTINUAR**: No pasar al siguiente archivo hasta que el test pase
3. **INFORMAR SIEMPRE**: Cada cambio debe ser comunicado a Bex antes de ejecutar
4. **CHECKLIST ES LEY**: Marcar cada paso completado en CENTRALIZACION_CHECKLIST.md
5. **⚠️ ANALIZAR CADA ARCHIVO**: NO asumir que todos los retry son iguales. Algunos necesitan wrappers especiales, otros no deben migrarse

## 🚀 PROCESO EXACTO PARA CADA ARCHIVO

### 📝 TEMPLATE DE TRABAJO (Repetir para CADA archivo)

```
1. LEER archivo actual y su test
2. BUSCAR patrones de retry/filetype
3. INFORMAR a Bex:
   - "En [archivo] encontré [N] lugares con retry logic"
   - "En [archivo] encontré [N] lugares con file type detection"
   - "Propongo cambiar: [describir cambios]"
4. ESPERAR OK de Bex
5. IMPLEMENTAR cambios
6. EJECUTAR: poetry run pytest [path/to/test] -xvs
7. SI PASA: Marcar ✅ en checklist
8. SI FALLA: Informar error y corregir
9. SIGUIENTE archivo
```

---

# 🔨 FASE 0: IMPLEMENTACIÓN BASE (Primera IA)

## Objetivo
Crear los módulos base `retry.py` y `file_types.py` que serán usados por todos.

## Pasos EXACTOS

### 1. Crear estructura
```bash
mkdir -p src/acolyte/core/utils
touch src/acolyte/core/utils/__init__.py
touch src/acolyte/core/utils/retry.py
touch src/acolyte/core/utils/file_types.py
```

### 2. Implementar retry.py
Copiar EXACTAMENTE desde `/CENTRALIZATION_RETRY_LOGIC.md`:

```python
from typing import TypeVar, Callable, Optional, Type, Tuple, Any
import asyncio
from functools import wraps

T = TypeVar('T')

async def retry_async(
    func: Callable[..., T],
    max_attempts: int = 3,
    backoff: str = "exponential",
    initial_delay: float = 0.5,
    max_delay: float = 30.0,
    retry_on: Tuple[Type[Exception], ...] = (Exception,),
    logger: Optional[Any] = None
) -> T:
    """
    Retry an async function with configurable backoff.
    
    Args:
        func: Async function to retry
        max_attempts: Maximum number of attempts
        backoff: "exponential", "linear", or "constant"
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay between retries
        retry_on: Tuple of exceptions to retry on
        logger: Optional logger for retry attempts
    
    Returns:
        Result from successful function call
        
    Raises:
        Last exception if all retries fail
    """
    last_exception = None
    
    for attempt in range(max_attempts):
        try:
            return await func()
        except retry_on as e:
            last_exception = e
            
            if attempt < max_attempts - 1:
                # Calculate delay based on backoff strategy
                if backoff == "exponential":
                    delay = min(initial_delay * (2 ** attempt), max_delay)
                elif backoff == "linear":
                    delay = min(initial_delay * (attempt + 1), max_delay)
                else:  # constant
                    delay = initial_delay
                
                if logger:
                    logger.warning(
                        "Retry attempt failed",
                        attempt=attempt + 1,
                        max_attempts=max_attempts,
                        delay=delay,
                        error=str(e)
                    )
                
                await asyncio.sleep(delay)
            else:
                if logger:
                    logger.error(
                        "All retry attempts failed",
                        attempts=max_attempts,
                        error=str(e)
                    )
    
    raise last_exception

# Decorator version
def with_retry(
    max_attempts: int = 3,
    backoff: str = "exponential",
    **kwargs
):
    """Decorator to add retry logic to async functions."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **func_kwargs):
            return await retry_async(
                lambda: func(*args, **func_kwargs),
                max_attempts=max_attempts,
                backoff=backoff,
                **kwargs
            )
        return wrapper
    return decorator
```

### 3. Implementar file_types.py
Copiar EXACTAMENTE desde `/CENTRALIZATION_FILE_TYPES.md`:

```python
from pathlib import Path
from typing import Set, Dict, Optional
from enum import Enum

class FileCategory(Enum):
    CODE = "code"
    DOCUMENTATION = "documentation"
    CONFIGURATION = "configuration"
    DATA = "data"
    OTHER = "other"

class FileTypeDetector:
    """Centralized file type detection and classification."""
    
    # Master mapping of extensions to languages
    LANGUAGE_MAP: Dict[str, str] = {
        ".py": "python",
        ".js": "javascript", 
        ".ts": "typescript",
        ".jsx": "javascript",
        ".tsx": "typescript",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
        ".rb": "ruby",
        ".php": "php",
        ".cs": "csharp",
        ".cpp": "cpp",
        ".c": "c",
        ".h": "c",
        ".hpp": "cpp",
        ".swift": "swift",
        ".kt": "kotlin",
        ".scala": "scala",
        ".r": "r",
        ".m": "objective-c",
        ".mm": "objective-cpp",
        ".sh": "bash",
        ".bash": "bash",
        ".zsh": "zsh",
    }
    
    # Category mappings
    CATEGORY_MAP: Dict[FileCategory, Set[str]] = {
        FileCategory.CODE: {
            ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs",
            ".c", ".cpp", ".h", ".hpp", ".cs", ".rb", ".php", ".swift",
            ".kt", ".scala", ".r", ".m", ".mm", ".sh", ".bash", ".zsh"
        },
        FileCategory.DOCUMENTATION: {
            ".md", ".rst", ".txt", ".adoc"
        },
        FileCategory.CONFIGURATION: {
            ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", 
            ".env", ".properties", ".xml"
        },
        FileCategory.DATA: {
            ".csv", ".sql"
        }
    }
    
    @classmethod
    def get_language(cls, path: Path) -> str:
        """Get programming language for a file."""
        return cls.LANGUAGE_MAP.get(path.suffix.lower(), "unknown")
    
    @classmethod
    def get_category(cls, path: Path) -> FileCategory:
        """Get category for a file."""
        suffix = path.suffix.lower()
        
        for category, extensions in cls.CATEGORY_MAP.items():
            if suffix in extensions:
                return category
        
        return FileCategory.OTHER
    
    @classmethod
    def is_supported(cls, path: Path) -> bool:
        """Check if file type is supported for indexing."""
        return cls.get_category(path) != FileCategory.OTHER
    
    @classmethod
    def get_all_supported_extensions(cls) -> Set[str]:
        """Get all supported file extensions."""
        all_extensions = set()
        for extensions in cls.CATEGORY_MAP.values():
            all_extensions.update(extensions)
        return all_extensions
```

### 4. Actualizar __init__.py
```python
from .retry import retry_async, with_retry
from .file_types import FileTypeDetector, FileCategory

__all__ = ['retry_async', 'with_retry', 'FileTypeDetector', 'FileCategory']
```

### 5. Crear tests básicos
```bash
mkdir -p tests/core/utils
touch tests/core/utils/__init__.py
touch tests/core/utils/test_retry.py
touch tests/core/utils/test_file_types.py
```

### 6. Test mínimo para retry.py
```python
# tests/core/utils/test_retry.py
import pytest
import asyncio
from acolyte.core.utils.retry import retry_async, with_retry

class TestRetryAsync:
    async def test_successful_first_attempt(self):
        """Test function succeeds on first attempt."""
        call_count = 0
        
        async def success():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = await retry_async(success)
        assert result == "success"
        assert call_count == 1
    
    async def test_retry_on_failure(self):
        """Test function retries on failure."""
        call_count = 0
        
        async def fail_twice():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Failed")
            return "success"
        
        result = await retry_async(fail_twice, max_attempts=3)
        assert result == "success"
        assert call_count == 3
```

### 7. Test mínimo para file_types.py
```python
# tests/core/utils/test_file_types.py
import pytest
from pathlib import Path
from acolyte.core.utils.file_types import FileTypeDetector, FileCategory

class TestFileTypeDetector:
    def test_get_language_python(self):
        """Test Python file detection."""
        assert FileTypeDetector.get_language(Path("test.py")) == "python"
    
    def test_get_language_unknown(self):
        """Test unknown file type."""
        assert FileTypeDetector.get_language(Path("test.xyz")) == "unknown"
    
    def test_get_category_code(self):
        """Test code file category."""
        assert FileTypeDetector.get_category(Path("test.py")) == FileCategory.CODE
    
    def test_is_supported(self):
        """Test supported file check."""
        assert FileTypeDetector.is_supported(Path("test.py")) is True
        assert FileTypeDetector.is_supported(Path("test.xyz")) is False
```

### 8. Verificar implementación
```bash
# Verificar imports
python -c "from acolyte.core.utils import retry_async, FileTypeDetector; print('✅ Imports OK')"

# Ejecutar tests
poetry run pytest tests/core/utils/test_retry.py -xvs
poetry run pytest tests/core/utils/test_file_types.py -xvs
```

## ✅ Checklist FASE 0
- [ ] Crear estructura de directorios
- [ ] Implementar retry.py
- [ ] Implementar file_types.py  
- [ ] Actualizar __init__.py
- [ ] Crear tests básicos
- [ ] Verificar imports
- [ ] Pasar tests

---

# 🔄 FASES 1-N: MIGRACIÓN ARCHIVO POR ARCHIVO

## 📋 ORDEN ESTRICTO DE ARCHIVOS

### FASE 1: Retry Logic - Services
1. `src/acolyte/services/conversation_service.py` ⚠️ **COMPLEJO** - Necesita wrapper para is_retryable()
2. `src/acolyte/services/chat_service.py` ⚠️ **COMPLEJO** - Similar a conversation_service
3. `src/acolyte/embeddings/unixcoder.py` ❌ **NO MIGRAR** - Usa fallback, no retry
4. `src/acolyte/core/ollama.py` ✅ **SIMPLE** - Retry básico
5. `src/acolyte/rag/retrieval/hybrid_search.py` ➕ **AÑADIR** - No tiene retry actualmente

### FASE 2: File Types - Services
6. `src/acolyte/services/indexing_service.py`
7. `src/acolyte/services/reindex_service.py`
8. `src/acolyte/services/task_service.py`

### FASE 3: File Types - API
9. `src/acolyte/api/index.py`

### FASE 4: File Types - Models
10. `src/acolyte/models/document.py`

### FASE 5: File Types - RAG
11. `src/acolyte/rag/chunking/factory.py`
12. `src/acolyte/rag/chunking/language_mappings.py`
13. `src/acolyte/rag/chunking/base.py`
14. `src/acolyte/rag/chunking/language_config.py`
15. `src/acolyte/rag/retrieval/filters.py`
16. `src/acolyte/rag/enrichment/service.py`
17. `src/acolyte/rag/compression/contextual.py`

### FASE 6: File Types - Chunkers
18. `src/acolyte/rag/chunking/languages/*.py` (todos)

### FASE 7: Dream
19. `src/acolyte/dream/analyzer.py`

## 🔍 PATRONES A BUSCAR

### Para Retry Logic
```python
# Buscar estos patrones:
for attempt in range(
max_attempts
retry
backoff
asyncio.sleep
DatabaseError.*is_retryable
```

### Para File Type Detection
```python
# Buscar estos patrones:
supported_extensions
EXTENSION_MAP
is_supported_file
detect_language
get_language
language_map
file_path.suffix
```

## 📝 EJEMPLO DE COMUNICACIÓN

```
IA: "Revisando src/acolyte/services/conversation_service.py"
IA: "Encontré 1 patrón de retry logic en líneas 200-220 (_execute_with_retry)"
IA: "Propongo:
     1. Añadir import: from acolyte.core.utils.retry import retry_async
     2. Reemplazar método _execute_with_retry con llamada a retry_async
     3. Eliminar el método antiguo"
BEX: "OK, procede"
IA: [hace cambios]
IA: "Ejecutando: poetry run pytest tests/services/test_conversation_service.py -xvs"
IA: "✅ Tests pasaron. Marcando en checklist."
```

## ⚠️ ADVERTENCIA CRÍTICA: RETRY LOGIC COMPLEJO

### ⚡ CADA ARCHIVO ES DIFERENTE

Después de revisar los archivos, **NO todos los retry son iguales**:

1. **conversation_service.py**: Usa `DatabaseError.is_retryable()` - solo reintenta ciertos errores
2. **chat_service.py**: Similar con `AcolyteError.is_retryable()` + métricas diferentes
3. **unixcoder.py**: NO usa retry, usa FALLBACK (CUDA → CPU) - NO MIGRAR
4. **ollama.py**: Retry simple inline
5. **hybrid_search.py**: NO tiene retry - AÑADIR si es necesario

### 🔧 NECESITARÁS WRAPPERS ESPECIALES

Para archivos con lógica condicional como conversation_service:

```python
# WRAPPER para preservar is_retryable()
async def retryable_db_operation():
    try:
        return await db_operation(*args, **kwargs)
    except DatabaseError as e:
        if not e.is_retryable():
            raise  # NO reintentar
        raise  # SÍ reintentar
```

### 📊 MÉTRICAS FUERA DEL RETRY

```python
# Las métricas específicas van FUERA
attempt_count = 0
async def operation_with_counter():
    nonlocal attempt_count
    attempt_count += 1
    return await original_operation()

result = await retry_async(operation_with_counter)
if attempt_count > 1:
    self.metrics.increment("retries_successful")
```

## ⚠️ CASOS ESPECIALES

### 1. Si el retry tiene lógica especial
```python
# ANTES
if attempt > 0:
    self.metrics.increment("retries_successful")

# SOLUCIÓN: Mantener lógica fuera del retry
result = await retry_async(operation)
if result and had_retries:
    self.metrics.increment("retries_successful")
```

### 2. Si file detection tiene casos especiales
```python
# Scripts sin extensión, archivos especiales, etc.
# Mantener lógica adicional DESPUÉS de FileTypeDetector
if not path.suffix and is_executable(path):
    # Lógica especial para scripts
```

## 🚫 ERRORES COMUNES A EVITAR

1. **NO cambiar comportamiento**: Si usaba 5 intentos, mantener 5
2. **NO eliminar métricas**: Preservar contadores y logs especiales
3. **NO cambiar excepciones**: Si solo reintentaba DatabaseError, mantenerlo
4. **NO modificar tests**: Solo ejecutarlos, no cambiarlos
5. **NO trabajar en paralelo**: Un archivo a la vez

## 🎯 CRITERIO DE ÉXITO

- ✅ Todos los archivos migrados
- ✅ Todos los tests pasan
- ✅ Comportamiento idéntico al original
- ✅ Cero duplicación de código
- ✅ Checklist 100% completado

---

**IMPORTANTE**: Después de completar FASE 0, este documento puede ser descartado. 
Solo se necesita CENTRALIZACION_CHECKLIST.md para las siguientes fases.
