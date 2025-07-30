# 🔄 Sistema de Reindexación Automática de ACOLYTE

## 📋 Tabla de Contenidos

- [Introducción](#introducción)
- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Flujo de Trabajo Completo](#flujo-de-trabajo-completo)
- [Implementación Técnica](#implementación-técnica)
- [Configuración](#configuración)
- [API y Métodos](#api-y-métodos)
- [Eventos y Mensajes](#eventos-y-mensajes)
- [Métricas y Monitoreo](#métricas-y-monitoreo)
- [Tests](#tests)
- [Casos de Uso](#casos-de-uso)
- [Limitaciones Conocidas](#limitaciones-conocidas)
- [Mejoras Futuras](#mejoras-futuras)
- [Troubleshooting](#troubleshooting)
- [Decisiones de Diseño](#decisiones-de-diseño)

## 🎯 Introducción

El Sistema de Reindexación Automática de ACOLYTE mantiene el índice de búsqueda vectorial (Weaviate) sincronizado con los cambios en el código del proyecto. Cuando GitService detecta cambios (pull, merge, checkout), automáticamente reindexá los archivos afectados sin intervención del usuario.

### ¿Por qué es necesario?

1. **Búsquedas precisas**: El RAG necesita información actualizada
2. **Contexto correcto**: ChatService usa el índice para encontrar código relevante
3. **Eficiencia**: Solo reindexá lo que cambió, no todo el proyecto
4. **Transparencia**: El usuario no necesita acordarse de reindexar manualmente

### Características Principales

- ✅ **Automático**: Se activa con eventos Git (pull, merge, checkout)
- ✅ **Inteligente**: Identifica archivos por patrón
- ✅ **Limitado**: Respeta límites configurables para evitar sobrecarga
- ✅ **Observable**: Métricas detalladas y logging estructurado
- ✅ **Resiliente**: No bloquea indexación manual si falla
- ✅ **Asíncrono**: No bloquea operaciones Git

## 🏗️ Arquitectura del Sistema

### Componentes Involucrados

```
┌─────────────────┐     ┌──────────────┐     ┌────────────────────┐     ┌──────────────────┐
│   GitService    │────▶│   EventBus   │────▶│  ReindexService    │────▶│ IndexingService  │
│                 │     │              │     │                    │     │                  │
│ Detecta cambios │     │  Pub/Sub     │     │ Maneja eventos de  │     │ Reindexa archivos│
│ en archivos     │     │              │     │ cache_invalidation │     │                  │
└─────────────────┘     └──────────────┘     └────────────────────┘     └──────────────────┘
         │                                              │
         │                                              ▼
         ▼                                    ┌──────────────────┐
┌─────────────────┐                           │    Weaviate      │
│ Publica evento: │                           │                  │
│CacheInvalidate  │                           │ Actualiza chunks │
│ - pattern       │                           │ y embeddings     │
│ - reason        │                           └──────────────────┘
│ - source        │
└─────────────────┘
```

### Flujo de Datos

1. **GitService** detecta cambios (después de pull, merge, etc.)
2. Analiza qué archivos cambiaron
3. Publica **CacheInvalidateEvent** con patrón de archivos
4. **EventBus** distribuye el evento a suscriptores
5. **ReindexService** recibe el evento (filtrado por `target_service="indexing"`)
6. Busca archivos que coinciden con el patrón
7. Llama a **IndexingService** para reindexar los archivos encontrados
8. **IndexingService** actualiza **Weaviate** con nuevos chunks y embeddings

## 🔄 Flujo de Trabajo Completo

### 1. Detección de Cambios (GitService)

```python
# En git_service.py - después de operaciones Git
async def _handle_post_pull(self):
    # Detecta archivos modificados
    changed_files = self._get_changed_files()

    # Para cada archivo cambiado
    for file in changed_files:
        # Crea patrón para el archivo
        pattern = f"*{file.name}*"

        # Publica evento
        event = CacheInvalidateEvent(
            source="git_service",
            key_pattern=pattern,
            reason=f"File updated after pull: {file}",
            target_service="indexing"
        )
        await event_bus.publish(event)
```

### 2. Suscripción al EventBus (IndexingService)

```python
# En reindex_service.__init__()
self._unsubscribe = event_bus.subscribe(
    EventType.CACHE_INVALIDATE,
    self._handle_cache_invalidation,
    filter=lambda e: isinstance(e, CacheInvalidateEvent)
                     and e.target_service == "indexing"
)
```

### 3. Manejo del Evento

```python
async def _handle_cache_invalidation(self, event: Event):
    # Verificar si IndexingService ya está indexando
    if self.indexing_service._is_indexing:
        logger.warning("Skipping - already indexing")
        self.metrics.increment("reindexing.skipped_busy")
        return

    # Extraer patrón
    file_hint = event.key_pattern.strip("*")

    # Buscar archivos
    matching_files = await self._find_files_matching_pattern(file_hint)

    # Aplicar límite
    if len(matching_files) > self.config.get("indexing.max_reindex_files", 50):
        matching_files = matching_files[:50]

    # Reindexar
    if matching_files:
        task_id = f"reinx_{int(time.time())}_{generate_id()[:8]}"

        result = await self.indexing_service.index_files(
            files=matching_files,
            trigger="cache_invalidation",
            task_id=task_id
        )
```

### 4. Búsqueda de Archivos

```python
async def _find_files_matching_pattern(self, pattern: str) -> List[str]:
    project_root = Path(self.config.get("project.path", ".")).resolve()
    matching_files = []

    # Optimización: búsqueda específica si parece nombre completo
    if "." in pattern and not pattern.startswith("."):
        # Buscar coincidencias exactas primero
        for file_path in project_root.rglob(f"*{pattern}"):
            if self._is_valid_file(file_path):
                matching_files.append(str(file_path))
    else:
        # Búsqueda parcial más amplia
        for file_path in project_root.rglob("*"):
            if pattern.lower() in file_path.name.lower():
                if self._is_valid_file(file_path):
                    matching_files.append(str(file_path))

    return matching_files

def _is_valid_file(self, path: Path) -> bool:
    return (path.is_file() and
            self.indexing_service.is_supported_file(path) and
            not self.indexing_service.should_ignore(str(path)))
```

## 🔧 Implementación Técnica

### Estructura del CacheInvalidateEvent

```python
@dataclass
class CacheInvalidateEvent(Event):
    """Evento para invalidar cache y triggear reindexación."""
    source: str           # Ej: "git_service"
    key_pattern: str      # Ej: "*auth.py*"
    reason: str           # Ej: "Files changed after pull"
    target_service: str   # Debe ser "indexing" para IndexingService

    event_type: EventType = EventType.CACHE_INVALIDATE
```

### Generación de Task ID

```python
# Formato: reinx_<timestamp>_<short_id>
task_id = f"reinx_{int(time.time())}_{generate_id()[:8]}"

# Ejemplo: "reinx_1703123456_a1b2c3d4"
# - reinx: Prefijo para identificar reindexación
# - timestamp: Para ordenar cronológicamente
# - short_id: Para unicidad (8 chars de hex32)
```

### Trigger Type

```python
# La reindexación usa un trigger especial
trigger = "cache_invalidation"

# Otros triggers soportados:
# - "manual": Usuario solicita indexación
# - "commit": Post-commit hook
# - "pull": Post-pull (ya no usado directamente)
# - "checkout": Branch change
# - "fetch": Preparation
```

## ⚙️ Configuración

### En `.acolyte`

```yaml
indexing:
  # Límites de reindexación
  max_reindex_files: 50 # Máximo de archivos por evento

  # Configuración general que también aplica
  batch_size: 20 # Archivos por batch
  max_file_size_mb: 10 # Tamaño máximo de archivo
  concurrent_workers: 4 # Workers paralelos

  # Patrones ignorados (se respetan en reindexación)
ignore:
  patterns:
    - "*.pyc"
    - "__pycache__/"
    - ".git/"
    - "*.log"
    - "node_modules/"
    - ".venv/"
    - "*.egg-info/"
```

### Configuración No Implementada (Futura)

```yaml
# Estas configuraciones están documentadas pero NO implementadas aún
indexing:
  # Reindexación avanzada (FUTURO)
  reindex_queue_size: 100 # Cola de eventos pendientes
  reindex_cooldown_seconds: 5 # Evitar duplicados
  reindex_batch_size: 5 # Procesar en mini-batches
  pattern_cache_ttl_seconds: 60 # Cache de búsquedas
  verify_timestamps: true # Verificar si archivo cambió
```

## 📡 API y Métodos

### Métodos Públicos

No hay métodos públicos específicos para reindexación. El sistema es completamente automático.

### Métodos Internos

#### `_handle_cache_invalidation(event: Event)`

Maneja eventos de invalidación de cache.

**Parámetros**:

- `event`: CacheInvalidateEvent con patrón y razón

**Comportamiento**:

1. Verifica si ya está indexando
2. Extrae patrón del evento
3. Busca archivos coincidentes
4. Aplica límite de archivos
5. Genera task_id único
6. Llama a `index_files()` con trigger especial

**Métricas**:

- `indexing.cache_invalidations_received`
- `indexing.cache_invalidations_skipped`
- `indexing.reindex_triggered`
- `indexing.reindex_files_count`
- `indexing.reindex_success/failed`
- `indexing.cache_invalidation_errors`

#### `_find_files_matching_pattern(pattern: str) -> List[str]`

Busca archivos en el proyecto que coinciden con el patrón.

**Parámetros**:

- `pattern`: Patrón de búsqueda (ej: "auth.py", "auth", "user\_")

**Comportamiento**:

1. Si contiene "." → búsqueda exacta de nombre
2. Si no → búsqueda parcial case-insensitive
3. Respeta archivos soportados
4. Respeta patrones ignorados
5. Devuelve paths absolutos

**Optimizaciones**:

- Búsqueda específica para nombres completos
- Early exit al alcanzar límite
- Deduplicación de resultados

## 📊 Eventos y Mensajes

### Eventos Publicados

IndexingService NO publica eventos de reindexación específicos, pero sí publica `ProgressEvent` durante el proceso:

```python
ProgressEvent(
    source="indexing_service",
    operation="indexing_files",
    current=10,
    total=50,
    message="Processing: src/auth.py",
    task_id="reinx_1703123456_a1b2c3d4",
    files_skipped=5,
    chunks_created=100,
    embeddings_generated=100,
    errors=0
)
```

### Eventos Consumidos

```python
CacheInvalidateEvent(
    source="git_service",
    key_pattern="*auth.py*",
    reason="Files changed after pull",
    target_service="indexing"  # CRÍTICO: debe ser "indexing"
)
```

### Logs Importantes

```python
# Inicio de reindexación
logger.info(
    "Re-indexing files after cache invalidation",
    pattern=file_hint,
    files_count=len(matching_files),
    task_id=task_id,
    reason=event.reason
)

# Finalización exitosa
logger.info(
    "Re-indexing completed successfully",
    task_id=task_id,
    files_processed=result["files_processed"],
    chunks_created=result["chunks_created"],
    duration_seconds=result["duration_seconds"]
)

# Warnings importantes
logger.warning(
    "Too many files match pattern, limiting re-indexing",
    pattern=file_hint,
    total_matches=len(matching_files),
    limit=max_reindex_files
)
```

## 📈 Métricas y Monitoreo

### Métricas Implementadas

```python
# Contadores
indexing.cache_invalidations_received    # Total eventos recibidos
indexing.cache_invalidations_skipped     # Eventos saltados (ya indexando)
indexing.reindex_triggered               # Reindexaciones iniciadas
indexing.reindex_success                 # Reindexaciones exitosas
indexing.reindex_failed                  # Reindexaciones fallidas
indexing.cache_invalidation_errors       # Errores en el handler

# Gauges
indexing.reindex_files_count             # Archivos en última reindexación

# Timers (heredados de index_files)
indexing.index_files_total_ms            # Tiempo total de reindexación
```

### Dashboard Conceptual

```
┌─────────────────────────────────────────────┐
│          Reindexación Automática            │
├─────────────────────────────────────────────┤
│ Eventos Recibidos:        1,234            │
│ Reindexaciones:             456            │
│ Archivos Promedio:           12            │
│ Tasa de Éxito:             98.5%           │
│                                             │
│ Última Reindexación:                        │
│   Trigger: cache_invalidation               │
│   Patrón: *auth.py*                         │
│   Archivos: 3                               │
│   Duración: 2.5s                            │
│   Task ID: reinx_1703123456_a1b2c3d4       │
└─────────────────────────────────────────────┘
```

## 🧪 Tests

### Tests Unitarios Implementados

En `tests/services/test_indexing_service_reindexing.py`:

1. **test_handle_cache_invalidation_success**

   - Verifica reindexación exitosa
   - Valida archivos encontrados
   - Confirma task_id y trigger

2. **test_handle_cache_invalidation_already_indexing**

   - Verifica skip cuando ya está indexando
   - Confirma métrica de skip

3. **test_handle_cache_invalidation_no_files_found**

   - Maneja caso sin archivos coincidentes
   - No debe llamar index_files

4. **test_handle_cache_invalidation_max_files_limit**

   - Respeta límite de archivos
   - Trunca lista si excede límite

5. **test_handle_cache_invalidation_wildcard_pattern**

   - Ignora patrones "\*" (todo)
   - Evita reindexación masiva

6. **test_find_files_matching_pattern_exact_filename**

   - Búsqueda exacta de nombres
   - "auth.py" encuentra solo auth.py

7. **test_find_files_matching_pattern_partial**

   - Búsqueda parcial
   - "auth" encuentra auth.py, user_auth.py, test_auth.py

8. **test_find_files_matching_pattern_case_insensitive**

   - Insensible a mayúsculas
   - "auth" encuentra AUTH_CONFIG.py

9. **test_find_files_matching_pattern_respects_filters**

   - Respeta archivos ignorados
   - Respeta extensiones soportadas

10. **test_eventbus_integration**

    - Integración con EventBus
    - Filtrado correcto por target_service

11. **test_handle_cache_invalidation_error_handling**

    - Manejo de errores sin crash
    - Métrica de errores

12. **test_task_id_generation_uniqueness**

    - IDs únicos para cada reindexación
    - Formato correcto

13. **test_metrics_tracking**
    - Todas las métricas se registran
    - Valores correctos

### Ejecutar Tests

```bash
# Todos los tests de reindexación
poetry run pytest tests/services/test_indexing_service_reindexing.py -v

# Con coverage
poetry run pytest tests/services/test_indexing_service_reindexing.py --cov=acolyte.services.indexing_service --cov-report=html

# Test específico
poetry run pytest tests/services/test_indexing_service_reindexing.py::TestIndexingServiceReindexing::test_handle_cache_invalidation_success -v
```

## 🎯 Casos de Uso

### 1. Pull desde Repository Remoto

```
Usuario: git pull origin main
Git: Actualiza 5 archivos

GitService:
1. Detecta: auth.py, user.py, models.py modificados
2. Publica: CacheInvalidateEvent para cada archivo
3. Reason: "File updated after pull: auth.py"

IndexingService:
1. Recibe 3 eventos
2. Encuentra y reindexá los 3 archivos
3. Actualiza Weaviate con nuevos chunks

ChatService:
- Próxima búsqueda encuentra código actualizado
```

### 2. Merge de Feature Branch

```
Usuario: git merge feature/new-auth
Git: Merge con 10 archivos cambiados

GitService:
1. Detecta conflictos resueltos y archivos mergeados
2. Agrupa por directorio si son muchos
3. Publica eventos con patrones

IndexingService:
1. Procesa cada patrón
2. Límite de 50 archivos previene sobrecarga
3. Reindexá en batches de 20
```

### 3. Checkout a Otra Branch

```
Usuario: git checkout develop
Git: Cambia a branch con diferente código

GitService:
1. Detecta archivos diferentes entre branches
2. Publica eventos para archivos modificados

IndexingService:
1. Reindexá archivos que cambiaron
2. Mantiene índice sincronizado con branch actual
```

### 4. Revert de Commits

```
Usuario: git revert HEAD~3
Git: Revierte últimos 3 commits

GitService:
1. Detecta archivos afectados por revert
2. Publica eventos para reindexación

IndexingService:
1. Actualiza índice con versiones revertidas
2. ChatService usa código correcto
```

## ⚠️ Limitaciones Conocidas

### 1. No hay Queue de Eventos

**Problema**: Si está indexando, eventos se pierden
**Impacto**: Archivos no se reindecan hasta próximo cambio
**Workaround**: Usuario puede indexar manualmente

### 2. No Verifica Timestamps

**Problema**: Reindexá aunque archivo no cambió realmente
**Impacto**: Trabajo innecesario, pero no daña
**Futuro**: Comparar file.mtime con indexed_at

### 3. Búsqueda en Todo el Proyecto

**Problema**: Puede ser lento en proyectos grandes
**Impacto**: Delay en reindexación
**Mitigación**: Límite de archivos previene worst case

### 4. Sin Deduplicación de Eventos

**Problema**: Múltiples eventos rápidos para mismo archivo
**Impacto**: Reindexación duplicada
**Futuro**: Cooldown por patrón

### 5. Patrón Simple de Matching

**Problema**: No soporta glob avanzado o regex
**Impacto**: Matching menos preciso
**Actual**: Solo "\*" wildcards y búsqueda parcial

## 🚀 Mejoras Futuras

### 1. Queue de Reindexación Pendiente (Alta Prioridad)

**Problema**: Si ya está indexando, el evento se pierde.

```python
class IndexingService:
    def __init__(self):
        # ...
        self._reindex_queue: asyncio.Queue[CacheInvalidateEvent] = asyncio.Queue()
        self._queue_processor_task = None

    async def _handle_cache_invalidation(self, event: Event):
        if self._is_indexing:
            # En lugar de solo loguear, agregar a la cola
            await self._reindex_queue.put(event)
            logger.info("Added to reindex queue", pattern=event.key_pattern)
            return

        # Procesar normalmente...

    async def _process_reindex_queue(self):
        """Process pending reindex requests after current indexing."""
        while not self._reindex_queue.empty():
            try:
                event = await self._reindex_queue.get()
                await self._handle_cache_invalidation(event)
            except Exception as e:
                logger.error("Failed to process queued reindex", error=str(e))
```

### 2. Verificación de Timestamps (Alta Prioridad)

**Problema**: Re-indexa archivos que no han cambiado.

**Estado actual**: Implementado método `_filter_files_needing_reindex()` en ReindexService con TODO para completar la comparación de timestamps con Weaviate.

```python
async def _should_reindex_file(self, file_path: str) -> bool:
    """Check if file needs reindexing based on timestamps."""
    try:
        # Get file modification time
        file_stat = Path(file_path).stat()
        file_modified = datetime.fromtimestamp(file_stat.st_mtime, tz=timezone.utc)

        # Query Weaviate for last indexed time
        where_filter = {
            "path": ["file_path"],
            "operator": "Equal",
            "valueText": file_path
        }

        result = await self.weaviate.query.get("CodeChunk", ["indexed_at"])
            .with_where(where_filter)
            .with_limit(1)
            .do()

        if result and result["data"]["Get"]["CodeChunk"]:
            indexed_at = parse_iso_datetime(result["data"]["Get"]["CodeChunk"][0]["indexed_at"])

            # Only reindex if file is newer
            return file_modified > indexed_at

        # Not indexed yet
        return True

    except Exception:
        # On error, reindex to be safe
        return True
```

### 3. Optimización de Búsqueda (Media Prioridad)

**Problema**: Búsqueda recursiva en todo el proyecto puede ser lenta.

```python
async def _find_files_matching_pattern(self, pattern: str) -> List[str]:
    """Optimized file search with caching and limits."""
    cache_key = f"file_pattern:{pattern}"

    # Check cache first
    if hasattr(self, '_pattern_cache'):
        cached = self._pattern_cache.get(cache_key)
        if cached and (time.time() - cached['time']) < 60:  # 1 minute cache
            return cached['files']

    # Use pathlib's match for efficiency
    matching_files = []
    max_depth = self.config.get("indexing.max_search_depth", 10)

    # If pattern looks like path, search more specifically
    if "/" in pattern or "\\" in pattern:
        # Direct path search
        base_path = Path(pattern).parent
        pattern_glob = Path(pattern).name
    else:
        base_path = self.project_root
        pattern_glob = f"**/*{pattern}*" if "." not in pattern else f"**/{pattern}"

    # Limited depth search
    for file_path in base_path.rglob(pattern_glob):
        if self._is_supported_file(file_path) and not self._should_ignore(str(file_path)):
            matching_files.append(str(file_path))

            # Early exit if we have enough
            if len(matching_files) >= self.config.get("indexing.max_reindex_files", 50):
                break

    # Cache results
    if not hasattr(self, '_pattern_cache'):
        self._pattern_cache = {}
    self._pattern_cache[cache_key] = {'files': matching_files, 'time': time.time()}

    return matching_files
```

### 4. Logging Mejorado (Media Prioridad)

**Problema**: No hay suficiente detalle sobre qué se reindexó y por qué.

```python
async def _handle_cache_invalidation(self, event: Event):
    """Enhanced logging version."""
    start_time = time.time()

    logger.info(
        "Cache invalidation started",
        source=event.source,
        pattern=event.key_pattern,
        reason=event.reason,
        already_indexing=self._is_indexing
    )

    # ... find files ...

    logger.info(
        "Files found for reindexing",
        pattern=event.key_pattern,
        total_found=len(all_files),
        after_filtering=len(files_to_index),
        sample_files=files_to_index[:5]  # Show first 5
    )

    # ... reindex ...

    logger.info(
        "Reindexing completed",
        pattern=event.key_pattern,
        duration_seconds=time.time() - start_time,
        files_processed=result["files_processed"],
        chunks_created=result["chunks_created"],
        success_rate=f"{(1 - len(result.get('errors', [])) / max(result['files_processed'], 1)) * 100:.1f}%"
    )
```

### 5. Batch Processing Inteligente (Baja Prioridad)

**Problema**: Re-indexar muchos archivos puede bloquear indexación normal.

```python
async def _handle_cache_invalidation(self, event: Event):
    """Process in smaller batches to allow interleaving."""
    # ... find files ...

    if len(matching_files) > 10:
        # Process in batches
        batch_size = 5
        for i in range(0, len(matching_files), batch_size):
            batch = matching_files[i:i + batch_size]

            # Allow other operations between batches
            await asyncio.sleep(0.1)

            await self.index_files(
                files=batch,
                trigger="cache_invalidation",
                task_id=f"{task_id}_batch_{i//batch_size}"
            )
    else:
        # Small number, process all at once
        await self.index_files(files=matching_files, trigger="cache_invalidation", task_id=task_id)
```

### 6. Deduplicación de Eventos (Media Prioridad)

**Problema**: Múltiples eventos rápidos para el mismo patrón.

```python
class IndexingService:
    def __init__(self):
        # ...
        self._recent_patterns: Dict[str, float] = {}  # pattern -> timestamp
        self._pattern_lock = asyncio.Lock()

    async def _handle_cache_invalidation(self, event: Event):
        async with self._pattern_lock:
            # Check if we recently processed this pattern
            last_processed = self._recent_patterns.get(event.key_pattern, 0)
            if time.time() - last_processed < 5:  # 5 second cooldown
                logger.debug(
                    "Skipping duplicate pattern",
                    pattern=event.key_pattern,
                    seconds_since_last=time.time() - last_processed
                )
                return

            self._recent_patterns[event.key_pattern] = time.time()

        # Process normally...
```

### 📊 Métricas Adicionales Sugeridas

```python
# Nuevas métricas para mejor observabilidad
self.metrics.record("indexing.reindex_search_time_ms", search_duration * 1000)
self.metrics.gauge("indexing.reindex_queue_size", self._reindex_queue.qsize())
self.metrics.increment("indexing.reindex_cache_hits")
self.metrics.increment("indexing.reindex_files_skipped_uptodate")
self.metrics.histogram("indexing.reindex_batch_size", len(files))
```

### 🧪 Tests Adicionales Sugeridos

1. **Test de concurrencia**: Múltiples eventos simultáneos
2. **Test de performance**: Con miles de archivos
3. **Test de resiliencia**: Weaviate no disponible durante reindexación
4. **Test de deduplicación**: Eventos duplicados rápidos
5. **Test de integración E2E**: GitService → IndexingService completo

### 🔒 Consideraciones de Seguridad

1. **Path traversal**: Validar que los archivos encontrados están dentro del proyecto
2. **Resource exhaustion**: Límites estrictos en búsqueda recursiva
3. **Event flooding**: Rate limiting de eventos por patrón

### 📝 Configuración Sugerida

```yaml
# En .acolyte
indexing:
  # Reindexación
  max_reindex_files: 50
  max_search_depth: 10
  reindex_batch_size: 5
  reindex_cooldown_seconds: 5
  pattern_cache_ttl_seconds: 60

  # Queue
  max_queue_size: 100
  queue_process_delay_seconds: 1
```

### 🎯 Prioridad de Implementación

1. **Alta**: Queue de reindexación (evita pérdida de eventos)
2. **Alta**: Verificación de timestamps (evita trabajo innecesario)
3. **Media**: Logging mejorado (debugging)
4. **Media**: Deduplicación de eventos (eficiencia)
5. **Baja**: Optimización de búsqueda (performance)
6. **Baja**: Batch processing (UX)

## 🔧 Troubleshooting

### Problema: No se están reindexando archivos

**Verificar**:

1. GitService está publicando eventos:

   ```python
   # Agregar log temporal en git_service.py
   logger.info("Publishing cache invalidation", pattern=pattern)
   ```

2. IndexingService está suscrito:

   ```python
   # Verificar en __init__
   assert self._unsubscribe is not None
   ```

3. Filtro de eventos es correcto:
   ```python
   # El evento DEBE tener target_service="indexing"
   ```

**Solución**:

- Verificar logs en nivel DEBUG
- Confirmar que Weaviate está disponible
- Indexar manualmente como workaround

### Problema: Se reindexa demasiado

**Síntomas**:

- Mismos archivos se reindecan repetidamente
- Alto uso de CPU/memoria

**Verificar**:

```yaml
# En .acolyte
indexing:
  max_reindex_files: 50 # Reducir si es necesario
```

**Solución**:

- Reducir `max_reindex_files`
- Implementar deduplicación (mejora futura)
- Revisar patrones de GitService

### Problema: Eventos perdidos

**Síntomas**:

- Archivo cambió pero no se reindexó
- Logs muestran "already indexing"

**Verificar**:

```bash
# Buscar en logs
grep "Skipping - already indexing" acolyte.log
```

**Solución temporal**:

- Esperar que termine indexación actual
- Indexar manualmente archivo específico
- Implementar queue (mejora futura)

### Problema: Búsqueda lenta de archivos

**Síntomas**:

- Reindexación tarda mucho en empezar
- CPU alta durante búsqueda

**Verificar**:

- Tamaño del proyecto
- Patrones muy genéricos ("_._")

**Solución**:

- Patrones más específicos en GitService
- Excluir directorios grandes en .acolyteignore
- Implementar cache de búsqueda (mejora futura)

## 📐 Decisiones de Diseño

### 1. ¿Por qué no reindexar todo siempre?

**Decisión**: Solo reindexar archivos específicos
**Razón**:

- Eficiencia: Proyecto grande = mucho tiempo
- UX: Usuario no espera delays después de git pull
- Recursos: Menos CPU/memoria/embeddings API calls

### 2. ¿Por qué usar EventBus?

**Decisión**: Comunicación asíncrona vía eventos
**Razón**:

- Desacoplamiento: GitService no conoce IndexingService
- Extensibilidad: Otros servicios pueden escuchar
- Asíncrono: No bloquea operaciones Git

### 3. ¿Por qué límite de archivos?

**Decisión**: max_reindex_files = 50
**Razón**:

- Prevenir DoS accidental
- Merge grande no bloquea sistema
- Balance entre completitud y performance

### 4. ¿Por qué no verificar timestamps?

**Decisión**: Reindexar sin verificar si cambió
**Razón**:

- Simplicidad inicial
- Git dice que cambió = probablemente cambió
- Verificación requiere query a Weaviate (latencia)
- Futuro: Implementar cuando sea problema real

### 5. ¿Por qué task_id con timestamp?

**Decisión**: `reinx_{timestamp}_{id}`
**Razón**:

- Debugging: Fácil ver cuándo ocurrió
- Ordenable: Sort cronológico natural
- Único: Timestamp + ID previene colisiones
- Identificable: Prefijo "reinx" claro

### 6. ¿Por qué no usar git hooks directamente?

**Decisión**: GitService con GitPython
**Razón**:

- Portabilidad: Funciona en Windows/Mac/Linux
- Control: Manejo de errores en Python
- Integración: Mismo proceso, no scripts externos
- Testing: Más fácil mockear que hooks reales

## 📚 Referencias

### Archivos Clave

- `services/indexing_service.py`: Implementación principal
- `services/git_service.py`: Detección de cambios
- `core/events.py`: Definición de eventos
- `tests/services/test_indexing_service_reindexing.py`: Tests completos

### Documentación Relacionada

- Esta sección de "Mejoras Futuras": Contiene todas las mejoras sugeridas
- `services/README.md`: Contexto del módulo services
- `PROMPT.md`: Sistema de eventos y arquitectura general

### Configuración

- `.acolyte`: Configuración del proyecto
- `.acolyteignore`: Patrones a ignorar

---

_Documento creado para ACOLYTE - Sistema de reindexación automática v1.0_
