# Build & CI/CD Subagents

Build & CI/CD subagents author and maintain build pipelines and CI/CD workflow configurations. They create GitHub Actions workflows, GitLab CI pipelines, and reusable workflow templates; optimise build times; and configure artifact storage and environment variables. Pipeline changes affect the whole team's development workflow, so review carefully before merging.

**Risk Tier: 🟠 Tier 3 — Medium-High** — Modifies CI/CD pipeline configurations; errors can break builds for the entire team. Review pipeline changes in a feature branch before merging to main.

## When to Use Build & CI/CD Agents

Use these subagents when you need to:
- **Create CI/CD pipelines** — Author new pipeline configurations for GitHub Actions, GitLab CI, CircleCI, etc.
- **Optimise build performance** — Reduce build times through better caching and parallelisation
- **Write reusable workflows** — Create shared workflow templates and composite actions
- **Configure artifact storage** — Set up build artifact publishing and distribution
- **Manage environment configuration** — Configure CI/CD environment variables and stage settings

## Available Subagents

### [**artifact-publisher**](artifact-publisher.md) — Configure build artifact storage and distribution
Sets up artifact storage, versioning, and distribution — npm registry publishing, Docker image pushing, binary releases to GitHub/S3, or internal artifact repositories. Handles signing, checksums, and retention policies.

**Use when:** Setting up automated publishing of build artifacts, Docker images, or binary releases as part of a CI/CD pipeline.

### [**build-optimizer**](build-optimizer.md) — Optimise build times and caching
Analyses build pipelines to identify bottlenecks, implements layer caching (Docker, npm, pip), parallelises independent steps, and reduces redundant work. Targets both local and CI build performance.

**Use when:** CI builds are slow, caching is not working effectively, or you want to reduce the feedback loop for developers.

### [**environment-configurator**](environment-configurator.md) — Set up CI/CD environment configuration
Configures environment variables, secrets management, stage-specific settings, and deployment targets across CI/CD environments. Ensures secrets are never in code and configuration is environment-aware.

**Use when:** Setting up a new pipeline stage (staging, production), managing secrets in CI/CD, or configuring environment-specific behaviour.

### [**pipeline-builder**](pipeline-builder.md) — Author CI/CD pipeline configurations
Creates complete CI/CD pipeline configurations for GitHub Actions, GitLab CI, CircleCI, Jenkins, and Azure Pipelines. Implements test, build, security scan, and deploy stages with appropriate dependencies and conditions.

**Use when:** Setting up CI/CD for a new project, migrating from one CI/CD platform to another, or restructuring an existing pipeline.

### [**workflow-author**](workflow-author.md) — Write reusable workflow templates and composite actions
Creates reusable GitHub Actions workflow templates, composite actions, and shared pipeline components. Enables teams to standardise CI/CD patterns across repositories.

**Use when:** You want to standardise CI/CD patterns across multiple repositories, or extract commonly repeated pipeline steps into reusable components.

## Quick Selection Guide

| Task | Subagent | Notes |
|------|----------|-------|
| Create a new CI/CD pipeline | **pipeline-builder** | GitHub Actions, GitLab CI, CircleCI, Jenkins |
| Speed up slow CI builds | **build-optimizer** | Caching strategies, parallelisation, redundancy elimination |
| Create reusable GitHub Actions | **workflow-author** | Composite actions, reusable workflows, organisation templates |
| Publish artifacts or Docker images | **artifact-publisher** | Registry publishing, binary releases, signing |
| Configure CI secrets and environments | **environment-configurator** | Env vars, secrets management, stage configuration |

## Common Combinations

**"Set up CI/CD for a new project"**
- **pipeline-builder** → full pipeline → **environment-configurator** → secrets and stage config → **artifact-publisher** → artifact storage and publishing → **build-optimizer** → initial caching setup.

**"Standardise CI/CD across a monorepo"**
- **workflow-author** → reusable workflow templates → **pipeline-builder** → per-package pipelines using templates → **build-optimizer** → monorepo-aware caching.

**"Reduce 20-minute builds to under 5 minutes"**
- **build-optimizer** → bottleneck analysis and caching → **workflow-author** → parallel job templates → **pipeline-builder** → restructured pipeline.

**"Set up secure deployment pipeline"**
- **environment-configurator** → secrets and environment config → **pipeline-builder** → deploy pipeline with approval gates → **artifact-publisher** → signed artifact distribution.

## Getting Started

1. **Test pipeline changes in a branch** — Always test pipeline changes in a feature branch before merging to avoid breaking main.
2. **Use dry-run modes** — Most CI/CD platforms have ways to validate pipeline syntax before running; use them.
3. **Start with a minimal pipeline** — Get a simple pipeline working first, then add complexity (caching, parallelisation, artifact publishing).
4. **Keep secrets out of code** — Use **environment-configurator** to ensure all secrets are in the CI/CD platform's secret store, never in YAML files.
5. **Measure build times** — Track build time before and after **build-optimizer** changes to quantify improvement.
