# 🔄 Retry Logic Centralization

## 📋 Problema Actual

El patrón de retry con exponential backoff está duplicado en múltiples lugares:

```python
# Repetido en 5+ servicios
for attempt in range(max_attempts):
    try:
        result = await operation()
        return result
    except Exception as e:
        if attempt < max_attempts - 1:
            await asyncio.sleep(2 ** attempt)
        else:
            raise
```

Cada implementación es ligeramente diferente:
- Algunos usan 3 intentos, otros 5
- Diferentes tiempos de backoff
- Manejo de excepciones inconsistente
- Sin métricas unificadas

## 🎯 Solución Propuesta

### Ubicación: `src/acolyte/core/utils/retry.py`

```python
from typing import TypeVar, Callable, Optional, Type, Tuple
import asyncio
from functools import wraps

T = TypeVar('T')

async def retry_async(
    func: Callable[..., T],
    max_attempts: int = 3,
    backoff: str = "exponential",
    initial_delay: float = 0.5,
    max_delay: float = 30.0,
    retry_on: Tuple[Type[Exception], ...] = (Exception,),
    logger: Optional[Any] = None
) -> T:
    """
    Retry an async function with configurable backoff.
    
    Args:
        func: Async function to retry
        max_attempts: Maximum number of attempts
        backoff: "exponential", "linear", or "constant"
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay between retries
        retry_on: Tuple of exceptions to retry on
        logger: Optional logger for retry attempts
    
    Returns:
        Result from successful function call
        
    Raises:
        Last exception if all retries fail
    """
    last_exception = None
    
    for attempt in range(max_attempts):
        try:
            return await func()
        except retry_on as e:
            last_exception = e
            
            if attempt < max_attempts - 1:
                # Calculate delay based on backoff strategy
                if backoff == "exponential":
                    delay = min(initial_delay * (2 ** attempt), max_delay)
                elif backoff == "linear":
                    delay = min(initial_delay * (attempt + 1), max_delay)
                else:  # constant
                    delay = initial_delay
                
                if logger:
                    logger.warning(
                        "Retry attempt failed",
                        attempt=attempt + 1,
                        max_attempts=max_attempts,
                        delay=delay,
                        error=str(e)
                    )
                
                await asyncio.sleep(delay)
            else:
                if logger:
                    logger.error(
                        "All retry attempts failed",
                        attempts=max_attempts,
                        error=str(e)
                    )
    
    raise last_exception

# Decorator version
def with_retry(
    max_attempts: int = 3,
    backoff: str = "exponential",
    **kwargs
):
    """Decorator to add retry logic to async functions."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **func_kwargs):
            return await retry_async(
                lambda: func(*args, **func_kwargs),
                max_attempts=max_attempts,
                backoff=backoff,
                **kwargs
            )
        return wrapper
    return decorator
```

## 📍 Dónde se usa actualmente

### 1. **conversation_service.py**
```python
# Líneas ~200-220
async def _execute_with_retry(self, operation_name: str, db_operation: Any, ...)
```

### 2. **chat_service.py**
```python
# Líneas ~400-420
async def _call_ollama_with_retry(self, messages, max_tokens)
```

### 3. **indexing_service.py**
```python
# Pattern similar en operaciones de Weaviate
```

### 4. **git_service.py**
```python
# Retry para operaciones Git que pueden fallar
```

### 5. **database.py**
```python
# Implícito en el manejo de SQLiteBusyError
```

## 💡 Beneficios

1. **Consistencia**: Un solo comportamiento de retry
2. **Configurabilidad**: Fácil ajustar para diferentes casos
3. **Métricas**: Un lugar para añadir telemetría
4. **Testing**: Solo necesitas testear una implementación
5. **Migración Turso**: Cambiar retry logic en UN lugar

## 🔨 Ejemplos de Migración

### Ejemplo 1: conversation_service.py
```python
# ANTES (líneas ~200-220)
async def _execute_with_retry(
    self,
    operation_name: str,
    db_operation: Any,
    *args: Any,
    max_attempts: int = 3,
    **kwargs: Any
) -> Any:
    for attempt in range(max_attempts):
        try:
            result = await db_operation(*args, **kwargs)
            if attempt > 0:
                self.metrics.increment("services.conversation_service.db_retries_successful")
            return result
        except DatabaseError as e:
            if e.is_retryable() and attempt < max_attempts - 1:
                backoff_time = 0.5 * (2**attempt)
                await asyncio.sleep(backoff_time)
                continue
            else:
                raise

# DESPUÉS
from acolyte.core.utils.retry import retry_async

# Reemplazar llamadas a _execute_with_retry con:
result = await retry_async(
    lambda: db_operation(*args, **kwargs),
    max_attempts=max_attempts,
    retry_on=(DatabaseError,),
    logger=self.logger
)
# Nota: Manejar métricas aparte si es necesario
```

### Ejemplo 2: chat_service.py
```python
# ANTES (líneas ~400-420)
async def _call_ollama_with_retry(self, messages, max_tokens):
    for attempt in range(self.max_retries):
        try:
            response = await self.ollama.chat(
                model=self.model_name,
                messages=messages,
                options={"num_predict": max_tokens}
            )
            return response
        except httpx.TimeoutException:
            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
            else:
                raise ExternalServiceError("Ollama timeout after retries")

# DESPUÉS
from acolyte.core.utils.retry import retry_async

# Reemplazar el método completo con:
response = await retry_async(
    lambda: self.ollama.chat(
        model=self.model_name,
        messages=messages,
        options={"num_predict": max_tokens}
    ),
    max_attempts=self.max_retries,
    retry_on=(httpx.TimeoutException,),
    logger=self.logger
)
```

## 🔍 Patrones Exactos a Buscar

```python
# Patrón 1: for loop con range
for attempt in range(max_attempts):
    try:
        # operación
    except:
        if attempt < max_attempts - 1:
            await asyncio.sleep(...)

# Patrón 2: while loop con contador
attempt = 0
while attempt < max_attempts:
    try:
        # operación
    except:
        attempt += 1
        if attempt < max_attempts:
            await asyncio.sleep(...)

# Patrón 3: métodos con "retry" en el nombre
async def _execute_with_retry(...)
async def _call_with_retry(...)
async def retry_operation(...)
```

## ⚠️ Casos Especiales

### 1. Métricas personalizadas
```python
# Si el código original tiene métricas especiales:
if attempt > 0:
    self.metrics.increment("retries_successful")

# Solución: Capturar si hubo reintentos
attempt_count = 0
async def operation_with_metrics():
    nonlocal attempt_count
    attempt_count += 1
    return await original_operation()

result = await retry_async(operation_with_metrics)
if attempt_count > 1:
    self.metrics.increment("retries_successful")
```

### 2. Excepciones con condiciones
```python
# Si el código verifica condiciones en la excepción:
except DatabaseError as e:
    if e.is_retryable():
        # retry

# Solución: Crear wrapper
async def retryable_operation():
    try:
        return await original_operation()
    except DatabaseError as e:
        if not e.is_retryable():
            raise
        raise  # Re-raise para que retry_async la maneje
```

### 3. Backoff custom
```python
# Si el backoff no es estándar:
wait_time = random.uniform(0.5, 2.0) * attempt

# Considerar si vale la pena mantener el comportamiento exacto
# o estandarizar a exponential/linear/constant
```

## ⚠️ Consideraciones para Turso

Turso tiene diferentes tipos de errores que SQLite:
- Errores de red (más comunes)
- Rate limiting
- Timeouts diferentes

Con retry centralizado, solo necesitas actualizar `retry.py` para manejar estos casos.