# 🔄 CENTRALIZATION TODO - Código Duplicado para Centralizar

> **Documento creado**: 2025-01-17  
> **Propósito**: Tracking de patrones duplicados que deben centralizarse en Core

## 📊 Estado General

Este documento rastrea funcionalidad duplicada entre módulos que debería centralizarse para:
- Reducir duplicación de código
- Prevenir bugs por inconsistencias
- Facilitar mantenimiento
- Estandarizar comportamientos

## 🎯 Alta Prioridad

## 📈 Media Prioridad

### 1. 📊 Progress Reporting Pattern

**Problema**: Patrón de reporte de progreso repetido pero no estandarizado

**Ubicaciones actuales**:
- `services/indexing_service.py` - _notify_progress()
- `api/websockets/progress.py` - Manejo de eventos
- `embeddings/metrics.py` - Podría reportar progreso
- `dream/orchestrator.py` - Podría reportar fases

**Propuesta**: `core/progress.py`
```python
from typing import Optional, Dict, Any

class ProgressReporter:
    """Standardized progress reporting across all services."""
    
    def __init__(self, total: int, task_id: str, operation: str):
        self.total = total
        self.current = 0
        self.task_id = task_id
        self.operation = operation
        self.start_time = datetime.utcnow()
    
    async def increment(self, message: str, metadata: Optional[Dict] = None):
        """Report progress increment."""
        self.current += 1
        await self._publish_event(message, metadata)
    
    async def update(self, current: int, message: str):
        """Update to specific progress value."""
        self.current = current
        await self._publish_event(message)
```

---

### 2. 🧮 Token Estimation Utilities

**Problema**: Estimaciones de tokens inconsistentes en diferentes módulos

**Ubicaciones actuales**:
- `dream/analyzer.py` - 1000 tokens por archivo (hardcoded)
- `semantic/summarizer.py` - len(text.split()) * 2
- `core/token_counter.py` - Tiene lógica pero no helpers de estimación
- Configuración: chars_per_token varía (3, 4, 3.8)

**Propuesta**: Extender `core/token_counter.py` con:
```python
class TokenEstimator:
    """Quick token estimation without full tokenization."""
    
    # Calibrated constants
    CODE_CHARS_PER_TOKEN = 3.8
    TEXT_CHARS_PER_TOKEN = 4.2
    MARKDOWN_CHARS_PER_TOKEN = 4.5
    
    @staticmethod
    def estimate_file_tokens(path: Path) -> int:
        """Estimate tokens for a file based on type and size."""
        pass
    
    @staticmethod
    def estimate_text_tokens(text: str, content_type: str = 'code') -> int:
        """Quick estimation without full tokenization."""
        pass
```

---

### 3. 🌐 Datetime Utilities

**Problema**: Manejo inconsistente de datetime (ya documentado)

**Estado**: ✅ TODO ya agregado en PROMPT.md

**Propuesta**: `core/utils.py` con helpers datetime

---

## 📉 Baja Prioridad

### 4. 🔢 Batch Processing Utilities

**Problema**: Lógica de procesamiento por batches repetida

**Ubicaciones**:
- `services/indexing_service.py` - Procesamiento de archivos
- `embeddings/unixcoder.py` - Encoding por batches
- `rag/enrichment/service.py` - Enriquecimiento por batches

**Propuesta**: `core/batch.py`

---

### 5. 💾 Memory Monitoring

**Problema**: Chequeos de memoria ad-hoc

**Ubicaciones**:
- `embeddings/unixcoder.py` - MemoryGuard
- `services/indexing_service.py` - Podría beneficiarse

---

### 6. 🔤 String Sanitization

**Problema**: Validación y sanitización de strings dispersa

**Ubicaciones**:
- Path validation en varios lugares
- Filename sanitization
- SQL injection prevention

---

### 7. 🗃️ Cache Configuration

**Problema**: Configuración de cache repetida

**Ubicaciones**:
- Todos los módulos usan max_size=1000, ttl=3600
- Podría ser una configuración central

---

### 8. ✅ Common Validation Helpers

**Problema**: Validaciones comunes repetidas

**Ejemplos**:
- `validate_not_empty()`
- `validate_range(min, max)`
- `validate_enum()`

---

## 🚀 Plan de Implementación Sugerido

1. **Fase 1** (Inmediata después de tests):
   - Progress reporting (mejora UX)
   - Token estimation (mejora precisión)

2. **Fase 2** (Después de documentación):
   - Datetime utilities
   - Batch processing

3. **Fase 3** (Optimización futura):
   - Memory monitoring
   - String sanitization
   - Cache configuration
   - Validation helpers

## 📝 Notas

- Cada centralización debe mantener retrocompatibilidad
- Agregar tests exhaustivos para utilities centralizadas
- Documentar migración para cada patrón
- Considerar performance impact de abstracciones

---

**Última actualización**: 2025-01-17 por IA colaboradora
