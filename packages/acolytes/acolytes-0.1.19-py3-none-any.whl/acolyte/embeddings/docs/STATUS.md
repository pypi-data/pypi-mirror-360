# 📊 Estado del Módulo Embeddings

## Componentes del Módulo

### types.py
Define tipos y estructuras base para todo el módulo.
- `EmbeddingVector`: Formato estándar de embeddings con validación
- TypedDicts para type safety con mypy
- `MetricsProvider` Protocol para evitar dependencias circulares

### unixcoder.py
Implementación principal de generación de embeddings.
- Modelo UniXcoder 768 dimensiones
- Lazy loading y singleton thread-safe
- Soporte para strings y Chunks
- Control de memoria con max_tokens_per_batch

### reranker.py
Re-ranking de precisión con CrossEncoder.
- Modelo ms-marco-MiniLM-L-6-v2
- Cache LRU de pares query-candidate
- Procesamiento en batches configurable

### cache.py
Sistema de cache base con TTL.
- LRU con OrderedDict (O(1) operations)
- Auto-limpieza cada 100 operaciones
- Generación de claves context-aware

### persistent_cache.py
Extensión del cache con persistencia.
- Guardado automático cada 5 minutos
- Formato numpy compressed (.npz)
- Thread daemon para guardado periódico

### context.py
Contexto enriquecido para embeddings.
- Validación estricta de tipos y rangos
- Campos obligatorios: language, file_path
- Enriquecimiento con imports, dependencies, tags

### metrics.py
Sistema de métricas detalladas.
- Performance: latencias, p95, SLA compliance
- Calidad: MRR, Precision@K, Recall@K
- Cache: hit rate, operaciones
- Singleton compartido entre componentes

## Funcionalidad Actual

### Generación de Embeddings
- Modelo UniXcoder cargado bajo demanda
- Detección automática GPU/CPU con fallback
- Normalización L2 automática
- Manejo de vector cero a unitario

### Cache System
- Cache en memoria con persistencia opcional
- TTL configurable (default 1 hora)
- Considera contexto completo para claves
- Estadísticas detalladas disponibles

### Batch Processing
- Control por número de items o tokens totales
- Estimación eficiente de tokens (~1.3 por palabra)
- Manejo graceful de textos que exceden límite
- Agrupación dinámica para optimizar GPU

### Re-ranking
- CrossEncoder para mayor precisión
- Solo aplica a top candidatos
- Cache de scores para pares repetidos
- Mantiene objetos Chunk en resultados

### Métricas y Monitoreo
- Habilitables via configuración
- Sin overhead significativo cuando deshabilitadas
- Tracking de SLA compliance (p95 < 5s)
- Métricas de calidad de búsqueda

## Limitaciones Conocidas

### Performance
- Primera carga del modelo toma ~30 segundos
- Re-ranking añade 100-200ms de latencia
- Cache requiere ~1GB RAM con 10k entradas

### Funcionalidad
- Solo soporta UniXcoder (no otros modelos)
- Dimensiones fijas en 768
- No hay quantización para reducir memoria

## TODOs Activos

### Mejoras Planeadas (v2)
- TODO: Soporte para más modelos (CodeBERT, CodeT5)
- TODO: Quantización int8 para reducir memoria 75%
- TODO: Cache distribuido para multi-instancia
- TODO: Fine-tuning específico por proyecto

### Optimizaciones Pendientes
- REVISAR: Batch size óptimo para diferentes GPUs
- REVISAR: TTL adaptativo basado en frecuencia de cambios

## Dependencias con Otros Módulos

### Dependencias Entrantes
- RAG/HybridSearch usa encode() para búsqueda
- IndexingService usa encode_batch() para procesar chunks
- ChatService obtiene singleton para contexto

### Dependencias Salientes
- Core/Tracing para métricas base
- Core/Database para persistir device state
- Models/Chunk para interfaz to_search_text()

## Configuración Requerida

```yaml
embeddings:
  cache_size: 10000
  device: auto
  batch_size: 20
  max_tokens_per_batch: 10000
  enable_metrics: true

cache:
  ttl_seconds: 3600
  save_interval: 300
```

## Patrones de Implementación

### Logger Global
- SIEMPRE usar `from acolyte.core.logging import logger`  
- NUNCA crear `AsyncLogger("embeddings")`

### MetricsCollector
- Instanciar sin parámetros: `MetricsCollector()`
- Namespace en la métrica: `collector.increment("embeddings.operation.count")`

### Datetime Utils  
- Timestamps: `from acolyte.core.utils.datetime_utils import utc_now, utc_now_iso`
- Para cálculos: `timestamp = utc_now()`
- Para persistencia: `iso_str = utc_now_iso()`

## Estado de Integración

### APIs Expuestas
- `get_embeddings()`: Singleton principal
- `get_reranker()`: Singleton de re-ranking
- `get_embeddings_metrics()`: Métricas si habilitadas

### Formatos de Datos
- Input: strings, Chunks, listas
- Output: EmbeddingVector (768 dims)
- Storage: numpy arrays, listas float64

### Manejo de Errores
- ConfigurationError para config inválida
- ExternalServiceError para fallos de modelo
- Fallback graceful GPU → CPU
- Validación completa de inputs
