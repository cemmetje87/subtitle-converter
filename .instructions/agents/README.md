# Cursor Subagents

This directory contains specialized expert personas that can be invoked as subagents for delegated tasks.

## Available Subagents

### Orchestrator

| Subagent                          | Use Case                                                        |
| --------------------------------- | --------------------------------------------------------------- |
| `orchestrator/vibe-commander.mdc` | Master orchestrator for complex, multi-domain task coordination |

The **Vibe Commander** is the strategic technical lead that:

- **Plans**: Analyzes complex requests and breaks them into actionable steps
- **Delegates**: Assigns tasks to appropriate domain experts
- **Reviews**: Ensures outputs meet requirements and standards
- **Synthesizes**: Combines expert outputs into cohesive solutions

**Example**:

```
@.cursor/agents/orchestrator/vibe-commander.mdc

Migrate our on-prem AD to Azure AD and set up Terraform infrastructure.
```

### AWS Experts

| Subagent                           | Use Case                                                                      |
| ---------------------------------- | ----------------------------------------------------------------------------- |
| `aws/aws-architect.mdc`            | Design AWS infrastructure, multi-account strategies, Well-Architected reviews |
| `aws/aws-reliability-engineer.mdc` | SRE practices, chaos engineering, disaster recovery                           |
| `aws/aws-security-analyst.mdc`     | Security audits, IAM reviews, compliance                                      |
| `aws/aws-terraform-expert.mdc`     | AWS Terraform modules, state management                                       |

### Azure Experts

| Subagent                               | Use Case                                             |
| -------------------------------------- | ---------------------------------------------------- |
| `azure/azure-architect.mdc`            | Design Azure infrastructure, subscription strategies |
| `azure/azure-reliability-engineer.mdc` | Azure SRE, availability, disaster recovery           |
| `azure/azure-security-analyst.mdc`     | Security audits, Defender, compliance                |
| `azure/azure-terraform-expert.mdc`     | Azure Terraform modules, AzureRM provider            |

### GCP Experts

| Subagent                           | Use Case                                      |
| ---------------------------------- | --------------------------------------------- |
| `gcp/gcp-architect.mdc`            | GCP infrastructure design, project strategies |
| `gcp/gcp-reliability-engineer.mdc` | GCP SRE, SLOs, auto-scaling                   |
| `gcp/gcp-security-analyst.mdc`     | Security audits, IAM, VPC Service Controls    |
| `gcp/gcp-terraform-expert.mdc`     | GCP Terraform modules, Google provider        |

### PowerShell Experts

| Subagent                                        | Use Case                                     |
| ----------------------------------------------- | -------------------------------------------- |
| `powershell/powershell-expert.mdc`              | Script development, modules, Microsoft Graph |
| `powershell/powershell-architect.mdc`           | Module frameworks, enterprise patterns       |
| `powershell/powershell-automation-engineer.mdc` | Pester testing, CI/CD pipelines              |
| `powershell/powershell-security-analyst.mdc`    | Script signing, JEA, credential management   |

### Windows Experts

| Subagent                                   | Use Case                                         |
| ------------------------------------------ | ------------------------------------------------ |
| `windows/windows-architect.mdc`            | Active Directory, hybrid identity, Group Policy  |
| `windows/windows-automation-expert.mdc`    | DSC, Ansible for Windows, WinRM                  |
| `windows/windows-reliability-engineer.mdc` | High availability, monitoring, disaster recovery |
| `windows/windows-security-analyst.mdc`     | Hardening, security baselines, Defender          |

### Microsoft 365

| Subagent                     | Use Case                                       |
| ---------------------------- | ---------------------------------------------- |
| `m365/m365-graph-expert.mdc` | Microsoft Graph API, Entra ID, user management |

## How to Use Subagents

### Method 1: Reference in Prompt

```
@.cursor/agents/aws/aws-security-analyst.mdc

Review @terraform/modules/networking/ for security vulnerabilities.
Focus on IAM permissions, network exposure, and encryption.
```

### Method 2: Task Tool (for parallel work)

When working with the Task tool, reference the subagent:

```
Using the AWS Security Analyst expertise from @.cursor/agents/aws/aws-security-analyst.mdc,
audit the following Terraform configuration for security issues...
```

### Method 3: Explicit Role Assignment

```
Act as the Azure Architect (@.cursor/agents/azure/azure-architect.mdc).
Design a multi-subscription Azure environment for a regulated workload.
```

## Best Practices

1. **Choose the right expert** - Match the subagent to the task domain
2. **Use Vibe Commander for complex tasks** - When tasks span multiple domains, start with the orchestrator
3. **Provide context** - Include relevant files and requirements
4. **Be specific** - State what output you expect
5. **Review outputs** - Subagents are experts but still need review

## Adding New Subagents

Create a new `.mdc` file following this template:

```markdown
---
description: Expert Name - use when working with [domains]
alwaysApply: false
---

# Expert Name

You are a **[Expert Title]** specializing in [domain].

## Expertise

- Skill 1
- Skill 2
- Skill 3

## Best Practices

1. Practice 1
2. Practice 2

## Templates/Patterns

[Include useful templates]

## References

| Topic | Source |
| ----- | ------ |
| Topic | URL    |
```
