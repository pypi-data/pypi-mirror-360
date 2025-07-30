# 🏗️ Dream Module Architecture

## Design Philosophy

Dream is ACOLYTE's deep analysis system, analogous to "Deep Search" in modern AIs but specialized for code analysis. It performs exhaustive project analysis during extended windows, always requiring explicit user permission.

## Architectural Decisions

### Decision #1: Permission-Based Activation
**Why**: User control is paramount. Deep analysis uses significant resources.
**Implementation**: Every analysis requires explicit approval via `request_analysis()` → `start_analysis(approved=True)`.

### Decision #2: Two Operational Modes
**Why**: Resilience and flexibility for different deployment scenarios.
**Implementation**: 
- FULL MODE: With Weaviate (complete search capabilities)
- DEGRADED MODE: Without Weaviate (limited but functional)

### Decision #3: State Machine Design
**Why**: Predictable flow, resumable analysis, clear progress tracking.
**Implementation**: 6 states with defined transitions via `DreamStateManager`.

### Decision #4: Fatigue as Technical Metric
**Why**: Objective measurement of when reorganization benefits search performance.
**Implementation**: Git-based metrics (instability, volatility, conflicts) not "AI tiredness".

### Decision #5: Sliding Window for 32k Models
**Why**: Enable deep analysis even on smaller context windows.
**Implementation**: 28k new code + 1.5k preserved context per cycle.

### Decision #6: Configurable Analysis Prompts
**Why**: Allow customization without code changes.
**Implementation**: Markdown files in `prompts/` directory, loadable at runtime.

### Decision #7: Dual Storage for Insights
**Why**: Database for queries, markdown for human review.
**Implementation**: `InsightWriter` manages both SQLite and `.acolyte-dreams/` files.

### Decision #8: Factory Pattern for Weaviate
**Why**: Clean dependency injection while maintaining flexibility.
**Implementation**: `create_dream_orchestrator(weaviate_client)` for full capabilities.

## Component Architecture

```
DreamOrchestrator (Main Coordinator)
    ├── DreamStateManager (State Machine)
    ├── FatigueMonitor (Metrics Calculator)
    ├── DreamAnalyzer (Analysis Engine)
    └── InsightWriter (Persistence Layer)
```

### DreamOrchestrator
- Central coordination point
- Manages analysis lifecycle
- Handles permissions and triggers
- Background task management

### DreamStateManager
- SQLite-backed state persistence
- Thread-safe state transitions
- Phase duration management
- Abort capability

### FatigueMonitor
- Git metadata analysis
- Component-based scoring (0-10)
- Weaviate search for file activity
- Graceful degradation without search

### DreamAnalyzer
- Multi-phase analysis (initial → deep)
- Prompt management and loading
- Window management for context
- Capability transparency

### InsightWriter
- Dual persistence strategy
- Secure filename sanitization
- Compression for large data
- Markdown generation

## Data Flow

```
1. ChatService detects need → request_analysis()
2. User approves → start_analysis()  
3. Background task → _run_analysis_cycle()
4. State transitions: DROWSY → DREAMING → REM → DEEP_SLEEP → WAKING
5. Insights → Database + Markdown files
6. Fatigue reduced → Back to MONITORING
```

## Error Handling Strategy

- Each component handles its own errors
- Conservative defaults on failure
- Always return to MONITORING state
- Detailed error logging

## Performance Considerations

- 5-minute analysis cycles
- Batch file enrichment (95% improvement)
- Single search vs N queries pattern
- Async/await throughout

## Security Measures

- Path traversal prevention in InsightWriter
- No automatic activation
- Input sanitization for filenames
- Safe JSON parsing with error handling

## Extension Points

- Custom prompts via configuration
- Additional analysis types
- New fatigue components
- Alternative storage backends
