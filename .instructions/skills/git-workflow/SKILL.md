---
name: git-workflow
description: Git workflow automation with conventional commits, branch naming, and PR templates
triggers:
  - git commit
  - create branch
  - pull request
  - conventional commit
---

# Git Workflow Skill

Automates Git workflows following team conventions for commits, branches, and pull requests.

## Commands

### /commit

Generate a conventional commit message based on staged changes.

**Usage**: `/commit <type> [scope] <description>`

**Types**:
| Type | Use Case |
|------|----------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Code style (formatting, semicolons) |
| `refactor` | Code refactoring |
| `perf` | Performance improvements |
| `test` | Adding or updating tests |
| `chore` | Maintenance tasks |
| `ci` | CI/CD changes |
| `build` | Build system changes |

**Output Format**:

```
<type>(<scope>): <description>

[body - what and why]

[footer - references]
```

**Example**:

```bash
# Input
/commit feat auth add OAuth2 login support

# Output
feat(auth): add OAuth2 login support

Implements OAuth2 authentication flow with support for
Google and Microsoft providers.

Closes #123
```

**Rules**:

- Subject line under 72 characters
- Use imperative mood ("add" not "added")
- Reference issues in footer

---

### /branch

Create a properly named branch following conventions.

**Usage**: `/branch <type> <ticket> <description>`

**Branch Types**:
| Type | Pattern |
|------|---------|
| feature | `feature/<ticket>-<description>` |
| bugfix | `bugfix/<ticket>-<description>` |
| hotfix | `hotfix/<ticket>-<description>` |
| release | `release/<version>` |

**Example**:

```bash
# Input
/branch feature PROJ-123 user-authentication

# Output
git checkout -b feature/PROJ-123-user-authentication
```

**Rules**:

- Lowercase with hyphens
- Include ticket number
- Keep description short but meaningful

---

### /pr

Generate a pull request description template.

**Usage**: `/pr [title]`

**Output Template**:

```markdown
## Summary

<!-- Brief description of changes -->

## Changes

- [ ] Change 1
- [ ] Change 2

## Type of Change

- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update

## Testing

- [ ] Tests pass locally
- [ ] New tests added for changes
- [ ] Manual testing completed

## Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings introduced

## Related Issues

Closes #

## Screenshots (if applicable)
```

---

### /branch-cleanup

List and optionally delete merged branches.

**Usage**: `/branch-cleanup [--dry-run]`

**Actions**:

1. List branches merged into main/master
2. Exclude protected branches
3. Show deletion commands (or execute if not dry-run)

**Output**:

```bash
# Merged branches found:
git branch -d feature/PROJ-100-old-feature
git branch -d bugfix/PROJ-101-fixed-bug

# Remote cleanup:
git push origin --delete feature/PROJ-100-old-feature
```

---

## Workflow Integration

### Pre-commit Hook

This skill works with git hooks for validation:

```bash
# .git/hooks/commit-msg validation
# Ensures conventional commit format
```

### CI Integration

Branch naming is validated in CI pipelines.

## Tips

1. **Stage changes first** - `/commit` analyzes staged files
2. **Be specific** - Good commits explain "why" not just "what"
3. **Link issues** - Always reference related tickets
4. **Review before push** - Use `git log --oneline` to verify

## References

| Topic                 | Source                                                           |
| --------------------- | ---------------------------------------------------------------- |
| Conventional Commits  | https://www.conventionalcommits.org/                             |
| Git Branch Strategies | https://git-scm.com/book/en/v2/Git-Branching-Branching-Workflows |
