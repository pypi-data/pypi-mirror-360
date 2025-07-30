# 🎯 Módulo Models

Define todas las estructuras de datos del sistema ACOLYTE con validación estricta usando Pydantic v2.

## 📑 Documentación

- **[docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)** - Diseño interno y decisiones arquitectónicas
- **[docs/STATUS.md](./docs/STATUS.md)** - Estado actual del módulo
- **[docs/REFERENCE.md](./docs/REFERENCE.md)** - API completa con todas las clases y métodos
- **[docs/WORKFLOWS.md](./docs/WORKFLOWS.md)** - Flujos detallados y ejemplos de uso
- **[docs/INTEGRATION.md](./docs/INTEGRATION.md)** - Integración con otros módulos

## 🔧 Componentes Principales

- **base.py** - Mixins reutilizables (timestamps, IDs) y configuración base
- **chat.py** - Modelos OpenAI-compatible para el endpoint principal
- **chunk.py** - Fragmentos de código para RAG con 18 tipos especializados  
- **conversation.py** - Persistencia de conversaciones con resúmenes inteligentes
- **document.py** - Documentos e indexación con validación de paths
- **dream.py** - Sistema de optimización técnica (no antropomorfización)
- **semantic_types.py** - Tipos para el módulo Semantic (NLP)
- **task_checkpoint.py** - Agrupación jerárquica de sesiones por tarea
- **technical_decision.py** - Decisiones técnicas importantes con alternativas
- **common/metadata.py** - Metadata compartida (Git, archivos, lenguajes)

## 🆕 Migración a Pydantic v2 (16/06/25)

**Módulo Models completamente migrado a Pydantic v2**:
- `@model_validator` con tipo de retorno `Self` (no tipo concreto) en conversation.py
- Import de `typing_extensions.Self` agregado para compatibilidad
- `ConfigDict` en lugar de Config class en base.py
- Todos los field_validators con `@classmethod`
- Sin cambios de lógica, solo sintaxis actualizada

## ⚠️ Cambio Importante - Enums (17/06/25)

**Fix en TaskCheckpoint**: Los métodos `get_summary()` y `to_search_text()` ya no usan `.value` en enums.
- Debido a `use_enum_values=True` en `AcolyteBaseModel`, los enums ya son strings
- Corregido acceso directo: `self.task_type` en lugar de `self.task_type.value`
- Afecta a cualquier código que use estos métodos

## ⚡ Quick Start

```python
# Crear un mensaje para chat
from acolyte.models.chat import Message, Role, ChatRequest

message = Message(role=Role.USER, content="¿Cómo implemento auth JWT?")
request = ChatRequest(
    model="acolyte:latest",
    messages=[message],
    temperature=0.7
)

# Crear una conversación con resúmenes
from acolyte.models.conversation import Conversation

conversation = Conversation(
    session_id="sess_a3f4b2c1d5e6f7a8b9c0d1e2f3a4b5c6",
    summary="Usuario pregunta sobre auth JWT",
    keywords=["auth", "jwt", "security"]
)
conversation.add_message(message)
```
