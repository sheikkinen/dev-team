# Architecture Planning: Incremental Design

**Current Architecture:** {CURRENT_ARCHITECTURE}
**Research Context:** {RESEARCH}  
**User Story:** {USER_STORY}

## Planning Objective
Revise architecture incrementally to support the current user story while keeping design simple.

## Output Format
Return JSON with architecture components and C4 model context:

```json
{
  "components": [
    {
      "name": "ComponentName",
      "purpose": "Brief description",
      "interfaces": ["method1", "method2"],
      "dependencies": ["OtherComponent"],
      "c4_level": "container|component",
      "c4_type": "service|ui|database|external"
    }
  ],
  "data_flow": [
    {
      "from": "ComponentA",
      "to": "ComponentB", 
      "data": "description",
      "protocol": "method_call|event|api|data_store"
    }
  ],
  "c4_context": {
    "system_boundary": "Game system boundaries",
    "external_dependencies": ["external systems if any"],
    "containers": ["main application containers"]
  },
  "changes": "Summary of architectural changes for this story"
}
```

## Requirements
- Keep architecture minimal and focused
- Only add components needed for current story
- Reuse existing components when possible
- Simple, clear interfaces
- Follow C4 model principles (Context, Containers, Components, Code)
- Identify system boundaries and external dependencies
- Avoid over-engineering