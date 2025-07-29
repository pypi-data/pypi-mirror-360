# 📊 AUDITORÍA DE ALINEACIÓN - INSTRUCCIONES

## 🚀 PROCESO CORRECTO DE AUDITORÍA

### 1. PREPARACIÓN INICIAL

1. **Leer PROMPT.md** - Es la BIBLIA del proyecto, memorizarlo
2. **Leer PROMPT_PATTERNS.md** - Entender cómo funciona el código del proyecto
3. **NO MODIFICAR** ALIGNMENT_AUDIT.md ni ALIGNMENT_COV.md durante la auditoría
4. **SOLO MODIFICAR** ALIGNMENT_CHECKLIST.md

### 2. ORDEN DE REVISIÓN DE MÓDULOS

1. **Models** - Define estructuras base
2. **Core** - Infraestructura que todos usan
3. **Embeddings** - Base para búsqueda
4. **Semantic** - Lógica de procesamiento
5. **Services** - Usa models y core
6. **RAG** - Usa embeddings
7. **Dream** - Usa todo lo anterior
8. **API** - Punto final, usa todo

### 3. TIMELINE AL EXAMINAR UN MÓDULO

**PRIMERO - Leer TODA la documentación del módulo:**

1. README.md del módulo
2. docs/ARCHITECTURE.md
3. docs/INTEGRATION.md
4. docs/REFERENCE.md
5. docs/STATUS.md
6. docs/WORKFLOWS.md

**DESPUÉS - Examinar cada archivo .py:** 

⚠️ **OBLIGATORIO: REVISIÓN LÍNEA POR LÍNEA** ⚠️
- **NO ESCANEAR SUPERFICIALMENTE**
- **LEER CADA LÍNEA DEL ARCHIVO**
- **NO ASUMIR NADA**
- **SI SALTAS LÍNEAS = REPETIR TODO DESDE CERO**

1. **Leo archivo completo LÍNEA POR LÍNEA**
   - SI SE DETECTA UN TODO, HACK, FIXME, REVIEW, OPTIMIZE, NOTE: **AVISAR URGENTEMENTE A BEX**
   - **DETECTAR STRINGS QUE REQUIEREN i18n** (preparación para futuro multiidioma):
     - **SÍ marcar para i18n**:
       - Mensajes de error al usuario: `raise ValueError("No se puede procesar")`
       - Respuestas al usuario: `return "Optimización recomendada"`
       - Logs visibles al usuario: `logger.info("Procesando archivo...")`
       - Prompts/preguntas al usuario
     - **NO marcar para i18n**:
       - Field descriptions (son para desarrolladores)
       - Comentarios de código
       - Nombres técnicos internos
   - **ANOTAR COMO ISSUE**: `i18n: user-facing error` o `i18n: user responses`
2. **Verifico .pyi** - ¿Existe? ¿Está COMPLETAMENTE sincronizado con el .py? Verificar:
   - Mismas clases y métodos
   - Mismos parámetros y tipos
   - Sin métodos extra o faltantes
   - Decoradores importantes (@property, @classmethod, etc)
3. **Detecto violaciones PROMPT.md**:
   - Logger correcto (`from acolyte.core.logging import logger`)
   - generate_id() vs uuid
   - Pydantic v2 (.model_validate, .model_dump)
   - Comentarios en inglés
   - MetricsCollector sin namespace
4. **IMPLEMENTO datetime centralization** - Si el archivo usa datetime:
   - Añadir import: `from acolyte.core.utils.datetime_utils import utc_now, utc_now_iso, parse_iso_datetime`
   - Reemplazar `datetime.utcnow()` por `utc_now()`
   - Reemplazar `datetime.utcnow().isoformat()` por `utc_now_iso()`
   - Documentar en columna "Implementado" del checklist
   - Ver [Guía de Implementación Datetime](#guía-datetime-centralization) al final
5. **COMPARO con PROMPT_PATTERNS.md** - Verificar que los patrones implementados coincidan:
   - DatabaseManager patterns
   - HybridSearch 70/30
   - Cache patterns
   - Error handling
   - Async patterns
   - Etc.
6. **Busco en ALIGNMENT_COV.md** - Ver % y líneas no cubiertas
   - Identificar líneas críticas sin cobertura
   - Si hay paths no testeados importantes, añadir:
     ```python
     logger.warning("[UNTESTED PATH] description of the case")
     # o
     logger.info("[UNTESTED BRANCH] this branch has no tests")
     ```
   - Documentar en Issues si no se puede testear
7. **Verifico impacto Turso** - import weaviate/sqlite3
8. **Reporto resumen** - Solo lo importante
9. **Espero tu OK** - Qué arreglar
10. **Hago cambios**
11. **Le digo a BEX que ejecute test del archivo** - `poetry runpytest tests/path/to/test_file.py`
12. **Marco ✅ en CHECKLIST**

## 🎯 QUÉ REVISAR EN CADA ARCHIVO

### 1. ALINEACIÓN CON PROMPT.md

**REVISIÓN EXHAUSTIVA - NO SUPERFICIAL**:

- **Logger**: Verificar que usa `from acolyte.core.logging import logger`
- **IDs**: Usar `generate_id()` (NO uuid.uuid4())
- **Métricas**: MetricsCollector() sin parámetros (NO namespace)
- **Pydantic**: Métodos v2 (.model_validate, .model_dump) NO v1 (.parse_obj, .dict)
- **Idioma**: TODOS los comentarios en inglés
- **Marcadores**: TODO, FIXME, HACK, NOTE, REVIEW, OPTIMIZE → **PARAR Y AVISAR**
- **i18n**: Strings que el USUARIO FINAL verá → **DOCUMENTAR EN ISSUES**

### 2. COBERTURA DE TESTS

- Buscar el archivo específico en ALIGNMENT_COV.md (raíz)
- Identificar líneas no cubiertas críticas

### 3. IMPACTO TURSO

Buscar y clasificar:

- **Imports**: `import weaviate`, `import sqlite3`
- **Weaviate**: Client(), .query.get(), .with_near_vector()
- **SQLite**: execute_async(), transaction(), FetchType
- **Level**: High/Medium/Low/None

## 📝 ALIGNMENT_CHECKLIST.md FORMAT

```
| File | Reviewed | Turso | Implemented | Issues |
|------|----------|-------|-------------|--------|
| core/database.py | ✅ | High | datetime_utils | i18n: error messages |
```

### Legend

- **Reviewed**: ✅ Completed, ❌ Pending
- **Turso**: High/Medium/Low/None (migration impact)
- **Implemented**: Changes applied during audit (datetime_utils, etc.)
- **Issues**: Only unresolved problems and/or TODOs and/or FIXMEs to do.

## ⚠️ REGLAS IMPORTANTES

- **NO modificar** ALIGNMENT_AUDIT.md ni ALIGNMENT_COV.md
- **SOLO modificar** ALIGNMENT_CHECKLIST.md
- **Issues OBLIGATORIOS para**:
  - Cualquier TODO/FIXME/HACK encontrado
  - Strings que el usuario final verá (i18n futuro)
  - Patterns incorrectos no arreglables
  - Violaciones de PROMPT.md no corregibles
- **Leer TODA la documentación del módulo ANTES de revisar cualquier .py**

---

## 📅 Guía: Datetime Centralization

### 🎯 Objetivo

Reemplazar todas las instancias de `datetime.utcnow()` con los helpers centralizados de `core/utils/datetime_utils.py` durante la auditoría de alineación.

### 🔄 Patrones de Reemplazo

#### Patrón 1: Datetime simple

```python
# ANTES
from datetime import datetime
timestamp = datetime.utcnow()

# DESPUÉS
from acolyte.core.utils.datetime_utils import utc_now
timestamp = utc_now()
```

#### Patrón 2: ISO format

```python
# ANTES
from datetime import datetime
iso_time = datetime.utcnow().isoformat()

# DESPUÉS
from acolyte.core.utils.datetime_utils import utc_now_iso
iso_time = utc_now_iso()
```

#### Patrón 3: Añadir tiempo

```python
# ANTES
from datetime import datetime, timedelta
future = datetime.utcnow() + timedelta(hours=1)

# DESPUÉS
from acolyte.core.utils.datetime_utils import utc_now, add_time
future = add_time(utc_now(), hours=1)
```

#### Patrón 4: Parsear ISO strings

```python
# ANTES
from datetime import datetime
dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))

# DESPUÉS
from acolyte.core.utils.datetime_utils import parse_iso_datetime
dt = parse_iso_datetime(iso_string)
```

#### Patrón 5: Time ago

```python
# ANTES
from datetime import datetime
diff = datetime.utcnow() - created_at
if diff.days > 0:
    msg = f"{diff.days} days ago"
# ... más lógica

# DESPUÉS
from acolyte.core.utils.datetime_utils import time_ago
msg = time_ago(created_at)
```

### ⚠️ Casos Especiales

#### SQLite Timestamps

SQLite espera ISO format. Siempre usar:

```python
# Para guardar
timestamp = utc_now_iso()

# Para leer
dt = parse_iso_datetime(row['timestamp'])
```

#### Weaviate Metadata

Weaviate también espera ISO format:

```python
metadata = {
    "last_modified": utc_now_iso(),
    "indexed_at": utc_now_iso()
}
```

#### Tests con Mock Time

En archivos de test:

```python
from acolyte.core.utils.datetime_utils import set_mock_time, utc_now_testable
from datetime import datetime, timezone

def test_something_with_time():
    # Arrange
    test_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    set_mock_time(test_time)

    # Act
    result = function_that_uses_time()

    # Assert
    assert result.timestamp == test_time

    # Cleanup
    set_mock_time(None)
```

### 🚫 NO Hacer

1. **NO dejar `datetime.utcnow()`** - Siempre reemplazar
2. **NO usar `datetime.now()`** sin timezone - Usar `utc_now()`
3. **NO asumir timezone** - Siempre usar ensure_utc() si hay duda
4. **NO formatear manualmente** - Usar format_iso()

**Documentación completa**: `docs/DATETIME_IMPLEMENTATION_GUIDE.md`
