# 📊 Estado del Módulo API

## Componentes del Módulo

### openai.py
Implementa endpoints OpenAI-compatible bajo `/v1/*`.

**Endpoints operativos**:
- `POST /v1/chat/completions` - Endpoint principal de chat con sesión automática
- `GET /v1/models` - Lista modelos disponibles (retorna acolyte:latest)
- `POST /v1/embeddings` - Genera embeddings usando UniXcoder

**Características activas**:
- Detecta nuevo chat y carga contexto previo automáticamente
- System Prompt Dinámico con contexto del proyecto
- Campos debug opcionales sin romper compatibilidad
- Sesiones automáticas con ID único generado

### health.py
Sistema de health checks completo.

**Endpoints operativos**:
- `GET /api/health` - Estado de todos los servicios
- `GET /api/stats` - Estadísticas generales del sistema
- `GET /api/websocket-stats` - Estadísticas de conexiones WebSocket

**Verificaciones implementadas**:
- Weaviate: conexión real con estadísticas de collections
- Ollama: verificación de disponibilidad
- SQLite: estado de base de datos
- Detección de collections faltantes y total de vectores

### index.py
Endpoints de indexación para dashboard y git hooks.

**Endpoints operativos**:
- `POST /api/index/project` - Indexación completa del proyecto
- `POST /api/index/git-changes` - Re-indexación tras commits

**Pipeline funcional**:
- Chunking → Enrichment → Embeddings → Weaviate
- Progreso en tiempo real vía EventBus
- Validación exhaustiva de paths (~50 líneas)
- Manejo de archivos nuevos y modificados

### dream.py
Sistema de optimización de base vectorial.

**Endpoints operativos**:
- `GET /api/dream/status` - Estado actual del optimizador
- `POST /api/dream/optimize` - Iniciar optimización (requiere confirmación)
- `GET /api/dream/insights` - Patrones descubiertos

**Estado actual**: 
- Simulación temporal thread-safe con funciones helper
- Preparado para integración con módulo `/dream` real
- Sistema de ventana deslizante configurado
- Thread-safety con `asyncio.Lock()`

### websockets/progress.py
WebSocket para operaciones largas.

**Endpoint operativo**:
- `WS /api/ws/progress/{id}` - Stream de progreso de indexación

**Características implementadas**:
- Sistema EventBus completamente funcional
- Filtrado preciso por task_id
- Heartbeat automático para detectar desconexiones
- Límite configurable de conexiones (1-1000)
- TypedDict para type safety

## Funcionalidad Pendiente

### Para v2
- **Endpoint de búsqueda manual**: Para dashboard web futuro
- **Reemplazo de simulaciones**: Dream real cuando módulo esté listo
- **CLI integration**: Comandos desde terminal
- **Métricas avanzadas**: Dashboards de performance

### TODOs Activos

1. **Dashboard Web**
   - TODO: Implementar frontend para indexación manual
   - Endpoints ya listos, falta UI

## Limitaciones Conocidas

### Simulaciones Temporales
- **Dream System**: Usa estado simulado hasta implementación real
- **Fatiga calculada**: Basada en métricas simuladas, no reales

### Configuración
- **Emojis en logs**: No configurable aún vía `.acolyte`
- **Debug por defecto**: True, cambiar requiere editar `.acolyte`

### Performance
- **Indexación inicial**: Puede ser lenta en proyectos grandes
- **WebSocket**: Límite de 1000 conexiones simultáneas

## Dependencias con Otros Módulos

### Requiere de Services
- **ChatService**: Para procesamiento de chat
- **IndexingService**: Para indexación de archivos
- **ConversationService**: Para gestión de sesiones

### Requiere de Core
- **EventBus**: Para distribución de eventos
- **WebSocketManager**: Para gestión de conexiones
- **IDGenerator**: Para IDs únicos de sesión
- **SecureConfig**: Para leer `.acolyte`
- **AsyncLogger**: Para logging sin latencia

### Requiere de Embeddings
- **UniXcoderEmbeddings**: Para endpoint `/v1/embeddings`

## Métricas de Calidad

- **Cobertura de endpoints**: 100% implementados
- **Thread safety**: Garantizado en operaciones concurrentes
- **Latencia logging**: 0ms con QueueHandler
- **Compatibilidad OpenAI**: 100% formato estándar
- **Seguridad paths**: Validación exhaustiva implementada

## Cobertura de Tests (21/06/25)

- ✅ **Excelente cobertura**:
  - openai.py: 98%
  - dream.py: 100%
  - health.py: 92%
  - index.py: 90%
  - websockets/progress.py: 95%

## Notas de Implementación

### Session ID Simplificado
- Migrado de timestamp complejo a IDGenerator simple
- De 40 líneas a 1 línea de código
- 128 bits de entropía sin colisiones

### Health Checks Mejorados
- Separación clara de 4 tipos de error
- Mensajes específicos con sugerencias
- Código simplificado para mono-usuario

### WebSocket con EventBus
- Migrado de sistema acoplado a pub-sub
- Sin llamadas directas entre servicios
- Resiliente a fallos de componentes

## Versión y Compatibilidad

- **Versión API**: v1 (OpenAI compatible)
- **Python mínimo**: 3.11+
- **FastAPI**: Latest
- **Binding**: localhost only (127.0.0.1)
