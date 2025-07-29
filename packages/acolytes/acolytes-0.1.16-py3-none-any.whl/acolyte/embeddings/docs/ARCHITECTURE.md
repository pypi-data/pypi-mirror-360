# 🏗️ Arquitectura del Módulo Embeddings

## Principios de Diseño

### 1. **Singleton Thread-Safe con Lazy Loading**
El módulo implementa el patrón Double-Checked Locking (DCL) para garantizar:
- Solo se carga el modelo UNA vez (ahorra ~1GB RAM para UniXcoder)
- Thread-safe sin penalizar performance
- El lock solo se usa durante la inicialización

### 2. **EmbeddingVector como Formato Estándar**
Todas las operaciones de embeddings usan `EmbeddingVector`:
- Formato interno: NumPy array (float32, 768 dimensiones, normalizado L2)
- Formato storage: Lista Python via `.to_weaviate()` (float64)
- Ubicación central: `/embeddings/types.py`

### 3. **Sistema de Dos Etapas para Precisión**
- **Etapa 1**: Búsqueda vectorial amplia (100+ candidatos) - Rápida
- **Etapa 2**: Re-ranking con CrossEncoder (top 10-20) - Precisa

### 4. **Cache Inteligente con Persistencia**
- Operaciones 100% en memoria para máxima performance
- Guardado automático cada 5 minutos a disco
- Recuperación de estado al reiniciar (no más cache frío)

## Decisiones Arquitectónicas

### Decisión #1: UniXcoder vs Otros Modelos
**Por qué UniXcoder**: Modelo específicamente entrenado para código multilenguaje con mejor performance en benchmarks de búsqueda de código.

### Decisión #2: 768 Dimensiones Fijas
**Razón**: Balance óptimo entre precisión y eficiencia. Suficiente para capturar semántica sin overhead excesivo.

### Decisión #3: Normalización L2 Obligatoria
**Beneficio**: Permite usar producto punto como cosine similarity, optimizando cálculos vectoriales.

### Decisión #4: Cache Context-Aware
**Por qué**: El mismo código en diferentes contextos (imports, dependencies) debe tener embeddings diferentes para mayor precisión.

### Decisión #5: Persistencia con NumPy Compressed
**Razón**: Formato `.npz` ofrece compresión eficiente manteniendo precisión float32 y carga rápida.

### Decisión #6: Re-ranking Solo en Top Candidatos
**Trade-off**: CrossEncoder es más preciso pero lento. Aplicarlo solo a top candidatos balancea precisión y latencia.

### Decisión #7: Device State Persistido
**Problema resuelto**: Si CUDA falla, el sistema recuerda usar CPU en futuros reinicios, evitando reintentos fallidos.

### Decisión #8: Control de Memoria por Tokens
**Solución**: `max_tokens_per_batch` previene OOM con archivos grandes, estimando ~1.3 tokens por palabra.

### Decisión #9: Protocol Pattern para Métricas
**Beneficio**: `MetricsProvider` Protocol evita dependencias circulares permitiendo type safety con mypy.

### Decisión #10: Limpieza Automática del Cache
**Implementación**: Cada 100 operaciones `set()` se ejecuta limpieza de entradas expiradas, liberando memoria sin intervención manual.

### Decisión #11: Logger Global Singleton
**Patrón obligatorio**: `from acolyte.core.logging import logger`
- NUNCA crear instancias de AsyncLogger
- Un solo logger compartido para todo el sistema

### Decisión #12: MetricsCollector Sin Namespace
**Uso correcto**: `self.collector = MetricsCollector()` sin parámetros
- Los módulos incluyen namespace en el nombre de la métrica
- Ejemplo: `self.collector.increment("embeddings.cache.hit")`

### Decisión #13: Datetime Centralization
**Helpers obligatorios**: `from acolyte.core.utils.datetime_utils import utc_now, utc_now_iso`
- Para timestamps usar `utc_now()` NO `datetime.utcnow()`
- Para persistencia usar `utc_now_iso()`

## Patrones Arquitectónicos

### Patrón Singleton con DCL
```python
def get_embeddings():
    global _embeddings_instance
    if _embeddings_instance is None:  # Primera verificación (sin lock)
        with _lock:
            if _embeddings_instance is None:  # Segunda verificación (con lock)
                _embeddings_instance = UniXcoderEmbeddings()
    return _embeddings_instance
```

### Patrón Strategy para Cache
- `ContextAwareCache`: Base con operaciones en memoria
- `SmartPersistentCache`: Extiende con persistencia diferida

### Dependency Injection para Métricas
```python
class UniXcoderEmbeddings:
    def __init__(self, metrics: Optional[MetricsProvider] = None):
        self.metrics = metrics or get_embeddings_metrics()
```

## Flujo de Datos Principal

```
Input → Preparación → Cache Check → Modelo → Vector → Normalización → Storage
                           ↓                                  ↓
                      Cache Miss                         Cache + Return
```

## Manejo de Vector Cero

Cuando se intenta normalizar un vector cero:
1. Se detecta automáticamente (norma == 0)
2. Se convierte en vector unitario `[1, 0, 0, ...]`
3. Se loguea warning para debugging
4. Mantiene propiedad de normalización sin errores

## Thread Safety y Concurrencia

El módulo es completamente thread-safe:
- Singleton con DCL para inicialización
- Cache usa `threading.RLock` para operaciones
- Device detection es thread-safe con property
- Persistencia usa thread daemon separado

## Optimizaciones de Performance

1. **Lazy Loading**: Modelos se cargan solo cuando se necesitan
2. **Batch Processing**: Reduce overhead de tokenización
3. **Cache LRU**: O(1) para get/set con OrderedDict
4. **Device Detection**: Solo una vez, luego cached
5. **Estimación de Tokens**: Sampling para evitar tokenización completa
