# 🔧 Refactorización de ConversationService

## 📋 Contexto del Sistema

### Arquitectura General
- **Sistema Híbrido 70/30**: Búsqueda semántica (70%) + léxica (30%)
- **SQLite**: Almacena conversaciones resumidas (~90% reducción), NO conversaciones completas
- **Weaviate**: Solo para chunks de código, NO para conversaciones
- **Decisión #39**: HybridSearch ya fue eliminado de ConversationService (19/06/25)

### Sistemas Centralizados en Core
1. **Manejo de Errores**: `/core/exceptions.py` - Sistema completo con jerarquía de excepciones
2. **Métricas**: `/core/tracing.py` - MetricsCollector centralizado
3. **Base de Datos**: `/core/database.py` - DatabaseManager singleton
4. **IDs**: `/core/id_generator.py` - Sistema unificado hex32
5. **Eventos**: `/core/events.py` - EventBus para coordinación

## 🗜️ Esquema de Base de Datos

### Tabla: conversations
```sql
CREATE TABLE conversations (
    session_id TEXT PRIMARY KEY,  -- ID hex32 único
    role TEXT NOT NULL,           -- 'system' para resúmenes de sesión
    content TEXT,                 -- Resúmenes concatenados con " | "
    content_summary TEXT,         -- Keywords en JSON array
    metadata TEXT,                -- JSON con created_at, status, etc.
    related_sessions TEXT,        -- JSON array de session_ids
    total_tokens INTEGER,         -- Contador acumulativo
    task_checkpoint_id TEXT,      -- FK a tasks (opcional)
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Notas sobre el Esquema
- **Una sesión = Una fila** con role='system'
- **content**: Resúmenes acumulados separados por " | "
- **content_summary**: Keywords extraidos para búsqueda rápida
- **metadata**: JSON con status ('active', 'completed'), timestamps
- **related_sessions**: Mantiene continuidad temporal entre chats

### Relación Task ↔ Session
- **Las sessions empiezan SIN task** (task_checkpoint_id = NULL)
- **TaskService** detecta si el mensaje indica nueva tarea ("vamos a implementar X")
- **TaskService** asocia la session a la task actualizando task_checkpoint_id
- **Una Task puede tener múltiples sessions**, pero una session solo una Task
- **get_session_context()** carga la task SI la session ya tiene una asociada

## 🔄 Flujo del Módulo

### Flujo Principal de Conversación

```
1. Usuario envía mensaje
   ↓
2. ChatService.process_message()
   ↓
3. ConversationService.create_session() o get_last_session()
   ↓
4. ChatService busca contexto relevante
   ↓
5. ConversationService.get_session_context()
   ↓
6. ChatService genera respuesta con Ollama
   ↓
7. Semantic.summarize() genera resúmen
   ↓
8. ConversationService.save_conversation_turn()
   ↓
9. TaskService actualiza si hay tarea activa
```

### Flujo de Búsqueda

```
1. Usuario busca "aquella vez que refactorizamos auth"
   ↓
2. ConversationService.search_conversations()
   ↓
3. _search_by_keywords() en SQLite
   ↓
4. Extrae keywords: ["refactorizamos", "auth"]
   ↓
5. Busca en content y content_summary con LIKE
   ↓
6. Retorna ConversationSearchResult tipados
```

## 📍 Estado Actual del Módulo

### Ubicación
`/src/acolyte/services/conversation_service.py`

### Responsabilidades Actuales
1. **Gestión de Sesiones**: crear, obtener última, completar
2. **Gestión de Resúmenes**: guardar turnos, extraer keywords
3. **Búsqueda**: por keywords en SQLite (NO semántica)
4. **Contexto Complejo**: sesiones + tareas + decisiones
5. **Eventos**: manejo de invalidación de cache
6. **Retry Logic**: para operaciones críticas de BD

### Dependencias

#### Hacia ConversationService (quién lo usa)
- **ChatService**: Orquestador principal, usa todos los métodos
- **TaskService**: Para asociar sesiones con tareas
- **API Layer**: `/v1/chat/completions` endpoint
- **Scripts**: Para análisis y estadísticas

#### Desde ConversationService (qué usa)
- **Core**: Database, Metrics, Events, Exceptions, TokenCounter, Config, IDGenerator
- **Models**: ConversationSearchRequest, ConversationSearchResult, TaskCheckpoint, TechnicalDecision
- **NO USA**: HybridSearch, Weaviate, RAG modules

## 🚨 Problemas Identificados

### 1. Método Excesivamente Largo
- `get_session_context()`: 163 líneas (298-461)
- Hace demasiadas cosas en un solo método
- Difícil de testear y mantener

### 2. Inconsistencia en Manejo de Errores
- `find_related_sessions()`: Lanza `DatabaseError` ✅
- `get_last_session()`: Retorna `None` ❌
- `search_conversations()`: Lanza `DatabaseError` ✅

### 3. Violación del Principio de Responsabilidad Única
- Mezcla gestión de sesiones con construcción de contexto complejo
- Maneja directamente objetos de otros dominios (Task, Decision)

### 4. Uso Subóptimo del Sistema de Errores
- Usa `DatabaseError` genérico en lugar de excepciones específicas de SQLite
- No agrega sugerencias a las excepciones
- No aprovecha el contexto rico disponible

### 5. Código Legacy
- Métodos con nombres legacy: `_search_by_keywords` (antes `_fallback_search`)
- Comentarios sobre HybridSearch eliminado

## 📐 Propuesta de Refactorización

### Principios Guía
1. **Mantener compatibilidad**: No romper la API pública
2. **Aprovechar sistemas centralizados**: Usar Core al máximo
3. **Separación de responsabilidades**: Un método, una responsabilidad
4. **Testabilidad**: Métodos pequeños y testeables
5. **Claridad**: Nombres descriptivos y documentación clara

### Estructura Propuesta

```python
class ConversationService:
    """
    Gestiona conversaciones con persistencia en SQLite.
    
    Responsabilidades:
    - CRUD de sesiones de conversación
    - Búsqueda por keywords
    - Coordinación con otros servicios
    """
    
    # === Métodos Públicos (API estable) ===
    
    async def create_session(self, initial_message: str) -> str:
        """Crea nueva sesión con continuidad automática."""
        
    async def save_conversation_turn(self, ...):
        """Guarda resumen de turno de conversación."""
        
    async def find_related_sessions(self, ...):
        """Busca sesiones relacionadas por keywords."""
        
    async def get_session_context(self, ...):
        """Obtiene contexto completo (simplificado)."""
        
    async def search_conversations(self, ...):
        """Búsqueda tipada de conversaciones."""
        
    async def get_last_session(self) -> Optional[Dict[str, Any]]:
        """Obtiene última sesión o None."""
        
    async def complete_session(self, session_id: str) -> None:
        """Marca sesión como completada."""
    
    # === Métodos Privados (Helpers) ===
    
    async def _get_session_or_fail(self, session_id: str) -> Dict[str, Any]:
        """Obtiene sesión o lanza NotFoundError con contexto rico."""
        
    def _parse_summary_turns(self, session: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parsea resúmenes de turnos desde content."""
        
    async def _get_related_sessions_data(self, related_ids: List[str]) -> List[Dict[str, Any]]:
        """Obtiene datos de sesiones relacionadas."""
        
    async def _build_task_context(self, task_id: str) -> Dict[str, Any]:
        """Construye contexto de tarea (delegando a modelos)."""
        
    async def _build_decisions_context(self, task_id: str) -> List[Dict[str, Any]]:
        """Construye contexto de decisiones (delegando a modelos)."""
```

## 📝 Tareas de Refactorización

### 1. Dividir `get_session_context()`

```python
async def get_session_context(self, session_id: str, include_related: bool = True) -> Dict[str, Any]:
    """Versión refactorizada - máximo 30 líneas."""
    start_time = time.time()
    
    try:
        # 1. Obtener sesión base
        session = await self._get_session_or_fail(session_id)
        
        # 2. Construir contexto básico
        context = {
            "session": session,
            "summary_turns": self._parse_summary_turns(session),
            "related_sessions": [],
            "task": None,
            "decisions": []
        }
        
        # 3. Enriquecer con datos relacionados
        if include_related and session.get("related_sessions"):
            related_ids = json.loads(session["related_sessions"])
            context["related_sessions"] = await self._get_related_sessions_data(related_ids)
        
        # 4. Enriquecer con contexto de tarea
        if session.get("task_checkpoint_id"):
            context["task"] = await self._build_task_context(session["task_checkpoint_id"])
            context["decisions"] = await self._build_decisions_context(session["task_checkpoint_id"])
        
        return context
        
    finally:
        self._record_metrics(start_time, "get_session_context")
```

### 2. Mejorar Manejo de Errores

```python
async def _get_session_or_fail(self, session_id: str) -> Dict[str, Any]:
    """Ejemplo de uso correcto del sistema de errores."""
    try:
        result = await self.db.execute_async(
            "SELECT * FROM conversations WHERE session_id = ? AND role = 'system'",
            (session_id,),
            FetchType.ONE
        )
        
        if not result.data:
            error = NotFoundError(
                f"Session {session_id} not found",
                context={"session_id": session_id, "role": "system"}
            )
            error.add_suggestion("Verificar que la sesión existe")
            error.add_suggestion("Comprobar que la sesión no fue completada")
            error.add_suggestion("Usar get_last_session() para obtener la sesión activa")
            raise error
            
        return result.data
        
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            raise SQLiteBusyError(
                "Database locked while fetching session",
                context={"session_id": session_id, "operation": "get_session"}
            )
        raise DatabaseError(f"Failed to fetch session: {str(e)}", cause=e)
```

### 3. Consistencia en `get_last_session()`

**Decisión**: Mantener el comportamiento actual (retorna None) pero documentarlo mejor:

```python
async def get_last_session(self) -> Optional[Dict[str, Any]]:
    """
    Obtiene la última sesión del usuario.
    
    Returns:
        Dict con datos de la sesión o None si:
        - No hay sesiones en el sistema
        - Ocurre un error al consultar la BD (se loguea pero no se propaga)
    
    Note:
        Este método NO lanza excepciones por diseño, ya que se usa
        para continuidad automática donde la ausencia de sesión previa
        es un caso válido.
    """
```

### 4. Eliminar Código y Comentarios Legacy

- Eliminar todos los comentarios sobre HybridSearch
- Actualizar docstrings para reflejar arquitectura actual
- Limpiar imports no utilizados

### 5. Optimizar Búsquedas

```python
async def _search_by_keywords(self, query: str, ...) -> List[Dict[str, Any]]:
    """
    Búsqueda optimizada con índices apropiados.
    
    TODO: Verificar que existen índices en:
    - conversations.content
    - conversations.content_summary
    - conversations.timestamp
    - conversations.role
    """
```

## 📚 Documentación Relevante a Leer

### Esencial
1. `/docs/AUDIT_DECISIONS.md` - Decisiones 1, 4, 7, 12, 39
2. `/core/exceptions.py` - Sistema completo de errores
3. `/core/docs/REFERENCE.md` - APIs de DatabaseManager y MetricsCollector
4. `/models/conversation.py` - Modelos ConversationSearchRequest/Result

### Contexto
1. `/services/docs/ARCHITECTURE.md` - Arquitectura del módulo Services
2. `/services/docs/INTEGRATION.md` - Cómo se conecta con otros módulos
3. `/docs/PROMPT.md` - Sección sobre ConversationService

### Para Testing
1. `/core/docs/TESTING_GUIDE.md` - Patrones de testing
2. **⚠️ NO HAY TESTS EXISTENTES** para ConversationService
3. Oportunidad de crear tests durante la refactorización

## ✅ Criterios de Aceptación

1. **Sin cambios en API pública**: Todos los métodos públicos mantienen misma firma
2. **Crear tests unitarios**: Mínimo 80% cobertura ya que no hay tests existentes
3. **Métricas preservadas**: Mismos nombres de métricas
4. **Documentación actualizada**: Docstrings y comentarios reflejan cambios
5. **Código más legible**: Métodos < 50 líneas, responsabilidades claras
6. **Excepciones enriquecidas**: Usar sistema de errores Core con contexto y sugerencias

## 💡 Ejemplo de Uso Actual

### Desde ChatService
```python
# ChatService usa ConversationService así:
async def process_message(self, message: str, session_id: Optional[str] = None):
    # 1. Crear o recuperar sesión
    if not session_id:
        session_id = await self.conversation_service.create_session(message)
    
    # 2. Obtener contexto completo
    context = await self.conversation_service.get_session_context(
        session_id, 
        include_related=True
    )
    
    # 3. Procesar mensaje...
    
    # 4. Guardar resúmen del turno
    await self.conversation_service.save_conversation_turn(
        session_id=session_id,
        user_message=message,
        assistant_response=response,
        summary=summary,  # Generado por Semantic
        tokens_used=total_tokens,
        task_checkpoint_id=task_id
    )
```

### Desde API
```python
# Endpoint de búsqueda
@router.post("/v1/conversations/search")
async def search_conversations(request: ConversationSearchRequest):
    results = await conversation_service.search_conversations(request)
    return {"conversations": results}
```

## 🚀 Pasos para Ejecutar

1. **Leer toda la documentación listada**
2. **Analizar tests existentes** (si los hay)
3. **Crear branch**: `refactor/conversation-service`
4. **Refactorizar incrementalmente**: Un cambio a la vez
5. **Ejecutar tests** después de cada cambio
6. **Actualizar documentación** en `/services/docs/`
7. **Code review** con foco en mantenibilidad

## ⚠️ Advertencias

1. **NO cambiar esquema de BD**: La tabla conversations debe mantenerse igual
2. **NO romper compatibilidad**: ChatService depende fuertemente de esta API
3. **NO introducir nuevas dependencias**: Usar solo lo que ya existe en Core
4. **NO sobre-optimizar**: Claridad > performance en este caso

## 📊 Métricas de Éxito

- Reducción de complejidad ciclomática
- Métodos más cortos y enfocados
- Mejor aprovechamiento de sistemas Core
- Mayor testabilidad
- Documentación clara y actualizada
- **Crear suite de tests** con al menos 80% cobertura

---

**Última actualización**: 19/06/25
**Autor**: Sistema ACOLYTE
**Estado**: Pendiente de ejecución
