# 📚 API Reference - Módulo Services

## conversation_service.py

### Clase ConversationService

#### Métodos Principales

##### `create_session(initial_message: str) → str`
Crea nueva sesión con ID único y busca sesiones relacionadas automáticamente.

**Parámetros:**
- `initial_message`: Mensaje inicial del usuario

**Retorna:**
- `str`: session_id generado con formato hex32

**Características:**
- Usa IDGenerator centralizado con `generate_id()`
- Busca automáticamente sesiones relacionadas por similitud semántica
- Inicializa metadata con timestamps

##### `save_conversation_turn(session_id: str, user_message: str, assistant_response: str, summary: str, tokens_used: int, task_checkpoint_id: Optional[str] = None) → None`
Guarda resumen del turno (~90% reducción) y actualiza total_tokens acumulativo.

**Parámetros:**
- `session_id`: ID de la sesión actual
- `user_message`: Mensaje original del usuario
- `assistant_response`: Respuesta original del asistente
- `summary`: Resumen extractivo generado por Semantic
- `tokens_used`: Tokens originales procesados
- `task_checkpoint_id`: ID de la tarea asociada (opcional)

**Características:**
- Solo guarda resúmenes en messages (role="turn_summary")
- Concatena resúmenes manteniendo últimos 4 turnos
- Compression ratio basado en tokens, no caracteres
- SmartTokenCounter integrado para métricas precisas

##### `find_related_sessions(query: str, current_session_id: str, limit: int = 10) → List[Dict[str, Any]]`
Busca sesiones relacionadas usando RAG híbrido (70% semántico, 30% léxico).

**Parámetros:**
- `query`: Texto a buscar
- `current_session_id`: Sesión actual para excluir
- `limit`: Máximo de resultados

**Retorna:**
- Lista de sesiones con metadata y score de similitud

**Características:**
- Usa HybridSearch del módulo RAG
- Threshold de similitud: 0.7
- Fallback a SQLite si falla Weaviate

##### `get_session_context(session_id: str, include_related: bool = True) → Dict[str, Any]`
Recupera contexto completo con resúmenes, sesiones relacionadas, tarea y decisiones.

**Parámetros:**
- `session_id`: ID de la sesión
- `include_related`: Si incluir sesiones relacionadas

**Retorna:**
- Diccionario con contexto completo:
  - `session`: Datos de la sesión
  - `messages`: Resúmenes concatenados
  - `related_sessions`: Sesiones similares
  - `task`: Tarea activa si existe
  - `task_summary`: Resumen rico usando get_summary()
  - `decision_summaries`: Decisiones técnicas

**Características:**
- Usa get_summary() para contexto rico
- Crea objetos TaskCheckpoint y TechnicalDecision desde BD
- Fallback robusto si falla creación de objetos

##### `search_conversations(request: ConversationSearchRequest) → List[ConversationSearchResult]`
Búsqueda semántica con modelos tipados Pydantic para validación automática.

**Parámetros:**
- `request`: ConversationSearchRequest con validación automática

**Retorna:**
- Lista de ConversationSearchResult tipados

**Características:**
- Type safety con Pydantic
- Validación automática de request
- Mejor integración con API

##### `get_last_session() → Optional[Dict[str, Any]]`
Obtiene última sesión para continuidad automática.

##### `complete_session(session_id: str) → None`
Marca sesión como completada actualizando metadata.

##### `invalidate_cache_for_file(file_path: str) → None`
Invalida cache relacionado con archivo modificado publicando eventos.

#### Métodos Internos

##### `_execute_with_retry(operation_name: str, db_operation: Callable, *args, max_attempts: int = 3) → Any`
Retry logic robusto para operaciones SQLite con backoff exponential.

**Características:**
- Exponential backoff: 0.5s, 1s, 2s
- Usa `is_retryable()` para locks y timeouts
- Métricas: `db_retries_attempted`, `db_retries_successful`

##### `_fallback_search_typed(query: str, exclude_session_id: Optional[str], limit: int, time_range: Optional[tuple], request: ConversationSearchRequest) → List[ConversationSearchResult]`
Búsqueda fallback en SQLite retornando modelos tipados.

### Configuración

Lee desde `.acolyte`:
- `limits.max_related_sessions`: Máximo de sesiones relacionadas (default: 10)
- `limits.related_sessions_chain`: Longitud cadena de continuidad (default: 5)  
- `limits.max_summary_turns`: Turnos a mantener en resumen (default: 4)

---

## task_service.py

### Clase TaskService

#### Métodos Principales

##### `create_task(title: str, description: str, task_type: TaskType, initial_session_id: str) → str`
Crea nueva tarea que agrupa múltiples sesiones relacionadas.

**Parámetros:**
- `title`: Título descriptivo
- `description`: Descripción detallada
- `task_type`: IMPLEMENTATION, DEBUGGING, REFACTORING, etc.
- `initial_session_id`: Primera sesión asociada

**Retorna:**
- `str`: task_id generado

**Características:**
- Usa `generate_id()` para IDs hex32
- Crea relación inicial en task_sessions
- Detecta automáticamente tipo si no se especifica

##### `associate_session_to_task(task_id: str, session_id: str) → None`
Asocia sesión a tarea existente con relación many-to-many.

##### `get_task_full_context(task_id: str) → Dict[str, Any]`
Recupera contexto completo con sesiones, decisiones, timeline y archivos clave.

**Retorna:**
- Diccionario con:
  - `task`: Datos de la tarea
  - `sessions`: Todas las sesiones asociadas
  - `decisions`: Decisiones técnicas
  - `timeline`: Cronología de eventos
  - `key_files`: Archivos modificados frecuentemente

##### `save_technical_decision(decision: TechnicalDecision) → None`
Guarda decisión técnica detectada con validación de IDs requeridos.

**Parámetros:**
- `decision`: Objeto TechnicalDecision completo

**Características:**
- Valida que decision tenga task_id y session_id
- Usa `generate_id()` para el ID de la decisión
- Serializa alternatives_considered como JSON

##### `find_active_task(user_id: str = "default") → Optional[TaskCheckpoint]`
Encuentra tarea activa del usuario (siempre "default" en mono-usuario).

##### `complete_task(task_id: str) → None`
Marca tarea como completada actualizando status.

##### `get_recent_decisions(task_id: str, limit: int = 5) → List[TechnicalDecision]`
Obtiene objetos TechnicalDecision recientes para usar get_summary().

**Características:**
- Convierte filas de BD a objetos TechnicalDecision
- Parsea alternatives_considered como JSON
- Manejo robusto de errores con fallback

---

## chat_service.py

### Clase ChatService

#### Constructor

```python
def __init__(self,
    conversation_service: Optional[ConversationService] = None,
    task_service: Optional[TaskService] = None,
    semantic_analyzer: Optional[Any] = None,
    rag_service: Optional[Any] = None,
    git_service: Optional[GitService] = None,
    debug: bool = False)
```

**Características:**
- Inyección de dependencias para evitar imports circulares
- Todos los servicios son opcionales con fallback
- Debug mode configurable por instancia

#### Métodos Principales

##### `process_message(message: str, session_id: Optional[str] = None, debug: Optional[bool] = None) → Dict[str, Any]`
Procesa mensaje completo orquestando análisis, búsqueda, generación y persistencia.

**Parámetros:**
- `message`: Mensaje del usuario
- `session_id`: ID de sesión existente o None para nueva
- `debug`: Override del debug mode de la instancia

**Retorna:**
- Diccionario con:
  - `response`: Respuesta generada
  - `session_id`: ID de la sesión
  - `tokens_used`: Tokens procesados
  - `debug_info`: Info de debug si está activado

**Flujo completo:**
1. Análisis de intención con Semantic
2. Detección de nueva tarea
3. Búsqueda híbrida con RAG
4. Compresión contextual si query específico
5. Construcción de System Prompt
6. Generación con Ollama (con retry)
7. Generación de resumen
8. Detección de decisiones técnicas
9. Persistencia en ConversationService

##### `get_active_session_info() → Dict[str, Any]`
Obtiene información de sesión activa para dashboard o status checks.

#### Métodos Helper Críticos

##### `_handle_new_chat() → str`
Gestión automática de contexto previo (Decisión #7).

**Características:**
- Carga tarea activa si existe
- Si no hay tarea, carga última sesión
- No pregunta, asume continuidad

##### `_generate_with_retry(system_prompt: str, user_message: str, context_chunks: list, max_tokens: int, max_attempts: int = 3) → str`
Retry logic robusto para Ollama con backoff exponencial.

**Características:**
- 3 intentos con backoff: 1s, 2s, 4s
- Usa `is_retryable()` de excepciones
- Métricas: `ollama_retries_attempted`, `ollama_retries_successful`

##### `_get_project_info() → Dict[str, Any]`
Obtiene info del proyecto desde .acolyte + integración GitService.

**Retorna:**
- `name`: Nombre del proyecto
- `stack`: Stack tecnológico (lista plana)
- `structure`: Estructura de directorios
- `branch`: Branch actual si GitService disponible
- `recent_files`: Archivos modificados recientemente

##### `_infer_task_type(message: str) → TaskType`
Inferencia inteligente de TaskType usando patterns.

**Patterns:**
- IMPLEMENTATION: "implementar", "crear", "añadir"
- DEBUGGING: "error", "bug", "arreglar"
- REFACTORING: "refactorizar", "mejorar", "optimizar"
- RESEARCH: "investigar", "analizar", "estudiar"

### Correcciones Importantes

#### Flujo de Chunks para Resúmenes

```python
# Semantic necesita chunks para extraer entidades
summary = await self.semantic.generate_summary(
    user_msg=message,
    assistant_msg=response,
    context_chunks=chunks  # NECESARIO para extraer entidades
)
```

#### TokenBudgetManager

```python
# Semantic retorna objeto TokenDistribution
distribution = await self.semantic.analyze_query_intent(query)

# TokenBudgetManager espera string, usar solo el tipo
self.token_manager.allocate_for_query_type(distribution.type)  # .type
```

#### Conversión DetectedDecision → TechnicalDecision

```python
# Semantic detecta decisión pero sin IDs
detected = await self.semantic.detect_technical_decision(message)

if detected:
    # ChatService completa los IDs necesarios
    decision = TechnicalDecision(
        decision_type=detected.decision_type,
        title=detected.title,
        description=detected.description,
        rationale=detected.rationale,
        alternatives_considered=detected.alternatives_considered,
        impact_level=detected.impact_level,
        session_id=self.current_session.id,  # ChatService tiene el ID
        task_id=self.current_task.id if self.current_task else None
    )

    # Guardar vía TaskService
    await self.task_service.save_technical_decision(decision)
```

---

## indexing_service.py

### Clase IndexingService

#### Estado: 95% Implementado

Pipeline completo implementado, solo falta re-indexación automática por patrón.

#### Métodos Principales

##### `index_files(files: List[str], trigger: str = "manual", task_id: Optional[str] = None) → Dict[str, Any]`
Orquesta chunking, enrichment, embeddings y Weaviate con task_id opcional para progreso WebSocket.

**Parámetros:**
- `files`: Lista de archivos a indexar
- `trigger`: Origen de la indexación
  - 'commit': Desde post-commit hook
  - 'pull': Desde post-merge hook (invalida cache)
  - 'checkout': Desde post-checkout hook
  - 'fetch': Desde post-fetch hook
  - 'manual': Solicitado por usuario
- `task_id`: ID opcional para notificaciones WebSocket

**Retorna:**
- Diccionario con estadísticas:
  - `indexed`: Archivos indexados exitosamente
  - `failed`: Archivos que fallaron
  - `chunks_created`: Total de chunks generados
  - `embeddings_generated`: Total de embeddings

**Características:**
- Progress tracking via EventBus con task_id
- Batch processing: 20 archivos por batch
- 4 workers paralelos configurables
- Respeta .acolyteignore

#### Pipeline Completo

##### `_chunk_files(files: List[str]) → List[Chunk]`
Usa AdaptiveChunker de RAG cuando está disponible.

**Características:**
- Análisis AST para Python con detección de complejidad
- Respeto de límites naturales del código
- Overlap inteligente que preserva contexto
- Fallback a implementación simple si no disponible

##### `_detect_chunk_type(content: str, file_extension: str) → ChunkType`
Usa regex patterns para detectar 18 tipos:
- FUNCTION, METHOD, CLASS, CONSTRUCTOR
- INTERFACE, TYPE_DEFINITION, ENUM
- IMPORT_BLOCK, CONFIG, CONSTANT
- DECORATOR, ASYNC_FUNCTION, GENERATOR
- PROPERTY, ABSTRACT_METHOD, STATIC_METHOD
- MIXIN, TRAIT

##### `_process_batch(files: List[str], trigger: str) → Dict[str, Any]`
Procesa batch completo: chunking → enrichment → embeddings → Weaviate.

##### `_prepare_weaviate_object(chunk: Chunk, enrichment_metadata: Dict) → Dict[str, Any]`
Combina chunk + metadata Git + patterns para objeto Weaviate final.

**Campos generados:**
- Todos los campos del chunk original
- Metadata Git aplanada (git_last_author, git_stability_score, etc.)
- Patterns detectados (is_test_code, has_error_handling, etc.)
- chunk_type en MAYÚSCULAS para compatibilidad BD

##### `_index_to_weaviate(data_object: Dict, vector: List[float]) → None`
Indexación directa en Weaviate con embeddings.

**Características:**
- Soporta EmbeddingVector y listas Python
- Manejo de errores con logging detallado
- Usa to_weaviate() cuando disponible

##### `_filter_files(files: List[str]) → List[str]`
Respeta .acolyteignore, valida tamaño y extensiones.

**Validaciones:**
- Tamaño máximo: 10MB por archivo
- 40+ extensiones soportadas
- Patterns de .acolyteignore

##### `_notify_progress(progress: IndexingProgress, task_id: Optional[str] = None, files_skipped: int = 0, chunks_created: int = 0, embeddings_generated: int = 0, errors_count: int = 0) → None`
Publica ProgressEvent via EventBus con estadísticas completas.

**Características:**
- Incluye task_id para filtrado en WebSocket
- Estadísticas reales: files_skipped, chunks_created, etc.
- current_file del objeto progress
- WebSocket recibe estadísticas reales
- Logging inteligente solo en intervalos del 10%

---

## git_service.py

### Clase GitService

#### Métodos Principales

##### `detect_changes_from_others() → List[Dict[str, Any]]`
Detecta cambios de otros desarrolladores DESPUÉS de pull/fetch.

**Retorna:**
- Lista de diccionarios con:
  - `type`: Tipo de cambio (add, modify, delete)
  - `files`: Archivos afectados
  - `author`: Autor del cambio
  - `date`: Fecha del cambio

**Características:**
- Solo detecta después de que el usuario hace pull
- Compara con último estado conocido
- Identifica cambios por otros desarrolladores

##### `analyze_potential_conflicts(files_to_modify: List[str]) → Dict[str, Any]`
Analiza conflictos potenciales con severity 0-10 y sugerencias.

**Retorna:**
- Diccionario con:
  - `severity`: 0-10 basado en overlaps y autores
  - `conflicts`: Lista de conflictos detectados
  - `suggestions`: Sugerencias para resolver

##### `get_co_modification_patterns(file_path: str, days_back: int = 30) → List[Tuple[str, float]]`
Encuentra archivos que cambian juntos para grafo neuronal.

**Retorna:**
- Lista de tuplas (archivo, frecuencia)

##### `notify_in_chat(notification_type: str, data: Dict[str, Any]) → str`
Genera notificación amigable para mostrar en chat.

**Tipos soportados:**
- `file_updated`: "Veo que actualizaste auth.py..."
- `potential_conflicts`: Conflictos con severity
- `branch_changed`: Cambio de rama
- `others_changes`: Cambios de otros devs

#### Sistema de Cache y Eventos

##### `@property repo → Repo`
Cache con TTL de 5 minutos + lazy loading.

**Características:**
- Detecta cambios externos automáticamente
- Se recarga cuando expira TTL
- Thread-safe con locks

##### `_publish_cache_invalidation(reason: str, files: List[str], target_services: List[str] = ["conversation", "indexing", "enrichment"]) → None`
Integración completa con EventBus.

**Publica CacheInvalidateEvent con:**
- `source`: "git_service"
- `target_service`: Servicios objetivo
- `key_pattern`: Patrón de archivos
- `reason`: Razón de invalidación

##### `invalidate_repo_cache() → None`
Invalida cache del repo cuando se detectan cambios externos.

#### Notificaciones Específicas

- `_notify_file_updated(data: Dict) → str`: Archivos actualizados
- `_notify_conflicts(data: Dict) → str`: Conflictos detectados
- `_notify_branch_change(data: Dict) → str`: Cambios de rama
- `_notify_others_changes(data: Dict) → str`: Cambios de otros

### Detección de Identidad

Maneja múltiples identidades del desarrollador:
- Compara emails en minúsculas
- Soporta múltiples emails/nombres
- Funciona sin configuración Git

## Observaciones

- **NO endpoints HTTP**: Solo lógica interna, API los expone
- **Inyección de dependencias**: ChatService acepta servicios externos
- **Fallback graceful**: Si falla Weaviate, continúa con SQLite
- **Cache coordinado**: Sistema de invalidación via EventBus funcional
- **Mono-usuario**: user_id siempre "default", sin rate limiting
- **Decisión #1 cumplida**: Solo guarda resúmenes, ~90% reducción
- **Decisión #11 cumplida**: Git reactivo, NO fetch automático
- **Retry logic robusto**: ConversationService y ChatService con backoff
- **Modelos tipados**: ConversationSearch usa Pydantic
- **Sistema de errores consolidado**: Importan desde `core.exceptions`
- **Métricas extensivas**: Cada operación importante se mide
- **Límites configurables**: Via .acolyte para flexibilidad
- **18 ChunkTypes**: Detección automática por regex patterns
- **Pipeline indexación completo**: No es esqueleto
- **Sistema cache TTL**: GitService 5 minutos para cambios externos
- **Integración EventBus**: GitService publica, otros invalidan cache
- **IDs centralizados**: Todos usan `generate_id()` formato hex32
- **Logging estratégico**: En puntos críticos sin spam
