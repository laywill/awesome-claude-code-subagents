# Developer Experience & Tooling Subagents

Developer Experience & Tooling subagents improve the inner development loop — build tools, workflows, developer productivity, and the systems that help engineering teams work more effectively. They configure build systems, create internal tools, set up git workflows, build Slack integrations, and design AI prompts. Changes are limited to local configuration and tool code.

**Risk Tier: 🟡 Tier 2 — Medium** — Modifies build configs, workflow scripts, and tooling code; changes are local and reviewable.

## When to Use Developer Experience & Tooling Agents

Use these subagents when you need to:
- **Optimise build systems** — Improve build speed, caching, and toolchain configuration
- **Reduce developer friction** — Identify and fix pain points in the development workflow
- **Configure git workflows** — Set up branching strategies, hooks, and automation
- **Build internal tools** — Create tools that improve team productivity
- **Create Slack integrations** — Build bots and workflow automations for team communication
- **Design AI prompts** — Optimise prompts for LLM-based features and systems

## Available Subagents

### [**build-engineer**](build-engineer.md) — Configure and optimise build systems
Sets up and optimises build systems (Webpack, Vite, Rollup, Gradle, Make, etc.) for speed, reliability, and developer experience. Configures caching, parallelisation, incremental builds, and hot reloading.

**Use when:** Build times are slow, builds are unreliable, or you're migrating to a new build tool.

### [**dx-optimizer**](dx-optimizer.md) — Identify and fix developer experience friction
Audits the developer experience — onboarding time, feedback loop speed, tooling complexity, documentation gaps — and produces prioritised improvements. Makes the development environment faster and more pleasant.

**Use when:** Developer productivity is lagging, onboarding new engineers takes too long, or the team has accumulated DX friction over time.

### [**git-workflow-manager**](git-workflow-manager.md) — Configure branching strategies and git workflows
Sets up git branching strategies (Git Flow, trunk-based development, etc.), pre-commit hooks, commit message conventions, and PR templates. Automates code quality checks in the git workflow.

**Use when:** Establishing or improving git workflow conventions, setting up pre-commit hooks, or migrating branching strategy.

### [**prompt-engineer**](prompt-engineer.md) — Design and optimise LLM prompts
Designs, tests, and optimises prompts for LLM-based features — system prompts, few-shot examples, chain-of-thought instructions, and tool definitions. Improves output quality and reliability.

**Use when:** Building AI-powered features that use LLMs, or when existing prompts produce inconsistent or poor-quality outputs.

### [**slack-expert**](slack-expert.md) — Build Slack integrations and bots
Creates Slack apps, bots, workflow automations, and slash commands using the Slack API and Bolt framework. Integrates Slack with internal systems for notifications, approvals, and team workflows.

**Use when:** Building a Slack bot, setting up automated notifications, creating approval workflows, or integrating Slack with internal tools.

### [**tooling-engineer**](tooling-engineer.md) — Build and maintain internal developer tools
Develops custom internal tools — scripts, CLIs, web dashboards, and automation tools — that improve engineering team productivity. Focuses on tools used by developers rather than end users.

**Use when:** Your team needs a custom tool that doesn't exist (deployment scripts, internal dashboards, code generators, data migration utilities).

## Quick Selection Guide

| Task | Subagent | Notes |
|------|----------|-------|
| Speed up slow builds | **build-engineer** | Caching, parallelisation, incremental builds |
| Improve developer onboarding and workflow | **dx-optimizer** | Audit and prioritised DX improvements |
| Set up git hooks and branching conventions | **git-workflow-manager** | Pre-commit hooks, branch strategy, PR templates |
| Optimise LLM prompts for a feature | **prompt-engineer** | System prompts, few-shot, tool definitions |
| Build a Slack bot or notification | **slack-expert** | Slack API, Bolt framework, workflow automation |
| Create a custom internal tool | **tooling-engineer** | CLIs, scripts, dashboards, code generators |

## Common Combinations

**"Set up a new project's development environment"**
- **build-engineer** → build system → **git-workflow-manager** → git hooks and conventions → **dx-optimizer** → audit and improve onboarding → **readme-generator** (Documentation category) → developer setup guide.

**"Build an AI-powered feature"**
- **prompt-engineer** → design and optimise prompts → **mcp-developer** (General Development category) → build MCP integration → **tooling-engineer** → internal testing dashboard.

**"Improve deployment feedback loop"**
- **tooling-engineer** → deployment status CLI tool → **slack-expert** → Slack deployment notifications → **git-workflow-manager** → add deployment hooks.

**"Full DX audit and improvement sprint"**
- **dx-optimizer** → audit and priorities → **build-engineer** → speed improvements → **git-workflow-manager** → workflow automation → **tooling-engineer** → custom tools for top pain points.

## Getting Started

1. **Identify the friction** — Is it build speed, workflow complexity, missing tools, or AI prompt quality? Choose accordingly.
2. **Describe your current setup** — Share your existing build config, git setup, or tool stack so changes integrate smoothly.
3. **Test changes locally first** — Tool and config changes should be verified in a local environment before rolling out to the team.
4. **Document what you've built** — Use **readme-generator** or **runbook-writer** (Documentation category) to document new tools and workflows.
5. **Measure the improvement** — Track build times, onboarding time, or other DX metrics before and after changes.
