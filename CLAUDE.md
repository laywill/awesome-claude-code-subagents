# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a curated collection of Claude Code subagent definitions - specialized AI assistants for specific development tasks. Subagents are markdown files with YAML frontmatter that Claude Code can load and use.

## Repository Structure

The repository uses a 24-category risk-tiered structure organized as follows:

```
categories/
  01-research-and-discovery/              # 🟢 Tier 1 | Research & exploration
  02-architecture-and-design/             # 🟢 Tier 1 | System design
  03-analysis-and-review/                 # 🟢 Tier 1 | Code analysis & audit
  04-documentation/                       # 🟢 Tier 1 | Docs & guides
  05-planning-and-estimation/             # 🟢 Tier 1 | Project planning
  06-business-and-product/                # 🟢 Tier 1 | Business strategy
  07-language-and-framework-specialists/  # 🟡 Tier 2 | 34 language experts
  08-general-development/                 # 🟡 Tier 2 | Core development roles
  09-testing-and-qa/                      # 🟡 Tier 2 | Testing & QA
  10-refactoring-and-modernization/       # 🟡 Tier 2 | Code improvement
  11-bug-fixing-and-debugging/            # 🟡 Tier 2 | Debugging & diagnostics
  12-frontend-and-ui/                     # 🟡 Tier 2 | Frontend specialization
  13-developer-experience-and-tooling/    # 🟡 Tier 2 | DX & tools
  14-data-and-database/                   # 🟠 Tier 3 | Data layer
  15-data-science-and-ai/                 # 🟠 Tier 3 | ML & AI
  16-dependency-and-package-management/   # 🟠 Tier 3 | Dependency management
  17-build-and-ci-cd/                     # 🟠 Tier 3 | Build automation
  18-api-and-service-integration/         # 🔴 Tier 4 | API integration
  19-infrastructure-as-code/              # 🔴 Tier 4 | IaC & cloud
  20-security-and-secrets/                # 🔴 Tier 4 | Security hardening
  21-specialized-domains/                 # 🔴 Tier 4 | Niche domains
  22-deployment-and-release/              # ⛔ Tier 5 | Production deployment
  23-production-ops-and-observability/    # ⛔ Tier 5 | Production operations
  24-production-data-ops/                 # ⛔ Tier 5 | Production data
```

**Risk Tier Guide:**
- **Tier 1 (🟢)**: Low risk - read-only, advisory, analysis
- **Tier 2 (🟡)**: Medium risk - local code changes
- **Tier 3 (🟠)**: Medium-high risk - data/dependencies/build
- **Tier 4 (🔴)**: High risk - external systems, infrastructure
- **Tier 5 (⛔)**: Critical risk - production changes, deployments

## Subagent File Format

Each subagent follows this template:

```yaml
---
name: agent-name
description: When this agent should be invoked (used by Claude Code for auto-selection)
tools: Read, Write, Edit, Bash, Glob, Grep  # Comma-separated tool permissions
---

You are a [role description]...

[Agent-specific checklists, patterns, guidelines]

## Communication Protocol
[Inter-agent communication specs]

## Development Workflow
[Structured implementation phases]
```

### Tool Assignment by Role Type

- **Read-only** (reviewers, auditors): `Read, Grep, Glob`
- **Research** (analysts): `Read, Grep, Glob, WebFetch, WebSearch`
- **Code writers** (developers): `Read, Write, Edit, Bash, Glob, Grep`
- **Documentation**: `Read, Write, Edit, Glob, Grep, WebFetch, WebSearch`

## Contributing a New Subagent

When adding a new agent, update these files:

1. **Main README.md** - Add link in appropriate category (alphabetical order)
2. **Category README.md** - Add detailed description, update Quick Selection Guide table
3. **Agent .md file** - Create the actual agent definition

Format for main README: `- [**agent-name**](path/to/agent.md) - Brief description`

## Subagent Storage in Claude Code

| Type | Path | Scope |
|------|------|-------|
| Project | `.claude/agents/` | Current project only |
| Global | `~/.claude/agents/` | All projects |

Project subagents take precedence over global ones with the same name.

## Self Improvement

If you make a mistake or the User has to correct you on something: update your CLAUDE.md so you don't make that mistake again.
