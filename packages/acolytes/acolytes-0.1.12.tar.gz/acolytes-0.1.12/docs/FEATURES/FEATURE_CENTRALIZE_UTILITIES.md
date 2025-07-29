# 🔧 Centralización de Utilidades Comunes

## 📋 ¿Qué es?

La centralización de utilidades se refiere a extraer patrones de código que se repiten en múltiples lugares del proyecto y consolidarlos en funciones/clases reutilizables. El TODO específicamente menciona 2 patrones:

### 1. **Progress Reporting**
- Notificar progreso de operaciones largas
- Formato consistente de eventos de progreso
- Publicación a EventBus

### 2. **Token Estimation Utilities**
- Estimar tokens sin llamar a APIs externas
- Cálculos aproximados para planificación
- Diferentes ratios por tipo de contenido

## 🎯 ¿Para qué vale?

### Beneficios de centralización:

1. **Elimina duplicación de código**
   - Menos líneas totales = menos bugs potenciales
   - Un solo lugar para corregir errores
   - Cambios consistentes en todo el proyecto

2. **Mejora mantenibilidad**
   - Lógica compleja en un solo lugar
   - Tests unitarios centralizados
   - Documentación única

3. **Consistencia garantizada**
   - Mismo comportamiento en todos los usos
   - Mismos parámetros y configuración
   - Misma gestión de errores

4. **Facilita evolución**
   - Mejorar algoritmo beneficia a todos
   - Añadir features en un solo lugar
   - Optimización centralizada

### Problemas actuales por la duplicación:

- **Progress events** con diferentes formatos
- **Token counting** con diferentes aproximaciones

## 💡 ¿Por qué es óptimo?

### 1. **Principio DRY (Don't Repeat Yourself)**
- Una sola implementación en lugar de código duplicado
- Cambios en un solo lugar benefician a todos los usos

### 2. **Reduce superficie de bugs**
- Bug en utilidad = corregir en múltiples lugares actualmente
- Con centralización = corregir en 1 lugar
- Tests más completos posibles

### 3. **Mejora la legibilidad**
- Reemplaza bloques de 20+ líneas con una sola llamada clara
- Código más expresivo y fácil de entender

### 4. **Optimización de performance**
- Caché compartido para estimaciones de tokens
- Reutilización de cálculos frecuentes
- Evita recalcular métricas idénticas

## 🏗️ ¿Cómo debería ser?

### Estructura propuesta:

```
src/acolyte/core/utils/
├── __init__.py
├── progress.py       # Progress reporting helpers
└── tokens.py         # Token estimation utilities
```

### 1. **Progress Reporting** (`progress.py`)

```python
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

from acolyte.core.events import event_bus, ProgressEvent
from acolyte.core.utils.datetime_utils import utc_now

@dataclass
class ProgressTracker:
    """Helper for consistent progress reporting."""
    
    operation: str
    total: int
    source: str = "unknown"
    task_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    _current: int = 0
    _start_time: datetime = field(default_factory=utc_now)
    
    async def update(self, current: int, message: str = ""):
        """Update progress and emit event."""
        self._current = current
        
        # Calculate percentage
        percentage = (current / max(self.total, 1)) * 100
        
        # Calculate ETA if possible
        elapsed = (utc_now() - self._start_time).total_seconds()
        if current > 0 and elapsed > 0:
            rate = current / elapsed
            remaining = self.total - current
            eta_seconds = remaining / rate if rate > 0 else None
        else:
            eta_seconds = None
        
        # Create progress event
        event = ProgressEvent(
            source=self.source,
            operation=self.operation,
            current=current,
            total=self.total,
            message=message or f"Processing: {percentage:.1f}%",
            task_id=self.task_id,
            percentage=percentage,
            eta_seconds=eta_seconds,
            **self.metadata
        )
        
        # Publish event
        await event_bus.publish(event)
    
    async def increment(self, message: str = ""):
        """Increment current by 1 and emit event."""
        await self.update(self._current + 1, message)
    
    async def complete(self, message: str = "Complete"):
        """Mark as complete."""
        await self.update(self.total, message)
```

### 2. **Token Estimation** (`tokens.py`)

```python
import re
from typing import Dict, Optional
from functools import lru_cache

class TokenEstimator:
    """
    Estimate token counts without external API calls.
    
    Based on empirical observations:
    - Average English word ≈ 1.3 tokens
    - Code tends to have more tokens per "word"
    - Different languages have different ratios
    """
    
    # Empirical ratios (tokens per word)
    LANGUAGE_RATIOS: Dict[str, float] = {
        "english": 1.3,
        "python": 1.5,      # snake_case, special chars
        "javascript": 1.4,  # camelCase
        "java": 1.6,        # verboseLongNames
        "cpp": 1.7,         # namespace::class::method
        "markdown": 1.2,    # mostly natural language
        "json": 2.0,        # lots of delimiters
        "xml": 2.5,         # tags everywhere
    }
    
    # Simple word splitter (good enough for estimation)
    WORD_PATTERN = re.compile(r'\b\w+\b|[^\w\s]')
    
    @classmethod
    @lru_cache(maxsize=1000)
    def estimate_tokens(
        cls, 
        text: str, 
        language: str = "english",
        multiplier: float = 1.0
    ) -> int:
        """
        Estimate token count for text.
        
        Args:
            text: Text to estimate
            language: Language/format of text
            multiplier: Safety multiplier (default 1.0)
            
        Returns:
            Estimated token count
        """
        # Find all words and symbols
        words = cls.WORD_PATTERN.findall(text)
        word_count = len(words)
        
        # Get ratio for language
        ratio = cls.LANGUAGE_RATIOS.get(language, 1.3)
        
        # Calculate estimate
        estimate = int(word_count * ratio * multiplier)
        
        # Minimum of 1 token per 4 characters (safety)
        char_estimate = len(text) // 4
        
        return max(estimate, char_estimate)
    
    @classmethod
    def estimate_messages_tokens(
        cls,
        messages: list[Dict[str, str]],
        overhead_per_message: int = 4
    ) -> int:
        """
        Estimate tokens for a list of messages.
        
        Each message has overhead for role markers.
        """
        total = 0
        
        for message in messages:
            content = message.get("content", "")
            role = message.get("role", "")
            
            # Estimate content tokens
            content_tokens = cls.estimate_tokens(content)
            
            # Add overhead for message structure
            total += content_tokens + overhead_per_message
            
            # Add role tokens
            total += len(role.split())
        
        return total
```

### Integración con el código existente:

```python
# Progress reporting
from acolyte.core.utils.progress import ProgressTracker

tracker = ProgressTracker("indexing", total=100)
await tracker.update(50, "Halfway done")

# Token estimation
from acolyte.core.utils.tokens import TokenEstimator

tokens = TokenEstimator.estimate_tokens(text, language="python")
```

### Plan de migración:

1. **Fase 1**: Crear módulos de utilidades con tests
2. **Fase 2**: Identificar todos los lugares con código duplicado
3. **Fase 3**: Migrar gradualmente, servicio por servicio
4. **Fase 4**: Eliminar código duplicado
5. **Fase 5**: Documentar patrones de uso

### Beneficios medibles:

- **Reducción de código**: ~200-400 líneas menos
- **Consistencia**: 100% de eventos de progreso con mismo formato
- **Mantenibilidad**: 1 lugar para actualizar estimaciones de tokens
- **Tiempo de desarrollo**: 30% menos para nuevos servicios

## 🚀 Prioridad y Esfuerzo

**Prioridad**: Media
- Mejora consistencia del código
- Facilita mantenimiento futuro
- Reduce duplicación

**Esfuerzo estimado**:
- Crear utilidades: 0.5 días
- Migrar código existente: 1-2 días
- Tests completos: 0.5 días

**ROI**: Alto - Inversión inicial que mejora la calidad del código