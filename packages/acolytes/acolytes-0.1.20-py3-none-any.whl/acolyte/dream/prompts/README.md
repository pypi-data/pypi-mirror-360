# Dream Analysis Prompts

This directory contains the specialized prompts used by the Dream analyzer for different types of code analysis.

## Prompt Files

### bug_detection.md
Focuses on finding bugs and potential issues:
- Null pointer exceptions
- Race conditions
- Memory leaks
- Validation gaps
- Error handling issues

### security_analysis.md
Analyzes code for security vulnerabilities:
- Input validation issues
- SQL injection risks
- Authentication/authorization flaws
- Data exposure
- Insecure configurations

### performance_analysis.md
Identifies performance bottlenecks:
- N+1 queries
- Inefficient algorithms
- Missing caching opportunities
- Redundant computations
- Memory usage patterns

### architecture_analysis.md
Evaluates code architecture and design:
- Coupling and cohesion
- Dependency issues
- Missing abstractions
- Code organization
- Pattern violations

### pattern_detection.md
Detects code patterns and anti-patterns:
- Repeated code patterns
- Common anti-patterns
- Refactoring opportunities
- Best practice violations

## Customization

These prompts can be customized by:
1. Editing the markdown files directly
2. Creating custom prompt directories in `.acolyte` config
3. Overriding specific prompts via configuration

## Format Variables

All prompts support these variables:
- `{code}` - The code being analyzed
- `{context}` - Previous analysis context (for sliding window)

## JSON Output

All prompts request JSON output for consistent parsing and processing.
