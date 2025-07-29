# 🛑 ANTES DE REFACTORIZAR - Tests Primero

## ⚠️ CRÍTICO: Services tiene 0% cobertura de tests

**NO TOCAR NINGÚN CÓDIGO DE SERVICES** hasta completar estos tests.

## 📋 Por qué tests primero

1. **Services es el corazón de ACOLYTE** - Todo pasa por aquí
2. **Sin tests = refactorización a ciegas** - Alta probabilidad de romper algo
3. **Los tests documentan el comportamiento actual** - Sirven como especificación
4. **Detectan breaking changes** - Si un test falla tras refactorizar, algo se rompió

## 🎯 Tests Mínimos Requeridos

### 1. test_conversation_service.py

```python
"""Tests para ConversationService - API pública y comportamiento."""

import pytest
from acolyte.services import ConversationService
from acolyte.core.exceptions import NotFoundError, DatabaseError

class TestConversationServiceContract:
    """Verifica que la API pública no cambie."""
    
    async def test_has_required_methods(self):
        """ConversationService debe exponer estos métodos públicos."""
        service = ConversationService()
        
        # Métodos que DEBEN existir
        required_methods = [
            'create_session',
            'save_conversation_turn', 
            'find_related_sessions',
            'get_session_context',
            'search_conversations',
            'get_last_session',
            'complete_session'
        ]
        
        for method in required_methods:
            assert hasattr(service, method)
            assert callable(getattr(service, method))

class TestConversationServiceBehavior:
    """Verifica comportamiento actual."""
    
    @pytest.fixture
    async def service(self):
        """Servicio limpio para cada test."""
        return ConversationService()
    
    async def test_create_session_returns_hex_id(self, service):
        """create_session debe retornar ID hex de 32 chars."""
        session_id = await service.create_session("Test message")
        
        assert isinstance(session_id, str)
        assert len(session_id) == 32
        assert all(c in '0123456789abcdef' for c in session_id)
    
    async def test_save_turn_requires_existing_session(self, service):
        """save_conversation_turn debe fallar si sesión no existe."""
        with pytest.raises(NotFoundError):
            await service.save_conversation_turn(
                session_id="nonexistent123",
                user_message="test",
                assistant_response="test",
                summary="test summary",
                tokens_used=100
            )
    
    async def test_session_continuity(self, service):
        """Las sesiones deben mantener continuidad temporal."""
        # Crear primera sesión
        session1 = await service.create_session("Primera")
        
        # Crear segunda sesión
        session2 = await service.create_session("Segunda")
        
        # La segunda debe tener la primera como relacionada
        context = await service.get_session_context(session2)
        related_ids = [s['id'] for s in context.get('related_sessions', [])]
        
        assert session1 in related_ids
```

### 2. test_chat_service.py

```python
"""Tests para ChatService - Orquestador principal."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from acolyte.services import ChatService

class TestChatServiceContract:
    """API pública de ChatService."""
    
    async def test_required_methods(self):
        """ChatService debe exponer estos métodos."""
        # Mock dependencies
        conv_service = Mock()
        task_service = Mock()
        
        service = ChatService(
            context_size=32768,
            conversation_service=conv_service,
            task_service=task_service
        )
        
        required = [
            'process_message',
            'request_dream_analysis',
            'get_active_session_info'
        ]
        
        for method in required:
            assert hasattr(service, method)

class TestChatServiceBehavior:
    """Comportamiento del orquestador."""
    
    @pytest.fixture
    async def service(self):
        """ChatService con mocks."""
        with patch('acolyte.services.chat_service.ConversationService') as MockConv:
            with patch('acolyte.services.chat_service.TaskService') as MockTask:
                # Configurar mocks
                mock_conv = AsyncMock()
                mock_conv.create_session = AsyncMock(return_value="test123")
                mock_conv.get_session_context = AsyncMock(return_value={
                    "session": {"id": "test123"},
                    "summary_turns": [],
                    "related_sessions": []
                })
                
                MockConv.return_value = mock_conv
                MockTask.return_value = AsyncMock()
                
                return ChatService(context_size=32768)
    
    async def test_process_message_returns_required_fields(self, service):
        """process_message debe retornar campos requeridos."""
        with patch.object(service.ollama, 'generate', return_value="Test response"):
            result = await service.process_message("Hello")
            
            # Verificar estructura de respuesta
            assert 'response' in result
            assert 'session_id' in result
            assert 'tokens_used' in result
            assert 'processing_time' in result
            
            # Verificar tipos
            assert isinstance(result['response'], str)
            assert isinstance(result['session_id'], str)
            assert isinstance(result['tokens_used'], dict)
            assert isinstance(result['processing_time'], (int, float))
```

### 3. test_indexing_service.py

```python
"""Tests para IndexingService - Pipeline de indexación."""

import pytest
from pathlib import Path
from acolyte.services import IndexingService

class TestIndexingServiceContract:
    """API pública del indexador."""
    
    async def test_required_methods(self):
        """IndexingService debe exponer estos métodos."""
        service = IndexingService()
        
        required = [
            'index_files',
            'estimate_files',
            'remove_file',
            'rename_file',
            'get_stats',
            'is_supported_file'
        ]
        
        for method in required:
            assert hasattr(service, method)

class TestIndexingServiceBehavior:
    """Comportamiento del pipeline."""
    
    @pytest.fixture
    async def service(self):
        return IndexingService()
    
    async def test_index_files_validates_trigger(self, service):
        """index_files debe validar triggers."""
        result = await service.index_files(
            files=[],
            trigger="invalid_trigger"
        )
        
        # Debe usar 'manual' como fallback
        assert result['trigger'] == 'manual'
    
    async def test_supported_extensions(self, service):
        """Verifica extensiones soportadas."""
        # Debe soportar
        assert service.is_supported_file(Path("test.py"))
        assert service.is_supported_file(Path("test.js"))
        assert service.is_supported_file(Path("test.md"))
        
        # NO debe soportar
        assert not service.is_supported_file(Path("test.exe"))
        assert not service.is_supported_file(Path("test.dll"))
```

## 📊 Métricas de Éxito

- [ ] Mínimo **20 tests por servicio**
- [ ] Cubrir **todos los métodos públicos**
- [ ] Cubrir **casos de error principales**
- [ ] Tests pasan con código actual
- [ ] **80% cobertura mínima**

## 🔧 Herramientas

```bash
# Ejecutar tests de un servicio
pytest tests/services/test_conversation_service.py -v

# Ver cobertura
pytest tests/services/ --cov=acolyte.services --cov-report=html

# Ejecutar solo tests de contrato (rápidos)
pytest tests/services/ -k "Contract" -v
```

## ⚡ Orden de Implementación

1. **ConversationService** - Ya tiene documento de refactor
2. **ChatService** - Orquestador crítico
3. **IndexingService** - Más complejo, hacer último
4. **TaskService** - Probablemente no necesita refactor
5. **GitService** - Probablemente no necesita refactor

## 🚨 Recordatorio Final

**NO REFACTORIZAR NADA** hasta que:
1. ✅ Tests escritos
2. ✅ Tests pasando
3. ✅ Cobertura > 80%
4. ✅ Revisión de que capturan comportamiento actual

Solo entonces proceder con la refactorización documentada.

---

**Fecha**: 19/06/25  
**Estado**: Pendiente de implementación  
**Prioridad**: CRÍTICA - Bloquea toda refactorización
