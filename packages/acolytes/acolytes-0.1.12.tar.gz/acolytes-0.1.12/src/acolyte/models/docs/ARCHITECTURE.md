# 🏗️ Arquitectura del Módulo Models

## Principios de Diseño

1. **Simplicidad primero**: Empezar con campos mínimos, expandir según necesidad
2. **Validación estricta**: Usar validators de Pydantic para seguridad
3. **Sin user_id**: Sistema mono-usuario local
4. **Sin rate limiting**: No hay límites en sistema local
5. **IDs compatibles**: hex32 estándar vía mixins especializados

## Configuración Base Avanzada

`AcolyteBaseModel` incluye configuración Pydantic optimizada:

```python
class AcolyteBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,   # Validar al asignar valores
        use_enum_values=True,       # Usar valores de enum en serialización
        json_encoders={             # Encoders customizados
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v),
        },
        extra="forbid",             # Prevenir campos extra
        json_schema_extra={         # Mejor documentación de schemas
            "additionalProperties": False
        }
    )
```

## Patrón Strategy para IDs

Resuelve inconsistencias arquitectónicas manteniendo compatibilidad total.

### Protocolo Unificado

```python
from acolyte.models.base import Identifiable

def process_any_model(model: Identifiable):
    pk = model.primary_key         # Funciona con cualquier estrategia
    field = model.primary_key_field # "id" o "session_id"
```

### Estrategias Implementadas

#### StandardIdMixin (Por defecto)
- **Usado por**: Chunk, Document, TaskCheckpoint, TechnicalDecision, etc.
- **Campo**: `id` (hex32 vía `generate_id()`)

#### SessionIdMixin (Dominio conversaciones)
- **Usado por**: Conversation
- **Campo**: `session_id` (hex32 vía `generate_id()`)
- **Justificación**: Evita redundancia BD (campos `id` + `session_id`)

## Sistema de Errores Unificado

Todo el manejo de errores está consolidado en `core/exceptions.py`:

```python
# Usar siempre imports desde Core
from acolyte.core.exceptions import ErrorResponse, DatabaseError, validation_error

# O para compatibilidad (models re-exporta)
from acolyte.models import ErrorResponse
```

## Logging y Métricas

### Logger Global
```python
# Usar siempre el logger global singleton
from acolyte.core.logging import logger

# NO crear instancias de AsyncLogger
# ✅ CORRECTO
logger.info("Model created", model_id=self.id)

# ❌ INCORRECTO  
self.logger = AsyncLogger("models")  # NO hacer esto
```

### MetricsCollector Pattern
```python
# Instanciar sin namespace
from acolyte.core.metrics import MetricsCollector

self.metrics = MetricsCollector()  # Sin parámetros

# Usar prefijos en las métricas
self.metrics.increment("models.conversation.created")
self.metrics.record("models.validation.time_ms", elapsed)
```

### Datetime Centralization
```python
# Usar helpers centralizados en lugar de datetime.utcnow()
from acolyte.core.utils.datetime_utils import utc_now, utc_now_iso

# ✅ CORRECTO
created_at: datetime = Field(default_factory=utc_now)
timestamp_iso = utc_now_iso()  # Para SQLite/Weaviate

# ❌ INCORRECTO
created_at = datetime.utcnow()  # Deprecated pattern
```

## Decisiones Arquitectónicas Clave

### Decisión #1: Resúmenes vs Conversaciones Completas
- **Diseño**: Una sesión = UNA fila en conversations con role='system'
- **Contenido**: Resúmenes acumulados, NO mensajes individuales
- **PRIMARY KEY**: `session_id` es el único identificador (sin campo 'id')
- **Reducción**: ~90% menos tokens almacenados

### Decisión #2: 18 ChunkTypes
Granularidad necesaria para búsqueda precisa en código:
- **Funcional**: FUNCTION, METHOD, CONSTRUCTOR, PROPERTY
- **Estructural**: CLASS, INTERFACE, MODULE, NAMESPACE
- **Documental**: COMMENT, DOCSTRING, README
- **Semántico**: IMPORTS, CONSTANTS, TYPES, TESTS
- **Jerárquico**: SUMMARY, SUPER_SUMMARY
- **Fallback**: UNKNOWN

### Decisión #3: Jerarquía Task > Session > Message
- Sesiones son cortas (horas)
- Tareas son largas (días/semanas)  
- Una tarea agrupa múltiples sesiones relacionadas

### Decisión #4: Dream es Técnico
NO es antropomorfización. Es optimización real de embeddings:
- Métricas reales de fragmentación
- Performance degradation medible
- Reorganización de vectores para mejor búsqueda

### Decisión #5: Embeddings Directos a Weaviate
Los embeddings NO se almacenan en modelos Pydantic:
- Se calculan con UniXcoder
- Van directo a Weaviate
- Los modelos solo tienen la interfaz `to_search_text()`

### Decisión #6: Validación Pragmática
Para sistema local mono-usuario:
- Solo validar errores reales (path traversal, paths absolutos)
- No sobre-proteger contra "ataques" imposibles
- Confiar en el usuario local

### Decisión #7: Interfaces Estándar
Dos interfaces clave para todos los modelos relevantes:
- `get_summary()` - Para humanos y System Prompt
- `to_search_text()` - Para embeddings y búsqueda

### Decisión #8: Configuración Dinámica
Valores leídos desde `.acolyte` (fuente de verdad):
- Límites de batch
- Configuración de cache
- Umbrales de optimización

### Decisión #9: Métodos Helper Seguros
Para campos `Optional` en GitMetadata:
- Métodos `get_*()` devuelven valores por defecto
- Evitan NULL errors en código consumidor
- Valores conservadores (neutros)

### Decisión #10: Enums en Mayúsculas para BD
- SQLite valida con CHECK constraints en MAYÚSCULAS
- Python debe convertir con `.upper()`
- Consistencia entre BD y código

## Compatibilidad con Base de Datos

### IDs Centralizados (hex32)
```python
from acolyte.core.id_generator import generate_id
id = generate_id()  # "a3f4b2c1d5e6f7a8b9c0d1e2f3a4b5c6"
```

### Weaviate sin Vectorizer
```json
// vectorizer: "none" porque usamos UniXcoder
// Los embeddings se calculan en Python
```

### SQLite con Validación Estricta
- PRIMARY KEY TEXT NOT NULL UNIQUE
- CHECK constraints para enums
- Foreign Keys para integridad referencial
