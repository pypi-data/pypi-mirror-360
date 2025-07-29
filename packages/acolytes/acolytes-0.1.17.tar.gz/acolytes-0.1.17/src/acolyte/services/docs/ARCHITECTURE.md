# 🏗️ Arquitectura del Módulo Services

## Principios de Diseño

1. **Lógica Python pura**: Sin endpoints HTTP, solo coordinación interna
2. **Inyección de dependencias**: ChatService acepta servicios externos para evitar imports circulares
3. **Persistencia dual**: SQLite (resúmenes + metadata) + Weaviate (búsqueda semántica)
4. **Git reactivo**: Servicios reaccionan a cambios del usuario, NO fetch automático (Decisión #11)
5. **Retry logic robusto**: ConversationService (SQLite) y ChatService (Ollama) con backoff exponencial
6. **Cache coordinado**: Sistema de invalidación via EventBus entre servicios

## Estructura de Archivos

```
services/
├── __init__.py              # Exports de los 5 servicios
├── conversation_service.py  # Gestión de conversaciones (SQLite + Weaviate)
├── task_service.py          # Agrupación de sesiones en tareas
├── chat_service.py          # Orquestación del flujo de chat
├── indexing_service.py      # Pipeline de indexación completo
└── git_service.py           # Operaciones Git internas reactivas
```

## Fuentes de Verdad

- **`.acolyte`** = Configuración (cómo funciona ACOLYTE)
- **SQLite** = Datos persistentes (conversaciones, tareas, sesiones)
- **Weaviate** = Índice de búsqueda (derivado de SQLite)

## Decisiones Clave Históricas

1. **Resúmenes inteligentes**: SQLite guarda resúmenes (~90% reducción), NO conversaciones completas
2. **Generación de resúmenes**: Semantic genera resúmenes extractivos después de cada interacción
3. **Modificación de código vía Cursor**: ACOLYTE genera respuestas naturales, Cursor decide si aplicar
4. **Sesiones relacionadas**: `related_sessions` mantiene continuidad temporal entre chats
5. **Persistencia dual**: SQLite (resúmenes + metadata) + Weaviate (código validado + embeddings)
6. **Jerarquía Task > Session > Message**: Tasks se crean automáticamente al detectar nuevo contexto
7. **Flujo automático al iniciar chat**: ACOLYTE carga contexto previo automáticamente
8. **System Prompt dinámico**: Dos capas - Base (Modelfile) + Dinámico por proyecto (Semantic)
9. **Archivos subidos**: Indexación inteligente contextual
10. **Distribución dinámica de tokens**: Ajuste automático según necesidad
11. **Git reactivo**: ACOLYTE NO hace fetch automático. Reacciona cuando usuario hace cambios
12. **total_tokens**: Contador interno de tokens originales para estadísticas y optimización
13. **Decisiones técnicas**: Nueva tabla `technical_decisions` con detección automática por patrones

## Decisiones de Esquemas de BD

1. **IDs compatibles**: SQLite y Python usan `secrets.token_hex(16)`
2. **session_id es UNIQUE**: Necesario para Foreign Keys desde task_sessions
3. **Tipos en MAYÚSCULAS en SQLite**: Python usa `.upper()` al insertar
4. **Vectorizer="none" en Weaviate**: Embeddings calculados externamente con UniXcoder
5. **Solo resúmenes en messages**: role="turn_summary" para cumplir Decisión #1

## Arquitectura de Resúmenes (Decisión #35)

```python
# Usar ConversationService directamente
from acolyte.services import ConversationService
service = ConversationService()

# Guardar resúmen de turno de conversación
await service.save_conversation_turn(
    session_id="abc123",
    user_message="mensaje original del usuario",
    assistant_response="respuesta original del asistente",
    summary="resúmen extractivo de Semantic",  # ~90% reducción
    tokens_used=1800
)
```

**Diseño actual**:

- Una sesión = UNA fila en conversations con role='system'
- El campo `content` acumula resúmenes: "Resúmen1 | Resúmen2 | ..."
- `session_id` es PRIMARY KEY (sin campo 'id')
- `total_tokens` cuenta tokens ORIGINALES procesados

## Patrón Strategy para IDs

Todos los servicios se benefician del patrón Strategy unificado para identificación de modelos implementado en `/models/base.py`.

### Interfaz Unificada

```python
from acolyte.models.base import get_model_primary_key, Identifiable

# Funciona con cualquier modelo (Chunk, Conversation, Task, etc.)
def process_any_model(model: Identifiable):
    pk = model.primary_key         # chunk.id o conversation.session_id
    field = model.primary_key_field # "id" o "session_id"

    # O usando helper functions
    pk = get_model_primary_key(model)
    field = get_model_primary_key_field(model)
```

### Cambios en BD

```python
# Cambio en schema BD
# ANTES: id TEXT PRIMARY KEY, session_id TEXT NOT NULL UNIQUE
# DESPUÉS: session_id TEXT PRIMARY KEY (sin redundancia)

# Cambio en ConversationService
# ANTES: INSERT INTO conversations (id, session_id, ...) VALUES (?, ?, ...)
# DESPUÉS: INSERT INTO conversations (session_id, ...) VALUES (?, ...)
```

### Beneficios

- Código más limpio: Sin lógica condicional por tipo de modelo
- Type safety: MyPy valida protocolo `Identifiable`
- Mantenimiento: Cambios centralizados en `base.py`
- Consistencia: Todos los IDs siguen el mismo formato
- Debuggeabilidad: Logs uniformes sin importar el tipo de modelo
- Extensibilidad: Nuevos modelos automáticamente compatibles

## Sistema IDGenerator Centralizado

**PROBLEMA RESUELTO**: Services tenía duplicación de lógica de generación de IDs.

**SOLUCIÓN IMPLEMENTADA**:

```python
# ANTES - Duplicación en cada service
import secrets
session_id = secrets.token_hex(16)

# AHORA - Sistema centralizado
from acolyte.core.id_generator import generate_id
session_id = generate_id()  # Formato hex32 estándar
```

**Archivos actualizados**:

- `conversation_service.py`: Línea 60 - `session_id = generate_id()`
- `task_service.py`: Líneas 38, 216 - `task_id = generate_id()`, `decision_id = generate_id()`

## Sistema de Invalidación de Cache Coordinado

### Tipos de Cache

1. **Cache Local de GitService** (`_repo_cache`)

   - Qué cachea: El objeto `Repo` de GitPython
   - Por qué: Evita recargar el repositorio en cada operación
   - Invalidación: TTL de 5 minutos (automática)
   - NO necesita eventos: Es un cache interno del servicio

2. **Cache de Búsquedas en HybridSearch** (`SearchCache`)
   - Qué cachea: Resultados de búsquedas (chunks encontrados)
   - Por qué: Evita búsquedas repetidas costosas
   - Invalidación: Sistema de eventos coordinado
   - SÍ necesita eventos: Debe invalidarse cuando cambian archivos

### Flujo de Invalidación

```
1. GitService detecta cambios (después de pull/commit/checkout)
   ↓
2. GitService publica CacheInvalidateEvent via EventBus
   ↓
3. ConversationService recibe el evento (está suscrito)
   ↓
4. ConversationService llama a HybridSearch.invalidate_cache()
   ↓
5. HybridSearch invalida su SearchCache
```

### Implementación

```python
# GitService publica eventos cuando detecta cambios
await self._publish_cache_invalidation(
    reason="Changes from other developers detected",
    files=[f for change in changes for f in change["files"]]
)

# ConversationService se suscribe a eventos de invalidación
self._cache_subscription = event_bus.subscribe(
    EventType.CACHE_INVALIDATE,
    self._handle_cache_invalidation,
    filter=lambda e: e.target_service in ["conversation", "all"]
)

# ConversationService invalida cache de HybridSearch
async def _handle_cache_invalidation(self, event: CacheInvalidateEvent):
    if self.hybrid_search and hasattr(self.hybrid_search, 'invalidate_cache'):
        if event.key_pattern == "*":
            self.hybrid_search.invalidate_cache()
        else:
            self.hybrid_search.invalidate_cache(pattern=event.key_pattern)
```

### Eventos de Invalidación

Los eventos `CacheInvalidateEvent` incluyen:

- **source**: Servicio que origina el evento
- **target_service**: Servicio(s) objetivo ("all" para todos)
- **key_pattern**: Patrón de archivos afectados (ej: "_auth.py_")
- **reason**: Razón de la invalidación

## Consumo de GitMetadata Evolucionada

Todos los servicios aprovechan la GitMetadata completa para análisis y contexto inteligente.

### conversation_service.py

- **Contexto Rico en Búsquedas**: Usa `git_metadata.stability_score` para priorizar chunks de código estable
- **Filtraje Inteligente**: Excluye chunks de archivos muy volátiles (`code_volatility_index > 0.8`)
- **Contexto de Colaboración**: Menciona quién escribió el código usando `contributors`

```python
# En get_session_context()
if chunk.metadata.git_metadata:
    context += f"Este código lo escribió principalmente {main_author} "
    if chunk.metadata.git_metadata.is_actively_developed:
        context += "y está en desarrollo activo."
    if chunk.metadata.git_metadata.stability_score < 0.5:
        context += "⚠️ Código volátil, posibles cambios frecuentes."
```

### task_service.py

- **Detección de Decisiones Arquitectónicas**: Usa campos Git para identificar patrones
- **Análisis de Patrones de Cambio**: `merge_conflicts_count` indica archivos problemáticos
- **Contexto de Estabilidad**: `stability_score` y `code_volatility_index` evalúan madurez

```python
# En detect_technical_decision()
if git_metadata.get_merge_conflicts_count() > 5:
    decision.impact_level = min(5, decision.impact_level + 1)

if git_metadata.get_code_volatility_index() > 0.7:
    await self._analyze_potential_architectural_change(file_path)
```

### chat_service.py

- **System Prompt Enriquecido**: Incluye información de estabilidad y actividad del código
- **Alertas de Colaboración**: Avisa cuando código tiene múltiples contribuyentes activos
- **Contexto Temporal**: Menciona si el código es nuevo (`file_age_days < 30`) o legacy
- **Detección de Archivos Problemáticos**: Usa `merge_conflicts_count` y `code_volatility_index`

```python
# En build_dynamic_context()
git_context = []
for chunk in selected_chunks:
    if chunk.metadata.git_metadata:
        gm = chunk.metadata.git_metadata

        if gm.get_is_actively_developed():
            git_context.append(f"{chunk.metadata.file_path}: desarrollo activo")

        if gm.get_merge_conflicts_count() > 3:
            git_context.append(f"{chunk.metadata.file_path}: 🔥 historial de conflictos")
```

### indexing_service.py

- **Priorización por Estabilidad**: Archivos estables se indexan con mayor prioridad
- **Detección de Archivos Problemáticos**: Identifica archivos que necesitan atención
- **Optimización de Batch**: Agrupa archivos por estabilidad para procesamiento eficiente

```python
# En prioritize_indexing_queue()
stable_files = []
problematic_files = []
normal_files = []

for file_info in files:
    if file_info.git_metadata:
        gm = file_info.git_metadata

        if gm.get_stability_score() > 0.8 and gm.get_merge_conflicts_count() == 0:
            stable_files.append(file_info)
        elif gm.get_code_volatility_index() > 0.7 or gm.get_merge_conflicts_count() > 3:
            problematic_files.append(file_info)

# Procesar primero archivos estables
queue = stable_files + problematic_files + normal_files
```

### git_service.py

- **Detección de Archivos Conflictivos**: Usa `merge_conflicts_count` para anticipar problemas
- **Análisis de Volatilidad**: `code_volatility_index` para alertas de archivos cambiantes
- **Contexto de Notificaciones**: Personaliza mensajes según el historial del archivo
- **Detección de Reorganizaciones**: `directories_restructured` para contexto de movimientos

```python
# En generate_change_notification()
notification_parts = []

if git_metadata.get_code_volatility_index() > 0.8:
    notification_parts.append("⚡ Archivo muy volátil, cambios frecuentes.")
elif git_metadata.get_stability_score() > 0.9:
    notification_parts.append("🛡️ Archivo muy estable, revisar cambios cuidadosamente.")

if git_metadata.get_merge_conflicts_count() > 3:
    notification_parts.append("⚠️ Historial de conflictos - especial atención al merge.")

notification = base_message + " " + " ".join(notification_parts)
```

## Patrones de Implementación

### Logger Global Singleton
**Patrón obligatorio**: `from acolyte.core.logging import logger`
- NUNCA crear instancias de AsyncLogger
- Un solo logger compartido para todo el sistema

### MetricsCollector Sin Namespace
**Uso correcto**: `self.metrics = MetricsCollector()` sin parámetros
- Los módulos incluyen namespace en el nombre de la métrica
- Ejemplo: `self.metrics.increment("services.conversation.sessions_created")`

### Datetime Centralization
**Helpers obligatorios**: `from acolyte.core.utils.datetime_utils import utc_now, utc_now_iso`
- Para timestamps usar `utc_now()` NO `datetime.utcnow()`
- Para persistencia usar `utc_now_iso()`
