# 📊 Estado del Módulo Semantic

## Componentes del Módulo

### summarizer.py
Generación de resúmenes extractivos con 70-80% reducción.
- Formato implementado: `[TIPO] Usuario: X | Contexto: Y | ACOLYTE: Z`
- Extracción de entidades usando regex patterns
- Detección de intención por keywords

### task_detector.py
Detección automática de nuevas tareas vs continuaciones.
- Patterns multiidioma configurables
- Similitud Jaccard + bonus por archivos compartidos
- TODO: Validar precisión con casos reales

### prompt_builder.py
Construcción de System Prompt dinámico con contexto específico.
- Integración con get_summary() de modelos
- Priorización inteligente cuando excede tokens
- Secciones: proyecto, sesión, continuidad, decisiones

### query_analyzer.py
Análisis de queries para distribución dinámica de tokens.
- Generation: 75% respuesta / 25% contexto
- Simple: 20% respuesta / 80% contexto
- Normal: 10% respuesta / 90% contexto

### decision_detector.py
Detección de decisiones técnicas importantes.
- Marcador explícito: @decision (configurable)
- Patterns automáticos multiidioma
- Retorna DetectedDecision (sin IDs de contexto)

### reference_resolver.py
Detección de referencias a sesiones anteriores.
- Solo detecta patterns, no busca
- Referencias temporales y específicas
- REVISAR: Añadir más patterns según uso real

### utils.py
Utilidades compartidas del módulo.
- detect_language(): Detección automática es/en

## Estado de Implementación

**Módulo 100% funcional** - Todos los componentes implementados y operativos.

### Cobertura de Tests (21/06/25)

- ✅ **Excelente cobertura en todos los archivos**:
  - prompt_builder.py: 100%
  - query_analyzer.py: 99%
  - reference_resolver.py: 100%
  - summarizer.py: 97%
  - task_detector.py: 98%
  - decision_detector.py: 91%
  - utils.py: 100%

### Métricas Implementadas

- **summarizer**: `generation_time_ms`, `compression_ratio`, `tokens_saved`
- **query_analyzer**: `analysis_time_ms`, `queries_analyzed`, `query_type.{type}`
- **task_detector**: `detection_time_ms`, `new_tasks_detected`, `confidence`
- **decision_detector**: `decisions_detected`, `impact_level`, `decision_type.{type}`
- **prompt_builder**: `build_time_ms`, `prompt_tokens`, `prompts_truncated`
- **reference_resolver**: `resolution_time_ms`, `references_resolved`

## Métricas Pendientes de Validar

### 1. Compresión Real Alcanzable
- **Objetivo**: 70-80% reducción manteniendo información clave
- **TODO**: Validar con corpus real de conversaciones
- **Métrica**: tokens_original / tokens_resumen

### 2. Latencia con Regex Complejos
- **Objetivo**: <100ms garantizada
- **TODO**: Benchmark con textos largos (>5000 tokens)
- **Preocupación**: Patterns multiidioma pueden ser costosos

### 3. Precisión de Detección
- **TODO**: Medir falsos positivos/negativos en:
  - Detección de nuevas tareas
  - Decisiones técnicas automáticas
  - Referencias temporales

## TODOs Activos

### v1 (MVP)
- Validar métricas de performance con tests de integración
- Medir precisión de detección en casos reales
- Optimizar regex si latencia >100ms

### v2 (Mejoras)
- REVISAR: Añadir más patterns de referencia según uso
- REVISAR: Ajustar thresholds de similitud para tareas
- Considerar cache LRU para análisis repetidos
- Añadir patterns para más idiomas (pt, fr)

## Limitaciones Conocidas

1. **Sin análisis semántico real**: Solo patterns y keywords
2. **Idiomas limitados**: Solo español e inglés
3. **Sin contexto global**: Cada análisis es independiente
4. **Patterns hardcodeados**: Aunque configurables, siguen siendo rígidos

## Dependencias con Otros Módulos

### Críticas
- **Core**: TokenCounter, TokenBudgetManager, Config, Metrics
- **Models**: Tipos de datos (Conversation, TaskCheckpoint, etc.)

### Consumidores
- **ChatService**: Principal consumidor de todas las funciones
- **ConversationService**: Solo usa resolve_temporal_references

## Configuración Requerida

```yaml
semantic:
  language: "es"  # Idioma por defecto
  
  summary:
    max_length: 100
    include_entities: true
    
  task_detection:
    confidence_threshold: 0.6
    patterns: {}  # Custom patterns opcionales
    
  decision_detection:
    auto_detect: true
    explicit_marker: "@decision"
    
  query_analysis:
    generation_keywords: []  # Keywords adicionales
```

## Notas de Performance

- Todos los métodos son síncronos (no async)
- Sin I/O ni operaciones bloqueantes
- Memoria: O(n) respecto al tamaño del texto
- CPU: O(n*m) donde m es número de patterns

## Validación de Calidad

- [x] Sin imports circulares
- [x] Tipos estructurados para todos los retornos
- [x] Logging estratégico sin impactar latencia
- [x] Configuración externalizada
- [x] Tests unitarios básicos
- [ ] Tests de integración completos
- [ ] Benchmarks de performance

## Correcciones Aplicadas

### Uso correcto de MetricsCollector (19/06/2025)

**Problema**: Los archivos del módulo estaban intentando usar `MetricsCollector(namespace="semantic.xxx")` pero MetricsCollector NO acepta namespace.

**Archivos corregidos**:
- `decision_detector.py` - Línea 37: `MetricsCollector(namespace="semantic.decision_detector")`
- `task_detector.py` - Línea 33: `MetricsCollector(namespace="semantic.task_detector")`
- `query_analyzer.py` - Línea 36: `MetricsCollector(namespace="semantic.query_analyzer")`
- `prompt_builder.py` - Línea 23: `MetricsCollector(namespace="semantic.prompt_builder")`
- `reference_resolver.py` - Línea 49: `MetricsCollector(namespace="semantic.reference_resolver")`
- `summarizer.py` - Línea 53: `MetricsCollector(namespace="semantic.summarizer")`

**Solución aplicada**: 
- Usar `MetricsCollector()` sin parámetros
- Incluir namespace en el nombre de la métrica: `metrics.increment("semantic.module.metric")`

**Ejemplo correcto**:
```python
self.metrics = MetricsCollector()  # SIN namespace
# Luego al usar:
self.metrics.increment("semantic.task_detector.new_tasks_detected")
self.metrics.record("semantic.task_detector.confidence", 0.9)
```

**Lección aprendida**: El diseño de MetricsCollector es deliberadamente simple. Los módulos deben incluir su namespace en el nombre de cada métrica para facilitar la agregación y filtrado posterior.

## Patrones de Implementación

### Logger Global
- SIEMPRE usar `from acolyte.core.logging import logger`  
- NUNCA crear `AsyncLogger("semantic")`

### MetricsCollector
- Instanciar sin parámetros: `MetricsCollector()`
- Namespace en la métrica: `collector.increment("semantic.module.count")`

### Datetime Utils  
- Timestamps: `from acolyte.core.utils.datetime_utils import utc_now, utc_now_iso`
- Para cálculos: `timestamp = utc_now()`
- Para persistencia: `iso_str = utc_now_iso()`

### Migración get_config → Settings (19/06/2025)

**Problema**: Los archivos del módulo semantic estaban usando incorrectamente `get_config()` que NO EXISTE en el proyecto.

**Archivos corregidos**:
- `decision_detector.py` - Línea 12: `from acolyte.core.secure_config import get_config`
- `task_detector.py` - Línea 12: `from acolyte.core.secure_config import get_config` 
- `query_analyzer.py` - Línea 12: `from acolyte.core.secure_config import get_config`

**Cambio aplicado**:
```python
# ANTES (INCORRECTO):
from acolyte.core.secure_config import get_config
config = get_config()

# DESPUÉS (CORRECTO):
from acolyte.core.secure_config import Settings
settings = Settings()
```

**Contexto**: La función `get_config()` nunca existió en el proyecto. El patrón correcto es usar la clase `Settings`.

**Implicaciones para tests**: Los tests deben mockear la CLASE `Settings`, no una función `get_config`:

```python
@pytest.fixture
def mock_settings():
    settings = Mock()
    settings.get.side_effect = lambda key, default=None: {
        # configuración mock
    }.get(key, default)
    return settings

# En el test:
with patch('acolyte.core.secure_config.Settings', return_value=mock_settings):
    # código del test
```

### Correcciones en Tests del Módulo (19/06/2025)

**Problemas encontrados y solucionados**:

1. **Patches de logger incorrectos**:
   - **Problema**: Los tests patcheaban `acolyte.core.logging.logger` genéricamente
   - **Solución**: Patchear el logger en el módulo específico donde se usa
   - **Ejemplo**: `@patch('acolyte.semantic.decision_detector.logger')`

2. **Fixtures con campos auto-generados**:
   - **Problema**: Los fixtures pasaban `id`, `created_at`, `updated_at` a TaskCheckpoint
   - **Solución**: No pasar estos campos ya que son auto-generados por los mixins
   - **Archivos corregidos**: `test_prompt_builder.py`, `test_task_detector.py`

3. **Función detect_language mejorada**:
   - **Problema**: No detectaba correctamente contracciones en inglés como "let's"
   - **Solución**: Manejo especial para contracciones y más palabras indicadoras
   - **Archivo**: `utils.py`

4. **Side effects de mocks agotados**:
   - **Problema**: `side_effect` con lista de valores se agotaba
   - **Solución**: Usar funciones que manejen múltiples llamadas
   - **Archivo**: `test_prompt_builder.py`

5. **Nombres de fixtures inconsistentes**:
   - **Problema**: Fixtures con prefijo `semantic_` pero tests esperaban sin prefijo
   - **Solución**: Actualizar todos los tests para usar nombres correctos
   - **Archivo**: `test_task_detector.py`

**Estado actual de tests**:
- `test_decision_detector.py` ✅ Corregido (patch MetricsCollector)
- `test_utils.py` ✅ Corregido (mejorada detect_language)
- `test_query_analyzer.py` ✅ Corregido (comentario test)
- `test_prompt_builder.py` ✅ Corregido (fixture sample_task)
- `test_task_detector.py` ✅ Corregido (fixture sample_task)
- `test_summarizer.py` ✅ Ya estaba correcto
- `test_reference_resolver.py` ✅ Ya estaba correcto
- `test_init.py` ✅ No requiere cambios

**Corrección adicional aplicada**:
- MetricsCollector debe ser patcheado en el módulo específico donde se usa, no en `acolyte.core.tracing`
- Ejemplo: `@patch('acolyte.semantic.decision_detector.MetricsCollector')`
