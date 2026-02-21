# Meta & Orchestration Subagents

Meta & Orchestration subagents coordinate and manage other subagents rather than performing work directly. They decompose complex tasks, distribute work to the right specialists, synthesise outputs, and handle errors and context across multi-agent workflows. Their effective risk level equals the highest-risk agent they delegate to.

**Risk Tier: ⚪ Tier 0 — Meta** — Effective blast radius depends entirely on which agents are delegated to; review delegated agents' risk tiers carefully.

## When to Use Meta & Orchestration Agents

Use these subagents when you need to:
- **Coordinate parallel work** — Split a large task across multiple specialist agents simultaneously
- **Manage complex workflows** — Orchestrate multi-step processes with dependencies and conditional logic
- **Synthesise agent outputs** — Merge results from multiple agents into a coherent deliverable
- **Handle errors gracefully** — Recover from agent failures without losing progress
- **Manage shared context** — Pass state and findings between agents in long-running workflows
- **Monitor agent performance** — Track execution time, token usage, and output quality

## Available Subagents

### [**agent-installer**](agent-installer.md) — Install agent definitions into projects
Installs, configures, and manages Claude Code subagent definitions in project or global scope. Handles the `.claude/agents/` directory, resolves naming conflicts, and validates frontmatter.

**Use when:** Setting up a new project with subagents, or distributing agent definitions to team members.

### [**agent-organizer**](agent-organizer.md) — Catalogue and manage available agents
Inventories all available subagent definitions, identifies gaps and overlaps, and maintains a structured catalogue. Helps teams understand what agents exist and when to use each.

**Use when:** You have a large collection of agents and need to understand what's available or identify which agent fits a task.

### [**context-manager**](context-manager.md) — Manage shared state across agent invocations
Maintains shared context, state, and intermediate results across multiple agent invocations in a workflow. Prevents information loss between agent handoffs and manages token budgets.

**Use when:** Running multi-step workflows where agents need to share findings, decisions, or intermediate artifacts.

### [**error-coordinator**](error-coordinator.md) — Handle errors and retries in multi-agent workflows
Detects failures in agent pipelines, applies retry logic, escalates unresolvable errors, and ensures workflows degrade gracefully. Logs error patterns for future improvement.

**Use when:** Running complex automated pipelines where agent failures should be handled without human intervention.

### [**it-ops-orchestrator**](it-ops-orchestrator.md) — Orchestrate IT operations workflows
Coordinates IT operations tasks across infrastructure agents, managing the sequence of provisioning, configuration, deployment, and verification steps. Enforces approval gates for high-risk operations.

**Use when:** Executing multi-step IT operations that require coordination between infrastructure, security, and deployment agents.

### [**knowledge-synthesizer**](knowledge-synthesizer.md) — Synthesise outputs from multiple agents
Merges, reconciles, and synthesises outputs from multiple agents into a single coherent result. Resolves contradictions, fills gaps, and produces executive summaries.

**Use when:** Multiple agents have produced separate findings that need to be combined into one actionable deliverable.

### [**multi-agent-coordinator**](multi-agent-coordinator.md) — Coordinate multiple sub-agents across a task
Breaks complex tasks into subtasks, assigns each to the appropriate specialist agent, manages execution order, and assembles final results. The primary entry point for large multi-agent workflows.

**Use when:** A task is too complex for a single agent and can be decomposed into parallel or sequential subtasks handled by specialists.

### [**performance-monitor**](performance-monitor.md) — Monitor agent execution performance
Tracks agent execution metrics including token consumption, tool call counts, latency, and output quality. Identifies bottlenecks and produces performance reports.

**Use when:** Optimising multi-agent pipeline costs, debugging slow workflows, or monitoring quality over time.

### [**task-distributor**](task-distributor.md) — Decompose and assign work to sub-agents
Analyses a high-level objective, decomposes it into discrete tasks, identifies which agent is best suited for each, and coordinates parallel execution. Handles dependencies between tasks.

**Use when:** You have a large backlog of related tasks that should be delegated to the right specialists efficiently.

### [**workflow-orchestrator**](workflow-orchestrator.md) — Orchestrate multi-step workflows with dependencies
Manages complex workflows with conditional logic, parallel branches, and dependency chains. Tracks workflow state, handles branching scenarios, and ensures all steps complete correctly.

**Use when:** Executing a defined multi-step process (e.g. build → test → deploy → verify) with branching based on intermediate results.

## Quick Selection Guide

| Task | Subagent | Notes |
|------|----------|-------|
| Large task requiring multiple specialists | **multi-agent-coordinator** | Decomposes and assigns work across agents |
| Multi-step process with conditional logic | **workflow-orchestrator** | Manages dependencies and branching |
| Distribute a backlog of tasks to specialists | **task-distributor** | Best for parallel execution across agent types |
| Merge results from multiple agents | **knowledge-synthesizer** | Resolves conflicts and produces coherent output |
| Pass state between agent invocations | **context-manager** | Prevents information loss across handoffs |
| Handle agent failures gracefully | **error-coordinator** | Retry logic and escalation |
| IT ops requiring multiple infra agents | **it-ops-orchestrator** | Approval gates for high-risk steps |
| Track costs and performance | **performance-monitor** | Token and latency metrics |
| Set up agents in a project | **agent-installer** | Manages `.claude/agents/` directory |
| Understand what agents are available | **agent-organizer** | Inventory and gap analysis |

## Common Combinations

**"Execute a full feature from planning to deployment"**
- **task-distributor** → distributes work to **solution-architect**, **fullstack-developer**, **unit-test-writer**, **deployment-engineer** — Orchestrates the end-to-end pipeline.

**"Run a comprehensive code audit"**
- **multi-agent-coordinator** → runs **code-reviewer**, **security-auditor**, **performance-engineer**, **complexity-analyzer** in parallel → **knowledge-synthesizer** → combined report.

**"Automated nightly maintenance pipeline"**
- **workflow-orchestrator** → **vulnerability-patcher** → **dependency-upgrader** → **unit-test-writer** → **performance-monitor** tracks execution.

**"Onboard to a new codebase and plan next sprint"**
- **codebase-explorer** + **research-analyst** → **context-manager** stores findings → **task-planner** uses context → **effort-estimator** sizes tasks.

## Getting Started

1. **Identify the workflow** — Define the overall goal and the sequence or parallel steps needed.
2. **Choose an orchestrator** — Use `multi-agent-coordinator` for open-ended tasks, `workflow-orchestrator` for defined pipelines.
3. **List your specialists** — Identify which category agents will handle each subtask.
4. **Set approval gates** — For workflows involving Tier 4–5 agents, ensure human approval steps are included.
5. **Monitor with `performance-monitor`** — Track costs and quality, especially during initial runs.
