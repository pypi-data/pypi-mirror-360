# 📘 Referencia Técnica del Módulo Core

## 📦 chunking_config.py

### Enums
```python
class ChunkingStrategy(Enum):
    SEMANTIC = "semantic"       # Basado en significado del código
    HIERARCHICAL = "hierarchical"  # Respeta jerarquía de clases/funciones
    FIXED_SIZE = "fixed_size"   # Tamaño fijo con overlap
    ADAPTIVE = "adaptive"       # Ajuste dinámico según complejidad
```

### Clases

#### `ChunkingConfig`
```python
class ChunkingConfig:
    @staticmethod
    def get_strategy_config(strategy: ChunkingStrategy, language: str) -> StrategyConfig
    """Configuración optimizada por estrategia y lenguaje con reglas específicas"""
    
    @staticmethod
    def validate_chunk(chunk: str, min_size: int, max_size: int, language: str) -> ValidationResult
    """Valida calidad de chunk: tamaño, sintaxis, contexto y estructura preservada"""
```

#### `StrategyConfig` (dataclass)
```python
@dataclass
class StrategyConfig:
    chunk_size: int
    overlap: int
    min_chunk_size: int
    max_chunk_size: int
    rules: Dict[str, Any]
```

#### `ValidationResult` (dataclass)
```python
@dataclass
class ValidationResult:
    is_valid: bool
    score: float  # 0-1
    problems: List[str]
```

## 📦 database.py

### Clases

#### `DatabaseManager`
```python
class DatabaseManager:
    async def execute_async(
        self, 
        query: str, 
        params: tuple = (), 
        fetch: FetchType = FetchType.NONE
    ) -> QueryResult
    """Ejecución asíncrona con retry automático, thread-safety y clasificación de errores SQLite"""
    
    def transaction(self, isolation_level: str = "DEFERRED") -> ContextManager
    """Context manager para transacciones ACID con rollback automático"""
    
    def _classify_sqlite_error(self, sqlite_error: sqlite3.Error) -> DatabaseError
    """Mapea errores SQLite a excepciones específicas: Busy(reintentable), Corrupt(fatal), Constraint(validación)"""
```

#### `InsightStore`
```python
class InsightStore:
    async def store_insights(
        self, 
        session_id: str, 
        insights: List[Dict[str, Any]], 
        compression_level: int = 6
    ) -> StoreResult
    """Almacena insights con compresión zlib y deduplicación para Dream module"""
    
    async def get_insights(
        self, 
        query: str = "", 
        limit: int = 100
    ) -> List[Dict[str, Any]]
    """Búsqueda full-text en insights comprimidos"""
```

## 📦 exceptions.py

### Jerarquía de Excepciones

#### `AcolyteError` (Base)
```python
class AcolyteError(Exception):
    def __init__(self, message: str, code: str = None, cause: Exception = None):
        self.id = generate_id()
        self.message = message
        self.code = code
        self.cause = cause
        self.suggestions = []
        self.context = {}
    
    def add_suggestion(self, suggestion: str) -> None:
        """Añade sugerencia de resolución acumulativa"""
    
    def is_retryable(self) -> bool:
        """Determina si amerita retry automático"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Serializa para API con error_id, context, suggestions"""
```

#### Excepciones Específicas
- `DatabaseError` - Problemas con SQLite o Weaviate (retryable)
- `SQLiteBusyError` - BD ocupada temporalmente (retryable)
- `SQLiteCorruptError` - BD corrupta (fatal)
- `SQLiteConstraintError` - Violación de restricciones
- `VectorStaleError` - Embeddings desactualizados
- `ConfigurationError` - Configuración inválida o faltante
- `ValidationError` - Datos que no pasan validación
- `NotFoundError` - Recurso solicitado no existe
- `ExternalServiceError` - Fallas en servicios externos (retryable)

### Modelos de Respuesta HTTP

#### `ErrorType` (Enum)
```python
class ErrorType(str, Enum):
    VALIDATION = "validation_error"
    NOT_FOUND = "not_found"
    INTERNAL = "internal_error"
    EXTERNAL_SERVICE = "external_service_error"
    CONFIGURATION = "configuration_error"
    DATABASE = "database_error"
```

#### `ErrorDetail` (BaseModel)
```python
class ErrorDetail(BaseModel):
    field: str
    value: Any
    reason: str
```

#### `ErrorResponse` (BaseModel)
```python
class ErrorResponse(BaseModel):
    error: str
    message: str
    type: ErrorType
    details: Optional[List[ErrorDetail]] = None
    suggestions: Optional[List[str]] = None
    error_id: Optional[str] = None
```

### Helper Functions
```python
def validation_error(field: str, value: Any, reason: str) -> ErrorResponse:
    """Crea error de validación con detalles del campo"""

def not_found_error(resource: str, identifier: str) -> ErrorResponse:
    """Error estándar para recursos no encontrados"""

def internal_error(message: str, error_id: str = None) -> ErrorResponse:
    """Errores internos del servidor"""

def external_service_error(service: str, message: str) -> ErrorResponse:
    """Fallos de servicios externos"""

def configuration_error(message: str, field: str = None) -> ErrorResponse:
    """Errores de configuración"""

def from_exception(exc: AcolyteError) -> ErrorResponse:
    """Convierte AcolyteError → ErrorResponse automáticamente"""
```

## 📦 id_generator.py

### Tipos
```python
IDFormat = Literal["hex32", "uuid4"]
```

### Clases

#### `IDGenerator`
```python
class IDGenerator:
    DEFAULT_FORMAT: IDFormat = "hex32"
    
    @staticmethod
    def generate(format: IDFormat = "hex32") -> str:
        """Genera ID en formato específico (hex32 o uuid4)"""
    
    @staticmethod
    def to_db_format(id_str: str) -> str:
        """Convierte cualquier ID a hex32 compatible con SQLite"""
    
    @staticmethod
    def to_display_format(hex_str: str) -> str:
        """Convierte hex32 a UUID4 con guiones para display"""
    
    @staticmethod
    def detect_format(id_str: str) -> Optional[IDFormat]:
        """Detecta formato de ID (hex32 o uuid4)"""
    
    @staticmethod
    def is_valid_hex32(id_str: str) -> bool:
        """Valida formato hex32"""
    
    @staticmethod
    def is_valid_uuid4(id_str: str) -> bool:
        """Valida formato UUID4"""
```

### Funciones Convenience
```python
def generate_id(format: IDFormat = "hex32") -> str:
    """Función más usada, genera hex32 por defecto"""

def is_valid_id(id_str: str, format: Optional[IDFormat] = None) -> bool:
    """Valida formato de ID con auto-detección"""
```

## 📦 events.py

### Enums
```python
class EventType(str, Enum):
    PROGRESS = "progress"
    LOG = "log"
    STATUS = "status"
    ERROR = "error"
    INSIGHT = "insight"
    OPTIMIZATION_NEEDED = "optimization_needed"
    CACHE_INVALIDATE = "cache_invalidate"
```

### Clases Base

#### `BaseEvent`
```python
class BaseEvent:
    def __init__(self, event_type: EventType, source: str):
        self.id = generate_id()
        self.type = event_type
        self.source = source
        self.timestamp = datetime.utcnow()
        self.data = {}
```

### Eventos Específicos

#### `ProgressEvent`
```python
class ProgressEvent(BaseEvent):
    def __init__(
        self,
        source: str,
        operation: str,
        current: int,
        total: int,
        message: str = "",
        task_id: Optional[str] = None,
        files_skipped: int = 0,
        chunks_created: int = 0,
        embeddings_generated: int = 0,
        errors: int = 0,
        current_file: Optional[str] = None
    ):
        """Evento especializado para progreso de operaciones largas con estadísticas completas"""
    
    @property
    def percentage(self) -> float:
        """Calcula porcentaje de progreso"""
    
    def to_json(self) -> str:
        """Serializa a JSON incluyendo todos los campos y porcentaje calculado"""
```

#### `CacheInvalidateEvent`
```python
class CacheInvalidateEvent(BaseEvent):
    def __init__(
        self,
        source: str,
        reason: str,
        target_service: str = "all",
        pattern: Optional[str] = None,
        files: Optional[List[str]] = None
    ):
        """Evento para invalidación coordinada de caches entre servicios"""
```

### Sistema de Eventos

#### `EventBus`
```python
class EventBus:
    async def publish(self, event: BaseEvent) -> None:
        """Publica a suscriptores con error handling y filtros"""
    
    def subscribe(
        self,
        event_type: EventType,
        callback: Callable[[BaseEvent], Awaitable[None]],
        filter: Optional[Callable[[BaseEvent], bool]] = None
    ) -> str:
        """Suscripción con filtros opcionales, retorna subscription_id"""
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """Cancela suscripción"""
    
    def replay(
        self,
        from_timestamp: Optional[datetime] = None,
        to_timestamp: Optional[datetime] = None,
        event_types: Optional[List[EventType]] = None
    ) -> List[BaseEvent]:
        """Filtra eventos históricos para debugging"""
```

#### `WebSocketManager`
```python
class WebSocketManager:
    async def connect(self, websocket: WebSocket) -> None:
        """Acepta conexión única para sistema mono-usuario"""
    
    async def send_event(self, event: BaseEvent) -> bool:
        """Envía con retry automático y heartbeat cada 30s"""
    
    async def disconnect(self) -> None:
        """Cierra conexión limpiamente"""
    
    def is_connected(self) -> bool:
        """Verifica estado de conexión"""
```

## 📦 logging.py

### Clases

#### `AsyncLogger`
```python
class AsyncLogger:
    def __init__(self, name: str, debug_mode: bool = False):
        """Configura logger asíncrono con enqueue=True para latencia cero"""
    
    def error(self, message: str, include_trace: bool = None, **context) -> None:
        """Log error con stack trace configurable y contexto"""
    
    def info(self, message: str, **context) -> None:
    def warning(self, message: str, **context) -> None:
    def debug(self, message: str, **context) -> None:
    def critical(self, message: str, **context) -> None:
        """Logging asíncrono con contexto adicional"""
```

#### `SensitiveDataMasker`
```python
class SensitiveDataMasker:
    @staticmethod
    def mask(text: str) -> str:
        """Enmascara tokens largos, paths, API keys con regex"""
```

#### `PerformanceLogger`
```python
class PerformanceLogger:
    @contextmanager
    def measure(self, operation_name: str):
        """Context manager para medir duración de operaciones"""
```

## 📦 ollama.py

### Clases

#### `OllamaClient`
```python
class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", timeout: int = 30):
        """Cliente HTTP para Ollama con modelo fijo acolyte:latest"""
    
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> str:
        """Genera respuesta con cache, retry automático y modelo fijo acolyte:latest"""
    
    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[BaseModel],
        system: Optional[str] = None,
        **kwargs
    ) -> BaseModel:
        """Respuesta JSON validada con Pydantic"""
    
    async def count_tokens(self, text: str) -> int:
        """Cuenta tokens usando API de Ollama"""
    
    async def close(self) -> None:
        """Cierra sesión HTTP apropiadamente"""
```

## 📦 secure_config.py

### Clases

#### `Settings`
```python
class Settings:
    def __init__(self, config_path: Optional[Path] = None):
        """Lee configuración de .acolyte con validación"""
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtiene configuración con soporte paths anidados desde .acolyte"""
    
    def validate_localhost_binding(self, host: str) -> bool:
        """Fuerza binding a 127.0.0.1 estrictamente"""
    
    def validate_path_safety(self, path: Union[str, Path]) -> Path:
        """Previene path traversal con pathlib"""
```

## 📦 token_counter.py

### Enums
```python
class TruncateStrategy(str, Enum):
    END = "end"        # Corta al final
    START = "start"    # Corta al inicio
    MIDDLE = "middle"  # Corta en el medio
    SMART = "smart"    # Preserva inicio y fin
```

### Tipos
```python
TokenDistribution = TypedDict('TokenDistribution', {
    'system': int,
    'context': int,
    'response': int,
    'total_available': int
})
```

### Clases

#### `TokenCount` (dataclass)
```python
@dataclass
class TokenCount:
    total: int
    content: int
    role: int = 0
    name: int = 0
```

#### `SmartTokenCounter`
```python
class SmartTokenCounter:
    def __init__(self):
        """Inicializa con encoder simple sin dependencias"""
    
    def count_tokens(self, text: str) -> int:
        """Conteo con cache LRU y estimación rápida para textos largos"""
    
    def count(self, content: str, role: str = "", name: str = "") -> TokenCount:
        """Conteo detallado con desglose por componente"""
    
    def truncate_to_limit(
        self,
        text: str,
        limit: int,
        strategy: TruncateStrategy = TruncateStrategy.SMART
    ) -> str:
        """Truncado inteligente con 4 estrategias"""
```

#### `TokenBudgetManager`
```python
class TokenBudgetManager:
    def __init__(self, context_size: int):
        """Gestión del límite TOTAL del modelo"""
    
    def allocate(
        self,
        category: str,
        tokens: int,
        priority: int = 5
    ) -> bool:
        """Reserva tokens por categoría"""
    
    def use(self, category: str, tokens: int) -> bool:
        """Consume tokens reservados"""
    
    def optimize_allocations(self) -> Dict[str, int]:
        """Rebalancea según prioridades"""
    
    def allocate_for_query_type(
        self,
        query_type: str
    ) -> TokenDistribution:
        """Distribución automática: generation(75%/25%), simple(20%/80%), default(10%/90%)"""
    
    def allocate_for_dream_cycle(
        self,
        cycle_number: int
    ) -> Dict[str, int]:
        """Ventana deslizante para Dream: 28k código + 1.5k contexto en modelos 32k"""
```

## 📦 tracing.py

### Clases

#### `LocalTracer`
```python
class LocalTracer:
    def __init__(self, service_name: str):
        """Tracer local simple para debugging"""
    
    @contextmanager
    def span(self, name: str, attributes: Dict[str, Any] = None):
        """Context manager para tracing de operaciones"""
```

#### `MetricsCollector`
```python
class MetricsCollector:
    def __init__(self):
        """Sistema BASE de métricas para todo ACOLYTE.
        
        IMPORTANTE: NO acepta namespace. Los módulos deben incluir
        su namespace en el nombre de la métrica:
        - CORRECTO: metrics.increment("semantic.task_detector.count")
        - INCORRECTO: MetricsCollector(namespace="semantic")
        """
    
    def increment(self, name: str, value: float = 1.0):
        """Incrementa contador."""
    
    def gauge(self, name: str, value: float):
        """Establece valor actual."""
    
    def record(self, name: str, value: float):
        """Registra una medición (alias de gauge)."""
    
    def get_metrics(self) -> Dict[str, float]:
        """Obtiene todas las métricas registradas."""
```

## 🔗 Dependencias del Módulo

### Dependencias Externas
- `aiosqlite` - Persistencia asíncrona SQLite con thread-safety
- `loguru` - Sistema de logging asíncrono con enqueue=True
- `aiohttp` - Cliente HTTP para Ollama con retry automático
- `pydantic` - Validación de configuración y modelos de error
- `pathlib` - Validación segura de paths sin shell commands
- `asyncio` - Locks para thread-safety y serialización

### Enlaces Internos
- `DatabaseManager` - Singleton usado por InsightStore y módulos persistentes
- `AsyncLogger` - Singleton para logging consistente en TODO el sistema
- `Settings` - Singleton para configuración centralizada desde .acolyte
- `MetricsCollector` - Base para métricas del sistema (composición, no herencia)
- `IDGenerator` - Funciones usadas por todos los mixins en Models
- `EventBus` - Hub central para comunicación entre módulos vía eventos