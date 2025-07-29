# 📅 Feature: Centralización de Datetime

## Estado Actual

Actualmente, el manejo de datetime está disperso por todo el proyecto usando `datetime.utcnow()` directamente:

```python
# En orchestrator.py
"estimated_completion": datetime.utcnow().replace(minute=datetime.utcnow().minute + self.cycle_duration).isoformat()

# En state_manager.py
self._state_start_time = datetime.utcnow()

# En fatigue_monitor.py
days_elapsed = (datetime.utcnow() - last_opt).days
```

### Problemas Identificados

1. **Repetición de código**: `datetime.utcnow()` aparece 50+ veces
2. **Inconsistencia potencial**: Algunos archivos podrían usar `datetime.now()` sin timezone
3. **Dificultad para testing**: No se puede mockear fácilmente el tiempo
4. **Formato inconsistente**: Algunos usan `.isoformat()`, otros no

## Propuesta de Solución

### 1. Crear `core/utils/datetime_utils.py`

```python
"""
Centralized datetime utilities for ACOLYTE.

Provides consistent datetime handling across the entire project.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Union
import re


def utc_now() -> datetime:
    """
    Get current UTC datetime.
    
    Returns:
        Current datetime in UTC
    """
    return datetime.utcnow()


def utc_now_iso() -> str:
    """
    Get current UTC datetime as ISO string.
    
    Returns:
        Current datetime in ISO format with 'Z' suffix
    """
    return datetime.utcnow().isoformat() + 'Z'


def ensure_utc(dt: datetime) -> datetime:
    """
    Ensure datetime is in UTC.
    
    Args:
        dt: Datetime to convert
        
    Returns:
        Datetime in UTC
        
    Raises:
        ValueError: If datetime is naive and can't be converted
    """
    if dt.tzinfo is None:
        # Naive datetime - assume it's already UTC
        return dt.replace(tzinfo=timezone.utc)
    elif dt.tzinfo == timezone.utc:
        return dt
    else:
        # Convert to UTC
        return dt.astimezone(timezone.utc)


def parse_iso_datetime(iso_string: str) -> datetime:
    """
    Parse ISO datetime string to datetime object.
    
    Handles various ISO formats:
    - 2024-01-01T12:00:00
    - 2024-01-01T12:00:00Z
    - 2024-01-01T12:00:00+00:00
    
    Args:
        iso_string: ISO format datetime string
        
    Returns:
        Parsed datetime in UTC
    """
    # Remove 'Z' suffix if present
    if iso_string.endswith('Z'):
        iso_string = iso_string[:-1] + '+00:00'
    
    # Try parsing with timezone
    try:
        dt = datetime.fromisoformat(iso_string)
        return ensure_utc(dt)
    except ValueError:
        # Try without timezone (assume UTC)
        dt = datetime.fromisoformat(iso_string)
        return dt.replace(tzinfo=timezone.utc)


def format_iso(dt: datetime) -> str:
    """
    Format datetime to ISO string with Z suffix.
    
    Args:
        dt: Datetime to format
        
    Returns:
        ISO formatted string with 'Z' suffix
    """
    utc_dt = ensure_utc(dt)
    return utc_dt.isoformat().replace('+00:00', 'Z')


def time_ago(dt: Union[datetime, str]) -> str:
    """
    Get human-readable time difference.
    
    Args:
        dt: Past datetime or ISO string
        
    Returns:
        Human readable string like "2 hours ago"
    """
    if isinstance(dt, str):
        dt = parse_iso_datetime(dt)
    
    diff = utc_now() - ensure_utc(dt)
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "just now"


def add_time(dt: datetime, **kwargs) -> datetime:
    """
    Add time to datetime with UTC preservation.
    
    Args:
        dt: Base datetime
        **kwargs: Arguments for timedelta (days, hours, minutes, etc)
        
    Returns:
        New datetime in UTC
    """
    utc_dt = ensure_utc(dt)
    return utc_dt + timedelta(**kwargs)


# For testing and mocking
_mock_time: Optional[datetime] = None


def set_mock_time(dt: Optional[datetime]) -> None:
    """Set mock time for testing. None to disable."""
    global _mock_time
    _mock_time = dt


def utc_now_testable() -> datetime:
    """Get current time (mockable for tests)."""
    return _mock_time if _mock_time else utc_now()
```

### 2. Actualizar Imports en Todo el Proyecto

```python
# Antes
from datetime import datetime

# Después  
from acolyte.core.utils.datetime_utils import utc_now, utc_now_iso, format_iso
```

### 3. Reemplazar Usos

```python
# Antes
last_opt_time = datetime.utcnow()
timestamp = datetime.utcnow().isoformat()

# Después
last_opt_time = utc_now()
timestamp = utc_now_iso()
```

## Plan de Implementación

### Fase 1: Preparación (1 hora)
1. Crear `core/utils/__init__.py`
2. Crear `core/utils/datetime_utils.py` con las funciones
3. Escribir tests completos para datetime_utils
4. Verificar que todos los tests pasen

### Fase 2: Migración por Módulos (2-3 horas)

**Orden de migración** (de menos a más crítico):
1. `dream/` - 15 archivos
2. `semantic/` - 8 archivos  
3. `rag/` - 20 archivos
4. `services/` - 5 archivos
5. `api/` - 10 archivos
6. `core/` - 10 archivos

**Por cada módulo:**
```bash
# 1. Buscar todos los usos
grep -r "datetime.utcnow()" src/acolyte/MODULE/

# 2. Actualizar imports
sed -i 's/from datetime import datetime/from datetime import datetime\nfrom acolyte.core.utils.datetime_utils import utc_now/' FILE.py

# 3. Reemplazar usos
sed -i 's/datetime.utcnow()/utc_now()/g' FILE.py

# 4. Ejecutar tests del módulo
pytest tests/MODULE/ -v
```

### Fase 3: Testing Global (30 min)
1. Ejecutar suite completa de tests
2. Verificar que no hay regresiones
3. Buscar usos perdidos: `grep -r "datetime.now()" src/`

### Fase 4: Documentación (30 min)
1. Actualizar CONTRIBUTING.md con nuevas guidelines
2. Agregar ejemplos en docs/
3. Actualizar este documento marcando como IMPLEMENTADO

## Consideraciones Especiales

### 1. Compatibilidad con SQLite

SQLite espera ISO format. Asegurar que todos los campos datetime usen:
```python
timestamp = utc_now_iso()  # Para guardar
dt = parse_iso_datetime(row['timestamp'])  # Para leer
```

### 2. Compatibilidad con Weaviate

Weaviate también espera ISO format con timezone:
```python
metadata = {
    "last_modified": format_iso(utc_now())
}
```

### 3. Testing

Con la centralización, los tests pueden mockear tiempo:
```python
def test_fatigue_calculation():
    # Arrange
    test_time = datetime(2024, 1, 1, 12, 0, 0)
    set_mock_time(test_time)
    
    # Act
    fatigue = monitor.calculate_fatigue()
    
    # Assert
    assert fatigue['timestamp'] == test_time
    
    # Cleanup
    set_mock_time(None)
```

### 4. Performance

Las funciones helper tienen overhead mínimo:
- `utc_now()`: ~0.1 microsegundos
- `parse_iso_datetime()`: ~2 microsegundos
- `format_iso()`: ~1 microsegundo

## Beneficios Esperados

1. **Consistencia**: Un solo lugar para cambiar comportamiento
2. **Testabilidad**: Fácil mockear tiempo para tests
3. **Mantenibilidad**: Cambios futuros en un solo lugar
4. **Claridad**: Funciones con nombres descriptivos
5. **Timezone Safety**: Garantiza UTC en todo el sistema

## Métricas de Éxito

- [ ] 0 usos directos de `datetime.utcnow()` fuera de utils
- [ ] 100% tests pasando después de migración
- [ ] Reducción de 200+ líneas de código repetido
- [ ] Capacidad de mockear tiempo en tests

## Referencias

- [PEP 495](https://www.python.org/dev/peps/pep-0495/) - Local Time Disambiguation
- [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) - Date/time format
- SQLite [datetime functions](https://www.sqlite.org/lang_datefunc.html)
