---
name: spec-driven-workflow
description: Structured development workflow - requirements, design, tasks, implementation
triggers:
  - spec-driven
  - spec workflow
  - create spec
  - requirements document
  - design document
---

# Spec-Driven Development Workflow

This skill teaches a structured approach to feature development, transforming rough ideas into well-documented, implementable specifications.

## Overview

Instead of jumping straight to code, follow this workflow:

```
Idea → Requirements → Design → Tasks → Implementation
```

Each phase produces documented artifacts that serve as the source of truth.

## Commands

### /spec-start <feature-name>

Start a new spec-driven workflow for a feature:

1. Create `.specs/{feature-name}/` directory
2. Create `requirements.md` template
3. Begin requirements gathering

### /spec-requirements

Generate or refine requirements document with:
- User stories (As a..., I want..., So that...)
- Acceptance criteria
- Edge cases and error scenarios
- Non-functional requirements

### /spec-design

Generate technical design document with:
- Architecture decisions
- Component breakdown
- Data models
- API contracts
- Testing strategy

### /spec-tasks

Break design into discrete, implementable tasks with:
- Clear task descriptions
- Dependencies between tasks
- Mapping to requirements
- Success criteria per task

### /spec-implement

Execute the next uncompleted task:
1. Read requirements and design
2. Implement minimal code for task
3. Verify against acceptance criteria
4. Mark task complete

## Workflow Phases

### Phase 1: Requirements Gathering

**Output**: `.specs/{feature-name}/requirements.md`

```markdown
# Feature: {Feature Name}

## Introduction
Brief overview of the feature...

## User Stories

### US-1: {Story Title}
**As a** {user type}
**I want to** {action}
**So that** {benefit}

**Acceptance Criteria**:
- WHEN {condition} THEN {expected result}
- IF {condition} THEN {expected result}

## Edge Cases
- {Edge case 1}
- {Edge case 2}

## Non-Functional Requirements
- {Performance requirement}
- {Security requirement}
```

### Phase 2: Design Document

**Output**: `.specs/{feature-name}/design.md`

```markdown
# Design: {Feature Name}

## Overview
Technical approach for implementing...

## Architecture

### Component Diagram
{Mermaid diagram}

## Components

### {Component Name}
- Purpose: {description}
- Interface: {methods/APIs}
- Dependencies: {other components}

## Data Models

### {Model Name}
| Field | Type | Constraints |
|-------|------|-------------|
| id | UUID | Primary key |

## Error Handling
- {Error type}: {Response}

## Testing Strategy
- Unit tests for {scope}
- Integration tests for {scope}
```

### Phase 3: Task List

**Output**: `.specs/{feature-name}/tasks.md`

```markdown
# Tasks: {Feature Name}

## Task List

### 1. {Task Title}
- [ ] {Subtask 1}
- [ ] {Subtask 2}

**Dependencies**: {Task numbers}
**Requirement**: {US-X}
**Tests**: {Test description}

### 2. {Task Title}
...
```

### Phase 4: Implementation

Execute tasks one at a time:
1. Read all spec documents
2. Implement minimal code for current task
3. Write tests to verify acceptance criteria
4. Request review before proceeding

## Rules

### Never Skip Phases

```
❌ Idea → Code
❌ Idea → Tasks → Code
✓  Idea → Requirements → Design → Tasks → Code
```

### Explicit Approval Required

Each phase should be reviewed before proceeding:

| Transition | Review Focus |
|------------|--------------|
| → Requirements | Business alignment, completeness |
| → Design | Technical feasibility, architecture fit |
| → Tasks | Breakdown quality, dependencies |
| → Implementation | Code quality, test coverage |

### Task Granularity

Tasks should be:
- **Discrete**: One clear objective
- **Test-driven**: Has verification criteria
- **Traceable**: Links to requirement
- **Manageable**: Completable in reasonable time
- **Ordered**: Dependencies respected

## Directory Structure

```
project/
└── .specs/
    ├── user-authentication/
    │   ├── requirements.md
    │   ├── design.md
    │   └── tasks.md
    └── payment-processing/
        ├── requirements.md
        ├── design.md
        └── tasks.md
```

## Tips

1. **Start with "why"** - Requirements should explain the business need
2. **Include diagrams** - Use Mermaid for visual documentation
3. **Document decisions** - Record alternatives considered and why rejected
4. **Keep specs current** - Update when implementation diverges
5. **Review before code** - Catch issues early in requirements/design

## Note on Enforcement

Unlike Kiro's enforced workflow, this skill provides **advisory guidance**. The agent will follow this workflow when asked but won't automatically enforce phase gates. For best results:

- Explicitly request each phase
- Review outputs before proceeding
- Reference spec files during implementation
