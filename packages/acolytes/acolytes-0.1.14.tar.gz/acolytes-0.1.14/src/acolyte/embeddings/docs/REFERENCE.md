# 📚 API Reference - Módulo Embeddings

## types.py

### `class EmbeddingVector`
Formato estándar de embeddings en ACOLYTE.

**Constructor**
```python
__init__(data: Union[np.ndarray, List[float]]) → None
```
Inicializa embedding con validación 768 dims y normalización L2.

**Properties**
- `numpy → np.ndarray`: Array para operaciones matemáticas (float32)
- `list → List[float]`: Lista para serialización genérica
- `dimension → int`: Siempre retorna 768

**Methods**
- `to_weaviate() → List[float]`: Convierte a float64 para Weaviate
- `validate() → bool`: Valida formato completo
- `cosine_similarity(other: EmbeddingVector) → float`: Calcula similitud

### TypedDicts
- `EmbeddingsMetricsSummaryDict`: Resumen de métricas del módulo
- `RerankerMetricsSummary`: Resumen de métricas del re-ranker

### `class MetricsProvider(Protocol)`
Interfaz para sistemas de métricas.

```python
def record_operation(operation: str, latency_ms: float, success: bool = True) → None
def record_cache_hit() → None
def record_cache_miss() → None
def get_cache_hit_rate() → float
def get_p95_latency() → float
```

## unixcoder.py

### `class UniXcoderEmbeddings`
Generador principal de embeddings. Singleton thread-safe.

**Constructor**
```python
__init__(metrics: Optional[MetricsProvider] = None) → None
```

**Properties**
- `device → torch.device`: Device actual con detección automática

**Methods principales**
```python
encode(
    text: Union[str, Chunk], 
    context: Optional[RichCodeContext] = None
) → EmbeddingVector
```
Genera embedding para texto/Chunk con cache.

```python
encode_batch(
    texts: List[Union[str, Chunk]], 
    contexts: Optional[List[RichCodeContext]] = None,
    batch_size: Optional[int] = None,
    max_tokens_per_batch: Optional[int] = None
) → List[EmbeddingVector]
```
Procesa múltiples textos eficientemente.

```python
encode_with_rerank(
    query: str, 
    candidates: List[str], 
    top_k: int = 10,
    initial_retrieval_factor: int = 3
) → List[Tuple[str, float]]
```
Búsqueda de dos etapas con re-ranking.

```python
get_metrics_summary() → EmbeddingsMetricsSummaryDict
```
Retorna resumen completo de métricas.

## reranker.py

### `class CrossEncoderReranker`
Re-ranker de precisión. Singleton thread-safe.

**Constructor**
```python
__init__(
    model_name: str = None,
    metrics: Optional[MetricsProvider] = None
) → None
```

**Methods**
```python
rerank(
    query: str, 
    candidates: List[str], 
    top_k: int = 10,
    return_scores: bool = True
) → List[Tuple[str, float]]
```
Re-rankea candidatos para mayor precisión.

```python
rerank_chunks(
    query: str,
    chunks: List[Chunk],
    top_k: int = 10
) → List[Tuple[Chunk, float]]
```
Versión que mantiene objetos Chunk.

## cache.py

### `class ContextAwareCache`
Cache LRU con TTL y contexto.

**Constructor**
```python
__init__(max_size: int = 10000, ttl_seconds: int = 3600) → None
```

**Methods**
```python
get(text: Union[str, Chunk], context: Optional[RichCodeContext]) → Optional[EmbeddingVector]
set(text: Union[str, Chunk], context: Optional[RichCodeContext], embedding: EmbeddingVector) → None
clear() → None
cleanup_expired() → int
get_stats() → CacheStats
```

**Properties**
- `size → int`: Número actual de entradas

## persistent_cache.py

### `class SmartPersistentCache(ContextAwareCache)`
Cache con persistencia automática.

**Constructor**
```python
__init__(
    max_size: int = 10000,
    ttl_seconds: int = 3600,
    save_interval: int = 300
) → None
```

**Methods adicionales**
```python
save_to_disk() → None
close() → None
get_persistent_stats() → Dict[str, Any]
```

**Context Manager**
```python
with SmartPersistentCache() as cache:
    # Uso del cache
# Auto-guarda al salir
```

## context.py

### `class RichCodeContext`
Contexto enriquecido para embeddings.

**Campos**
```python
@dataclass
class RichCodeContext:
    language: str          # Obligatorio
    file_path: str        # Obligatorio
    imports: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    semantic_tags: List[str] = field(default_factory=list)
    test_coverage: Optional[float] = None  # 0.0-1.0
    complexity: Optional[int] = None       # >= 0
```

**Methods**
```python
to_dict() → RichCodeContextDict
```

## metrics.py

### `class EmbeddingsMetrics`
Sistema completo de métricas. Singleton.

**Methods principales**
```python
record_operation(operation: str, latency_ms: float, success: bool = True) → None
record_cache_hit() → None
record_cache_miss() → None
get_cache_hit_rate() → float
get_p95_latency() → float
get_summary() → EmbeddingsMetricsSummary
log_summary() → None
```

### `class PerformanceMetrics`
Tracking de latencias y SLA.

```python
start_operation(operation: str) → str
end_operation(op_id: str) → float
get_p95(operation: str = None) → float
get_stats() → PerformanceStatsDict
check_sla_compliance() → Tuple[bool, Dict[str, bool]]
```

### `class SearchQualityMetrics`
Métricas de calidad de búsqueda.

```python
record_search_results(query: str, results: List[str], search_time_ms: float = None) → None
record_click(query: str, clicked_result: str) → None
record_relevance_feedback(query: str, relevance_list: List[bool]) → None
calculate_mrr() → float
calculate_precision_at_k(k: int) → float
calculate_recall_at_k(k: int) → float
get_quality_report() → SearchQualityReport
```

## __init__.py

### Funciones Singleton

```python
def get_embeddings() → UniXcoderEmbeddings
```
Retorna instancia singleton del generador de embeddings.

```python
def get_reranker() → CrossEncoderReranker
```
Retorna instancia singleton del re-ranker.

```python
def get_embeddings_metrics() → Optional[MetricsProvider]
```
Retorna singleton de métricas si habilitadas.

## Excepciones

El módulo puede lanzar:
- `ConfigurationError`: Configuración inválida
- `ExternalServiceError`: Fallo al cargar modelos
- `ValueError`: Inputs inválidos (dimensiones, tipos)

## Constantes

- `EMBEDDING_DIM = 768`: Dimensiones fijas del sistema
- `DEFAULT_CACHE_SIZE = 10000`: Tamaño por defecto del cache
- `DEFAULT_TTL = 3600`: TTL por defecto (1 hora)
