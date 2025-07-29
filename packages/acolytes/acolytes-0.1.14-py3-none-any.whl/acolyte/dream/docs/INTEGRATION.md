# 🔗 Dream Module Integration

## Module Dependencies

### What Dream Uses

```
Core ──────────► Services ──────────► Dream
  │                  │                   │
  ├─ logging         ├─ EnrichmentService └─ All components
  ├─ id_generator    ├─ OllamaClient
  ├─ database        └─ (ChatService creates Dream)
  ├─ config
  └─ exceptions

RAG ───────────► Dream (when available)
  │                │
  ├─ HybridSearch  └─ FatigueMonitor, DreamAnalyzer
  └─ ChunkingService
```

### Who Uses Dream

```
Dream ◄────────── ChatService ◄────────── API
                      │                     │
                      ├─ create_dream_      ├─ /api/dream/*
                      │  orchestrator()     └─ WebSocket (future)
                      └─ Fatigue checks
```

## Service Integration

### ChatService Integration

```python
# ChatService creates Dream with full capabilities
class ChatService:
    def __init__(self):
        # Create weaviate client
        self.weaviate_client = weaviate.Client(...)
        
        # Use factory for Dream with dependencies
        self.dream_orchestrator = create_dream_orchestrator(
            weaviate_client=self.weaviate_client
        )
    
    async def process_message(self, message: str):
        # Check if analysis request
        if self._is_analysis_request(message):
            return await self._handle_analysis_request(message)
        
        # Normal processing
        response = await self._generate_response(message)
        
        # Check fatigue if code-related
        if self._is_code_query(message):
            await self._check_and_suggest_dream(message, response)
```

### API Integration

```python
# API endpoints use Dream directly
from acolyte.dream import DreamOrchestrator

# Note: API creates without weaviate (degraded mode)
dream = DreamOrchestrator()

@app.get("/api/dream/status")
async def get_dream_status():
    state_info = await dream.state_manager.get_state_info()
    fatigue_info = await dream.check_fatigue_level()
    
    return {
        "state": state_info["current_state"],
        "fatigue": fatigue_info,
        "capabilities": "limited"  # No weaviate
    }
```

## Component Dependencies

### DreamOrchestrator
- **Required**: StateManager, InsightWriter
- **Optional**: FatigueMonitor, DreamAnalyzer (need weaviate)

### FatigueMonitor
- **Required**: EnrichmentService
- **Optional**: HybridSearch (degraded without)

### DreamAnalyzer  
- **Required**: OllamaClient
- **Optional**: HybridSearch, EmbeddingService, NeuralGraph

### InsightWriter
- **Required**: DatabaseManager
- **Optional**: None

## Database Integration

### Tables Used

```sql
-- dream_state (singleton)
CREATE TABLE dream_state (
    id INTEGER PRIMARY KEY,
    current_state TEXT,
    session_id TEXT,
    last_optimization TIMESTAMP,
    fatigue_level REAL,
    optimization_count INTEGER
);

-- dream_insights  
CREATE TABLE dream_insights (
    id TEXT PRIMARY KEY,
    session_id TEXT,
    insight_type TEXT,
    title TEXT,
    description TEXT,
    confidence REAL,
    impact TEXT,
    entities_involved BLOB,  -- Compressed JSON
    code_references BLOB,    -- Compressed JSON
    created_at TIMESTAMP
);
```

## Configuration Integration

Dream reads from `.acolyte`:

```yaml
dream:
  # Used by orchestrator
  fatigue_threshold: 7.5
  emergency_threshold: 9.5
  cycle_duration_minutes: 5
  
  # Used by analyzer
  prompts_directory: null
  analysis:
    window_sizes:
      "32k": {...}
  
  # Used by insight_writer
  dream_folder_name: ".acolyte-dreams"
```

## Event Flow

### Analysis Request from User

```
1. User → ChatService: "Analyze security"
2. ChatService → DreamOrchestrator.request_analysis()
3. DreamOrchestrator → Returns permission request
4. ChatService → User: "May I take 5 minutes?"
5. User → ChatService: "Yes"
6. ChatService → DreamOrchestrator.start_analysis()
7. DreamOrchestrator → Background task
```

### Fatigue Suggestion Flow

```
1. User → ChatService: "Why is login slow?"
2. ChatService → Generates response
3. ChatService → DreamOrchestrator.check_fatigue_level()
4. If high + code query:
   - ChatService adds suggestion to response
5. User sees: "Answer + fatigue suggestion"
```

## Error Propagation

```python
# Dream handles errors gracefully
try:
    await dream.start_analysis(...)
except ValidationError:
    # User-facing error
    return {"error": "Invalid request"}
except DatabaseError:
    # Infrastructure error
    return {"error": "Service unavailable"}
```

## Performance Contracts

- Fatigue check: <100ms
- State check: <10ms  
- Analysis request: <50ms
- Full analysis: 5 minutes

## Capability Modes

### FULL Mode (with Weaviate)
```python
# ChatService creates with weaviate
dream = create_dream_orchestrator(weaviate_client)
# All features work
```

### DEGRADED Mode (without Weaviate)
```python
# API creates without weaviate
dream = DreamOrchestrator()
# Limited features, safe defaults
```

## Extension Points

### Custom Analysis Types
1. Add prompt to `dream/prompts/`
2. Configure in `.acolyte`
3. Add to analyzer priorities

### Custom Fatigue Components
1. Extend FatigueMonitor
2. Add calculation method
3. Include in total calculation

### Additional Storage
1. Implement writer interface
2. Add to InsightWriter
3. Configure output location

## Integration Checklist

- [ ] ChatService uses factory pattern
- [ ] Weaviate client passed to Dream
- [ ] Database tables created
- [ ] Configuration in .acolyte
- [ ] API endpoints connected
- [ ] Error handling consistent
- [ ] Tests mock dependencies

## Migration Considerations

**Database Impact**: HIGH
- Both Dream tables need migration
- Compressed BLOB handling
- State persistence critical
