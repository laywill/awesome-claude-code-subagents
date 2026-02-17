# Dependency & Package Management Subagents

Dependency & Package Management subagents manage project dependencies, resolve conflicts, patch vulnerabilities, and handle package publishing. Because dependency changes affect the entire project's build and can introduce supply-chain risk, this tier requires careful review — always check what changed and verify tests pass after updates.

**Risk Tier: 🟠 Tier 3 — Medium-High** — Modifies dependency trees and lock files; can break builds, introduce incompatibilities, or expose supply-chain risk. Review changes carefully and run the full test suite after updates.

## When to Use Dependency Management Agents

Use these subagents when you need to:
- **Update outdated dependencies** — Systematically upgrade packages to current versions
- **Patch security vulnerabilities** — Fix known CVEs in dependencies with minimal disruption
- **Resolve dependency conflicts** — Untangle version mismatches and lockfile issues
- **Manage monorepo workspaces** — Keep shared dependencies consistent across packages
- **Publish packages** — Prepare and publish packages to npm, PyPI, crates.io, etc.
- **Audit dependency health** — Understand the state of your dependency tree

## Available Subagents

### [**dependency-manager**](dependency-manager.md) — Manage and resolve project dependencies
Audits the dependency tree, resolves version conflicts, removes unused dependencies, and keeps package manifests clean. Works across npm/yarn/pnpm, pip/poetry, cargo, go mod, and Maven.

**Use when:** Your dependency tree has conflicts, bloated dependencies, or needs a general health check.

### [**dependency-upgrader**](dependency-upgrader.md) — Upgrade dependencies with compatibility checks
Systematically upgrades dependencies to newer versions, checks for breaking changes in changelogs and migration guides, and updates code where necessary to maintain compatibility.

**Use when:** You want to upgrade multiple dependencies while minimising breakage risk, especially for minor and patch version bumps across many packages.

### [**lockfile-resolver**](lockfile-resolver.md) — Resolve lockfile conflicts and mismatches
Resolves merge conflicts in lockfiles (package-lock.json, yarn.lock, Cargo.lock, etc.), regenerates consistent lockfiles, and resolves peer dependency conflicts and resolution mismatches.

**Use when:** Merge conflicts in a lockfile are blocking a PR, or the lockfile is inconsistent with the package manifest.

### [**monorepo-manager**](monorepo-manager.md) — Manage monorepo workspace configurations
Manages workspace configurations in Nx, Turborepo, pnpm workspaces, or Lerna. Ensures shared dependencies are consistent, cross-package references are correct, and build pipelines are optimised.

**Use when:** Managing a monorepo with multiple packages and you need to keep dependencies aligned, build order correct, or shared configuration consistent.

### [**package-publisher**](package-publisher.md) — Prepare and publish packages
Prepares packages for publishing — bumping versions, updating changelogs, building distributables, and publishing to npm, PyPI, crates.io, or other registries. Handles semantic versioning and release workflows.

**Use when:** Releasing a library or tool to a public or private package registry.

### [**vulnerability-patcher**](vulnerability-patcher.md) — Patch CVEs in dependencies
Identifies and patches known security vulnerabilities in dependencies with minimal disruption. Evaluates the risk of each vulnerability, proposes the safest upgrade path, and verifies compatibility.

**Use when:** `npm audit`, `pip-audit`, `cargo audit`, or `dependency-auditor` has flagged CVEs that need remediation.

## Quick Selection Guide

| Task | Subagent | Notes |
|------|----------|-------|
| General dependency health check | **dependency-manager** | Conflicts, unused deps, manifest cleanup |
| Upgrade all deps to latest | **dependency-upgrader** | Breaking change analysis, automated code updates |
| Fix lockfile merge conflicts | **lockfile-resolver** | All lockfile formats (npm, yarn, pnpm, Cargo) |
| Manage a monorepo | **monorepo-manager** | Nx, Turborepo, pnpm workspaces, Lerna |
| Publish a package to npm/PyPI | **package-publisher** | Versioning, changelogs, registry publishing |
| Patch specific CVEs | **vulnerability-patcher** | Targeted security fixes with minimal disruption |

## Common Combinations

**"Monthly dependency maintenance"**
- **dependency-auditor** (Analysis category) → audit report → **vulnerability-patcher** → fix CVEs → **dependency-upgrader** → upgrade remaining deps → full test suite verification.

**"Secure a dependency tree before a release"**
- **vulnerability-patcher** → patch CVEs → **dependency-manager** → clean up tree → **lockfile-resolver** → consistent lockfile → **unit-test-writer** (Testing category) → verify nothing broke.

**"Publish a new library release"**
- **changelog-generator** (Documentation category) → release notes → **package-publisher** → version bump and publish → **readme-generator** (Documentation category) → update docs.

**"Untangle a messy monorepo"**
- **monorepo-manager** → workspace alignment → **dependency-manager** → resolve tree conflicts → **lockfile-resolver** → consistent lockfiles → **build-engineer** (DX category) → verify build pipeline.

## Getting Started

1. **Run tests before and after** — Always run the full test suite before upgrading dependencies to establish a baseline, and again after to catch regressions.
2. **Upgrade incrementally** — Don't upgrade all dependencies at once; start with patch and minor versions before tackling major upgrades.
3. **Review lockfile diffs** — After any dependency change, review the lockfile diff to understand exactly what changed.
4. **Prioritise CVEs by severity** — Use **vulnerability-patcher** to focus on critical and high CVEs first.
5. **Use a staging environment** — Test dependency changes in a staging environment before applying to production builds.
