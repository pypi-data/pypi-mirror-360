# 📚 Dream Module API Reference

## Core Classes

### DreamOrchestrator

Main coordinator for the Dream analysis system.

```python
class DreamOrchestrator:
    def __init__(self, weaviate_client: Optional[Any] = None) -> None
    
    async def check_fatigue_level(self) -> Dict[str, Any]
    """Check current fatigue level without suggesting."""
    
    async def request_analysis(
        self,
        trigger: DreamTrigger,
        focus_areas: Optional[List[str]] = None,
        user_query: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]
    """Request permission to start analysis."""
    
    async def start_analysis(
        self,
        request_id: str,
        approved: bool,
        focus_areas: Optional[List[str]] = None,
        priorities: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]
    """Start analysis after user approval."""
    
    async def get_recent_insights(
        self, 
        limit: int = 10, 
        insight_type: Optional[str] = None
    ) -> List[Dict[str, Any]]
    """Get recent insights from database."""
    
    def generate_suggestion_message(
        self, 
        fatigue_level: float, 
        is_emergency: bool
    ) -> str
    """Generate suggestion message for user."""
```

### DreamStateManager

Manages analysis state transitions.

```python
class DreamStateManager:
    def __init__(self) -> None
    
    async def get_current_state(self) -> DreamState
    """Get current Dream state."""
    
    async def transition_to(self, new_state: DreamState) -> None
    """Transition to new state with validation."""
    
    async def get_session_id(self) -> Optional[str]
    """Get current session ID."""
    
    async def set_session_id(self, session_id: str) -> None
    """Set session ID for current analysis."""
    
    async def abort_analysis(self) -> None
    """Abort current analysis and return to MONITORING."""
    
    async def get_state_info(self) -> Dict[str, Any]
    """Get detailed state information."""
    
    async def get_estimated_completion(self) -> Optional[str]
    """Get estimated completion time."""
    
    async def get_last_optimization_time(self) -> Optional[str]
    """Get last optimization timestamp."""
```

### FatigueMonitor

Calculates code fatigue based on Git metrics.

```python
class FatigueMonitor:
    def __init__(self, weaviate_client: Optional[Any] = None) -> None
    
    async def calculate_fatigue(self) -> Dict[str, Any]
    """Calculate current fatigue level and components."""
    
    async def reduce_fatigue(self, factor: float = 0.3) -> None
    """Reduce fatigue after optimization."""
    
    async def check_fatigue_triggers(self) -> Dict[str, Any]
    """Check for specific fatigue trigger conditions."""
    
    def explain_fatigue_level(self, level: float) -> str
    """Get human-readable fatigue explanation."""
```

### DreamAnalyzer

Performs the actual code analysis.

```python
class DreamAnalyzer:
    def __init__(
        self, 
        weaviate_client: Optional[Any] = None,
        embeddings_service: Optional[Any] = None,
        graph_service: Optional[Any] = None
    ) -> None
    
    async def explore_codebase(
        self,
        focus_areas: Optional[List[str]] = None,
        context_size: int = 32768
    ) -> Dict[str, Any]
    """Initial exploration phase."""
    
    async def analyze_deeply(
        self,
        initial_findings: Dict[str, Any],
        priorities: Dict[str, float]
    ) -> Dict[str, Any]
    """Deep analysis phase based on initial findings."""
    
    def get_capability_info(self) -> Dict[str, Any]
    """Get information about available capabilities."""
```

### InsightWriter

Persists insights to database and files.

```python
class InsightWriter:
    def __init__(self) -> None
    
    async def write_insights(
        self,
        session_id: str,
        insights: List[Dict[str, Any]],
        focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]
    """Write insights to database and markdown."""
    
    async def write_to_database(
        self,
        session_id: str,
        insights: List[Dict[str, Any]]
    ) -> int
    """Store insights in dream_insights table."""
    
    async def write_to_markdown(
        self,
        session_id: str,
        insights: List[Dict[str, Any]],
        focus_areas: Optional[List[str]] = None
    ) -> str
    """Generate markdown analysis report."""
```

## Enums

### DreamState

Analysis states.

```python
class DreamState(Enum):
    MONITORING = "MONITORING"      # Normal operation
    DROWSY = "DROWSY"              # Preparing for analysis
    DREAMING = "DREAMING"          # Initial exploration
    REM = "REM"                    # Deep analysis
    DEEP_SLEEP = "DEEP_SLEEP"      # Consolidation
    WAKING = "WAKING"              # Preparing results
```

### DreamTrigger

What initiated the analysis.

```python
class DreamTrigger(Enum):
    USER_REQUEST = "USER_REQUEST"              # Explicit user request
    FATIGUE_SUGGESTION = "FATIGUE_SUGGESTION"  # ChatService suggestion
```

### FatigueLevel

Fatigue severity levels.

```python
class FatigueLevel(Enum):
    LOW = "LOW"            # 0-3
    MODERATE = "MODERATE"  # 3-6
    HIGH = "HIGH"          # 6-7.5
    CRITICAL = "CRITICAL"  # 7.5-9.5
    EMERGENCY = "EMERGENCY" # 9.5+
```

### AnalysisCapability

Available analysis capabilities.

```python
class AnalysisCapability(Enum):
    FULL = "FULL"        # All components available
    LIMITED = "LIMITED"  # Some components missing
    MINIMAL = "MINIMAL"  # Basic functionality only
```

## Factory Function

```python
def create_dream_orchestrator(
    weaviate_client: Optional[Any] = None
) -> DreamOrchestrator:
    """
    Create a DreamOrchestrator with dependencies.
    
    Args:
        weaviate_client: Optional Weaviate client for full capabilities
        
    Returns:
        Configured DreamOrchestrator instance
    """
```

## Response Formats

### Fatigue Check Response

```python
{
    "fatigue_level": 7.8,
    "components": {
        "time_factor": 0.8,
        "file_instability": 2.5,
        "recent_activity": 2.0,
        "code_volatility": 1.5,
        "architectural_changes": 1.0
    },
    "is_high": True,
    "is_emergency": False,
    "threshold": 7.5,
    "explanation": "High code activity detected",
    "last_optimization": "2024-01-15T10:30:00Z"
}
```

### Analysis Request Response

```python
{
    "status": "permission_required",
    "request_id": "abc123...",
    "trigger": "USER_REQUEST",
    "message": "To perform a complete analysis...",
    "estimated_duration_minutes": 5,
    "focus_areas": ["security", "performance"],
    "benefits": ["Vulnerability detection", "Attack surface analysis"],
    "context_size": 32768
}
```

### Analysis Start Response

```python
{
    "status": "started",
    "session_id": "def456...",
    "message": "Starting deep analysis...",
    "estimated_completion": "2024-01-15T10:35:00Z",
    "current_state": "DROWSY"
}
```

### Insight Format

```python
{
    "id": "ghi789...",
    "session_id": "def456...",
    "insight_type": "BUG_RISK",
    "title": "Potential SQL Injection",
    "description": "Unsanitized input in query",
    "confidence": 0.85,
    "impact": "HIGH",
    "entities_involved": ["auth.py", "User.query"],
    "code_references": ["auth.py:45-52"],
    "created_at": "2024-01-15T10:34:00Z"
}
```

## Configuration

All via `.acolyte` file:

```yaml
dream:
  # Fatigue thresholds
  fatigue_threshold: 7.5
  emergency_threshold: 9.5
  
  # Analysis settings
  cycle_duration_minutes: 5
  dream_folder_name: ".acolyte-dreams"
  
  # Optional overrides
  prompts_directory: null  # Custom prompts location
  prompts:  # Override specific prompts
    bug_detection: "path/to/custom_bug_prompt.md"
  
  # Analysis configuration
  analysis:
    avg_tokens_per_file: 1000
    usable_context_ratio: 0.9
    chars_per_token: 4
    
    window_sizes:
      "32k":
        strategy: "sliding_window"
        new_code_size: 27000
        preserved_context_size: 1500
      "128k+":
        strategy: "single_pass"
        system_reserve: 5000
    
    default_priorities:
      bugs: 0.3
      security: 0.25
      performance: 0.2
      architecture: 0.15
      patterns: 0.1
```

## Error Handling

All methods may raise:

- `ValidationError`: Invalid parameters or state
- `DatabaseError`: Database operation failures
- `ExternalServiceError`: Weaviate/Ollama issues

Errors are logged and safe defaults returned when possible.
