## 📁 Archivos Nuevos a Crear

### Para IndexingService:
- `/services/indexing_pipeline.py`
- `/services/indexing_api.py`
- `/services/chunking_orchestrator.py`
- `/services/indexing_stats.py`
- `/services/helpers/import_checker.py`

### Para ChatService:
- `/services/chat_processor.py`
- `/services/dream_helper.py`
- `/services/helpers/message_steps.py`
- `/services/helpers/prompt_formatter.py`

### Para ConversationService:
- `/services/conversation_search.py`
- `/services/context_builder.py`
- `/services/helpers/keyword_extractor.py`

### Compartidos:
- `/services/helpers/__init__.py`
- `/services/base_service.py`

Total: ~15 archivos nuevos para distribuir las responsabilidades actuales.

Dado que `__init__.py` exporta las clases, podemos hacer una **refactorización interna** sin romper nada:

```python
# Otros módulos importan así:
from acolyte.services import ChatService  # ✅ No cambia

# NO importan así:
from acolyte.services.chat_service import ChatService  # ❌
```

## 🔄 Estrategia Revisada

### Mantener archivos actuales, extraer lógica a helpers internos:

```
services/
├── __init__.py              # Sin cambios
├── conversation_service.py  # Clase principal delegando a helpers
├── chat_service.py          # Clase principal delegando a helpers  
├── indexing_service.py      # Clase principal delegando a helpers
└── _internal/               # Submódulo privado (con _)
    ├── __init__.py
    ├── conversation_helpers.py
    ├── chat_steps.py
    ├── indexing_pipeline.py
    └── shared_utils.py
```

### Ventajas:
- ✅ **Cero cambios** en imports externos
- ✅ API pública idéntica
- ✅ Refactorización progresiva
- ✅ Backwards compatible
- ✅ El `_` indica que es interno

### Ejemplo:
```python
# chat_service.py (refactorizado)
from ._internal.chat_steps import MessageProcessor

class ChatService:
    def __init__(self, ...):
        self._processor = MessageProcessor()
    
    async def process_message(self, ...):
        # Delegar al helper interno
        return await self._processor.process(...)
```

**Mucho mejor approach** que crear archivos completamente nuevos.