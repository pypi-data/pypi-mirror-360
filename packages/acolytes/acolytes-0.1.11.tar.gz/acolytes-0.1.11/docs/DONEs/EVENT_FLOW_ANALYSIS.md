# 🔄 ANÁLISIS DEL FLUJO DE EVENTOS DURANTE INDEXACIÓN

## Resumen Ejecutivo

El sistema de eventos en ACOLYTE es crítico para la comunicación entre servicios. Durante la indexación se publican principalmente **ProgressEvent** para actualización en tiempo real. Los eventos siguen un formato específico que NO debe modificarse sin actualizar todos los consumidores.

## 📋 Eventos Publicados Durante Indexación

### 1. ProgressEvent - El Principal

**Publicado por**: `IndexingService._notify_progress()` (línea 707)

**Formato EXACTO**:
```python
ProgressEvent(
    source="indexing_service",
    operation="indexing_files",
    current=234,              # Archivos procesados
    total=585,                # Total de archivos
    message="Processing: src/main.py",
    task_id="idx_1234567890_abc",  # Crítico para filtrado
    
    # Campos adicionales de estadísticas:
    files_skipped=12,         # Archivos ignorados
    chunks_created=1847,      # Chunks creados hasta ahora
    embeddings_generated=1847,# Embeddings generados
    errors=3,                 # Errores encontrados
    current_file="src/main.py"# Archivo actual
)
```

**Serialización JSON**:
```json
{
    "id": "0123456789abcdef0123456789abcdef",
    "type": "progress",
    "timestamp": "2025-01-08T10:30:45.123456",
    "source": "indexing_service",
    "operation": "indexing_files",
    "current": 234,
    "total": 585,
    "percentage": 40.0,
    "message": "Processing: src/main.py",
    "task_id": "idx_1234567890_abc",
    "files_skipped": 12,
    "chunks_created": 1847,
    "embeddings_generated": 1847,
    "errors": 3,
    "current_file": "src/main.py"
}
```

### 2. CacheInvalidateEvent - Trigger de Re-indexación

**NO publicado por IndexingService**, pero inicia re-indexación.

**Publicado por**: GitService
**Consumido por**: ReindexService

**Formato**:
```python
CacheInvalidateEvent(
    source="git_service",
    target_service="indexing",
    key_pattern="*auth.py*",
    reason="Files updated after pull"
)
```

## 🎯 Flujo Detallado de Eventos

### Fase 1: Inicio de Indexación
```
1. Usuario ejecuta 'acolyte index'
2. CLI envía POST a /api/index/project
3. API retorna task_id: "idx_1234567890_abc"
4. BackgroundTask inicia _run_project_indexing
```

### Fase 2: Procesamiento y Notificación
```python
# En IndexingService.index_files():
for i in range(0, len(valid_files), self.batch_size):
    batch = valid_files[i:i+self.batch_size]
    result = await self._process_batch(batch, trigger)
    
    # Notificar progreso
    await self._notify_progress(
        progress={
            "total_files": len(valid_files),
            "processed_files": i + len(batch),
            "current_file": batch[-1],
            "percentage": (i + len(batch)) / len(valid_files) * 100
        },
        task_id=task_id,  # CRÍTICO para WebSocket
        files_skipped=files_skipped,
        chunks_created=total_chunks,
        embeddings_generated=total_embeddings,
        errors_count=len(errors)
    )
```

### Fase 3: Publicación en EventBus
```python
# En _notify_progress():
progress_event = ProgressEvent(...)
await event_bus.publish(progress_event)
```

### Fase 4: WebSocket Consume Eventos

**En `api/ws.py`** (no mostrado pero inferido):
```python
# WebSocket filtra por task_id
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    # Suscribe a eventos donde task_id coincide
    unsubscribe = event_bus.subscribe(
        EventType.PROGRESS,
        lambda e: send_if_matches(e, task_id),
        filter=lambda e: e.task_id == task_id
    )
```

## ⚠️ Suscriptores de Cada Tipo de Evento

### ProgressEvent
1. **WebSocketManager**
   - Propósito: Actualizar UI en tiempo real
   - Filtro: Por task_id si se proporciona
   - Acción: Envía JSON al cliente web

2. **MetricsCollector** (implícito)
   - Propósito: Estadísticas del sistema
   - Filtro: Ninguno
   - Acción: Actualiza gauges y counters

### CacheInvalidateEvent
1. **ReindexService**
   - Propósito: Re-indexar archivos modificados
   - Filtro: `target_service == "indexing"`
   - Acción: Encola archivos para re-indexación

2. **ConversationService** (potencial)
   - Propósito: Invalidar cache de conversaciones
   - Filtro: `target_service == "conversation"`
   - Acción: Limpia cache interno

## 🔍 Formato Crítico que NO Debe Cambiar

### Campos Obligatorios en ProgressEvent:
- `type`: Siempre "progress"
- `source`: Identifica el servicio emisor
- `operation`: Tipo de operación
- `current` y `total`: Para calcular porcentaje
- `task_id`: Para filtrado en WebSocket

### Campos que Pueden Agregarse:
- Nuevas estadísticas en el nivel raíz
- Metadata adicional
- PERO no cambiar estructura existente

## 📊 Ejemplo de Flujo Completo

```
T+0ms    CLI: POST /api/index/project
T+10ms   API: Retorna {"task_id": "idx_123_abc", "websocket_url": "/api/ws/progress/idx_123_abc"}
T+20ms   BackgroundTask: Inicia indexación
T+100ms  IndexingService: Procesa primer batch
T+150ms  EventBus: Publica ProgressEvent #1
T+151ms  WebSocket: Envía {"type": "progress", "current": 20, "total": 585...}
T+200ms  IndexingService: Procesa segundo batch
T+250ms  EventBus: Publica ProgressEvent #2
T+251ms  WebSocket: Envía {"type": "progress", "current": 40, "total": 585...}
...
T+30s    IndexingService: Completa indexación
T+30s    EventBus: Publica ProgressEvent final
T+30s    WebSocket: Envía {"type": "progress", "current": 585, "total": 585...}
```

## 🚨 Consideraciones Críticas

### 1. NO Cambiar el Formato Sin Migración
El frontend espera este formato EXACTO. Cambiar campos romperá la UI.

### 2. Task ID es Opcional pero Crítico
- Sin task_id: El WebSocket muestra TODOS los eventos de indexación
- Con task_id: Filtrado preciso para múltiples indexaciones

### 3. Frecuencia de Eventos
- Se publica un evento por batch (20 archivos por defecto)
- En proyecto de 1000 archivos = 50 eventos
- Evitar publicar por cada archivo (spam)

### 4. Error Handling
```python
try:
    await event_bus.publish(progress_event)
except Exception as e:
    # NO fallar indexación por error de notificación
    logger.warning("Failed to notify progress", error=str(e))
```

## 📝 Recomendaciones

1. **Mantener retrocompatibilidad** en formato de eventos
2. **Documentar cambios** si se agregan campos
3. **Versionar eventos** si cambios breaking son necesarios
4. **Test E2E** debe verificar formato de eventos
5. **Logs estructurados** para debugging de eventos

## Conclusión

El sistema de eventos es robusto pero frágil en cuanto a formato. Los ProgressEvent son críticos para UX durante indexación. Cualquier optimización debe mantener el contrato de eventos intacto.
