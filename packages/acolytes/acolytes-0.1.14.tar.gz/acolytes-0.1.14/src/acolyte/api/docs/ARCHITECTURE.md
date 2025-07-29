# 🏗️ Arquitectura del Módulo API

## Principios de Diseño

1. **Compatibilidad Total OpenAI**: Los endpoints `/v1/*` mantienen 100% compatibilidad con el formato OpenAI para integración sin fricción
2. **Localhost Only**: Binding estricto a 127.0.0.1 por seguridad en sistema monousuario
3. **Extensiones No Invasivas**: Campos debug opcionales van AL FINAL para no romper parsers externos
4. **Simplicidad con Propósito**: Cada decisión balancea minimalismo con funcionalidad real necesaria

## Decisiones Arquitectónicas

### Decisión #1: Sistema Dream/Fatiga como Optimizador Real
**NO es antropomorfización gratuita**. Es un optimizador técnico que:
- Reorganiza embeddings por frecuencia de uso (hot/cold data)
- Detecta patrones durante ventanas de contexto completas
- Reduce latencia de búsquedas hasta 30% tras optimización
- La metáfora "fatiga" hace comprensible un proceso técnico complejo
- Requiere permiso explícito del usuario (usa CPU intensivamente)

### Decisión #2: WebSocket Solo para Progreso
- Indexación inicial puede tardar 5-10 minutos en proyectos grandes
- Implementación minimalista: solo porcentaje y archivo actual
- NO incluye streaming de logs (over-engineering para mono-usuario)
- Usa EventBus de Core para pub/sub, no reimplementa

### Decisión #3: Sin Endpoints Git Públicos
- Git operations son servicios internos Python
- `GitPython` + `pathlib` = máxima seguridad sin comandos shell
- ACOLYTE reacciona a cambios Git detectados por hooks locales
- Sin superficie de ataque HTTP para operaciones Git

### Decisión #4: Sesiones Automáticas Sin session_id Explícito
- Cada conversación = nueva sesión (como abrir nueva pestaña)
- ACOLYTE conecta contextos automáticamente
- SQLite (metadata) + Weaviate (código) = memoria asociativa
- Experiencia de usuario optimizada sin gestión manual

### Decisión #5: Sin Endpoints de Mantenimiento Explícitos
- Conversaciones NUNCA se borran (memoria infinita)
- Limpieza solo vía CLI: `acolyte db vacuum` 
- Solo limpia archivos eliminados >365 días Y sistema >50GB
- Optimiza búsquedas, no borra memoria

### Decisión #6: Compatibilidad Total OpenAI
- Cursor, Continue, etc. esperan formato exacto
- Siempre usa `acolyte:latest` sin importar modelo solicitado
- `/v1/models` devuelve fake ID pero mantiene compatibilidad

### Decisión #7: Logging Asíncrono con Emojis
- QueueHandler = logs nunca bloquean responses
- Emojis = mejor visibilidad durante desarrollo
- Headers de debug solo cuando `debug=true`
- Formato: `timestamp | level | component | message`

### Decisión #8: Organización de Rutas
- `/v1/*` = OpenAI compatible (obligatorio)
- `/api/health` = Sistema (no `/api/v1/health`)
- `/api/dream/*` = Optimización (agrupa funcionalidad)
- `/api/index/*` = Dashboard/git hooks
- `/api/ws/*` = WebSockets (separado de REST)

## Patrones Arquitectónicos

### Sistema EventBus (Pub-Sub)
```
┌─────────────────┐    ┌──────────┐    ┌──────────────┐    ┌────────┐
│ IndexingService │───►│ EventBus │───►│   WebSocket  │───►│ Client │
│                 │    │          │    │   Handler    │    │        │
│ _notify_progress│    │ publish()│    │ task_id      │    │ UI     │
│ (con task_id)   │    │          │    │ filtering    │    │ Update │
└─────────────────┘    └──────────┘    └──────────────┘    └────────┘
```

**Características**:
- Desacoplamiento total entre servicios
- Filtrado preciso por task_id
- Thread-safe con colas asíncronas
- Resiliente: si WebSocket falla, indexación continúa
- Escalable: múltiples suscriptores posibles

### Simplificación de Session ID
**Evolución**: De 40 líneas con timestamp a 1 línea con IDGenerator
```python
# Antes: timestamp + verificaciones BD + reintentos
# Ahora: 
return f"sess_{generate_id()}"  # 128 bits de entropía
```

### Validación de Paths en Profundidad
- ~50 líneas dedicadas a seguridad en `GitChangeFile.validate_path()`
- Path traversal protection
- Symlink validation
- Character sanitization
- Path resolution con `pathlib.resolve(strict=False)`

## Flujo de Request Completo

```
User Request → FastAPI → Router → Service Layer
     ↑                                      ↓
     ←────── Response ←── Format ←──────┘
                                            ↓
                                    ┌───────┴───────┐
                                    ↓                ↓
                              Core Services     RAG/Ollama
                              (DB, Events)      (Search/Gen)
```

### Flujo Detallado `/v1/chat/completions`

1. **API** recibe request OpenAI-compatible
2. **ChatService** detecta si es nuevo chat → carga contexto automáticamente
3. **Semantic** construye System Prompt Dinámico
4. **RAG** busca código relevante (híbrida 70/30)
5. **Ollama** genera respuesta con contexto completo
6. **Semantic** genera resumen de la interacción
7. **ConversationService** guarda resumen en SQLite
8. **API** formatea respuesta OpenAI-compatible
9. Si hay código validado → **IndexingService** actualiza Weaviate

## Configuración por Capas

1. **Archivo `.acolyte`**: Fuente de verdad para configuración
   ```yaml
   ports:
     backend: 8000
     weaviate: 8080
     ollama: 11434
   websockets:
     max_connections: 100
     heartbeat_interval: 30
     connection_timeout: 60
   ```

2. **Límites de Seguridad Automáticos**: Previenen problemas de memoria
   - max_connections: 1-1000 (ajuste automático)
   - heartbeat_interval: 10s-5min
   - connection_timeout: 30s-1h

3. **Variables de Entorno**: Para desarrollo/debugging
   - `ACOLYTE_LOG_LEVEL=DEBUG`
   - `ACOLYTE_API_DEBUG=true`

## Sistema de Ventana Deslizante (Dream)

Preparado para múltiples ciclos de análisis cuando Dream real esté implementado:
- **Ventana 32k**: 28,000 tokens código nuevo + 1,500 tokens contexto previo  
- **Ventana 128k**: ~117,900 tokens en un solo ciclo
- **Priorización**: bugs > vulnerabilidades > patrones > mejoras
- Estado simulado con métricas reales de Git

## Thread Safety

- **Dream State**: Protegido con `asyncio.Lock()` 
- **WebSocket Connections**: Diccionario thread-safe con TypedDict
- **Event Queues**: Colas asíncronas para cada conexión
- **Atomic Operations**: `_atomic_complete_optimization()` para actualizaciones

## Seguridad

- **Localhost Only**: `host="127.0.0.1"` en FastAPI
- **Path Validation**: pathlib con múltiples capas de validación
- **No Shell Commands**: Solo GitPython para operaciones Git
- **No Authentication**: Diseñado para mono-usuario local
- **Connection Limits**: Protección contra agotamiento de recursos
