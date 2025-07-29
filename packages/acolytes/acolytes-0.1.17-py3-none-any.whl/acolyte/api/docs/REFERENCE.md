# 📚 Referencia Técnica del Módulo API

## Endpoints HTTP

### OpenAI Compatible (`/v1/*`)

#### POST /v1/chat/completions
Endpoint principal de chat compatible con OpenAI.

**Request**:
```python
class ChatCompletionRequest(BaseModel):
    model: str = "gpt-3.5-turbo"  # Ignorado - siempre usa acolyte:latest
    messages: List[Dict[str, str]]
    stream: bool = False
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    # Campos ACOLYTE opcionales:
    debug: bool = False
    explain_rag: bool = False
```

**Response**:
```python
class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    usage: Dict[str, int]
    choices: List[Dict[str, Any]]
    # Con debug=true añade:
    debug_info: Optional[Dict[str, Any]]
    rag_explanation: Optional[Dict[str, Any]]
```

#### GET /v1/models
Lista modelos disponibles.

**Response**:
```json
{
  "object": "list",
  "data": [{
    "id": "gpt-3.5-turbo",
    "object": "model",
    "created": 1677610602,
    "owned_by": "openai"
  }]
}
```

#### POST /v1/embeddings
Genera embeddings usando UniXcoder.

**Request**:
```python
class EmbeddingRequest(BaseModel):
    model: str = "text-embedding-ada-002"  # Ignorado
    input: Union[str, List[str]]
    encoding_format: str = "float"
```

**Response**:
```python
class EmbeddingResponse(BaseModel):
    object: str = "list"
    data: List[Dict[str, Any]]  # {object: "embedding", embedding: List[float], index: int}
    model: str = "text-embedding-ada-002"
    usage: Dict[str, int]  # {prompt_tokens: int, total_tokens: int}
```

### Sistema (`/api/*`)

#### GET /api/health
Health check completo del sistema.

**Response**:
```python
class HealthResponse(BaseModel):
    status: str  # "healthy" | "degraded" | "unhealthy"
    version: str
    services: Dict[str, ServiceHealth]
    timestamp: str

class ServiceHealth(BaseModel):
    status: str  # "healthy" | "unhealthy" | "not_available"
    message: Optional[str]
    details: Optional[Dict[str, Any]]
```

#### GET /api/stats
Estadísticas generales del sistema.

**Response**:
```python
{
    "uptime_seconds": float,
    "total_requests": int,
    "active_connections": int,
    "memory_usage_mb": float,
    "indexing_stats": Dict[str, Any]
}
```

#### GET /api/websocket-stats
Estadísticas de conexiones WebSocket.

**Response**:
```python
{
    "active_connections": int,
    "total_connections": int,
    "connections": List[ConnectionInfo]
}
```

### Dream (`/api/dream/*`)

#### GET /api/dream/status
Estado del optimizador.

**Response**:
```python
class DreamStatus(BaseModel):
    state: str  # "awake" | "optimizing" | "dreaming"
    fatigue_level: float  # 0.0 - 10.0
    recommendation: str
    can_work: bool
    optimal_duration_minutes: int
    last_optimization: Optional[str]
    insights_available: int
```

#### POST /api/dream/optimize
Iniciar optimización.

**Request**:
```python
class OptimizeRequest(BaseModel):
    confirm: bool = False
    duration_minutes: int = 20
```

**Response**:
```python
class OptimizeResponse(BaseModel):
    status: str
    message: str
    estimated_completion: str
```

### Indexación (`/api/index/*`)

#### POST /api/index/project
Indexación completa del proyecto.

**Request**:
```python
class IndexProjectRequest(BaseModel):
    path: str = "."
    force: bool = False
    include_hidden: bool = False
```

**Response**:
```python
class IndexResponse(BaseModel):
    task_id: str
    status: str
    message: str
    estimated_files: int
```

#### POST /api/index/git-changes
Re-indexación tras cambios Git.

**Request**:
```python
class GitChangesRequest(BaseModel):
    trigger: str  # "commit" | "pull" | "checkout" | "fetch"
    files: List[str]
    metadata: GitMetadata

class GitMetadata(BaseModel):
    event: str
    commit_message: Optional[str]
    is_pull: Optional[bool]
    is_merge_local: Optional[bool]
    current_branch: Optional[str]
    commits_behind: Optional[int]
    invalidate_cache: bool = False
```

### WebSocket

#### WS /api/ws/progress/{task_id}
Stream de progreso de indexación.

**Messages**:
```python
class ProgressMessage(BaseModel):
    type: str = "progress"
    current: int
    total: int
    percentage: float
    message: str
    # Campos estadísticos:
    files_skipped: int
    chunks_created: int
    embeddings_generated: int
    errors: int
    current_file: Optional[str]
```

## Modelos Pydantic

### GitChangeFile
```python
class GitChangeFile(BaseModel):
    path: str
    change_type: str  # "added" | "modified" | "deleted"
    
    @field_validator('path')
    def validate_path(cls, v: str) -> str:
        # ~50 líneas de validación exhaustiva
        # Previene: path traversal, symlinks maliciosos,
        # caracteres peligrosos, paths absolutos
```

### ConnectionInfo (TypedDict)
```python
class ConnectionInfo(TypedDict):
    websocket: WebSocket
    last_ping: float
    last_activity: float
    connected_at: datetime
    event_queue: asyncio.Queue[ProgressEvent]
```

## Funciones Helper Internas

### health.py
```python
def get_indexing_service() -> Optional[IndexingService]:
    """Obtiene instancia singleton con manejo robusto de errores."""
    
async def _check_weaviate() -> ServiceHealth:
    """Verifica Weaviate con 4 niveles de error específicos."""
    
async def _check_ollama() -> ServiceHealth:
    """Verifica disponibilidad de Ollama."""
    
async def _check_sqlite() -> ServiceHealth:
    """Verifica base de datos SQLite."""
```

### dream.py
```python
async def _get_dream_state() -> Dict[str, Any]:
    """Obtiene estado thread-safe del optimizador."""
    
async def _atomic_update_state(key: str, value: Any):
    """Actualización atómica del estado."""
    
async def _atomic_complete_optimization():
    """Completa ciclo de optimización atómicamente."""
    
def _simulate_fatigue_level() -> float:
    """Calcula fatiga basada en tiempo y actividad."""
```

### index.py
```python
def _get_indexing_service() -> IndexingService:
    """Obtiene servicio con imports dinámicos."""
    
async def _wait_for_task_completion(
    task_id: str, 
    max_wait_seconds: int = 300
) -> Dict[str, Any]:
    """Espera completación con timeout."""
```

### websockets/progress.py
```python
async def handle_heartbeat(websocket: WebSocket, task_id: str):
    """Maneja heartbeat y detecta desconexiones."""
    
async def handle_events(
    websocket: WebSocket, 
    task_id: str,
    event_queue: asyncio.Queue
):
    """Procesa y envía eventos filtrados."""
```

## Configuración

### Variables de Configuración (`.acolyte`)
```yaml
api:
  debug: true  # Habilita campos debug en responses

ports:
  backend: 8000
  weaviate: 8080
  ollama: 11434

websockets:
  max_connections: 100      # 1-1000
  heartbeat_interval: 30    # 10-300 segundos
  connection_timeout: 60    # 30-3600 segundos
```

### Constantes del Módulo
```python
# Límites de seguridad WebSocket
MAX_CONNECTIONS_MIN = 1
MAX_CONNECTIONS_MAX = 1000
HEARTBEAT_MIN = 10
HEARTBEAT_MAX = 300
TIMEOUT_MIN = 30
TIMEOUT_MAX = 3600

# Configuración Dream
DREAM_WINDOW_32K = 28000
DREAM_CONTEXT_32K = 1500
DREAM_WINDOW_128K = 117900
```

## Headers HTTP

### Siempre incluidos
- `X-Request-ID`: ID único de request

### Con debug=true
- `X-Processing-Time`: Tiempo en ms
- `X-Tokens-Used`: Tokens consumidos
- `X-Optimization-Score`: Score de optimización

## Códigos de Error

### HTTP Status Codes
- `200`: Éxito
- `400`: Request inválido
- `404`: Recurso no encontrado
- `422`: Entidad no procesable (validación)
- `500`: Error interno del servidor

### WebSocket Close Codes
- `1000`: Cierre normal
- `1008`: Policy violation (límite conexiones)
- `1011`: Error interno del servidor

## Métodos de IndexingService Utilizados

El módulo consume los siguientes métodos:

```python
# Métodos principales
async def index_files(
    self, 
    files: List[str],
    task_id: Optional[str] = None
) -> IndexingResult

def is_supported_file(self, file_path: Path) -> bool

async def get_stats(self) -> Dict[str, Any]

# Métodos de gestión
async def estimate_files(
    self, 
    path: Path,
    include_hidden: bool = False
) -> EstimateResult

async def remove_file(self, file_path: Path) -> bool

async def rename_file(
    self,
    old_path: Path,
    new_path: Path
) -> bool
```

## Observaciones Técnicas

1. **Thread Safety**: Todo el estado compartido usa `asyncio.Lock()`
2. **Error Handling**: Manejo robusto con mensajes específicos
3. **Performance**: Logging asíncrono garantiza latencia cero
4. **Security**: Validación exhaustiva de paths y binding localhost
5. **Compatibility**: 100% compatible con clientes OpenAI
