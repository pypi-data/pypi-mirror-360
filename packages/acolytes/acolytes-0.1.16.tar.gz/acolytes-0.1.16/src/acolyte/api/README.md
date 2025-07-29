# 🌐 Módulo API

Interfaz HTTP/WebSocket de ACOLYTE. Expone funcionalidad mediante API REST compatible con OpenAI para integración con herramientas externas (Cursor, Continue, VSCode). Configurado para escuchar SOLO en localhost (127.0.0.1).

## 📑 Documentación

- **[docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)** - Diseño interno, decisiones arquitectónicas y patrones
- **[docs/STATUS.md](./docs/STATUS.md)** - Estado actual, componentes implementados y TODOs
- **[docs/REFERENCE.md](./docs/REFERENCE.md)** - API completa, endpoints, modelos y funciones
- **[docs/WORKFLOWS.md](./docs/WORKFLOWS.md)** - Flujos detallados, ejemplos y casos de uso
- **[docs/INTEGRATION.md](./docs/INTEGRATION.md)** - Cómo se integra con otros módulos

## 🔧 Componentes Principales

- **openai.py** - Endpoints `/v1/*` compatibles con OpenAI (chat, models, embeddings)
- **health.py** - Health checks y estadísticas del sistema
- **index.py** - Endpoints de indexación para dashboard y git hooks
- **dream.py** - Sistema Dream integrado (Deep Search para tu código)
- **websockets/progress.py** - WebSocket para progreso de operaciones largas

## 🌟 Sistema Dream Integrado

El endpoint `/api/dream/*` ahora está completamente funcional:

- **`GET /api/dream/status`** - Nivel de fatiga actual y recomendaciones
- **`POST /api/dream/optimize`** - Iniciar análisis profundo (requiere aprobación)
- **`GET /api/dream/insights`** - Ver insights descubiertos

Dream es como activar "Deep Search" en ChatGPT pero para tu código.

## ⚡ Quick Start

```python
# Configurar en Cursor/Continue
{
    "api_endpoint": "http://localhost:8000/v1",
    "apiKey": "not-needed",
    "model": "gpt-3.5-turbo"
}

# Usar con Python
import requests

response = requests.post("http://localhost:8000/v1/chat/completions", json={
    "messages": [{"role": "user", "content": "Explica async/await"}],
    "model": "gpt-3.5-turbo"
})

# Health check
health = requests.get("http://localhost:8000/api/health").json()
print(f"Status: {health['status']}")

# Check Dream fatigue
dream_status = requests.get("http://localhost:8000/api/dream/status").json()
if dream_status["fatigue_level"] > 7.5:
    print("Alta fatiga detectada - considera ejecutar análisis profundo")
```

## 🔌 Endpoints Principales

### OpenAI Compatible
- `POST /v1/chat/completions` - Chat principal
- `GET /v1/models` - Lista modelos
- `POST /v1/embeddings` - Genera embeddings

### Sistema
- `GET /api/health` - Estado del sistema
- `GET /api/dream/status` - Estado Dream y fatiga
- `POST /api/dream/optimize` - Iniciar análisis profundo
- `GET /api/dream/insights` - Obtener insights
- `POST /api/index/project` - Indexar proyecto
- `WS /api/ws/progress/{id}` - Progreso real-time

## 🚀 Características Clave

- **100% Compatible OpenAI** - Funciona con cualquier cliente OpenAI
- **Dream System Real** - Análisis profundo con fatiga basada en métricas Git
- **WebSocket EventBus** - Notificaciones real-time de progreso
- **Thread-Safe** - Operaciones concurrentes seguras
- **Validación Robusta** - ~50 líneas de validación de paths
- **Debug Opcional** - Información detallada cuando la necesitas

## 📝 Notas

- Puerto por defecto: 8000 (configurable en `.acolyte`)
- Binding: Solo localhost por seguridad
- Logging: Asíncrono con latencia cero
- Estado: Production-ready con Dream completamente funcional
- Dream: Siempre requiere permiso explícito del usuario

## 🔧 Cambios Recientes (20/06/25)

- **Migración a Lifespan**: Actualizado de `@app.on_event` (deprecated) al nuevo sistema de `lifespan` de FastAPI
- **Fix NumPy Warning**: Corregido warning de reimportación de NumPy en el módulo embeddings
- **Tests Index Fixed**: Corregidos tests de `test_index.py` - Los objetos Path en Python son read-only, actualizado el approach de mocking
- **Fix Header Handling**: Corregido manejo de `Header(None)` en endpoints OpenAI - Ahora se verifica explícitamente si es None antes de usar generate_id()
- **ConfigurationError Handling**: Agregado manejo específico para ConfigurationError en chat_completions - Ahora devuelve 400 en lugar de 500
