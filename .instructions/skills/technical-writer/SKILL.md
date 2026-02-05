---
name: technical-writer
description: Generates and reviews technical documentation (API docs, guides, READMEs)
triggers:
  - doc api
  - doc guide
  - doc readme
  - doc check
  - write documentation
  - update documentation
---

# Technical Writer Skill

## Overview

This skill provides a suite of commands to automate the creation and maintenance of technical documentation. It ensures documentation is consistent, clear, and up-to-date with the codebase.

## Commands

### /doc-api [path]

Generates or updates API documentation for the specified file or directory.

**Usage:**

- `/doc-api src/api/users.ts` - Document a specific file
- `/doc-api src/api/` - Document all files in a directory

**Actions:**

1. Analyzes code for exported functions, classes, and types.
2. Generates JSDoc/Docstring comments if missing.
3. Creates a markdown reference file if requested.

### /doc-guide <topic>

Drafts a user guide or tutorial on a specific topic.

**Usage:**

- `/doc-guide "How to set up authentication"`
- `/doc-guide "Deployment workflow"`

**Actions:**

1. Scans the codebase for relevant logic and patterns.
2. Drafts a step-by-step guide in markdown format.
3. Includes code snippets and configuration examples.

### /doc-readme

Updates or creates a README.md file following standard templates.

**Usage:**

- `/doc-readme` - Update the project root README
- `/doc-readme packages/ui` - Update a sub-package README

**Actions:**

1. Checks for existing sections (Install, Usage, Contributing).
2. Fills in missing information based on project files (package.json, requirements.txt).
3. Ensures badges and links are correct.

### /doc-check [path]

Reviews existing documentation for clarity, style, and broken links.

**Usage:**

- `/doc-check docs/` - Check all docs
- `/doc-check README.md` - Check specific file

**Actions:**

1. Checks for spelling and grammar issues.
2. Verifies that code examples match actual implementation.
3. Validates internal and external links.

## Best Practices

- **Keep it concise**: Avoid fluff. Get straight to the point.
- **Use examples**: Always provide code snippets or usage examples.
- **Update often**: Documentation should evolve with the code.
