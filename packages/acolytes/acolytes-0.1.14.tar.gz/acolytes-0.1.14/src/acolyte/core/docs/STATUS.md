# 📊 Estado del Módulo Core

## Componentes del Módulo

### chunking_config.py
Configuración de estrategias de chunking para diferentes lenguajes.
- **Estado**: Funcional
- **TODO**: Mover lógica de implementación a `/rag/chunking/` cuando esté disponible

### database.py
Thread-safe SQLite manager con transacciones ACID.
- **Estado**: Completamente funcional
- **Características implementadas**:
  - IDs hex32 usando sistema centralizado
  - Thread-safety con `asyncio.Lock()`
  - Retry diferenciado por tipo de error SQLite
  - InsightStore para Dream module
  - Esquema fijo sin migraciones (decisión arquitectónica)

### database_schemas/
Directorio con esquemas SQL del sistema.
- **Estado**: Esquemas completos y estables

### events.py
Sistema de eventos pub/sub para WebSocket.
- **Estado**: Completamente funcional
- **Características implementadas**:
  - EventBus con suscripciones filtradas
  - WebSocketManager para conexión única
  - Heartbeat automático cada 30 segundos
  - ProgressEvent con campos estadísticos completos
  - Replay de eventos históricos para debugging

### exceptions.py
Sistema completo de errores (excepciones + HTTP).
- **Estado**: Sistema consolidado y funcional
- **Características**:
  - Jerarquía completa de excepciones
  - Modelos de respuesta HTTP
  - Funciones helper para crear errores
  - Conversión automática excepción → HTTP

### id_generator.py
Generador centralizado de IDs.
- **Estado**: Sistema completamente implementado
- **Resuelve**: Inconsistencia crítica entre formatos UUID4/hex32
- **Proporciona**: Generación, validación y conversión de IDs

### logging.py
Sistema de logging asíncrono simple.
- **Estado**: Completamente funcional
- **Características implementadas**:
  - AsyncLogger con latencia cero
  - SensitiveDataMasker con regex simple
  - Control de stack traces configurable
  - Rotación automática a 10MB

### ollama.py
Cliente para LLM local.
- **Estado**: Cliente funcional
- **Características**:
  - Siempre usa modelo `acolyte:latest`
  - Cache, streaming y retry con backoff
  - Respuestas estructuradas con Pydantic

### secure_config.py
Configuración y gestión de secretos.
- **Estado**: Sistema actualizado y funcional
- **Lee de**: `.acolyte` (no config.yaml)
- **Características**:
  - Localhost binding forzado
  - Validación de paths con pathlib
  - Soporte para configuración jerárquica

### token_counter.py
Gestión inteligente de tokens.
- **Estado**: Implementación completa
- **Cambios recientes**:
  - Eliminado tiktoken (dependencia OpenAI)
  - OllamaEncoder simplificado
  - Cache con @lru_cache (maxsize=10000)
  - Sistema de ventana deslizante para Dream

### tracing.py
Sistema de observabilidad local.
- **Estado**: Base funcional para métricas
- **Características**:
  - MetricsCollector como base para todos los módulos
  - LocalTracer para debugging (sin almacenar spans)
  - Almacenamiento en memoria con opción SQLite

## Dependencias con Otros Módulos

### IndexingService en /services
Las decisiones tomadas en Core tienen impacto directo:

1. **AdaptiveChunker movido a RAG**:
   - TODO: Usar ChunkingService cuando exista en `/rag/chunking/`
   - Razón: Separación entre infraestructura y lógica de dominio

2. **EventBus y WebSocketManager listos**:
   - Sistema de eventos completamente funcional
   - IndexingService publica ProgressEvent con estadísticas

3. **Sistema de invalidación de cache**:
   - Infraestructura lista
   - TODO: Implementar lógica de re-indexación en IndexingService

## Limpieza de Código Realizada

### Código Muerto Eliminado
1. `_log_id_operation()` en id_generator.py - Función de debug nunca utilizada
2. `DEFAULT_ID_FORMAT` en id_generator.py - Variable global redundante
3. `LocalTracer.spans` en tracing.py - Lista que nunca se poblaba

### Decisiones de No Implementación
1. **Clase `Span` para LocalTracer**: Mantiene simplicidad sin overhead

### Limpieza de Dependencias
1. `tiktoken` eliminado de pyproject.toml - No se usa, reemplazado por estimación simple
2. `_token_cache` eliminado de OllamaEncoder - Redundante con @lru_cache

### Correcciones de Estilo
1. `IDFormat` removido de exports en __init__.py - Type alias no exportable
2. `event_bus` duplicado eliminado en events.py
3. imports `re` y `os` movidos al inicio en logging.py (PEP 8)

## Alertas Resueltas de Auditoría

### Dependencias externas sin validación de versión
- **Resuelto**: pyproject.toml tiene rangos semánticos completos
- Ejemplo: `pydantic = "^2.6.0"`, `loguru = "^0.7.2"`

### Configuración hardcodeada en múltiples lugares
- **Resuelto**: Sistema completamente centralizado
- Fuente de verdad: `.acolyte`
- Gestor: `core/secure_config.py`

### Manejo de errores SQLite sin retry diferenciado
- **Resuelto**: Sistema diferenciado implementado
- `SQLiteBusyError`: Reintentable
- `SQLiteCorruptError`: No reintentable
- `SQLiteConstraintError`: No reintentable

## TODOs Pendientes

### Para v2
- Optimizar DatabaseManager para consultas concurrentes
- Añadir más tipos de excepción específicos en exceptions.py
- Extender LocalTracer con almacenamiento de spans (si se necesita)

### Integración Pendiente
- Coordinar con `/rag/chunking/` cuando implemente ChunkingService
- Verificar que Dream module use InsightStore correctamente

## Tests Implementados

**Ubicación**: `/tests/core/`

### test_id_generator.py
- Generación de IDs en diferentes formatos (hex32, uuid4)
- Conversión entre formatos (to_db_format, to_display_format)
- Validación de IDs (is_valid_id)
- Detección automática de formato
- Manejo de errores

### test_logging.py
- AsyncLogger: inicialización, niveles de log
- SensitiveDataMasker: enmascaramiento de tokens, paths, hashes
- PerformanceLogger: medición de operaciones
- Manejo de stack traces configurable

### test_exceptions.py
- Jerarquía de excepciones (AcolyteError y derivadas)
- Serialización de errores a diccionarios
- Modelos de respuesta HTTP (ErrorResponse)
- Funciones helper para crear errores
- Conversión de excepciones a respuestas API (from_exception)

### test_token_counter.py
- SmartTokenCounter: conteo de tokens, cache LRU
- TokenBudgetManager: allocación y gestión de presupuesto
- Distribución dinámica por tipo de query
- Sistema de ventana deslizante para Dream
- Optimización de allocaciones

### Ejecutar Tests
```bash
# Todos los tests del core
pytest tests/core -v

# Test específico
pytest tests/core/test_id_generator.py -v

# Con cobertura
pytest tests/core --cov=acolyte.core --cov-report=html
```