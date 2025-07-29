# 🏗️ Arquitectura del Módulo Semantic

## Principios de Diseño

1. **Sin ML/NLP libraries**: Solo regex y patterns para simplicidad y determinismo
2. **Latencia garantizada**: <100ms para todas las operaciones (objetivo)
3. **Multiidioma nativo**: Español e inglés con detección automática
4. **Configurable**: Patterns y thresholds configurables desde `.acolyte`
5. **Extractivo, no generativo**: Solo extrae y reorganiza información existente
6. **Métricas por composición**: Usa MetricsCollector de Core, nunca herencia

## Arquitectura del Módulo

```
semantic/
├── __init__.py              # Exports principales
├── summarizer.py            # Generación de resúmenes extractivos
├── task_detector.py         # Detección de inicio/continuación de tareas
├── prompt_builder.py        # Construcción de System Prompt dinámico
├── query_analyzer.py        # Análisis de intención para distribución de tokens
├── decision_detector.py     # Detección de decisiones técnicas
├── reference_resolver.py    # Resolución de referencias temporales
└── utils.py                 # Utilidades compartidas (detección de idioma)
```

## Decisiones Arquitectónicas

### Decisión #1: Sistema de dos capas para prompts
**Contexto**: ACOLYTE necesita personalidad consistente pero contexto dinámico  
**Decisión**: 
- **Base** (del Modelfile): Personalidad y principios de ACOLYTE
- **Dinámico** (de Semantic): Contexto específico del proyecto y sesión
**Consecuencias**: Flexibilidad sin perder identidad del asistente

### Decisión #2: Semantic genera TODOS los resúmenes
**Contexto**: Necesidad de formato consistente en todo el sistema  
**Decisión**: Centralizar generación de resúmenes en Semantic  
**Consecuencias**: Un solo lugar para ajustar formato y calidad

### Decisión #3: NO asumir que cambios se aplicaron
**Contexto**: El usuario puede rechazar sugerencias del asistente  
**Decisión**: Resúmenes dicen "ACOLYTE sugirió X", no "se implementó X"  
**Consecuencias**: Historial más preciso y confiable

### Decisión #4: Referencias temporales solo detectan
**Contexto**: Separación de responsabilidades  
**Decisión**: ReferenceResolver detecta patterns, ConversationService busca  
**Consecuencias**: Módulo Semantic no necesita acceso a BD

### Decisión #5: Patrón DTO para decisiones
**Contexto**: DecisionDetector no tiene contexto completo (session_id, task_id)  
**Decisión**: Retorna `DetectedDecision` (intermedio) que ChatService completa  
**Consecuencias**: Evita dependencias circulares y mantiene separación

### Decisión #6: Detección automática de tareas
**Contexto**: Fluidez en la conversación sin interrupciones  
**Decisión**: Detectar nuevas tareas por patterns sin preguntar al usuario  
**Consecuencias**: Experiencia más natural pero puede crear tareas incorrectas

### Decisión #7: Métricas por composición
**Contexto**: Arquitectura Core define MetricsCollector como base  
**Decisión**: Todos los módulos usan composición, NUNCA herencia  
**Consecuencias**: Consistencia arquitectónica y flexibilidad

### Decisión #8: Integración get_summary()
**Contexto**: Modelos definen métodos get_summary() para contexto rico  
**Decisión**: PromptBuilder usa estos métodos en vez de acceder campos directamente  
**Consecuencias**: Formato consistente y encapsulación respetada

### Decisión #9: Configuración dinámica desde .acolyte
**Contexto**: Evitar hardcoding y permitir personalización  
**Decisión**: Todos los patterns y thresholds se leen de configuración  
**Consecuencias**: Flexibilidad sin recompilar pero requiere validación

### Decisión #10: Distribución dinámica de tokens
**Contexto**: Diferentes queries necesitan diferentes balances contexto/respuesta  
**Decisión**: 
- Generation: 75% respuesta, 25% contexto
- Simple: 20% respuesta, 80% contexto  
- Normal: 10% respuesta, 90% contexto
**Consecuencias**: Respuestas completas cuando se necesitan

### Decisión #11: Detección automática de idioma
**Contexto**: Usuario puede cambiar de idioma sin avisar  
**Decisión**: Detectar idioma por mensaje, no por configuración global  
**Consecuencias**: Flexibilidad pero pequeño overhead por análisis

### Decisión #12: Resúmenes extractivos solamente
**Contexto**: Evitar alucinaciones y mantener simplicidad  
**Decisión**: Solo extraer y reorganizar, nunca generar contenido nuevo  
**Consecuencias**: Resúmenes 100% fieles al contenido original

### Decisión #13: Detección dual de decisiones técnicas
**Contexto**: Balance entre detección automática y control del usuario  
**Decisión**: Soportar marcador explícito (@decision) Y patterns automáticos  
**Consecuencias**: Flexibilidad sin perder decisiones importantes

### Decisión #14: Logger Global Singleton  
**Patrón obligatorio**: `from acolyte.core.logging import logger`
- NUNCA crear instancias de AsyncLogger
- Un solo logger compartido para todo el sistema

### Decisión #15: Datetime Centralization
**Helpers obligatorios**: `from acolyte.core.utils.datetime_utils import utc_now, utc_now_iso`
- Para timestamps usar `utc_now()` NO `datetime.utcnow()`
- Para persistencia usar `utc_now_iso()`

## Patrones de Implementación

### Patrón: Análisis sin Estado
Cada función es pura - mismo input produce mismo output siempre.

### Patrón: Configuración por Composición  
```python
class ModuleClass:
    def __init__(self):
        self.config = config_manager.get_semantic_config()
        self.metrics = MetricsCollector(namespace="semantic.module")
```

### Patrón: Retorno de Tipos Ricos
Siempre retornar tipos estructurados (SummaryResult, TaskDetection) en vez de tuplas o dicts.

## Principios Técnicos

- **Determinista**: Mismo input = mismo output siempre
- **Sin persistencia**: Solo analiza y retorna, Services maneja persistencia
- **Sin búsquedas**: RAG se encarga de búsquedas, Semantic solo procesa texto
- **Patterns configurables**: Todo se lee de `.acolyte` para flexibilidad sin hardcoding

## Algoritmos Clave

### Extracción de Entidades
```python
ENTITY_PATTERNS = {
    'file': r'\b([\w-]+\.(?:py|js|ts|jsx|tsx|java|go|rs|md))\b',
    'function': r'\b(?:def|function|func|fn)\s+(\w+)|\b(\w+)\s*\(',
    'class': r'\bclass\s+(\w+)|\b([A-Z]\w+)(?:Service|Controller|Model)',
    'line': r'(?:line|línea)\s*(\d+)',
    'error': r'(?:error|exception):\s*(.+?)(?:\.|$)'
}
```

### Clasificación de Intención
```python
INTENT_KEYWORDS = {
    'debugging': ['error', 'bug', 'fix', 'problema', 'crash'],
    'implementation': ['crear', 'implementar', 'añadir', 'nuevo'],
    'refactoring': ['refactorizar', 'mejorar', 'optimizar', 'limpiar'],
    'documentation': ['documentar', 'explicar', 'comentar'],
    'research': ['investigar', 'analizar', 'buscar', 'entender']
}
```

### Detección de Idioma
Análisis de palabras comunes con word boundaries para evitar falsos positivos.
