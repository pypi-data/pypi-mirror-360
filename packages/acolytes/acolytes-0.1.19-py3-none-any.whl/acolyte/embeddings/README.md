# 🧠 Módulo Embeddings

Genera representaciones vectoriales de código usando UniXcoder para búsqueda semántica avanzada con contexto rico y re-ranking.

## 📑 Documentación

- **[docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)** - Principios de diseño, decisiones y patrones
- **[docs/STATUS.md](./docs/STATUS.md)** - Estado actual y componentes del módulo
- **[docs/REFERENCE.md](./docs/REFERENCE.md)** - API completa con todas las clases y métodos
- **[docs/WORKFLOWS.md](./docs/WORKFLOWS.md)** - Flujos detallados y ejemplos de uso
- **[docs/INTEGRATION.md](./docs/INTEGRATION.md)** - Cómo se integra con otros módulos

## 🔧 Componentes Principales

- **types.py** - `EmbeddingVector` formato estándar, TypedDicts y Protocols
- **unixcoder.py** - Generador principal de embeddings (768 dims)
- **reranker.py** - Re-ranking de precisión con CrossEncoder
- **cache.py** - Cache LRU con TTL y contexto
- **persistent_cache.py** - Cache con guardado automático a disco
- **context.py** - `RichCodeContext` para embeddings mejorados
- **metrics.py** - Sistema completo de métricas y monitoreo

## ⚡ Quick Start

```python
from acolyte.embeddings import get_embeddings
from acolyte.embeddings.context import RichCodeContext

# Obtener singleton
embeddings = get_embeddings()

# Embedding simple
vector = embeddings.encode("def login(user, password):")

# Con contexto rico para mayor precisión
context = RichCodeContext(
    language="python",
    file_path="auth/login.py",
    imports=["jwt", "bcrypt"],
    semantic_tags=["authentication", "security"]
)
vector = embeddings.encode("login(user)", context)

# Procesamiento en batch
vectors = embeddings.encode_batch(
    texts=["code1", "code2", "code3"],
    max_tokens_per_batch=10000  # Control de memoria
)

# Búsqueda con re-ranking
results = embeddings.encode_with_rerank(
    query="validate JWT token",
    candidates=code_chunks,
    top_k=10
)
```

## 🔌 Configuración Básica

En `.acolyte`:

```yaml
embeddings:
  device: auto        # auto|cuda|cpu
  batch_size: 20      # Items por batch
  enable_metrics: true

cache:
  ttl_seconds: 3600   # 1 hora
  save_interval: 300  # 5 minutos
```

## 📦 Características Clave

- **Singleton thread-safe** con lazy loading (ahorra ~1GB RAM)
- **Cache persistente** que sobrevive reinicios
- **Re-ranking de dos etapas** para máxima precisión
- **Control de memoria** con max_tokens_per_batch
- **Métricas detalladas** de performance y calidad
- **Fallback GPU→CPU** con persistencia de estado
