# 📊 Feature: Sistema de Cálculo de Fatiga Mejorado

## Estado Actual

El `FatigueMonitor` actualmente retorna valores conservadores cuando hay errores:

```python
async def calculate_fatigue(self) -> Dict[str, Any]:
    try:
        # ... cálculo normal ...
    except Exception as e:
        logger.error("Failed to calculate fatigue", error=str(e))
        # Return moderate defaults (5.0 = middle of 0-10 scale)
        return {
            "total": 5.0,  # Middle value: neither healthy nor critical
            "components": {},
            "explanation": "Unable to calculate current fatigue level",
            "triggers": [],
            "error": str(e),
        }
```

### Limitaciones Actuales

1. **Falta de contexto**: No distingue entre tipos de errores
2. **Sin persistencia**: No recuerda última fatiga conocida
3. **Sin degradación gradual**: Salta directamente a 5.0
4. **Poca transparencia**: Usuario no sabe qué falló exactamente

## Propuesta de Solución

### 1. Sistema de Fatiga con Estado y Fallbacks Inteligentes

```python
# dream/fatigue_calculator.py
"""
Enhanced fatigue calculation with intelligent fallbacks and state persistence.
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
import json

from acolyte.core.logging import logger
from acolyte.core.database import get_db_manager, FetchType


class FatigueDataSource(Enum):
    """Sources of fatigue data in order of preference."""
    LIVE_METRICS = "live_metrics"          # Real-time from Git/Weaviate
    CACHED_RECENT = "cached_recent"        # Recent cached values (<1 hour)
    CACHED_OLD = "cached_old"              # Older cached values (<24 hours)
    HISTORICAL_AVERAGE = "historical_avg"   # Average from history
    ESTIMATED = "estimated"                 # Estimation based on time
    DEFAULT = "default"                     # Conservative default


@dataclass
class FatigueComponent:
    """Individual fatigue component with metadata."""
    name: str
    value: float
    weight: float
    source: FatigueDataSource
    confidence: float  # 0.0-1.0 confidence in this value
    last_updated: datetime
    error: Optional[str] = None
    
    @property
    def weighted_value(self) -> float:
        """Get weighted value considering confidence."""
        return self.value * self.weight * self.confidence


@dataclass
class FatigueState:
    """Complete fatigue state with metadata."""
    total: float
    components: Dict[str, FatigueComponent]
    source_quality: FatigueDataSource
    confidence: float
    explanation: str
    triggers: List[Dict[str, Any]]
    calculated_at: datetime
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "total": round(self.total, 1),
            "components": {
                name: {
                    "value": round(comp.value, 2),
                    "weight": comp.weight,
                    "source": comp.source.value,
                    "confidence": comp.confidence
                }
                for name, comp in self.components.items()
            },
            "source_quality": self.source_quality.value,
            "confidence": round(self.confidence, 2),
            "explanation": self.explanation,
            "triggers": self.triggers,
            "is_high": self.total > 7.5,
            "is_emergency": self.total > 9.5,
            "calculated_at": self.calculated_at.isoformat(),
            "metadata": self.metadata
        }


class FatigueCache:
    """Persistent cache for fatigue values."""
    
    def __init__(self):
        self.db = get_db_manager()
        self._ensure_cache_table()
    
    def _ensure_cache_table(self):
        """Ensure fatigue_cache table exists."""
        self.db.execute_sync("""
            CREATE TABLE IF NOT EXISTS fatigue_cache (
                component TEXT PRIMARY KEY,
                value REAL NOT NULL,
                confidence REAL NOT NULL,
                source TEXT NOT NULL,
                updated_at DATETIME NOT NULL,
                metadata TEXT
            )
        """)
    
    async def get(self, component: str) -> Optional[FatigueComponent]:
        """Get cached component value."""
        result = await self.db.execute_async(
            "SELECT * FROM fatigue_cache WHERE component = ?",
            (component,),
            FetchType.ONE
        )
        
        if result.data:
            return FatigueComponent(
                name=component,
                value=result.data["value"],
                weight=1.0,  # Weight set by calculator
                source=FatigueDataSource(result.data["source"]),
                confidence=result.data["confidence"],
                last_updated=datetime.fromisoformat(result.data["updated_at"])
            )
        return None
    
    async def set(self, component: FatigueComponent):
        """Cache component value."""
        await self.db.execute_async("""
            INSERT OR REPLACE INTO fatigue_cache 
            (component, value, confidence, source, updated_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            component.name,
            component.value,
            component.confidence,
            component.source.value,
            component.last_updated.isoformat(),
            json.dumps({"error": component.error} if component.error else {})
        ))
    
    async def get_historical_average(self, component: str) -> float:
        """Get historical average for component."""
        # Get from dream_state metrics history
        result = await self.db.execute_async(
            "SELECT metrics FROM dream_state WHERE id = 1",
            (),
            FetchType.ONE
        )
        
        if result.data:
            metrics = json.loads(result.data.get("metrics", "{}"))
            history = metrics.get("fatigue_history", {})
            
            # Calculate average from history
            if component in history and history[component]:
                values = history[component][-10:]  # Last 10 values
                return sum(values) / len(values)
        
        # Default averages based on component
        defaults = {
            "time_factor": 0.5,
            "file_instability": 0.3,
            "recent_activity": 0.4,
            "code_volatility": 0.2,
            "architectural_changes": 0.1
        }
        return defaults.get(component, 0.3)


class EnhancedFatigueCalculator:
    """Enhanced fatigue calculation with multiple fallback strategies."""
    
    def __init__(self, monitor):
        self.monitor = monitor  # Original FatigueMonitor
        self.cache = FatigueCache()
        self.config = monitor.config
        
        # Component weights
        self.weights = {
            "time_factor": 0.1,          # 10% weight
            "file_instability": 0.3,     # 30% weight
            "recent_activity": 0.3,      # 30% weight
            "code_volatility": 0.2,      # 20% weight
            "architectural_changes": 0.1  # 10% weight
        }
    
    async def calculate(self) -> FatigueState:
        """Calculate fatigue with intelligent fallbacks."""
        components = {}
        overall_confidence = 1.0
        worst_source = FatigueDataSource.LIVE_METRICS
        
        # Try to calculate each component
        for comp_name, weight in self.weights.items():
            component = await self._calculate_component(comp_name, weight)
            components[comp_name] = component
            
            # Track overall quality
            overall_confidence *= component.confidence
            if component.source.value > worst_source.value:
                worst_source = component.source
        
        # Calculate total with confidence weighting
        total = sum(comp.weighted_value for comp in components.values())
        total = min(total, 10.0)  # Cap at 10
        
        # Adjust confidence
        overall_confidence = overall_confidence ** (1/len(components))
        
        # Generate explanation
        explanation = self._generate_explanation(components, total, worst_source)
        
        # Check triggers
        triggers = await self._check_triggers_safe(components)
        
        # Cache current state
        await self._cache_state(components)
        
        return FatigueState(
            total=total,
            components=components,
            source_quality=worst_source,
            confidence=overall_confidence,
            explanation=explanation,
            triggers=triggers,
            calculated_at=datetime.utcnow(),
            metadata={
                "has_weaviate": self.monitor.search is not None,
                "has_git": self.monitor.has_git
            }
        )
    
    async def _calculate_component(
        self, 
        name: str, 
        weight: float
    ) -> FatigueComponent:
        """Calculate single component with fallbacks."""
        # 1. Try live calculation
        try:
            method = getattr(self.monitor, f"_calculate_{name}")
            value = await method()
            
            return FatigueComponent(
                name=name,
                value=value,
                weight=weight,
                source=FatigueDataSource.LIVE_METRICS,
                confidence=1.0,
                last_updated=datetime.utcnow()
            )
        except Exception as e:
            logger.debug(f"Live calculation failed for {name}: {e}")
        
        # 2. Try recent cache (<1 hour)
        cached = await self.cache.get(name)
        if cached:
            age = datetime.utcnow() - cached.last_updated
            if age < timedelta(hours=1):
                cached.weight = weight
                cached.source = FatigueDataSource.CACHED_RECENT
                cached.confidence = 0.9
                return cached
            elif age < timedelta(hours=24):
                cached.weight = weight
                cached.source = FatigueDataSource.CACHED_OLD
                cached.confidence = 0.7
                return cached
        
        # 3. Try historical average
        try:
            avg_value = await self.cache.get_historical_average(name)
            return FatigueComponent(
                name=name,
                value=avg_value,
                weight=weight,
                source=FatigueDataSource.HISTORICAL_AVERAGE,
                confidence=0.5,
                last_updated=datetime.utcnow()
            )
        except Exception as e:
            logger.debug(f"Historical average failed for {name}: {e}")
        
        # 4. Use estimation
        estimated_value = self._estimate_component(name)
        return FatigueComponent(
            name=name,
            value=estimated_value,
            weight=weight,
            source=FatigueDataSource.ESTIMATED,
            confidence=0.3,
            last_updated=datetime.utcnow()
        )
    
    def _estimate_component(self, name: str) -> float:
        """Estimate component value based on patterns."""
        # Time-based estimation
        now = datetime.utcnow()
        hour = now.hour
        day_of_week = now.weekday()
        
        # Business hours (Mon-Fri, 9-17)
        is_business_hours = day_of_week < 5 and 9 <= hour <= 17
        
        estimations = {
            "time_factor": 0.5,  # Neutral estimate
            "file_instability": 0.4 if is_business_hours else 0.2,
            "recent_activity": 0.5 if is_business_hours else 0.1,
            "code_volatility": 0.3 if is_business_hours else 0.1,
            "architectural_changes": 0.1  # Rare event
        }
        
        return estimations.get(name, 0.3)
    
    def _generate_explanation(
        self,
        components: Dict[str, FatigueComponent],
        total: float,
        source: FatigueDataSource
    ) -> str:
        """Generate human-readable explanation."""
        # Base explanation
        level_desc = FatigueLevel.get_description(total)
        
        # Add source quality warning if needed
        if source != FatigueDataSource.LIVE_METRICS:
            quality_warnings = {
                FatigueDataSource.CACHED_RECENT: "using recent cached data",
                FatigueDataSource.CACHED_OLD: "using older cached data",
                FatigueDataSource.HISTORICAL_AVERAGE: "using historical averages",
                FatigueDataSource.ESTIMATED: "using estimates",
                FatigueDataSource.DEFAULT: "using default values"
            }
            level_desc += f" ({quality_warnings.get(source, 'limited data')})"
        
        # Add component highlights
        high_components = [
            name for name, comp in components.items()
            if comp.value * comp.weight > 1.0
        ]
        
        if high_components:
            level_desc += f". High activity in: {', '.join(high_components)}"
        
        return level_desc
    
    async def _check_triggers_safe(
        self,
        components: Dict[str, FatigueComponent]
    ) -> List[Dict[str, Any]]:
        """Check triggers with fallback to component data."""
        try:
            # Try original trigger detection
            return await self.monitor._check_fatigue_triggers()
        except Exception as e:
            logger.debug(f"Trigger check failed: {e}")
            
            # Fallback: Generate triggers from components
            triggers = []
            
            # High instability trigger
            if components.get("file_instability", FatigueComponent("", 0, 0, FatigueDataSource.DEFAULT, 0, datetime.utcnow())).value > 0.7:
                triggers.append({
                    "type": "high_instability",
                    "severity": "medium",
                    "message": "Files showing high instability",
                    "confidence": components["file_instability"].confidence
                })
            
            # High activity trigger
            if components.get("recent_activity", FatigueComponent("", 0, 0, FatigueDataSource.DEFAULT, 0, datetime.utcnow())).value > 0.8:
                triggers.append({
                    "type": "high_activity",
                    "severity": "medium",
                    "message": "Unusually high code activity",
                    "confidence": components["recent_activity"].confidence
                })
            
            return triggers
    
    async def _cache_state(self, components: Dict[str, FatigueComponent]):
        """Cache current component states."""
        for component in components.values():
            await self.cache.set(component)
        
        # Update historical data
        try:
            result = await self.monitor.db.execute_async(
                "SELECT metrics FROM dream_state WHERE id = 1",
                (),
                FetchType.ONE
            )
            
            if result.data:
                metrics = json.loads(result.data.get("metrics", "{}"))
                history = metrics.get("fatigue_history", {})
                
                # Add current values to history
                for name, comp in components.items():
                    if name not in history:
                        history[name] = []
                    history[name].append(comp.value)
                    # Keep last 100 values
                    history[name] = history[name][-100:]
                
                metrics["fatigue_history"] = history
                
                await self.monitor.db.execute_async(
                    "UPDATE dream_state SET metrics = ? WHERE id = 1",
                    (json.dumps(metrics),)
                )
        except Exception as e:
            logger.debug(f"Failed to update history: {e}")
```

### 2. Integración con FatigueMonitor Actual

```python
# En fatigue_monitor.py
class FatigueMonitor:
    def __init__(self, weaviate_client):
        # ... existing init ...
        
        # Initialize enhanced calculator
        self._enhanced_calculator = None
    
    async def calculate_fatigue(self) -> Dict[str, Any]:
        """Calculate current fatigue level using enhanced system."""
        # Use enhanced calculator if available
        if self._enhanced_calculator is None:
            try:
                from .fatigue_calculator import EnhancedFatigueCalculator
                self._enhanced_calculator = EnhancedFatigueCalculator(self)
            except ImportError:
                pass
        
        if self._enhanced_calculator:
            try:
                state = await self._enhanced_calculator.calculate()
                return state.to_dict()
            except Exception as e:
                logger.error(f"Enhanced calculation failed: {e}")
        
        # Fallback to original implementation
        return await self._original_calculate_fatigue()
```

### 3. UI/API Enhancements

```python
# dream/fatigue_dashboard.py
"""
Dashboard data generator for fatigue visualization.
"""

class FatigueDashboard:
    """Generate dashboard data for fatigue monitoring."""
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive fatigue dashboard data."""
        monitor = FatigueMonitor(self.weaviate_client)
        
        # Current state
        current = await monitor.calculate_fatigue()
        
        # Historical data
        history = await monitor.get_fatigue_history(days=7)
        
        # Component breakdown over time
        component_history = await self._get_component_history()
        
        # Predictions
        predictions = self._predict_fatigue_trend(history)
        
        return {
            "current": current,
            "history": {
                "timeline": [
                    {
                        "timestamp": ts.isoformat(),
                        "value": value,
                        "source": "calculated"
                    }
                    for ts, value in history
                ],
                "components": component_history
            },
            "predictions": predictions,
            "recommendations": self._generate_recommendations(current, predictions),
            "data_quality": {
                "source": current.get("source_quality", "unknown"),
                "confidence": current.get("confidence", 0),
                "missing_sources": self._identify_missing_sources()
            }
        }
```

## Plan de Implementación

### Fase 1: Core Infrastructure (2-3 horas)
1. Crear `dream/fatigue_calculator.py`
2. Implementar FatigueCache con tabla SQLite
3. Implementar EnhancedFatigueCalculator
4. Tests unitarios para cada componente

### Fase 2: Integration (1-2 horas)
1. Integrar con FatigueMonitor existente
2. Mantener compatibilidad hacia atrás
3. Tests de integración
4. Verificar API responses

### Fase 3: Enhancement (2 horas)
1. Implementar FatigueDashboard
2. Agregar endpoint `/api/dream/fatigue/detailed`
3. Documentar nueva funcionalidad

## Consideraciones Especiales

### 1. Migración de Datos

Script para migrar datos existentes:
```sql
-- Create fatigue_cache from existing data
INSERT INTO fatigue_cache (component, value, confidence, source, updated_at)
SELECT 
    'historical_baseline' as component,
    fatigue_level as value,
    0.5 as confidence,
    'historical_avg' as source,
    updated_at
FROM dream_state
WHERE fatigue_level IS NOT NULL;
```

### 2. Performance

- Cache en memoria para lecturas frecuentes
- Batch updates cada 5 minutos
- Índices en fatigue_cache para queries rápidas

### 3. Configuración

Nueva configuración en `.acolyte`:
```yaml
dream:
  fatigue:
    cache_ttl_hours: 24
    history_retention_days: 30
    confidence_thresholds:
      high: 0.8
      medium: 0.5
      low: 0.3
    estimation_strategy: "time_based"  # or "historical"
```

## Beneficios Esperados

1. **Resiliencia**: Sistema funciona incluso sin Weaviate/Git
2. **Transparencia**: Usuario ve calidad de datos
3. **Predictibilidad**: Sin saltos bruscos en valores
4. **Debugging**: Trazabilidad de cada componente

## Métricas de Éxito

- [ ] 100% uptime de cálculo de fatiga
- [ ] <100ms latencia con cache
- [ ] 95%+ precisión vs cálculo completo
- [ ] UI muestra claramente fuente de datos

## Ejemplos de Mejora

### Antes
```json
{
  "total": 5.0,
  "components": {},
  "explanation": "Unable to calculate current fatigue level",
  "error": "Connection timeout"
}
```

### Después
```json
{
  "total": 6.8,
  "components": {
    "time_factor": {
      "value": 0.7,
      "source": "live_metrics",
      "confidence": 1.0
    },
    "file_instability": {
      "value": 0.5,
      "source": "cached_recent",
      "confidence": 0.9
    },
    "recent_activity": {
      "value": 0.4,
      "source": "historical_avg",
      "confidence": 0.5
    }
  },
  "source_quality": "cached_recent",
  "confidence": 0.78,
  "explanation": "Moderate fatigue level (using mixed data sources). High activity in: time_factor",
  "data_quality_warning": "Some metrics using cached data due to Weaviate unavailability"
}
```

## Roadmap Futuro

1. **Machine Learning**: Predecir fatiga futura basado en patrones
2. **Alertas Proactivas**: Notificar antes de alcanzar umbral
3. **Auto-ajuste**: Adaptar pesos según proyecto
4. **Visualización**: Gráficos en tiempo real

## Referencias

- [Time Series Forecasting](https://facebook.github.io/prophet/)
- [Graceful Degradation Patterns](https://martinfowler.com/articles/patterns-of-distributed-systems/graceful-degradation.html)
- [Confidence Intervals in ML](https://scikit-learn.org/stable/modules/calibration.html)
