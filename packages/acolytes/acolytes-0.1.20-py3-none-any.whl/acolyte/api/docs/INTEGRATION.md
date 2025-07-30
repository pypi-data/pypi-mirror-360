# 🔗 Integración del Módulo API

## Módulos que Usan API

### Herramientas Externas
- **Cursor**: Usa `/v1/chat/completions` para asistencia de código
- **Continue**: Usa endpoints `/v1/*` para integración IDE
- **VSCode Extensions**: Pueden usar API OpenAI-compatible
- **Dashboard Web** (futuro): Usará `/api/index/*` y WebSocket
- **Git Hooks**: Usan `/api/index/git-changes` para sincronización

### Scripts Internos
- **Instalación**: Puede usar API o importar directamente
- **CLI Commands** (futuro): Usarán endpoints sistema

## Módulos que API Usa

### De Core (Infraestructura)
```python
from acolyte.core.events import EventBus, EventType
from acolyte.core.websocket_manager import WebSocketManager
from acolyte.core.logging import logger
from acolyte.core.secure_config import get_secure_config
from acolyte.core.exceptions import (
    ValidationError, 
    ErrorResponse,
    validation_error
)
from acolyte.core.id_generator import generate_id
```

**Uso específico**:
- **EventBus**: Recibe eventos de progreso de IndexingService
- **WebSocketManager**: Gestiona conexiones WebSocket activas
- **Logger**: Logging asíncrono sin latencia
- **SecureConfig**: Lee configuración de `.acolyte`
- **Exceptions**: Manejo consistente de errores
- **IDGenerator**: Genera session_id únicos

### De Services (Lógica de Negocio)
```python
from acolyte.services import (
    ChatService,
    ConversationService, 
    IndexingService,
    TaskService
)
```

**Uso específico**:
- **ChatService**: Procesa mensajes de chat (`/v1/chat/completions`)
- **ConversationService**: Gestiona sesiones y contexto
- **IndexingService**: Indexa archivos (`/api/index/*`)
- **TaskService**: Tracking de tareas complejas

### De Models (Estructuras de Datos)
```python
from acolyte.models import (
    ConversationSearch,
    TaskCheckpoint,
    TechnicalDecision,
    ErrorResponse
)
```

**Uso específico**:
- Validación automática con Pydantic
- Serialización JSON para responses
- Type hints para mejor IDE support

### De Embeddings
```python
from acolyte.embeddings import UniXcoderEmbeddings
```

**Uso específico**:
- **UniXcoderEmbeddings**: Para endpoint `/v1/embeddings`
- Genera vectores de 768 dimensiones
- Compatible con formato OpenAI

## Contratos de Interfaz

### EventBus Contract
```python
# API se suscribe a eventos de progreso
subscription = event_bus.subscribe(
    EventType.PROGRESS,
    handler=self._handle_progress_event,
    filter=lambda e: e.task_id == task_id
)

# Formato esperado de ProgressEvent
class ProgressEvent:
    task_id: str
    current: int
    total: int
    message: str
    files_skipped: int
    chunks_created: int
    embeddings_generated: int
    errors: int
    current_file: Optional[str]
```

### ChatService Contract
```python
# API llama a ChatService
response = await chat_service.process_message(
    session_id=session_id,
    message=user_message,
    model=model_name,
    temperature=temperature,
    max_tokens=max_tokens,
    stream=stream,
    debug=debug
)

# Response esperado
class ChatResponse:
    content: str
    usage: Dict[str, int]
    session_id: str
    debug_info: Optional[Dict]
```

### IndexingService Contract
```python
# API llama a IndexingService
result = await indexing_service.index_files(
    files=file_list,
    task_id=task_id
)

# Stats disponibles
stats = await indexing_service.get_stats()
# Returns: {
#   "total_chunks": int,
#   "total_documents": int,
#   "embeddings_generated": int,
#   "last_indexed": str
# }
```

## Flujos de Integración

### Flujo: API → Services → Core

```
1. Request HTTP llega a API
2. API valida con Pydantic models
3. API llama a Service apropiado
4. Service usa Core para:
   - Logging (AsyncLogger)
   - Base de datos (DatabaseManager)
   - Configuración (SecureConfig)
   - Eventos (EventBus)
5. Service retorna resultado
6. API formatea respuesta
```

### Flujo: IndexingService → EventBus → API

```
1. IndexingService procesa archivos
2. Por cada archivo:
   - Publica ProgressEvent a EventBus
   - Incluye task_id en mensaje
3. WebSocket handler (suscrito):
   - Recibe evento
   - Filtra por task_id
   - Envía a cliente conectado
4. Cliente recibe actualizaciones real-time
```

### Flujo: Error Handling

```
1. Error ocurre en Service
2. Service lanza excepción tipada
3. API catch y convierte:
   - ValidationError → 422
   - NotFoundError → 404
   - AcolyteError → 500
4. API retorna ErrorResponse
```

## Puntos de Extensión

### Añadir Nuevo Endpoint

1. **Definir en router apropiado**:
   ```python
   # En api/new_feature.py
   router = APIRouter(prefix="/api/feature")
   
   @router.post("/action")
   async def new_action(request: ActionRequest):
       # Implementación
   ```

2. **Registrar en `__init__.py`**:
   ```python
   from .new_feature import router as feature_router
   app.include_router(feature_router)
   ```

3. **Añadir modelos en `models/`**:
   ```python
   class ActionRequest(BaseModel):
       field: str
       options: Dict[str, Any]
   ```

### Extender OpenAI Compatibility

Para añadir campos custom sin romper compatibilidad:

```python
# En respuesta, añadir AL FINAL
response = {
    ...standard_openai_fields...,
    # Campos ACOLYTE van después
    "acolyte_session_id": session_id,
    "acolyte_context_used": context_info
}
```

### Integrar Nuevo Service

1. **Importar en endpoint**:
   ```python
   from acolyte.services import NewService
   ```

2. **Usar con manejo de errores**:
   ```python
   try:
       service = NewService()
       result = await service.process()
   except ServiceNotAvailable:
       raise HTTPException(503, "Service temporarily unavailable")
   ```

## Configuración de Integración

### Ports Configuration
```yaml
# En .acolyte
ports:
  backend: 8000     # API escucha aquí
  weaviate: 8080    # API conecta aquí
  ollama: 11434     # API conecta aquí
```

### Service Discovery
```python
# API descubre servicios via configuración
config = get_secure_config()
weaviate_url = f"http://localhost:{config.ports.weaviate}"
ollama_url = f"http://localhost:{config.ports.ollama}"
```

### Timeout Configuration
```yaml
# Timeouts para servicios externos
timeouts:
  ollama_generation: 30  # segundos
  weaviate_search: 5
  indexing_file: 10
```

## Dependencias Críticas

### Must Have (Sin estos, API no funciona)
- **Core**: Todo el módulo API depende de Core
- **ChatService**: Para endpoint principal `/v1/chat/completions`
- **Models**: Para validación y serialización

### Nice to Have (Funcionalidad degradada sin estos)
- **IndexingService**: Solo afecta endpoints `/api/index/*`
- **Weaviate**: API funciona pero sin búsqueda semántica
- **Ollama**: API funciona pero no genera respuestas

### Optional (Features adicionales)
- **DreamService**: Cuando esté implementado real
- **Dashboard**: Para UI web futura

## Testing Integration

### Mock Services para Tests
```python
# En tests/api/test_chat.py
@pytest.fixture
def mock_chat_service():
    service = Mock(spec=ChatService)
    service.process_message.return_value = {
        "content": "Test response",
        "usage": {"total_tokens": 100}
    }
    return service

def test_chat_endpoint(mock_chat_service):
    # Inyectar mock
    app.dependency_overrides[ChatService] = lambda: mock_chat_service
    # Test endpoint
```

### Integration Tests
```python
# Test completo con servicios reales
@pytest.mark.integration
async def test_full_chat_flow():
    # Requiere servicios corriendo
    response = await client.post("/v1/chat/completions", ...)
    assert response.status_code == 200
```

## Monitoreo de Integraciones

### Métricas por Servicio
```python
# API rastrea para cada servicio
metrics = {
    "chat_service": {
        "calls": 1523,
        "errors": 2,
        "avg_latency_ms": 234
    },
    "indexing_service": {
        "files_processed": 127,
        "active_tasks": 1
    }
}
```

### Health Check Detallado
```python
# API verifica cada dependencia
GET /api/health

{
    "services": {
        "ollama": {"status": "healthy"},
        "weaviate": {"status": "healthy"},
        "sqlite": {"status": "healthy"},
        "indexing": {"status": "healthy"}
    }
}
```

## Troubleshooting Integraciones

### Service Not Available
```python
# Si un servicio no está disponible
try:
    result = await service.method()
except ServiceNotAvailable:
    # Degradar gracefully
    return {"error": "Feature temporarily unavailable"}
```

### Event Bus No Conecta
```python
# Verificar suscripción
if not self._subscription:
    self._subscription = event_bus.subscribe(...)
```

### Timeout en Servicios
```python
# Configurar timeouts apropiados
async with timeout(30):  # 30 segundos max
    result = await slow_service.process()
```
