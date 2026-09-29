# Planning & Estimation Subagents

Planning & Estimation subagents translate goals and requirements into actionable plans, effort estimates, and risk assessments. They help teams decide what to build next, how long it will take, and what could go wrong. These agents produce plans and recommendations — they never write implementation code or modify infrastructure.

**Risk Tier: 🟢 Tier 1 — Low** — Produces plans, estimates, and risk assessments only; no code or infrastructure changes.

## When to Use Planning & Estimation Agents

Use these subagents when you need to:

- **Break down features** — Decompose epics into implementable tasks with clear ordering
- **Estimate effort** — Get realistic estimates with confidence ranges and assumptions
- **Plan migrations** — Design phased migration paths between frameworks or platforms
- **Plan releases** — Define scope, sequencing, and rollout strategy for upcoming releases
- **Identify risks** — Surface technical risks before they become blockers
- **Facilitate agile** — Structure sprints, manage backlogs, and run agile ceremonies

## Available Subagents

### [**effort-estimator**](effort-estimator.md) — Estimate implementation effort

Produces effort estimates for features, tasks, and projects using story points, time ranges, or t-shirt sizing. Identifies key assumptions and uncertainty sources, and provides confidence intervals.

**Use when:** You need honest effort estimates before committing to a sprint or project timeline.

### [**migration-planner**](migration-planner.md) — Plan phased migrations

Designs detailed, phased migration plans for moving between frameworks, versions, languages, or platforms. Identifies dependencies, parallel-run strategies, and rollback points.

**Use when:** Undertaking a major migration (e.g. React 17 → 19, Python 2 → 3, monolith → microservices) and need a safe, incremental plan.

### [**product-manager**](product-manager.md) — Define requirements and roadmaps

Defines product requirements, prioritises features, and maintains roadmaps. Translates business goals into technical requirements and helps teams align on what to build and why.

**Use when:** You need to structure product requirements, prioritise a backlog, or communicate the product direction to engineering.

### [**project-manager**](project-manager.md) — Plan projects and track progress

Creates project plans with milestones, dependencies, and resource allocations. Tracks progress, identifies blockers, and manages scope changes to keep projects on schedule.

**Use when:** Managing a medium-to-large project with multiple workstreams and dependencies that need active coordination.

### [**release-planner**](release-planner.md) — Plan release scope and rollout

Defines release scope, sequencing, and rollout strategy including feature flags, gradual rollouts, and rollback criteria. Produces release checklists and go/no-go criteria.

**Use when:** Planning a major release and need to define what's in scope, how it rolls out, and what triggers a rollback.

### [**risk-assessor**](risk-assessor.md) — Identify and mitigate technical risks

Identifies technical risks in a proposed approach or project plan, assesses likelihood and impact, and proposes mitigations. Produces a risk register with priority rankings.

**Use when:** Before committing to an approach, before a major release, or when you sense unknown unknowns in a project.

### [**scrum-master**](scrum-master.md) — Facilitate agile ceremonies and sprints

Facilitates sprint planning, retrospectives, and backlog grooming. Manages sprint capacity, identifies impediments, and helps teams work in a healthy agile cadence.

**Use when:** Running a scrum team and need help structuring ceremonies, managing velocity, or improving team processes.

### [**task-planner**](task-planner.md) — Break features into implementable tasks

Decomposes features or epics into granular, implementable tasks with clear acceptance criteria, ordering constraints, and ownership recommendations.

**Use when:** A feature is too large or ambiguous to implement directly and needs to be broken down into actionable work items.

## Quick Selection Guide

| Task | Subagent | Notes |
| --- | --- | --- |
| Break a feature into tasks | **task-planner** | Granular tasks with acceptance criteria and ordering |
| Estimate a sprint or project | **effort-estimator** | Confidence intervals and key assumptions |
| Plan a framework/platform migration | **migration-planner** | Phased approach with rollback points |
| Define product requirements | **product-manager** | Requirements, prioritisation, roadmaps |
| Manage a multi-workstream project | **project-manager** | Milestones, dependencies, resource allocation |
| Plan a major release | **release-planner** | Scope, rollout strategy, rollback criteria |
| Identify project risks | **risk-assessor** | Risk register with likelihood, impact, mitigations |
| Run sprint planning or retrospectives | **scrum-master** | Agile ceremony facilitation |

## Common Combinations

### "Plan a new feature from requirements to tasks"

- **product-manager** → requirements → **risk-assessor** → risks identified → **task-planner** → broken into tasks → **effort-estimator** → sized for sprint planning.

### "Prepare for a major migration"

- **migration-planner** → phased plan → **risk-assessor** → risks per phase → **release-planner** → rollout strategy per phase → **effort-estimator** → total effort sizing.

### "Plan a major release"

- **release-planner** → scope and rollout strategy → **risk-assessor** → go/no-go risks → **project-manager** → timeline and dependencies.

### "Sprint planning and retrospective"

- **task-planner** → breaks backlog items down → **effort-estimator** → sizes each task → **scrum-master** → facilitates capacity planning and assignment.

## Getting Started

1. **Define your goal** — Is it a single feature, a release, or a long-running project? Choose the appropriate planning agent.
2. **Provide context** — Share requirements, tech stack, team size, and constraints so estimates and plans are realistic.
3. **Combine with risk assessment** — Always run **risk-assessor** alongside planning agents to surface unknowns early.
4. **Use outputs as inputs** — Task breakdowns feed sprint planning; release plans feed deployment agents.
5. **Iterate** — Plans change; re-run planning agents as requirements evolve to keep plans current.
