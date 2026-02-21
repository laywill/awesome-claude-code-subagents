# Documentation & Technical Writing Subagents

Documentation & Technical Writing subagents write and maintain all forms of project documentation — from API references and runbooks to changelogs and READMEs. They transform code, commit history, and domain knowledge into clear, structured documents that help teams build, operate, and understand systems. All agents in this category write documentation files only.

**Risk Tier: 🟢 Tier 1 — Low** — Writes documentation files only; no code, infrastructure, or configuration is modified.

## When to Use Documentation Agents

Use these subagents when you need to:
- **Document APIs** — Generate reference docs from code or OpenAPI specs
- **Write runbooks** — Create operational procedures for incident response and routine tasks
- **Record decisions** — Capture architectural choices with context and rationale
- **Generate changelogs** — Produce release notes from commit history or PR descriptions
- **Refresh READMEs** — Update project READMEs with current setup instructions and examples
- **Write technical content** — Produce guides, tutorials, and explanations for varied audiences

## Available Subagents

### [**adr-author**](adr-author.md) — Write Architecture Decision Records
Creates well-structured Architecture Decision Records (ADRs) capturing the context, decision, considered alternatives, and consequences of architectural choices. Follows the MADR or Nygard ADR format.

**Use when:** You've made a significant architectural decision and need to document the reasoning for future team members and reviewers.

### [**api-documenter**](api-documenter.md) — Generate API reference documentation
Produces API reference documentation from source code, OpenAPI specs, or endpoint descriptions. Generates usage examples, request/response schemas, error codes, and authentication guidance.

**Use when:** Publishing a public or internal API and need comprehensive, accurate reference documentation.

### [**changelog-generator**](changelog-generator.md) — Generate changelogs from commit history
Parses git commit history, PR titles, and conventional commit messages to produce structured changelogs grouped by type (features, fixes, breaking changes). Follows Keep a Changelog conventions.

**Use when:** Preparing a release and need to generate or update CHANGELOG.md from recent commits and merged PRs.

### [**documentation-engineer**](documentation-engineer.md) — Write long-form technical documentation
Authors comprehensive technical documentation including architecture guides, developer onboarding docs, integration guides, and conceptual overviews. Structures content for both new and experienced readers.

**Use when:** You need substantial technical documentation that goes beyond a README — integration guides, developer portals, or architecture documentation.

### [**readme-generator**](readme-generator.md) — Generate or refresh project READMEs
Creates or updates project README files with installation instructions, usage examples, configuration reference, and contributing guidelines. Tailored to the project's tech stack and audience.

**Use when:** Starting a new project, open-sourcing a repository, or when the existing README is outdated or incomplete.

### [**runbook-writer**](runbook-writer.md) — Write operational runbooks
Produces step-by-step operational runbooks for incident response procedures, routine maintenance tasks, and system operations. Includes prerequisites, decision trees, escalation paths, and rollback steps.

**Use when:** Preparing for production operations, documenting incident response procedures, or capturing institutional knowledge before a team member leaves.

### [**technical-writer**](technical-writer.md) — Write structured technical content
Creates clear, accurate technical content tailored to the target audience — from end-user guides to internal engineering documentation. Adapts tone, depth, and structure for the intended readers.

**Use when:** You need technical content that bridges the gap between engineering and other audiences (product, support, customers, or regulators).

## Quick Selection Guide

| Task | Subagent | Notes |
|------|----------|-------|
| Document an API endpoint or service | **api-documenter** | OpenAPI-sourced or manually described APIs |
| Capture an architectural decision | **adr-author** | MADR/Nygard format with context and consequences |
| Generate CHANGELOG.md for a release | **changelog-generator** | Parses git log and conventional commits |
| Write a project README | **readme-generator** | Tailored to tech stack and audience |
| Create operational runbooks | **runbook-writer** | Step-by-step procedures with escalation paths |
| Author long-form technical docs | **documentation-engineer** | Integration guides, architecture docs |
| Write for non-engineering audiences | **technical-writer** | Adjusts depth and tone for the reader |

## Common Combinations

**"Document a new service from scratch"**
- **readme-generator** → project README → **api-documenter** → API reference → **runbook-writer** → deployment and operational procedures → **adr-author** → key design decisions.

**"Prepare a release"**
- **changelog-generator** → release notes from commits → **api-documenter** → updated API reference for changed endpoints → **readme-generator** → updated README with new features.

**"Knowledge transfer before a team member leaves"**
- **runbook-writer** → operational procedures → **documentation-engineer** → architecture and system knowledge → **adr-author** → rationale for past decisions.

**"Open-source a project"**
- **readme-generator** → public-facing README → **api-documenter** → public API reference → **technical-writer** → contributing guide and code of conduct.

## Getting Started

1. **Identify what's missing** — Choose the documentation type most needed (API ref, runbook, ADR, README, changelog).
2. **Provide source material** — Share code, OpenAPI specs, commit history, or describe the system verbally.
3. **Specify your audience** — Developers, operators, end users, or regulators each need different depth and tone.
4. **Review and refine** — Documentation agents produce drafts; review for accuracy and completeness before publishing.
5. **Keep it updated** — Re-run agents after major changes to keep documentation current.
