# 🔗 Integración del Módulo Models

## Quién Usa Este Módulo

### API Layer (`/api`)
**Modelos utilizados**: `ChatRequest`, `ChatResponse`, `Message`, `Role`, `Choice`, `Usage`
- **Propósito**: Validación automática de requests/responses OpenAI-compatible
- **Integración**: FastAPI convierte JSON → Pydantic → validación automática
- **Flujo**: HTTP Request → `ChatRequest.model_validate()` → Procesamiento → `ChatResponse` → JSON

### ChatService (`/services/chat.py`)
**Modelos utilizados**: Todos los modelos de conversación y chat
- **Propósito**: Orquestación de conversaciones con persistencia
- **Integración**: Recibe `ChatRequest`, gestiona `Conversation`, retorna `ChatResponse`
- **Métodos clave**: `process_message()` usa modelos para validación y estructura

### ConversationService (`/services/conversation.py`)
**Modelos utilizados**: `Conversation`, `ConversationSearchRequest`, `ConversationSearchResult`
- **Propósito**: Gestión de sesiones y búsqueda semántica
- **Integración**: CRUD de conversaciones, búsqueda con embeddings
- **Métodos clave**: `save_conversation_turn()`, `search_conversations()`

### TaskService (`/services/task.py`)
**Modelos utilizados**: `TaskCheckpoint`, `TechnicalDecision`
- **Propósito**: Agrupación jerárquica y decisiones técnicas
- **Integración**: Gestiona relaciones Task > Session > Message
- **Métodos clave**: `create_task()`, `save_technical_decision()`

### RAG Module (`/rag`)
**Modelos utilizados**: `Chunk`, `ChunkMetadata`, `ChunkType`, `Document`, `DocumentType`
- **ChunkingService**: Usa `ChunkType` para clasificar fragmentos
- **EnrichmentService**: Enriquece chunks con `GitMetadata`
- **IndexingService**: Procesa `Document` → `Chunk` → Weaviate
- **HybridSearch**: Busca y retorna `Chunk` objects

### Dream Service (`/dream`)
**Modelos utilizados**: `DreamState`, `OptimizationMetrics`, `DreamInsight`, `OptimizationRequest/Result`
- **Propósito**: Sistema de optimización de embeddings
- **Integración**: Lee `GitMetadata` para calcular fatiga
- **Singleton**: `DreamState` es compartido globalmente

### Semantic Module (`/semantic`)
**Modelos utilizados**: Todos los tipos en `semantic_types.py`
- **QueryAnalyzer**: Retorna `TokenDistribution`
- **TaskDetector**: Retorna `TaskDetection`
- **Summarizer**: Retorna `SummaryResult`
- **ReferenceResolver**: Retorna `SessionReference`
- **DecisionDetector**: Retorna `DetectedDecision`

### EnrichmentService (`/rag/enrichment`)
**Modelos utilizados**: `GitMetadata`, `FileMetadata`, `LanguageInfo`
- **Propósito**: Calcular y almacenar métricas Git
- **Integración**: Enriquece chunks antes de indexación
- **Cálculos**: Implementa todos los métodos `_calculate_*`

### IndexingService (`/services/indexing.py`)
**Modelos utilizados**: `Document`, `IndexingBatch`, `IndexingProgress`
- **Propósito**: Pipeline de indexación completo
- **Integración**: Valida documentos, crea batches, reporta progreso
- **WebSocket**: Usa `IndexingProgress` para updates

## Qué Módulos Usa

### Core Infrastructure
- **`/core/id_generator`**: Para generar IDs hex32 únicos
  ```python
  from acolyte.core.id_generator import generate_id
  ```
- **`/core/exceptions`**: Sistema unificado de errores
  ```python
  from acolyte.core.exceptions import ErrorResponse, validation_error
  ```
- **`/core/secure_config`**: Para leer configuración
  ```python
  from acolyte.core.secure_config import Settings
  ```

### External Libraries
- **Pydantic v2**: Base de toda la validación
- **Python stdlib**: datetime, pathlib, uuid, yaml
- **PyYAML**: Para leer `.acolyte`

## Contratos de Interfaz

### Protocolo Identifiable
Todos los modelos con ID implementan este protocolo:
```python
class Identifiable(Protocol):
    @property
    def primary_key(self) -> str: ...
    
    @property
    def primary_key_field(self) -> str: ...
```

### Interfaces Estándar

#### get_summary()
Implementado en: `TaskCheckpoint`, `TechnicalDecision`
```python
def get_summary(self) -> str:
    """Retorna resumen legible para humanos"""
```

#### to_search_text()
Implementado en: `Chunk`, `TaskCheckpoint`, `TechnicalDecision`
```python
def to_search_text(self, rich_context=None) -> str:
    """Retorna texto optimizado para embeddings"""
```

## Puntos de Extensión

### Añadir Nuevo Mixin
1. Crear clase que herede de `AcolyteBaseModel`
2. Definir campos y comportamiento
3. Usar en modelos que lo necesiten

### Añadir Nuevo Tipo de Chunk
1. Añadir valor a enum `ChunkType`
2. Actualizar lógica en ChunkingService
3. Ajustar estrategias de compresión si aplica

### Añadir Nueva Metadata
1. Crear modelo en `common/metadata.py`
2. Añadir campo Optional en modelos relevantes
3. Implementar métodos helper seguros

## Flujos de Integración Comunes

### Flujo de Chat Completo
```
API → ChatRequest → ChatService → Conversation → ConversationService → SQLite
                                       ↓
                                  TaskCheckpoint → TaskService
                                       ↓
                                TechnicalDecision
```

### Flujo de Indexación
```
File → Document → IndexingService → ChunkingService → Chunk
                                           ↓
                                    EnrichmentService → GitMetadata
                                           ↓
                                    EmbeddingService → Weaviate
```

### Flujo de Búsqueda
```
Query → ConversationSearchRequest → ConversationService → Embeddings
                                            ↓
                                        Weaviate → ConversationSearchResult
```

## Consideraciones de Diseño

### Separación de Responsabilidades
- **Models**: Solo estructura y validación básica
- **Services**: Lógica de negocio y persistencia
- **Core**: Infraestructura compartida

### Evolución del Schema
- Campos nuevos como `Optional` para compatibilidad
- Métodos helper para evitar breaking changes
- Mixins para funcionalidad reutilizable

### Performance
- Validación temprana previene errores costosos
- IDs hex32 optimizados para SQLite
- Resúmenes reducen 90% el almacenamiento

## Dependencias Críticas

### Sin estos módulos, Models no funciona:
1. **Core/IDGenerator**: Para generar IDs únicos
2. **Core/Exceptions**: Para manejo de errores
3. **Pydantic**: Para toda la validación

### Models es crítico para:
1. **Todos los Services**: Estructuras de datos
2. **API Layer**: Validación de requests
3. **RAG Module**: Modelos de chunks y documentos
