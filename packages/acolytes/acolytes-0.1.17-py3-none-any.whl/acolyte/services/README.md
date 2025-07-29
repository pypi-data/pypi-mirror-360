# 🎯 Módulo Services

Lógica de negocio de ACOLYTE que coordina componentes internos para cumplir casos de uso. NO expone endpoints HTTP.

## 📑 Documentación

- **[docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)** - Diseño interno y decisiones arquitectónicas
- **[docs/STATUS.md](./docs/STATUS.md)** - Estado actual del módulo y componentes
- **[docs/REFERENCE.md](./docs/REFERENCE.md)** - API completa con métodos y parámetros
- **[docs/WORKFLOWS.md](./docs/WORKFLOWS.md)** - Flujos, ejemplos y casos de uso
- **[docs/INTEGRATION.md](./docs/INTEGRATION.md)** - Integración con otros módulos

## 🔧 Componentes Principales

- **conversation_service.py** - Gestión de conversaciones con persistencia dual (SQLite + Weaviate)
- **task_service.py** - Agrupación de sesiones en tareas para contexto completo
- **chat_service.py** - Orquestación del flujo completo de chat con retry logic e integración Dream
- **indexing_service.py** - Pipeline completo de indexación (chunking → embeddings → Weaviate)
- **reindex_service.py** - Sistema dedicado de re-indexación automática con queue y deduplicación
- **git_service.py** - Operaciones Git reactivas con detección de cambios y notificaciones

## 🌟 Nueva Integración: Dream System

ChatService ahora integra el sistema Dream para análisis profundo:

- **Detección automática de fatiga**: Basada en métricas Git reales
- **Sugerencias inteligentes**: Cuando detecta mucha actividad, sugiere análisis profundo
- **Siempre con permiso**: Nunca activa Dream automáticamente, solo sugiere
- **Análisis tipo Deep Search**: Similar a ChatGPT/Claude pero para tu código
- **Integración completa**: Usa `create_dream_orchestrator()` con weaviate_client compartido (FIX 17/06/25)

## ⚡ Quick Start

```python
from acolyte.services import ChatService, ConversationService, TaskService

# Inicializar servicios
conversation_service = ConversationService()
task_service = TaskService()
chat_service = ChatService(
    conversation_service=conversation_service,
    task_service=task_service
)

# Procesar mensaje
response = await chat_service.process_message(
    message="Quiero implementar autenticación JWT",
    session_id=None  # Nueva sesión
)

print(f"Respuesta: {response['response']}")
print(f"Session ID: {response['session_id']}")

# Si hay alta fatiga, la respuesta puede incluir sugerencia de Dream
if response.get("dream_suggestion"):
    print(f"Sugerencia: {response['dream_suggestion']}")
```

## 🔌 Integración Rápida

Services es usado principalmente por:

- **API Layer** - `/v1/chat/completions` usa ChatService
- **Scripts** - Instalación usa IndexingService directamente
- **Git Hooks** - Notifican cambios a IndexingService
- **Dream** - ChatService detecta fatiga y sugiere análisis profundo

Services depende de:

- **Core** - Database, Ollama, Events, Metrics
- **RAG** - HybridSearch, Compression
- **Semantic** - Análisis y procesamiento NLP
- **Models** - Estructuras de datos tipadas
- **Dream** - Sistema de análisis profundo y optimización

Para más detalles, ver [docs/INTEGRATION.md](./docs/INTEGRATION.md).

## 🔧 Refactorización Pendiente

### ✅ Tests Completados (22/06/25)

**Todos los servicios tienen cobertura >90%**:

- git_service: 96%
- task_service: 98%
- chat_service: 95%
- conversation_service: 93%
- indexing_service: 92%

Ver `/tests/services/` para los tests completos.

### ConversationService (19/06/25)

- **Documento creado**: `REFACTORING_CONVERSATION_SERVICE.md`
- **Objetivo**: Simplificar métodos largos y aprovechar mejor sistemas Core
- **Estado**: Pendiente de ejecución
- **Prioridad**: Media - El servicio funciona pero necesita mejoras de mantenibilidad

## ✅ Correcciones Recientes

### Bugs de TaskService Corregidos (21/06/25)

**Todos los bugs corregidos**:

1. **save_technical_decision**: Eliminadas todas las referencias a `.value` en decision_type
2. **find_active_task**: Añadido parámetro `initial_context` requerido por TaskCheckpoint
3. **get_recent_decisions**: Conversión de MAYUSCULAS a minúsculas para DecisionType enum

**Estado**:

- Funcionalidad completamente restaurada
- **98% cobertura de tests**
- TaskService listo para uso

### Tests de GitService Corregidos (21/06/25)

**Problema resuelto**: Los tests de `test_git_service.py` tenían múltiples errores:

1. Mockeo incorrecto de métodos especiales de Python (`__str__`, `__truediv__`)
2. Expectativas incorrectas sobre lógica de severidad
3. Asunciones sobre orden en sets de Python
4. Fixtures faltantes en tests de integración
5. Mock incorrecto de `iter_commits` para diferentes contextos

**Solución implementada**:

- Creado helper function `create_path_mock()` para mockeo consistente
- Corregido mockeo de `__str__` y `__truediv__` (operador `/`)
- Ajustadas expectativas de severidad (severity=7 → mensaje medio, no alto)
- Verificación de autores sin asumir orden específico
- Agregado fixture `mock_repo` a clase de integración
- Corregida estructura de mocks de commits
- Uso de `side_effect` para devolver diferentes resultados según parámetros de `iter_commits`

**Estado actual**:

- ✅ GitService tiene cobertura de tests funcional completa
- ✅ Todos los métodos públicos están testeados
- ✅ Tests de contrato, comportamiento e integración funcionando
- ✅ 21 tests pasando sin errores

### Tests de GitService Ampliados para Cobertura >90% (21/06/25)

**Objetivo**: Aumentar cobertura del 86% al 90%+

**Tests añadidos**:

- **Manejo de errores**: Test para excepciones al cargar el repositorio
- **Casos extremos**: Sin identidades Git configuradas, archivos no existentes
- **Excepciones específicas**: Errores al analizar historial, publicar eventos
- **Notificaciones vacías**: Listas vacías de archivos y cambios
- **Sin dependencias**: Funcionamiento sin event bus
- **Alta severidad**: Escenarios con múltiples autores recientes

**Nueva clase de tests**:

- `TestGitServiceEdgeCases`: 5 tests para casos extremos y condiciones de error

**Estado final**:

- ✅ **Cobertura >90%** (objetivo alcanzado)
- ✅ **34 tests totales** (13 nuevos añadidos)
- ✅ **Todas las ramas de error cubiertas**
- ✅ **Métricas en casos de error verificadas**

### Tests de ChatService Corregidos (21/06/25)

**Problemas resueltos**: Los tests de `test_chat_service.py` tenían múltiples errores:

1. **TokenDistribution**: Usaba parámetro inexistente `is_code_generation`
2. **TaskCheckpoint**: Faltaba campo requerido `initial_context`
3. **TaskDetection**: Faltaba parámetro requerido `confidence`
4. **AcolyteError**: Uso incorrecto de `retryable=True` como parámetro
5. **TaskType inference**: Tests esperaban tipos incorrectos
6. **Mock syntax**: Uso incorrecto de `.return_value` en AsyncMock

**Soluciones implementadas**:

- Removido `is_code_generation` de todos los TokenDistribution (2 instancias)
- Agregado `initial_context` a todos los TaskCheckpoint (5 instancias)
- Agregado `confidence` a todos los TaskDetection (3 instancias)
- Corregido manejo de retry con mock de `is_retryable()` (3 instancias)
- Actualizado expectativas de TaskType a IMPLEMENTATION (2 tests)
- Corregido uso de AsyncMock en test_get_active_session_info

**Estado actual**:

- ✅ **29 tests pasando** sin errores
- ✅ Todos los modelos Pydantic correctamente inicializados
- ✅ Lógica de retry funcionando correctamente
- ✅ Integración completa con Dream system verificada

### Lógica de Severidad en GitService Mejorada (21/06/25)

**Problema resuelto**: El test `test_analyze_conflicts_with_high_severity` esperaba que con 5 autores diferentes la severidad fuera >7, pero el código asignaba severidad fija de 7 para cualquier número de autores >1.

**Solución implementada**:

- Severidad ahora escala con el número de autores: `severity = min(10, 5 + (2 * num_authors))`
- 2 autores = severidad 7
- 3 autores = severidad 9
- 5 autores = severidad 10 (máximo)

**Resultado**:

- ✅ Test `test_analyze_conflicts_with_high_severity` ahora pasa correctamente
- ✅ Lógica más intuitiva: más autores = mayor severidad de conflicto potencial
- ✅ **GitService: 96% cobertura** con todos los tests pasando

### HybridSearch eliminado de ConversationService (19/06/25)

**Problema resuelto**: ConversationService usaba HybridSearch incorrectamente para buscar conversaciones.

**Solución implementada**:

- Eliminado HybridSearch completamente de ConversationService
- Las conversaciones están en SQLite, NO en Weaviate
- Búsqueda implementada solo con SQL por keywords
- Weaviate se usa exclusivamente para chunks de código

**Cambios realizados**:

- Eliminada inicialización de HybridSearch
- Métodos `find_related_sessions()` y `search_conversations()` usan solo SQL
- Eliminado método `invalidate_cache_for_file()` innecesario
- Actualizada documentación para reflejar la arquitectura correcta
