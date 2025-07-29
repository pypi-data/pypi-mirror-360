# 📊 Estado del Módulo Models

## Componentes del Módulo

### base.py
Mixins reutilizables y configuración base.
- `TimestampMixin`: Añade created_at/updated_at con método touch()
- `AcolyteBaseModel`: Configuración Pydantic optimizada  
- `StandardIdMixin`: Genera IDs hex32 automáticamente
- `SessionIdMixin`: ID especializado para conversaciones
- `IdentifiableMixin`: Alias de StandardIdMixin para compatibilidad
- Funciones helper para obtener primary key de cualquier modelo

### chat.py
Modelos OpenAI-compatible para el endpoint principal.
- `Role`: Enum con USER, ASSISTANT, SYSTEM
- `Message`: Validación de contenido no vacío
- `ChatRequest`: Compatible con OpenAI + campos debug opcionales
- `ChatResponse`: Respuesta estructurada con usage y choices
- `Choice`, `Usage`: Estructuras de soporte

### chunk.py
Fragmentos de código para RAG.
- `ChunkType`: 18 tipos especializados de código
- `ChunkMetadata`: Ubicación y contexto del fragmento
- `Chunk`: Contenido con interfaz to_search_text()

### conversation.py
Persistencia de conversaciones con memoria asociativa.
- `ConversationStatus`: Estados ACTIVE, COMPLETED
- `Conversation`: Usa SessionIdMixin, guarda resúmenes
- `ConversationSearchRequest`: Búsqueda semántica de conversaciones
- `ConversationSearchResult`: Resultados con relevance score
- Integración completa con ConversationService.search_conversations() verificada

### document.py
Documentos e indexación.
- `DocumentType`: 5 tipos (CODE, MARKDOWN, CONFIG, DATA, OTHER)
- `Document`: Validación básica de paths, marca de indexación
- `IndexingBatch`: Lee límites desde .acolyte dinámicamente
- `IndexingProgress`: Modelo para WebSocket updates

### dream.py
Sistema de optimización técnica de embeddings.
- `OptimizationStatus`: Estados del proceso
- `InsightType`: 5 tipos de insights descubiertos
- `OptimizationMetrics`: Cálculo de fatiga 0-10
- `DreamState`: Singleton con recomendaciones
- `DreamInsight`: Patrones descubiertos
- `OptimizationRequest/Result`: Control del proceso

### semantic_types.py
Tipos para procesamiento NLP, todos activamente usados.
- `TokenDistribution`: Resultado de análisis de query
- `TaskDetection`: Detección nueva tarea vs continuación
- `SummaryResult`: Resumen extractivo con ahorro de tokens
- `SessionReference`: Referencias temporales detectadas
- `DetectedDecision`: DTO para decisiones sin contexto

### task_checkpoint.py
Agrupación jerárquica de sesiones.
- `TaskType`: 6 tipos de tareas
- `TaskStatus`: Estados PLANNING, IN_PROGRESS, COMPLETED
- `TaskCheckpoint`: Agrupa sesiones, registra decisiones
- Métodos get_summary() y to_search_text() funcionales

### technical_decision.py
Decisiones técnicas con trazabilidad.
- `DecisionType`: ARCHITECTURE, LIBRARY, PATTERN, SECURITY
- `TechnicalDecision`: Incluye alternativas e impacto
- Métodos get_summary() y to_search_text() activos

### common/metadata.py
Metadata compartida entre módulos.
- `FileMetadata`: Info básica de archivos
- `GitMetadata`: Métricas Git completas con métodos helper
- `LanguageInfo`: Detección de lenguaje y frameworks

## Funcionalidades Activas

- **Validación automática**: Todos los validators Pydantic operativos
- **Timestamps automáticos**: TimestampMixin.touch() en servicios  
- **IDs únicos**: generate_id() integrado en mixins
- **Configuración dinámica**: .acolyte como fuente de verdad
- **Métodos helper**: GitMetadata.get_* previenen NULL errors
- **Interfaces estándar**: get_summary() y to_search_text()
- **Enum conversion**: Services convierten con .value.upper()

## Integraciones Verificadas

- **API Layer**: FastAPI usa ChatRequest/ChatResponse
- **ChatService**: Usa Conversation, TaskCheckpoint, TechnicalDecision  
- **ConversationService**: Métodos add_message(), complete()
- **RAG Module**: Chunk, ChunkMetadata, Document activos
- **Semantic Module**: Todos los types en uso
- **Dream Service**: DreamState para cálculo de fatiga
- **EnrichmentService**: GitMetadata con cálculos implementados

## Limitaciones Conocidas

- Validación de paths es básica (suficiente para mono-usuario)

## Dependencias con Otros Módulos

- **Core**: IDGenerator, Exceptions, SecureConfig
- **API**: Usa modelos para validación de requests/responses
- **Services**: Todos los servicios usan estos modelos
- **RAG**: Chunk y Document son fundamentales
- **Semantic**: Consume semantic_types
- **Dream**: Actualiza DreamState con métricas

## Patrones de Implementación

### Logger Global
- Todos los modelos que necesiten logging usan `from acolyte.core.logging import logger`
- NO crear instancias de AsyncLogger

### MetricsCollector
- Si un modelo necesita métricas: `self.metrics = MetricsCollector()`
- Usar prefijos en strings: `self.metrics.increment("models.validation.failed")`

### Datetime Utils
- Timestamps usan `from acolyte.core.utils.datetime_utils import utc_now, utc_now_iso`
- Para SQLite/Weaviate siempre usar `utc_now_iso()`
