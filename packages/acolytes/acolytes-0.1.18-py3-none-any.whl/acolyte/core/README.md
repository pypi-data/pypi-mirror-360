# 🛠️ Módulo Core

Componentes fundamentales del sistema ACOLYTE. Base sobre la cual se construye toda la aplicación.

## 📑 Documentación

- **[docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)** - Diseño interno, principios y decisiones arquitectónicas
- **[docs/STATUS.md](./docs/STATUS.md)** - Estado actual del módulo y componentes
- **[docs/REFERENCE.md](./docs/REFERENCE.md)** - API completa con todas las clases y métodos
- **[docs/WORKFLOWS.md](./docs/WORKFLOWS.md)** - Flujos principales y ejemplos de uso
- **[docs/INTEGRATION.md](./docs/INTEGRATION.md)** - Cómo Core se integra con otros módulos

## 🔧 Componentes Principales

- **chunking_config.py** - Configuración de estrategias de chunking para diferentes lenguajes
- **database.py** - Sistema de persistencia SQLite thread-safe con InsightStore
- **events.py** - Sistema pub/sub para WebSocket y coordinación entre módulos
- **exceptions.py** - Sistema completo de errores (excepciones Python + respuestas HTTP)
- **id_generator.py** - Generador centralizado de IDs hex32 compatible con SQLite
- **logging.py** - Sistema de logging asíncrono con latencia cero
- **ollama.py** - Cliente HTTP para LLM local (siempre usa acolyte:latest)
- **secure_config.py** - Configuración segura desde .acolyte con validación
- **token_counter.py** - Gestión inteligente de tokens con presupuesto dinámico
- **tracing.py** - Sistema base de métricas y observabilidad local

## ⚡ Quick Start

```python
# Generar IDs únicos
from acolyte.core.id_generator import generate_id
session_id = generate_id()  # "a3f4b2c1d5e6f7a8b9c0d1e2f3a4b5c6"

# Manejo de errores
from acolyte.core.exceptions import ValidationError
if not data:
    raise ValidationError("Data required")

# Logging global (patrón correcto)
from acolyte.core.logging import logger  # Singleton global
logger.info("Processing started")
# NO hacer: logger = AsyncLogger("my_module")

# Gestión de tokens
from acolyte.core.token_counter import SmartTokenCounter
counter = SmartTokenCounter()
tokens = counter.count_tokens("Hello world")

# Base de datos thread-safe
from acolyte.core.database import DatabaseManager
db = DatabaseManager()
result = await db.execute_async("SELECT * FROM conversations", fetch="all")

# EventBus global
from acolyte.core.events import event_bus  # Singleton global
await event_bus.publish(my_event)

# Datetime helpers
from acolyte.core.utils.datetime_utils import utc_now, utc_now_iso
timestamp = utc_now()  # NO usar datetime.utcnow()
```

## 🎯 Propósito

Core proporciona servicios centralizados que todos los módulos usan y extienden:

- **Sin duplicación**: Cada módulo USA la infraestructura de Core
- **Thread-safe**: Operaciones seguras para concurrencia
- **Localhost only**: Binding estricto a 127.0.0.1
- **Paths seguros**: Validación con pathlib
- **IDs centralizados**: Sistema unificado hex32

## 🔨 Cambios Recientes

### Test Fix - WebSocketManager heartbeat (23/06/25)

- **Problema**: Test `test_heartbeat_successful_ping` fallaba después de correcciones de lint
- **Causa**: El test no configuraba correctamente el estado del WebSocketManager
  - Solo configuraba `is_connected_flag = True`
  - No asignaba el mock websocket a `_websocket`
  - El método `is_connected()` requiere AMBOS: `_websocket is not None AND is_connected_flag`
- **Fix aplicado**:
  1. Asignar mock websocket ANTES de configurar el flag
  2. Usar Mock con `send_text = AsyncMock()` explícito (WebSocket no tiene send_text en su spec)
  3. Mockear `asyncio.sleep` para evitar esperar 30 segundos del heartbeat interval
  4. Usar `CancelledError` para salir limpiamente del loop después del primer ping
- **Lección**: Al mockear, respetar todas las dependencias internas del código
