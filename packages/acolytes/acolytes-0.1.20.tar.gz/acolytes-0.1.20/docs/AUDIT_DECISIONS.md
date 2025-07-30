# 📋 DECISIONES ARQUITECTÓNICAS - PROYECTO ACOLYTE

Documento maestro de decisiones técnicas tomadas durante el desarrollo. Total: 41 decisiones.

---

## 🏗️ DECISIONES FUNDAMENTALES

### 1. Arquitectura de Memoria: Resúmenes vs Conversaciones Completas

**Decisión**: SQLite guarda **resúmenes inteligentes** (~90% reducción), NO conversaciones completas.

**Rationale**:

- Permite "memoria infinita" sin explotar almacenamiento
- 500 tokens por interacción → 50 tokens de resumen
- El `context_size` es límite TOTAL del modelo (no se reinicia entre mensajes)

**Implementación**:

- Semantic genera resúmenes extractivos inmediatamente tras cada respuesta
- Formato: "[TIPO] Usuario: X | Contexto: Y | ACOLYTE: Z | Entidades: [...]"
- Todo debe caber: sistema + RAG + historial + pregunta + respuesta ≤ context_size

### 2. Sistema de IDs Unificado (Cambio de Paradigma)

**Problema crítico**: Inconsistencia entre `uuid.uuid4()` y `secrets.token_hex(16)` causaba incompatibilidad SQLite/Weaviate.

**Decisión**: Sistema centralizado en `core/id_generator.py`

- Formato único: hex32 sin guiones
- Un solo import: `from acolyte.core.id_generator import generate_id`
- Compatible con SQLite como PRIMARY KEY

**Archivos actualizados**:

- `core/database.py` (líneas 225, 384)
- `core/events.py` (línea 44)
- `models/base.py` (IdentifiableMixin)
- Todos los servicios migrados

### 3. Patrón Strategy para Identificación de Modelos

**Problema**: Conversation usaba `session_id` mientras otros modelos usaban `id`, violando SOLID.

**Decisión**: Protocolo unificado con estrategias específicas

```python
@runtime_checkable
class Identifiable(Protocol):
    @property
    def primary_key(self) -> str: ...
    @property
    def primary_key_field(self) -> str: ...

# Estrategias
class StandardIdMixin  # Para modelos con .id
class SessionIdMixin   # Para conversaciones con .session_id
```

**Beneficios**:

- Zero breaking changes (alias `IdentifiableMixin = StandardIdMixin`)
- BD optimizada (eliminada redundancia id + session_id)
- Interfaz uniforme para todos los servicios

---

## 🔄 FLUJO Y SESIONES

### 4. Flujo Automático al Iniciar Chat

**Decisión**: Continuidad automática sin preguntar al usuario

- Busca última sesión automáticamente
- Si hay tarea activa → Carga TODA la tarea
- Si no → Carga solo última sesión
- Campo `related_sessions` mantiene cadena temporal

### 5. Detección de Sesiones Relacionadas

**Decisión**: Sistema dual de relacionamiento

1. **Automático**: Cadena temporal (Chat 1 → Chat 2 → Chat 3)
2. **Por búsqueda**: Semántica cuando usuario pregunta explícitamente

**NO es búsqueda semántica automática**, es continuidad temporal.

### 6. Jerarquía Task > Session > Message

**Decisión**: Mantener jerarquía completa

- Tasks se crean automáticamente por palabras clave
- NO hay botón manual "crear tarea"
- Detección: "vamos a implementar", "necesito crear", etc.

---

## 💾 PERSISTENCIA Y DATOS

### 7. Persistencia Dual SQLite + Weaviate

**Decisión**:

- **SQLite**: Fuente de verdad (resúmenes + metadata + relaciones)
- **Weaviate**: Índice de búsqueda (código + embeddings)
- Código NO se indexa hasta validación del usuario

### 8. Campo total_tokens

**Decisión**: Contador interno de tokens ORIGINALES procesados

- NO incluye resúmenes
- Usuario no lo ve
- Para estadísticas y alertas (>100k sugiere nueva tarea)

### 9. Tabla technical_decisions

**Decisión**: Nueva tabla dedicada para decisiones importantes

```sql
CREATE TABLE technical_decisions (
    id TEXT PRIMARY KEY,
    decision_type TEXT,  -- ARCHITECTURE, LIBRARY, PATTERN, SECURITY
    title TEXT,
    rationale TEXT,
    impact_level INTEGER  -- 1-5
);
```

Detección automática por patrones + marcador explícito `@decision`.

---

## 🤖 INTERACCIÓN CON OLLAMA

### 10. System Prompt Dinámico de Dos Capas

**Decisión**:

1. **Base (Modelfile)**: Personalidad ACOLYTE (estático)
2. **Dinámico (Semantic)**: Contexto del proyecto actual

Incluye: proyecto info, sesión actual, archivos recientes, estado Git.

### 11. Distribución Dinámica de Tokens

**Decisión**: Ajuste automático según necesidad

- **Generación**: 75% respuesta / 25% contexto
- **Simple**: 20% respuesta / 80% contexto
- **Default**: 10% respuesta / 90% contexto

Detección por palabras clave: "crea archivo", "genera completo", etc.

### 12. Modificación de Código vía Cursor

**Decisión**: ACOLYTE genera respuestas naturales

- NO formato especial
- Cursor intercepta y decide si aplicar
- ACOLYTE no sabe si cambios se aplicaron

---

## 🔍 BÚSQUEDA Y RAG

### 13. Búsqueda Híbrida 70/30

**Decisión**:

- 70% búsqueda semántica (embeddings)
- 30% búsqueda léxica (BM25)
- Motor: Weaviate para ambas (simplifica arquitectura)

### 14. Compresión Contextual SIN LLM

**Decisión**: Heurística en vez de LLM adicional

- Ahorra 60-80% tokens en queries específicos
- Latencia <50ms garantizada
- Solo comprime cuando es útil

**Niveles**:

- Alta relevancia (>0.8): Sin compresión
- Media (>0.5): Sin comments/docstrings
- Baja (<0.3): Solo signatures

### 15. Embeddings con EmbeddingVector

**Decisión**: Clase wrapper unificada

- NumPy interno (float32, 768 dims)
- `.to_weaviate()` → lista float64
- Evita bugs conocidos de Weaviate

### 16. Eliminación de Clustering en Favor del Grafo Neuronal

**Decisión**: Eliminar `embeddings/clustering.py` completamente

- Clustering post-búsqueda tiene valor marginal
- Grafo neuronal expande con relaciones reales (IMPORTS, CALLS)
- Mejor recall y performance

---

## 📁 GESTIÓN DE ARCHIVOS

### 17. Manejo de Archivos Subidos

**Decisión**: Indexación inteligente contextual

- Default: Solo contexto conversación actual
- Temporal: Si tarea activa Y relevante (24h TTL)
- Permanente: Solo con confirmación explícita

### 18. Git Reactivo (NO Proactivo)

**Decisión**: ACOLYTE nunca hace fetch automático

- Usuario controla Git completamente
- Git hooks detectan cambios y notifican
- Si afecta trabajo actual, ACOLYTE avisa

**Hooks implementados**:

- `post-commit`: trigger 'commit'
- `post-merge`: trigger 'pull' (invalida cache)
- `post-checkout`: trigger 'checkout'
- `post-fetch`: trigger 'fetch'

---

## 🧠 SISTEMA DREAM

### 19. Dream como Optimizador Real

**Decisión**: NO es antropomorfización, es funcionalidad técnica

**Sistema de fatiga**:

- Basado en métricas Git reales
- Detecta: código inestable, hotspots, refactorizaciones
- Estados: MONITORING → DROWSY → DREAMING → REM → WAKING

**Gestión de ventana**:

- 32k models: 28k código nuevo + 1.5k contexto previo
- 128k models: 90% del total en un ciclo
- Insights en `.acolyte-dreams/`

### 20. Grafo Neuronal en RAG

**Decisión**: Va en `/rag/graph/`, no en Dream

**Almacenamiento dual**:

- **SQLite**: Relaciones estructurales (IMPORTS, CALLS, EXTENDS)
- **Weaviate**: Embeddings de patrones semánticos

Dream es consumidor intensivo pero no dueño del grafo.

---

## 🛡️ SEGURIDAD Y CALIDAD

### 21. Consolidación de Errores en Core

**Decisión**: TODO en `core/exceptions.py`

- Excepciones Python + modelos HTTP + helpers
- `from_exception()` convierte excepciones → HTTP
- Models re-exporta para compatibilidad

### 22. Sin Autenticación ni Rate Limiting

**Decisión**: Sistema mono-usuario local

- Solo localhost (127.0.0.1)
- Sin límites de requests
- Sin user_id en modelos

### 23. Logging Asíncrono Sin Emojis

**Decisión**:

- QueueHandler para latencia = 0
- Formato simple: `timestamp | level | component | message`
- Sin caracteres que rompan parsers

---

## 📊 MÉTRICAS Y CACHE

### 24. Patrón de Composición para Métricas

**Decisión**: Usar composición, NO herencia

```python
# ✅ CORRECTO
class ModuleMetrics:
    def __init__(self):
        self.collector = MetricsCollector()  # Composición
```

### 25. Sistema de Cache Coordinado

**Decisión**: EventBus para invalidación

**Flujo**: Git detecta → Publica evento → Services invalidan → HybridSearch limpia

**Tipos de cache**:

- Local del servicio: TTL 5 minutos (ej: repo Git)
- Búsquedas coordinado: Invalida por eventos

### 26. Configuración de Cache Unificada

**Decisión**: Valores consistentes

- max_size: 1000 entries
- ttl_seconds: 3600 (1 hora)
- strategy: LRU

---

## 🔧 DECISIONES DE IMPLEMENTACIÓN

### 27-38. Decisiones Técnicas Menores

27. **ChunkingService**: AST-aware para Python, overlap 20%
28. **EnrichmentService**: Métricas Git pendientes (merge_conflicts_count, etc.)
29. **18 ChunkTypes**: FUNCTION, METHOD, CLASS, etc. para precisión
30. **Fuzzy matching**: Normalización snake_case/camelCase en búsquedas
31. **Sin migraciones DB**: Esquema fijo para mono-usuario
32. **SensitiveDataMasker simple**: Regex básico suficiente
33. **EventBus.replay()**: 10k eventos en memoria para debug
34. **Keywords NO implementar**: Embeddings superiores
35. **Duplicados en insights OK**: Para MVP
36. **Estadísticas de sesión**: Implementadas en ConversationService
37. **Umbrales configurables**: Todos los límites en `.acolyte`

### 38. MetricsCollector sin Namespace

**Decisión**: MetricsCollector NO acepta parámetro namespace

**Rationale**:

- Mantiene API simple y consistente
- Todos los módulos usan el mismo patrón
- Más explícito: `metrics.increment("semantic.task_detector.count")`

**Uso correcto**:

```python
# ✅ CORRECTO
self.metrics = MetricsCollector()
self.metrics.increment("semantic.task_detector.new_tasks_detected")

# ❌ INCORRECTO
self.metrics = MetricsCollector(namespace="semantic")
self.metrics.increment("new_tasks_detected")
```

**Lección aprendida**: Nunca modificar código fuente para hacer pasar tests mal escritos

### 39. HybridSearch para Conversaciones - RESUELTO

**Problema detectado**: ConversationService usaba incorrectamente HybridSearch para buscar sesiones relacionadas

**Conflicto arquitectónico**:

- HybridSearch está diseñado exclusivamente para buscar chunks de código en Weaviate
- Las conversaciones se almacenan en SQLite, NO en Weaviate
- Se intentaba usar `file_path` como proxy para `session_id` (conceptualmente incorrecto)

**Solución implementada**:

- ✅ **Eliminado HybridSearch completamente** de ConversationService
- ✅ **Búsqueda SQL directa** es ahora la única forma de buscar conversaciones
- ✅ **Arquitectura clarificada**: SQLite para conversaciones, Weaviate solo para código
- ✅ **NO es un "fallback"**: La búsqueda SQL es la solución correcta y permanente

**Cambios realizados**:

```python
# ANTES: Intentaba usar HybridSearch incorrectamente
if self.hybrid_search:
    results = await self.hybrid_search.search(...)  # ❌ INCORRECTO

# AHORA: Búsqueda SQL directa para conversaciones
result = await self._fallback_search(query, current_session_id, limit)  # ✅ CORRECTO
# Nota: El nombre "_fallback_search" es legacy, pero es la búsqueda principal
```

### 40. Tests Antes de Refactorizar Services

**Decisión**: NO refactorizar Services sin tests previos

**Contexto**:

- Services tiene 0% cobertura de tests actual
- Es el módulo central que coordina todo ACOLYTE
- Refactorizar sin tests = alta probabilidad de romper el sistema

**Estrategia**:

1. ✅ Documentar comportamiento actual (caja negra)
2. ✅ Crear tests que capturen ese comportamiento
3. ✅ Verificar que pasan con código actual
4. ✅ Solo entonces proceder con refactorización

**Documentación**: `/tests/services/ANTES_DE_REFACTORIZAR.md`

**Beneficios**:

- Tests sirven como especificación del comportamiento
- Detectan breaking changes automáticamente
- Permiten refactorizar con confianza
- Documentan la API pública actual

**Estado**: 🔴 BLOQUEANTE - No proceder con refactorización hasta completar tests

### 41. Datetime Centralization - Implementación Durante Auditoría

**Decisión**: Centralizar todo manejo de datetime en `acolyte.core.utils.datetime_utils.py`

**Problema detectado**:

- 50+ repeticiones de `datetime.utcnow()` en el código
- Inconsistencia potencial entre archivos
- Dificultad para testing (no se puede mockear fácilmente)
- Formatos inconsistentes (algunos `.isoformat()`, otros no)

**Solución implementada**:

- ✅ **Crear `acolyte.core.utils.datetime_utils.py`** con helpers centralizados
- ✅ **Aplicar durante auditoría de alineación** en cada archivo
- ✅ **Ejecutar tests antes de marcar archivo como revisado**

**Funciones principales**:

```python
    def utc_now() -> datetime:      # Reemplaza datetime.utcnow()
    def utc_now_iso() -> str:       # Reemplaza datetime.utcnow().isoformat()
    def parse_iso_datetime(iso_string: str) -> datetime:
    def format_iso(dt: datetime) -> str:
    def time_ago(dt: Union[datetime, str]) -> str:
```

**Proceso de aplicación**:

1. Al revisar archivo, detectar usos de `datetime.utcnow()`
2. Añadir import: `from acolyte.core.utils.datetime_utils import utc_now, utc_now_iso`
3. Reemplazar patrones:
   - `datetime.utcnow()` → `utc_now()`
   - `datetime.utcnow().isoformat()` → `utc_now_iso()`
4. Ejecutar test del archivo: `pytest tests/path/to/test_file.py`
5. Documentar en columna "Implementado" como `datetime_utils`

**Beneficios**:

- Elimina duplicación de código
- Un solo lugar para cambios futuros
- Mockeable para tests: `set_mock_time(test_datetime)`
- Garantiza UTC en todo el sistema

---

## 📈 ESTADO ACTUAL

- **Decisiones aplicadas**: 100% de las documentadas
- **Módulos alineados**: Core, Models, API, Embeddings
- **Pendiente aplicar en**: RAG (parcial), Semantic, Dream
- **🔴 BLOQUEADO**: Services necesita tests antes de refactorizar (Decisión #40)
- **🎆 EN PROGRESO**: Datetime centralization durante auditoría (Decisión #41)

---

## 🚀 IMPACTO DE DECISIONES

### Arquitectura robusta:

- Sistema de IDs unificado
- Patrón Strategy para modelos
- Errores consolidados
- Cache coordinado

### Performance optimizada:

- Resúmenes vs conversaciones completas
- Compresión contextual inteligente
- Logging asíncrono
- Cache con TTL

### Experiencia mejorada:

- Flujo automático sin fricciones
- Distribución dinámica de tokens
- Git reactivo respeta control del usuario
- Dream como diferenciador del proyecto

---

### 42. Política de Paths No Cubiertos por Tests

**Decisión**: Marcar explícitamente paths no testeados con logs de advertencia

**Contexto del problema**:

- Objetivo de cobertura: ≥90% en todos los archivos
- Realidad: Algunos paths son difíciles de testear (errores raros, condiciones específicas)
- Riesgo: Código no testeado puede fallar en producción sin avisar

**Política implementada**:

1. **Si no se puede cubrir un path con tests**, añadir log de advertencia:

```python
if condicion_no_cubierta:
    logger.warning(
        "[UNTESTED PATH] Path no cubierto ejecutado: descripción del caso"
    )
    # Continuar con la lógica...
```

2. **Para paths críticos**, considerar lanzar excepción:

```python
if path_critico_no_testeado:
    logger.error("[UNTESTED PATH] Path crítico no cubierto ejecutado")
    raise UncoveredPathError("Se ejecutó un path no cubierto por tests")
```

**Aplicación durante auditoría**:

- Al revisar archivos con <90% cobertura
- Identificar líneas críticas no cubiertas en ALIGNMENT_COV.md
- Añadir warnings en esos paths
- Documentar en columna "Implementado" como `+logger-untested`

**Beneficios**:

- **Visibilidad**: Los logs muestran qué paths no testeados se ejecutan en producción
- **Priorización**: Identifica qué tests son más urgentes de añadir
- **Seguridad**: Alerta temprana de comportamiento no validado
- **Documentación viva**: El código mismo indica qué no está testeado

**Ejemplo real del proyecto**:

```python
# En embeddings/unixcoder.py (86% cobertura)
if not model_path.exists():
    logger.warning("[UNTESTED PATH] Model download path executed")
    self._download_model()  # Líneas 263-270 no cubiertas
```

### 43. Lazy Loading para Imports Pesados

**Decisión**: Implementar lazy loading para dependencias pesadas (torch, transformers, tree-sitter)

**Problema detectado**:

- Import de ACOLYTE tardaba ~6 segundos
- Dependencias pesadas se cargaban aunque no se usaran
- torch (~2GB), transformers (~500MB), tree-sitter (~150MB)
- Impacto negativo en CLI y tests

**Solución implementada**:

1. **Module-level lazy loading**: Imports dentro de funciones/métodos
2. **`__getattr__` pattern**: Carga atributos bajo demanda
3. **Property-based loading**: Inicialización diferida de componentes

**Cambios principales**:

- ✅ `acolyte/__init__.py`: `__getattr__` para módulos principales
- ✅ `core/__init__.py`: `__getattr__` para componentes core
- ✅ `embeddings/unixcoder.py`: Imports de torch/transformers en métodos
- ✅ `rag/chunking/`: Tree-sitter imports diferidos
- ✅ `services/`: Propiedades para dependencias opcionales

**Resultados**:

- **Antes**: ~6 segundos para `import acolyte`
- **Después**: ~0.01 segundos (**600x más rápido**)
- Tests unitarios ejecutan sin cargar ML
- CLI responde instantáneamente

**Patrones establecidos**:

```python
# ❌ INCORRECTO - Import a nivel de módulo
from heavy_module import HeavyClass

# ✅ CORRECTO - Import diferido
def get_heavy_thing():
    from heavy_module import HeavyClass
    return HeavyClass()

# ✅ CORRECTO - Con TYPE_CHECKING
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from heavy_module import HeavyClass
```

**Testing**:

- `tests/test_lazy_loading.py`: Tests unitarios
- `tests/integration/test_lazy_loading_integration.py`: Test completo
- `claude_test_all_modules.py`: Script de verificación rápida

**Beneficios**:

- Experiencia de usuario mejorada (respuesta instantánea)
- Tests más rápidos (no cargan dependencias innecesarias)
- Menor uso de memoria cuando no se usan todas las features
- Permite desarrollo modular sin penalización de performance

**Estado**: ✅ IMPLEMENTADO - Monitorear en nuevos módulos

---

**Documento maestro**: Consultar para cualquier duda arquitectónica
