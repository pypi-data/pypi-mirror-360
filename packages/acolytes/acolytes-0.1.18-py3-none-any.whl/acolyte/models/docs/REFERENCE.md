# 📚 Referencia API - Módulo Models

Estructuras de datos del sistema ACOLYTE con validación estricta Pydantic v2. Define modelos para chat OpenAI-compatible, fragmentos RAG, persistencia de conversaciones, agrupación de tareas, decisiones técnicas y sistema de optimización Dream.

## 📦 base.py

### `TimestampMixin`
Añade timestamps automáticos a cualquier modelo.
- **Campos**: `created_at: datetime`, `updated_at: datetime`
- `touch()` → `None`  
  Actualiza el timestamp de modificación a datetime UTC actual

### `AcolyteBaseModel`
Base para todos los modelos con configuración Pydantic optimizada.
- Validación al asignar valores
- Encoders JSON para datetime y UUID
- Prevención de campos extra
- Schema documentation mejorada

### `StandardIdMixin`
Estrategia estándar de identificación (mayoría de modelos).
- **Campo**: `id: str` (hex32 autogenerado)
- `primary_key` → `str` (property)  
  Retorna el ID del modelo
- `primary_key_field` → `str` (property)  
  Retorna 'id' como nombre del campo PK

### `SessionIdMixin`
Estrategia especializada para conversaciones.
- **Campo**: `session_id: str` (hex32 autogenerado)
- `primary_key` → `str` (property)  
  Retorna el session_id del modelo
- `primary_key_field` → `str` (property)  
  Retorna 'session_id' como nombre del campo PK

### Funciones Helper

- `get_model_primary_key(model: Identifiable)` → `str`  
  Obtiene el ID primario de cualquier modelo con protocolo Identifiable

- `get_model_primary_key_field(model: Identifiable)` → `str`  
  Obtiene el nombre del campo PK de cualquier modelo

## 📦 chat.py

### `Role` (Enum)
Roles válidos en conversaciones.
- `USER = "user"`
- `ASSISTANT = "assistant"`
- `SYSTEM = "system"`

### `Message`
Mensaje individual en una conversación.
- **Campos**: `role: Role`, `content: str`, `metadata: Optional[Dict[str, Any]]`
- `validate_content_not_empty(v: str)` → `str`  
  Validator que asegura contenido no vacío después de strip()

### `ChatRequest`
Request OpenAI-compatible con extensiones ACOLYTE.
- **Campos base**: `model: str`, `messages: List[Message]`, `temperature: Optional[float]`, `max_tokens: Optional[int]`, `stream: bool = False`
- **ACOLYTE específico**: `debug: bool = False`, `explain_rag: bool = False`
- `validate_message_flow(messages: List[Message])` → `List[Message]`  
  Valida que flujo de mensajes sea coherente (empezar con user/system)

### `ChatResponse`
Respuesta estructurada OpenAI-compatible.
- **Campos**: `id: str`, `object: str = "chat.completion"`, `created: int`, `model: str`, `choices: List[Choice]`, `usage: Usage`
- **Debug opcional**: `debug_info: Optional[Dict[str, Any]]`, `rag_explanation: Optional[Dict[str, Any]]`

### `Choice`
Opción individual en respuesta.
- **Campos**: `index: int`, `message: Message`, `finish_reason: str`

### `Usage`
Información de uso de tokens.
- **Campos**: `prompt_tokens: int`, `completion_tokens: int`, `total_tokens: int`

## 📦 chunk.py

### `ChunkType` (Enum)
18 tipos especializados de fragmentos de código.
- **Funcional**: `FUNCTION`, `METHOD`, `CONSTRUCTOR`, `PROPERTY`
- **Estructural**: `CLASS`, `INTERFACE`, `MODULE`, `NAMESPACE`
- **Documental**: `COMMENT`, `DOCSTRING`, `README`
- **Semántico**: `IMPORTS`, `CONSTANTS`, `TYPES`, `TESTS`
- **Jerárquico**: `SUMMARY`, `SUPER_SUMMARY`
- **Fallback**: `UNKNOWN`

### `ChunkMetadata`
Metadata asociada a un fragmento.
- **Campos**: `file_path: str`, `language: str`, `chunk_type: ChunkType`, `name: Optional[str]`, `start_line: int`, `end_line: int`, `last_modified: datetime`
- `line_count` → `int` (property)  
  Calcula número de líneas (end_line - start_line + 1)

### `Chunk`
Fragmento de código con contenido y metadata.
- **Campos**: `content: str`, `metadata: ChunkMetadata`, `summary: Optional[str]`
- `to_search_text(rich_context=None)` → `str`  
  Genera texto optimizado para embeddings con contexto rico o metadata básica

## 📦 conversation.py

### `ConversationStatus` (Enum)
Estados de una conversación.
- `ACTIVE = "active"`
- `COMPLETED = "completed"`

### `Conversation`
Sesión de chat con memoria persistente. Usa SessionIdMixin.
- **Campos**: `summary: str`, `keywords: List[str]`, `status: ConversationStatus`, `task_checkpoint_id: Optional[str]`, `related_sessions: List[str]`, `total_tokens: int`, `message_count: int`
- `add_message(message: Message)` → `None`  
  Añade mensaje, actualiza contadores y timestamps
- `get_context_window(max_messages: int = 10)` → `List[Message]`  
  Obtiene mensajes más recientes para contexto LLM
- `complete()` → `None`  
  Marca conversación como completada y actualiza timestamp

### `ConversationSearchRequest`
Request para búsqueda semántica de conversaciones.
- **Campos**: `query: str`, `limit: int = 10`, `threshold: float = 0.7`, `date_range: Optional[Tuple[datetime, datetime]]`, `task_id: Optional[str]`

### `ConversationSearchResult`
Resultado de búsqueda con relevancia.
- **Campos**: `session_id: str`, `relevance_score: float`, `summary: str`, `created_at: datetime`, `task_checkpoint_id: Optional[str]`, `matching_messages: List[Message]`

## 📦 document.py

### `DocumentType` (Enum)
Tipos de documentos soportados.
- `CODE = "code"`
- `MARKDOWN = "markdown"`
- `CONFIG = "config"`
- `DATA = "data"`
- `OTHER = "other"`

### `Document`
Documento para indexación con validación de seguridad.
- **Campos**: `file_path: str`, `content: str`, `document_type: DocumentType`, `size_bytes: int`, `indexed: bool = False`, `chunks_count: int = 0`, `language: Optional[str]`, `encoding: str = "utf-8"`
- `validate_path_safety(v: str)` → `str`  
  Validator que previene path traversal, paths absolutos y paths vacíos
- `mark_indexed(chunks_count: int)` → `None`  
  Marca documento como indexado con conteo de chunks

### `IndexingBatch`
Lote de documentos para procesamiento eficiente.
- **Campos**: `documents: List[Document]`, `total_size_bytes: int`
- `validate_batch_size()` → `IndexingBatch`  
  Valida tamaño total contra límite configurado en .acolyte
- `_get_batch_size_limit()` → `int`  
  Obtiene límite desde .acolyte con fallback a Settings

### `IndexingProgress`
Progreso de indexación para WebSocket.
- **Campos**: `current_file: str`, `files_processed: int`, `total_files: int`, `chunks_created: int`, `embeddings_generated: int`, `elapsed_seconds: float`, `estimated_remaining_seconds: Optional[float]`

## 📦 task_checkpoint.py

### `TaskType` (Enum)
Tipos de tareas de desarrollo.
- `IMPLEMENTATION = "implementation"`
- `DEBUGGING = "debugging"`
- `REFACTORING = "refactoring"`
- `DOCUMENTATION = "documentation"`
- `RESEARCH = "research"`
- `REVIEW = "review"`

### `TaskStatus` (Enum)
Estados del ciclo de vida de una tarea.
- `PLANNING = "planning"`
- `IN_PROGRESS = "in_progress"`
- `COMPLETED = "completed"`

### `TaskCheckpoint`
Agrupa múltiples sesiones relacionadas en una tarea coherente.
- **Campos**: `title: str`, `task_type: TaskType`, `status: TaskStatus`, `initial_context: str`, `session_ids: List[str]`, `key_decisions: List[str]`, `keywords: List[str]`
- `add_session(session_id: str)` → `None`  
  Asocia nueva sesión evitando duplicados
- `add_decision(decision: str)` → `None`  
  Registra decisión importante y actualiza timestamp
- `complete()` → `None`  
  Marca tarea como completada
- `get_summary()` → `str`  
  Genera resumen formato: "título (tipo) - N sesiones - Estado: X"
- `to_search_text()` → `str`  
  Genera texto para búsqueda semántica compatible con embeddings

## 📦 technical_decision.py

### `DecisionType` (Enum)
Categorías de decisiones técnicas.
- `ARCHITECTURE = "architecture"`
- `LIBRARY = "library"`
- `PATTERN = "pattern"`
- `SECURITY = "security"`

### `TechnicalDecision`
Decisión técnica documentada con alternativas y justificación.
- **Campos**: `title: str`, `description: str`, `decision_type: DecisionType`, `rationale: str`, `alternatives_considered: List[str]`, `impact_level: int`, `task_id: Optional[str]`, `session_id: Optional[str]`
- `get_summary()` → `str`  
  Resumen formato: "título (vs alternativas) - tipo - Impacto: X/5"
- `to_search_text()` → `str`  
  Texto para búsqueda con descripción, rationale y alternativas

## 📦 dream.py

### `OptimizationStatus` (Enum)
Estados del proceso de optimización.
- `IDLE = "idle"`
- `ANALYZING = "analyzing"`
- `OPTIMIZING = "optimizing"`
- `COMPLETED = "completed"`

### `InsightType` (Enum)
Tipos de insights descubiertos.
- `PATTERN = "pattern"`
- `CONNECTION = "connection"`
- `OPTIMIZATION = "optimization"`
- `ARCHITECTURE = "architecture"`
- `BUG_RISK = "bug_risk"`

### `OptimizationMetrics`
Métricas para calcular necesidad de optimización.
- **Campos**: `time_since_optimization: float`, `embedding_fragmentation: float`, `query_performance_degradation: float`, `new_embeddings_ratio: float`
- `fatigue_level` → `float` (property)  
  Calcula nivel total de fatiga (suma ponderada 0-10)
- `needs_optimization` → `bool` (property)  
  Determina si fatiga > 7.0

### `DreamState`
Estado singleton del sistema de optimización.
- **Campos**: `status: OptimizationStatus`, `metrics: OptimizationMetrics`, `last_optimization: Optional[datetime]`, `current_session_id: Optional[str]`, `insights_count: int`, `avg_query_time_ms: float`, `total_embeddings: int`
- `get_recommendation()` → `str`  
  Genera recomendación basada en nivel de fatiga

### `DreamInsight`
Insight descubierto durante análisis.
- **Campos**: `insight_type: InsightType`, `title: str`, `description: str`, `confidence: float`, `impact: str`, `entities_involved: List[str]`, `created_during_session: str`

### `OptimizationRequest`
Solicitud para iniciar optimización.
- **Campos**: `trigger: str`, `requested_duration_minutes: int = 5`, `focus_areas: List[str]`

### `OptimizationResult`
Resultado del proceso de optimización.
- **Campos**: `session_id: str`, `duration_minutes: float`, `insights_generated: int`, `embeddings_reorganized: int`, `query_time_improvement_ms: float`, `fragmentation_reduced: float`, `recommendations: List[str]`

## 📦 semantic_types.py

### `TokenDistribution` (dataclass)
Resultado de análisis de distribución de tokens.
- **Campos**: `type: str`, `response_ratio: float`, `context_ratio: float`

### `TaskDetection` (dataclass)
Resultado de detección de tareas.
- **Campos**: `is_new_task: bool`, `task_title: Optional[str]`, `confidence: float`, `continues_task: Optional[str]`

### `SummaryResult` (dataclass)
Resultado de generación de resumen.
- **Campos**: `summary: str`, `entities: List[str]`, `intent_type: str`, `tokens_saved: int`

### `SessionReference` (dataclass)
Referencia temporal detectada.
- **Campos**: `pattern_matched: str`, `context_hint: Optional[str]`, `search_type: str`

### `DetectedDecision` (dataclass)
Decisión técnica detectada sin contexto de sesión.
- **Campos**: `title: str`, `description: str`, `decision_type: str`, `confidence: float`, `rationale: Optional[str]`, `alternatives: List[str]`

## 📦 common/metadata.py

### `FileMetadata`
Metadata básica de archivos.
- **Campos**: `path: str`, `size: int`, `mime_type: str`, `encoding: str`, `modified_time: datetime`

### `GitMetadata`
Información Git enriquecida con métodos helper seguros.
- **Campos básicos**: `file_path: str`, `author: Optional[str]`, `last_commit_date: Optional[datetime]`, `total_commits: Optional[int]`
- **Campos avanzados**: `commits_last_30_days: Optional[int]`, `stability_score: Optional[float]`, `file_age_days: Optional[int]`, `is_actively_developed: Optional[bool]`, `contributors: Optional[Dict[str, Dict]]`, `merge_conflicts_count: Optional[int]`, `code_volatility_index: Optional[float]`, `directories_restructured: Optional[int]`

#### Métodos Helper Seguros
- `get_commits_last_30_days()` → `int` (default: 3)
- `get_stability_score()` → `float` (default: 0.5)
- `get_file_age_days()` → `int` (default: 30)
- `get_is_actively_developed()` → `bool` (default: False)
- `get_total_commits()` → `int` (default: 1)
- `get_merge_conflicts_count()` → `int` (default: 0)
- `get_directories_restructured()` → `int` (default: 0)
- `get_code_volatility_index()` → `float` (default: 0.1)

### `LanguageInfo`
Información detectada del lenguaje.
- **Campos**: `language: str`, `confidence: float`, `extension: str`, `frameworks: List[str]`

## 🔗 Dependencias

### Imports desde Core
- `generate_id` → IDs únicos hex32
- `ErrorResponse, validation_error, from_exception` → Sistema unificado de errores
- `Settings` → Configuración con fallback

### Librerías Externas
- `pydantic` → Validación y serialización
- `datetime, timezone` → Timestamps UTC
- `pathlib` → Validación de paths
- `uuid` → JSON encoders
- `yaml` → Lectura de .acolyte

## ⚠️ Excepciones

Los modelos pueden lanzar las siguientes excepciones:

- `ValidationError` (Pydantic) → Datos no cumplen esquema
- `ValueError` → Validación personalizada falla
- `FileNotFoundError` → Archivo .acolyte no existe (con fallback)

Todas las excepciones de lógica de negocio se importan desde `core.exceptions`.
