# Product Backlog: User Stories Splitting

**Research Input:** {RESEARCH}

## Split Objective
Split the research into focused user stories and core components.

## Output Format
Return JSON array with user stories:

```json
[
  {
    "id": "story_1",
    "title": "Brief story title",
    "description": "As a [user] I want [goal] so that [benefit]",
    "priority": "high|medium|low",
    "components": ["component1", "component2"]
  }
]
```

## Requirements
- 3-6 user stories maximum
- Each story should be implementable independently
- Focus on core functionality first
- Keep components simple and focused
- No technical implementation details