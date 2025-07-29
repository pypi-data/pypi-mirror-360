# 📚 Referencia API - Módulo Semantic

Procesamiento de lenguaje natural y gestión inteligente de conversaciones usando técnicas extractivas simples y deterministas. Genera resúmenes con 70-80% reducción, detecta tareas y decisiones técnicas, y construye prompts dinámicos. Soporta español e inglés con detección automática de idioma.

## 📦 summarizer.py

### `Summarizer`

#### `generate_summary(user_msg: str, assistant_msg: str, context_chunks: Optional[List[Chunk]]) → SummaryResult`
Genera resumen extractivo con 70-80% reducción usando patterns y regex.

**Parámetros:**
- `user_msg`: Mensaje del usuario a resumir
- `assistant_msg`: Respuesta del asistente a resumir  
- `context_chunks`: Chunks de contexto usados (opcional)

**Retorna:** 
- `SummaryResult` con resumen, métricas y entidades extraídas

**Formato de salida:**
```
[TIPO] Usuario: pregunta | Contexto: archivos | ACOLYTE: acción [indicadores]
```

#### `_extract_entities(user_msg: str, assistant_msg: str, chunks: Optional[List[Chunk]]) → List[str]`
Extrae entidades usando patterns: archivos (.py, .js, etc.), funciones, clases, módulos, errores.

#### `_detect_intent(user_msg: str) → str`
Clasifica intención: debugging, implementation, refactoring, documentation, research, general.

#### `_extract_suggested_action(assistant_msg: str) → str`
Identifica acción principal del asistente buscando verbos de acción en primeras 3 oraciones.

#### `_format_summary(user_msg: str, assistant_msg: str, intent: str, action: str, entities: List[str]) → str`
Formatea resumen en partes: [TIPO] Usuario | Contexto | ACOLYTE | [indicadores].

---

## 📦 task_detector.py

### `TaskDetector`

#### `detect_task_context(message: str, current_task: Optional[TaskCheckpoint], recent_messages: Optional[List[str]]) → TaskDetection`
Detecta nueva tarea, continuación explícita o similitud de contexto. Auto-detecta idioma y usa patterns configurables.

**Parámetros:**
- `message`: Mensaje actual del usuario
- `current_task`: Tarea activa si existe
- `recent_messages`: Últimos mensajes para contexto

**Retorna:**
- `TaskDetection` con tipo (new/continuation), título y confianza

#### `_check_new_task_patterns(message: str, lang: str) → Optional[TaskDetection]`
Busca patterns como "vamos a implementar", "let's implement" y extrae título de tarea.

#### `_check_continuation_patterns(message: str, lang: str, current_task: TaskCheckpoint) → Optional[TaskDetection]`
Detecta continuación con patterns como "sigamos con", "donde quedamos".

#### `_calculate_context_similarity(message: str, current_task: TaskCheckpoint, recent_messages: List[str]) → float`
Calcula similitud Jaccard + bonus por archivos/funciones compartidas (sin ML).

#### `_get_default_patterns() → Dict[str, Dict[str, List[str]]]`
Patterns por defecto en español e inglés si no hay configuración.

---

## 📦 prompt_builder.py

### `PromptBuilder`

#### `build_dynamic_context(project: Dict, session: Conversation, task: Optional[TaskCheckpoint], recent_files: Optional[List[str]], recent_decisions: Optional[List], available_tokens: int) → str`
Construye prompt dinámico con secciones: proyecto, sesión, continuidad, decisiones, capacidades.

**Parámetros:**
- `project`: Info del proyecto (nombre, stack)
- `session`: Conversación actual
- `task`: Tarea activa si existe
- `recent_files`: Archivos modificados recientemente
- `recent_decisions`: Decisiones técnicas recientes
- `available_tokens`: Límite de tokens disponibles

**Retorna:**
- System prompt optimizado para el contexto

#### `_build_project_section(project: Dict, recent_files: Optional[List[str]]) → str`
Sección con nombre, stack detectado, archivos recientes, branch actual.

#### `_build_session_section(session: Conversation, task: Optional[TaskCheckpoint]) → str`
Información de sesión: ID, mensajes previos, tarea activa.

#### `_build_continuity_section(task: TaskCheckpoint, session: Conversation) → str`
Contexto de continuidad usando task.get_summary() y última actividad.

#### `_build_decisions_section(recent_decisions: List) → str`
Usa get_summary() de TechnicalDecision para contexto rico de decisiones.

#### `_prioritize_context(sections: List[str], available_tokens: int) → str`
Prioriza: capacidades > sesión > proyecto > continuidad cuando excede límite.

---

## 📦 query_analyzer.py

### `QueryAnalyzer`

#### `analyze_query_intent(query: str) → TokenDistribution`
Auto-detecta idioma y determina distribución óptima de tokens.

**Parámetros:**
- `query`: Texto del query a analizar

**Retorna:**
- `TokenDistribution` con tipo y porcentajes:
  - generation: 75% respuesta, 25% contexto
  - simple: 20% respuesta, 80% contexto
  - normal: 10% respuesta, 90% contexto

#### `_is_generation_query(query: str, lang: str) → bool`
Detecta keywords de generación configurables + patterns universales como "template", "boilerplate".

#### `_is_simple_question(query: str, lang: str) → bool`
Criterios: pregunta corta con ?, patterns de definición ("qué es", "what is").

#### `_get_default_generation_keywords() → Dict[str, List[str]]`
Keywords por defecto: es=["crea", "implementa"], en=["create", "implement"].

#### `_get_default_simple_patterns() → Dict[str, List[str]]`
Patterns de preguntas simples en ambos idiomas.

---

## 📦 decision_detector.py

### `DecisionDetector`

#### `detect_technical_decision(message: str, context: Optional[str]) → Optional[DetectedDecision]`
Retorna DetectedDecision (tipo intermedio SIN session_id) para que ChatService complete contexto.

**Parámetros:**
- `message`: Mensaje a analizar
- `context`: Contexto adicional (opcional)

**Retorna:**
- `DetectedDecision` si se detecta, None si no

**Campos de DetectedDecision:**
- `decision_type`: ARCHITECTURE, LIBRARY, PATTERN, etc.
- `title`: Título corto de la decisión
- `description`: Mensaje completo
- `rationale`: Razón si se detecta
- `alternatives_considered`: Alternativas mencionadas
- `impact_level`: 1-5 estimado automáticamente

#### `_extract_explicit_decision(message: str) → DetectedDecision`
Busca marcador configurable (default: @decision) y extrae decisión marcada.

#### `_detect_automatic_decision(message: str, lang: str, context: Optional[str]) → Optional[DetectedDecision]`
Patterns automáticos + universales técnicos. Auto-detecta idioma del mensaje.

#### `_extract_rationale(message: str, start_pos: int) → Optional[str]`
Busca indicators ("porque", "because") después de la decisión.

#### `_estimate_impact(decision_type: DecisionType, message: str) → int`
Estima impacto 1-5: Security=5, Architecture=4, palabras críticas +1.

---

## 📦 reference_resolver.py

### `ReferenceResolver`

#### `resolve_temporal_references(message: str) → List[SessionReference]`
Detecta patterns temporales en español e inglés. NO hace búsqueda, solo detecta para ConversationService.

**Parámetros:**
- `message`: Mensaje a analizar

**Retorna:**
- Lista de `SessionReference` con tipo y contexto detectado

**Patterns implementados:**
- Temporales: "lo que hicimos", "what we did", "donde quedamos", "where were we"
- Específicos: "el archivo X que modificamos", "la función Y que arreglamos"
- Por tema: "cuando hablamos de", "when we discussed"

#### `_detect_specific_references(message: str) → List[SessionReference]`
Referencias específicas: archivos temporales, funciones, bugs, temas de sesión.

---

## 📦 utils.py

### Funciones Utilitarias

#### `detect_language(text: str, default: str = "es") → str`
Detecta idioma analizando palabras comunes con word boundaries.

**Parámetros:**
- `text`: Texto a analizar
- `default`: Idioma por defecto si no se puede determinar

**Retorna:**
- "es" o "en"

**Algoritmo:**
- Cuenta palabras comunes de cada idioma
- Requiere diferencia >2 palabras para decidir
- Usa word boundaries (\b) para evitar falsos positivos

---

## 🔗 Tipos de Datos

### Importados de models.semantic_types:

- `TokenDistribution`: Tipo de query y distribución de tokens
- `TaskDetection`: Nueva tarea o continuación con confianza
- `SummaryResult`: Resumen con métricas y entidades
- `DetectedDecision`: Decisión sin contexto de sesión
- `SessionReference`: Referencia a sesión anterior

### Importados de models:

- `Conversation`: Estructura de conversación
- `TaskCheckpoint`: Información de tarea
- `TechnicalDecision`: Solo para tipos, no instancias
- `Chunk`: Chunks de código de RAG
- `DecisionType`: Enum de tipos de decisión

---

## ⚠️ Consideraciones de Uso

1. **Todos los métodos son síncronos** - No usar await
2. **Sin efectos secundarios** - Solo análisis, no modifica datos
3. **Configuración desde .acolyte** - Verificar configuración antes de usar
4. **Límites de tokens** - Respetar available_tokens en prompt_builder
5. **Idioma automático** - No asumir idioma, se detecta por mensaje

---

## 📊 Métricas Disponibles

Cada componente registra métricas vía MetricsCollector:

- Tiempos de procesamiento (ms)
- Contadores de detecciones
- Ratios de compresión
- Distribuciones de tipos

Accesibles vía: `metrics.get_metrics()["semantic.component"]`
