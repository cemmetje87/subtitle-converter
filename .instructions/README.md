# Project Instructions

This directory contains configuration files for AI-assisted development workflows using specialized agents, rules, and skills.

## 📁 Directory Structure

```
.instructions/
├── agents/          # Specialized expert personas for specific domains
├── rules/           # Development standards and best practices
│   ├── always/      # Always-applied standards
│   └── auto/        # Language-specific rules (auto-applied by file type)
└── skills/          # Command-based workflows and templates
```

## 🤖 Agents

Agents are specialized expert personas that can be invoked for domain-specific tasks.

### Available Agent Categories

- **AWS**: Cloud architecture, security, reliability, Terraform
- **Azure**: Cloud architecture, security, reliability, Terraform
- **GCP**: Cloud architecture, security, reliability, Terraform
- **Kubernetes**: Container orchestration and management
- **PowerShell**: Automation, modules, security, architecture
- **Windows**: Server administration, automation, reliability
- **M365**: Microsoft Graph API, Entra ID
- **Orchestrator**: Multi-domain task coordination
- **Process**: Workflow automation
- **SRE**: Site reliability engineering
- **Technical Writer**: Documentation and knowledge management

### How to Use Agents

Reference an agent in your prompt:

```
@.instructions/agents/aws/aws-architect.mdc

Design a scalable AWS infrastructure for a web application.
```

See `agents/README.md` for detailed usage.

## 📋 Rules

Rules define development standards and best practices that are automatically or manually applied to your work.

### Always-Applied Rules (`rules/always/`)

These rules are always active:

- **base.mdc**: Fundamental development principles
- **security-best-practices.mdc**: Security standards
- **sre-best-practices.mdc**: SRE and operations standards
- **keep-it-simple.mdc**: KISS, YAGNI, and simplicity principles
- **development-standards.mdc**: General development practices

### Auto-Applied Rules (`rules/auto/`)

These rules activate based on file types:

- **python.mdc**: Python-specific standards (\*.py files)
- **typescript.mdc**: TypeScript standards (\*.ts files)
- **powershell.mdc**: PowerShell standards (\*.ps1 files)
- **terraform.mdc**: Terraform/IaC standards (\*.tf files)

### Project Context Rules

- **system-context.mdc**: Project-specific context (template - customize this!)
- **00-system-overview.mdc**: Multi-agent execution model

## ⚙️ Skills

Skills are command-based workflows that can be invoked on-demand.

### Available Skills

- **git-workflow**: `/commit`, `/branch`, `/pr`, `/branch-cleanup`
- **kubernetes**: `/k8s-deploy`, `/k8s-service`, `/k8s-secure`
- **powershell-automation**: `/pester-test`, `/gh-workflow`, `/ado-pipeline`
- **powershell-dev**: `/ps-function`, `/ps-module`, `/ps-class`
- **sre-workflows**: `/incident-review`, `/proposal`, `/runbook-template`
- **spec-driven**: `/spec-start`, `/spec-requirements`, `/spec-design`

### How to Use Skills

Reference a skill:

```
@.instructions/skills/git-workflow/SKILL.md

I need to create a conventional commit for the auth module.
```

Or use commands directly:

```
/commit feat(auth): add OAuth2 support
```

See `skills/README.md` for detailed usage.

## 🚀 Getting Started

### For a New Project

1. **Customize `rules/system-context.mdc`**:
   - Replace template sections with your actual project information
   - Define technology stack, architecture, and key components
   - Document external integrations and environment variables

2. **Review and enable rules**:
   - Check `rules/always/` for standards you want to apply
   - Enable language-specific rules in `rules/auto/` as needed
   - Set `alwaysApply: true/false` in rule frontmatter

3. **Choose relevant agents**:
   - Browse `agents/` for domain experts you'll need
   - Reference them in your work as needed

4. **Explore skills**:
   - Review `skills/` for workflow automations
   - Try out commands that match your workflow

### Customization

All `.mdc` files have YAML frontmatter that controls behavior:

```yaml
---
description: What this rule/agent does
globs: ["**/*.py"] # Which files this applies to
alwaysApply: true # Whether to auto-apply
---
```

## 📖 Examples

### Multi-Step Architecture Task

```
@.instructions/agents/orchestrator/vibe-commander.mdc

Design and implement a microservices architecture with the following requirements:
- FastAPI backend with PostgreSQL
- React frontend
- Kubernetes deployment
- CI/CD pipeline
```

The orchestrator will delegate to relevant experts (architecture, backend, DevOps, etc.).

### Code Review with Standards

```
@.instructions/rules/always/security-best-practices.mdc
@.instructions/rules/auto/python.mdc

Review this authentication module for security issues and Python best practices.
```

### Quick Git Workflow

```
@.instructions/skills/git-workflow/SKILL.md

/commit feat(api): add rate limiting middleware
```

## 🛠️ Adding Custom Content

### New Agent

Create `.instructions/agents/{category}/{name}.mdc`:

```markdown
---
description: Expert in {domain}
alwaysApply: false
---

# {Agent Name}

You are an expert in {domain}.

## Expertise

- Skill 1
- Skill 2

## Best Practices

1. Practice 1
2. Practice 2
```

### New Rule

Create `.instructions/rules/{category}/{name}.mdc`:

```markdown
---
description: Standards for {topic}
globs: ["**/*.ext"]
alwaysApply: true
---

# {Rule Name}

Standards and guidelines for {topic}.

## Guidelines

...
```

### New Skill

Create `.instructions/skills/{name}/SKILL.md`:

```markdown
---
name: skill-name
description: What it does
triggers:
  - trigger phrase
---

# Skill Name

## Commands

### /command-name

Usage and examples...
```

## 💡 Tips

1. **Start small**: Begin with `system-context.mdc` and basic rules
2. **Reference, don't memorize**: Use `@` references to load context as needed
3. **Combine effectively**: Mix agents, rules, and skills for comprehensive workflows
4. **Keep it current**: Update `system-context.mdc` as your project evolves
5. **Document decisions**: Use the system to help document architecture and decisions

## 📚 Further Reading

- See individual README files in `agents/` and `skills/` for detailed documentation
- Review rule files for coding standards and best practices
- Check out example prompts in agent documentation

---

**Note**: This instruction system is designed to work with AI coding assistants that support file references and context loading. Customize it to match your team's workflows and standards.
