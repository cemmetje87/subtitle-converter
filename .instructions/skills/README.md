# Cursor Skills

This directory contains dynamic, command-based skills that can be invoked on-demand.

## Available Skills

| Skill                     | Commands                                                                      | Use Case                          |
| ------------------------- | ----------------------------------------------------------------------------- | --------------------------------- |
| **git-workflow**          | `/commit`, `/branch`, `/pr`, `/branch-cleanup`                                | Git workflow automation           |
| **kubernetes**            | `/k8s-deploy`, `/k8s-service`, `/k8s-secure`, `/k8s-pdb`, `/k8s-troubleshoot` | K8s manifests and troubleshooting |
| **powershell-automation** | `/pester-test`, `/gh-workflow`, `/ado-pipeline`, `/ps-analyzer-config`        | PowerShell CI/CD                  |
| **powershell-dev**        | `/ps-function`, `/ps-module`, `/ps-class`, `/ps-enum`                         | PowerShell development            |
| **sre-workflows**         | `/incident-review`, `/proposal`, `/deploy-check`, `/runbook-template`         | SRE operations                    |
| **spec-driven**           | `/spec-start`, `/spec-requirements`, `/spec-design`, `/spec-tasks`            | Structured development            |

## How to Use Skills

### Method 1: Reference the Skill File

```
@.cursor/skills/git-workflow/SKILL.md

I need to commit changes to the auth module with a conventional commit message.
```

### Method 2: Use Trigger Phrases

Skills have defined triggers. Using trigger phrases may auto-load the skill:

```
# git-workflow triggers: "git commit", "conventional commit", "create branch"
Help me create a conventional commit for these changes.

# kubernetes triggers: "k8s deploy", "kubernetes security"
Generate a secure Kubernetes deployment for my API service.
```

### Method 3: Use Commands Directly

Reference the command in your prompt:

```
/commit feat auth - add OAuth2 support

/k8s-deploy my-api --image=myregistry/api:v1.0

/pester-test Get-UserInfo
```

## Skill Structure

Each skill has:

```
.cursor/skills/{skill-name}/
└── SKILL.md           # Skill definition with commands
```

### SKILL.md Format

```markdown
---
name: skill-name
description: What this skill does
triggers:
  - trigger phrase 1
  - trigger phrase 2
---

# Skill Name

Description...

## Commands

### /command-name

Usage and output...
```

## Creating New Skills

1. Create directory: `.cursor/skills/{skill-name}/`
2. Create `SKILL.md` with frontmatter
3. Define commands with clear usage and output examples
4. Add trigger phrases for auto-loading

## Skills vs Rules

| Aspect     | Skills              | Rules                        |
| ---------- | ------------------- | ---------------------------- |
| Loading    | Dynamic, on-demand  | Static, always/pattern-based |
| Purpose    | Workflows, commands | Standards, conventions       |
| Format     | `SKILL.md`          | `.mdc` with globs            |
| Invocation | Commands, triggers  | Auto or `@ruleName`          |

## Tips

1. **Use commands for generation** - Skills are best for producing output
2. **Reference for context** - `@skill-file` to load skill knowledge
3. **Combine with rules** - Rules for standards, skills for workflows
4. **Keep skills focused** - One domain per skill
