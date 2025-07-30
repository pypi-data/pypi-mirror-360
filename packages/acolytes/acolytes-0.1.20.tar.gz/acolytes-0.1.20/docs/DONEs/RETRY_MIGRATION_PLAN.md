# Plan de Migración a Retry Centralizado en ACOLYTE

## Objetivo

Unificar la lógica de reintentos (retry) en operaciones críticas de red, base de datos y servicios externos usando el módulo `retry_async` de `acolyte.core.utils.retry`. Esto mejora la robustez, la mantenibilidad y la experiencia de usuario ante fallos temporales.

---

## Archivos a migrar y pasos recomendados

### 1. `src/acolyte/services/indexing_service.py`

**Motivo:** Llama a Weaviate (red), embeddings (red/GPU), y realiza I/O. Todo el pipeline es async.

**Pasos:**

- Identificar todos los puntos donde se llama a:
  - Inserción en Weaviate (`self.weaviate.data_object.create`, batch, etc.)
  - Generación de embeddings (métodos de embeddings async)
- Envolver estas llamadas con `await retry_async(...)`, configurando:
  - `max_attempts` (ej. 3-5)
  - `retry_on` con las excepciones relevantes (ej. `ExternalServiceError`, `TimeoutError`, etc.)
  - `logger` para registrar los intentos
- Opcional: Añadir retry en lectura de archivos si se detectan errores temporales de I/O.

### 2. `src/acolyte/services/git_service.py`

**Motivo:** Usa GitPython (síncrono), pero puede fallar por bloqueos de disco/repositorio. Tiene métodos async, pero el acceso real es sync.

**Pasos:**

- Identificar operaciones críticas de acceso al repo (abrir repo, iterar commits, etc.).
- Usar `retry_async` dentro de un `run_in_executor` para no bloquear el event loop:
  ```python
  await retry_async(lambda: await asyncio.get_running_loop().run_in_executor(None, self._abrir_repo), ...)
  ```
- Configurar los parámetros de retry según la criticidad y tipo de error.

### 3. `src/acolyte/install/database.py`

**Motivo:** Inicializa SQLite (puede lanzar `SQLiteBusyError`), y conecta a Weaviate (red). Es async.

**Pasos:**

- Envolver la conexión a Weaviate y operaciones SQLite críticas con `retry_async`.
- Usar `retry_on` para excepciones como `SQLiteBusyError`, `ExternalServiceError`, etc.
- Configurar delays y número de intentos según la operación (instalación puede tolerar más reintentos).

### 4. `src/acolyte/core/database.py`

**Motivo:** Maneja toda la infraestructura de SQLite, tanto sync como async. Los errores como `SQLiteBusyError` son retryables.

**Pasos:**

- En métodos async (`execute_async`, transacciones), envolver las operaciones críticas con `retry_async` para errores retryables.
- En métodos sync, considerar lógica de retry manual o migrar a async si es posible.
- Usar la función `is_retryable()` de las excepciones para decidir cuándo reintentar.

---

## Notas adicionales

- **No migrar archivos que ya usan `retry_async`**: (ej. `conversation_service.py`, `chat_service.py`, `core/ollama.py`, `core/events.py`).
- **Para operaciones sync** (ej. GitPython), siempre usar `run_in_executor` para no bloquear el event loop.
- **Documentar** cada migración en el changelog y añadir tests para los casos de retry.
- **Configurar** los parámetros de retry (intentos, delays, backoff) según la criticidad y el tipo de operación.

---

**Última actualización:** julio 2024
