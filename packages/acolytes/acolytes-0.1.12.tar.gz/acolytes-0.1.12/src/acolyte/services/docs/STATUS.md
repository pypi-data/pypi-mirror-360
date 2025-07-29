# 📊 Estado del Módulo Services

## 🚀 Estado de Cobertura de Tests - COMPLETADO (22/06/25)

### ✅ TODOS COMPLETADOS >90%
- **git_service.py**: 96% cobertura
- **task_service.py**: 98% cobertura
- **chat_service.py**: 95% cobertura
- **conversation_service.py**: 93% cobertura
- **indexing_service.py**: 92% cobertura

**Estado**: Todos los servicios tienen cobertura excelente. Refactorización desbloqueada.

## Componentes del Módulo

### conversation_service.py
Gestión de conversaciones con persistencia en SQLite.
- Resúmenes inteligentes (~90% reducción) funcionando
- Búsqueda SQL por keywords (las conversaciones NO están en Weaviate)
- Retry logic para operaciones SQLite críticas
- Sistema de notificación de eventos de cache
- Modelos tipados ConversationSearch con Pydantic
- Weaviate solo se usa para chunks de código, no conversaciones
- **🔧 REFACTORIZACIÓN PENDIENTE**: Ver `REFACTORING_CONVERSATION_SERVICE.md`

### task_service.py  
Agrupación de sesiones en tareas para contexto completo.
- Jerarquía Task > Session > Message funcional
- Detección y guardado de decisiones técnicas
- Relaciones many-to-many entre tasks y sessions
- Métodos get_recent_decisions() para integrar con ChatService
- Regex completo de extensiones de archivos

### chat_service.py
Orquestación del flujo completo de chat.
- Flujo completo end-to-end implementado
- Inyección de dependencias para evitar imports circulares
- Retry logic robusto para Ollama con backoff exponencial
- Integración con compresión contextual para queries específicos
- Carga automática de contexto previo (Decisión #7)
- Distribución dinámica de tokens según tipo de query

### indexing_service.py
Pipeline completo de indexación de código.
- Pipeline completo: chunking → enrichment → embeddings → Weaviate
- Detección automática de 18 ChunkTypes por contenido
- Procesamiento en batches con progress tracking  
- Sistema EventBus para notificaciones en tiempo real
- Respeta .acolyteignore y valida extensiones soportadas
- ✅ Re-indexación movida a servicio dedicado `ReindexService`

### reindex_service.py
Sistema dedicado de re-indexación automática.
- Separación de responsabilidades (Single Responsibility)
- Cola asíncrona para procesar eventos de re-indexación
- Deduplicación de patrones con cooldown configurable
- Procesamiento en batches para evitar bloqueos
- Métricas detalladas de re-indexación
- Integración con EventBus para recibir CacheInvalidateEvent
- Lógica de búsqueda de archivos por patrón inteligente

### git_service.py
Operaciones Git internas reactivas.
- Operaciones puramente reactivas (NO fetch automático)
- Cache de repositorio con TTL de 5 minutos
- Sistema de notificaciones contextual para chat
- Análisis de conflictos potenciales y co-modificaciones
- Publicación de eventos CacheInvalidateEvent
- Detección robusta de identidad de desarrollador
- **✅ TESTS COMPLETOS**: 96% cobertura con 34 tests
  - Manejo completo de excepciones y casos extremos
  - Tests sin event bus para verificar fallback graceful
  - Cobertura de todas las notificaciones y escenarios de error

## Funcionalidades Pendientes

### ✅ Re-indexación Automática - REFACTORIZADO A ReindexService
**Movido de**: `IndexingService._handle_cache_invalidation()` a servicio dedicado

**Mejoras implementadas en ReindexService**:
- Servicio dedicado siguiendo Single Responsibility Principle
- Cola asíncrona para mejor control de flujo
- Deduplicación de patrones con cooldown configurable
- Procesamiento en batches para evitar bloqueos del sistema
- Métricas específicas de re-indexación separadas
- Mejor testabilidad con inyección de dependencias

**Flujo mejorado**:
1. GitService detecta cambios → publica `CacheInvalidateEvent`
2. ReindexService recibe evento y verifica deduplicación
3. Encola evento para procesamiento asíncrono
4. Busca archivos por patrón con cache opcional
5. Procesa en batches llamando a IndexingService
6. Notifica progreso con task_id único

```yaml
# Configuración en .acolyte
reindexing:
  batch_size: 5              # Archivos por batch
  pattern_cooldown: 5        # Segundos para ignorar duplicados
  
indexing:
  max_reindex_files: 50      # Límite total de archivos
```

**Ver**: `REINDEXING_SYSTEM.md` para documentación completa

## Limitaciones Conocidas

- Un solo modelo: acolyte:latest (por diseño)
- Requiere mínimo 8GB RAM
- Primera indexación puede tardar
- Los ciclos de optimización usan CPU intensivamente
- Sistema mono-usuario sin rate limiting

## Dependencias con Otros Módulos

### Requeridas (debe existir)
- **Core Database**: Para persistencia en SQLite
- **Core Ollama**: Para generación de respuestas  
- **Core Events**: Para sistema de invalidación coordinada
- **Core Metrics**: Para observabilidad base
- **Core IDGenerator**: Para IDs hex32 unificados

### Opcionales (fallback graceful)
- **Weaviate**: Fallback a SQLite si no está disponible
- **EnrichmentService**: IndexingService funciona sin él
- **ChunkingService**: IndexingService tiene implementación temporal

## Conexiones con Módulo Core - TODOs

### ChunkingService y AdaptiveChunker
- Origen: AdaptiveChunker pertenece conceptualmente a RAG
- Decisión #25: Implementado en `/rag/chunking/adaptive.py`
- Integración: IndexingService usa el chunking adaptativo del módulo RAG

### Sistema de Notificaciones EventBus
- Sistema de eventos implementado en `core/events.py`
- `ProgressEvent` existe y se usa para notificaciones
- Arquitectura: IndexingService → EventBus → API WebSocket
- WebSocket se suscribe automáticamente a eventos

### Re-indexación con Cache Invalidación
- Sistema de invalidación implementado
- Flujo: GitService detecta → publica CacheInvalidateEvent → IndexingService recibe
- Falta: Lógica para buscar archivos por patrón y re-indexarlos

## Decisiones Relacionadas en Core

- **Sin migraciones** (Decisión #27): Sistema mono-usuario con esquema estable
- **SensitiveDataMasker** (Decisión #28): Implementado con versión simple para logs
- **Keywords NO implementar** (Decisión #31): Búsqueda semántica es superior
- **Duplicados aceptados** (Decisión #32): Para MVP, aceptar duplicados en insights

## Métricas Implementadas

### ConversationService
- `session_creation_time_ms`: Tiempo de creación de sesión
- `search_results_count`: Sesiones relacionadas encontradas
- `summary_compression_ratio`: Ratio de compresión de resúmenes
- `fallback_to_sqlite_count`: Veces que se usa fallback

### TaskService
- `create_task`: Tiempo de creación de tarea
- `associate_session`: Tiempo de asociación
- `get_task_context`: Tiempo de recuperación de contexto
- `save_decision`: Tiempo de guardado de decisión

### ChatService
- `processing_time_seconds`: Tiempo total end-to-end
- `new_chat_init_time`: Tiempo de inicialización
- `messages_processed`: Contador de mensajes
- `compressed_searches`: Búsquedas con compresión

### IndexingService
- `index_files_total`: Tiempo total de indexación
- `files_indexed`: Archivos procesados
- `chunks_created`: Chunks creados
- `trigger.{type}`: Por tipo de trigger

### GitService
- `detect_changes_from_others`: Tiempo de detección
- `analyze_conflicts`: Tiempo de análisis
- `changes_detected`: Cambios detectados
- `conflict_severity`: Severidad promedio
