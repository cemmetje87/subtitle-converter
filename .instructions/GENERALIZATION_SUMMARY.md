# Instructions Generalization Summary

This document summarizes the changes made to generalize the `.instructions/` folder for use with any development project.

## What Was Changed

### ✅ Fully Generalized Files

These files are now completely project-agnostic and ready to use:

1. **`README.md`** (NEW)
   - Comprehensive guide to using the instructions system
   - Explains agents, rules, and skills
   - Includes examples and customization instructions

2. **`rules/system-context.mdc`** (REPLACED)
   - Template for project-specific context
   - Includes placeholders for technology stack, architecture, etc.
   - Users should customize this for their project

3. **`rules/00-system-overview.mdc`** (REPLACED)
   - Generalized multi-agent execution model
   - Removed all Employee Lifecycle Management System references
   - Project-agnostic description of agent collaboration

4. **`rules/always/sre-best-practices.mdc`** (RENAMED & UPDATED)
   - Previously: `blackline-sre-best-practices.mdc`
   - Removed company-specific references
   - Generalized SRE and engineering best practices

5. **Language-Specific Rules** (`rules/auto/`)
   - Already generic: `python.mdc`, `typescript.mdc`, `powershell.mdc`, `terraform.mdc`
   - No changes needed

6. **General Standards** (`rules/always/`)
   - Already generic: `base.mdc`, `security-best-practices.mdc`, `keep-it-simple.mdc`, `development-standards.mdc`
   - No changes needed

### 📂 Moved to Examples

Project-specific files were renamed with `.example` extension for reference:

- `rules/01-software-engineering-expert.mdc.example`
- `rules/02-sre-expert.mdc.example`
- `rules/03-devops-expert.mdc.example`
- `rules/05-entra-id-expert.mdc.example`
- `rules/windows-server.mdc.example`
- `rules/_reference_examples/` (renamed from `reference/`)

These files contain detailed, project-specific examples that users can reference when creating their own expert rules.

### 🔧 No Changes Needed

These directories were already generic:

- **`agents/`**: All agent personas are domain-generic (AWS, Azure, GCP, Kubernetes, etc.)
- **`skills/`**: All workflow skills are project-agnostic

## How to Use for Your Project

### Step 1: Customize System Context

Edit `rules/system-context.mdc` and replace the template sections with your actual project information:

- Project purpose and goals
- Technology stack
- Architecture overview
- External integrations
- Environment variables
- Development workflow

### Step 2: Review and Enable Rules

1. Check `rules/always/` and decide which standards to apply
2. Modify `alwaysApply: true/false` in rule frontmatter as needed
3. Review language-specific rules in `rules/auto/`

### Step 3: Optional - Create Custom Expert Rules

If needed, create project-specific expert rules based on the `.example` files:

```bash
# Copy an example as a starting point
cp rules/01-software-engineering-expert.mdc.example rules/01-software-engineering-expert.mdc

# Edit and customize for your project
```

### Step 4: Start Using the System

Reference files in your AI assistant prompts:

```
@.instructions/rules/system-context.mdc
@.instructions/agents/aws/aws-architect.mdc

Design a scalable infrastructure for my application.
```

## Key Files to Customize

1. **REQUIRED**: `rules/system-context.mdc` - Add your project details
2. **Optional**: Create domain expert rules from `.example` templates
3. **Optional**: Add project-specific skills to `skills/`

## What's Different from the Original?

| Aspect                 | Before                               | After                     |
| ---------------------- | ------------------------------------ | ------------------------- |
| **System Context**     | Employee Lifecycle Management System | Generic template          |
| **Company References** | Blackline-specific                   | Removed/generalized       |
| **External Systems**   | Workday, JIRA, AD, etc.              | Placeholder examples      |
| **Expert Rules**       | PowerShell/Windows-specific          | Moved to `.example` files |
| **SRE Practices**      | Company-specific runbooks            | Generic best practices    |

## Benefits of This Generalization

✅ **Reusable**: Works for any technology stack or project type
✅ **Customizable**: Easy to adapt to specific needs
✅ **Examples Included**: `.example` files show detailed implementations
✅ **Well-Documented**: Comprehensive README and inline documentation
✅ **Agent/Skill Library**: 40+ ready-to-use agents and workflows

## Next Steps

1. Read `.instructions/README.md` for detailed usage instructions
2. Customize `rules/system-context.mdc` with your project details
3. Explore `agents/` and `skills/` to see what's available
4. Try referencing files in your AI assistant prompts
5. Create custom rules/agents as needed for your project

## Support

For questions or issues:

- Review the `.example` files for detailed implementations
- Check `agents/README.md` and `skills/README.md` for usage guides
- Refer to rule files for coding standards

---

**Version**: 2.0 (Generalized)  
**Date**: 2026-02-06  
**Status**: Ready for any project
