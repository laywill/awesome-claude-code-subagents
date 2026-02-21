# Analysis & Review Subagents

Analysis & Review subagents audit existing code and systems, producing findings and recommendations without making any changes. They are your expert reviewers — catching security vulnerabilities, performance bottlenecks, accessibility violations, and quality gaps before they reach production. All agents in this category are read-only, making them safe to run at any point in your workflow.

**Risk Tier: 🟢 Tier 1 — Low** — Reads code and configurations only; produces findings and recommendations but makes no changes.

## When to Use Analysis & Review Agents

Use these subagents when you need to:
- **Review code quality** — Get expert feedback on PRs, diffs, or entire codebases
- **Find security issues** — Identify vulnerabilities, insecure patterns, and OWASP risks
- **Optimise performance** — Profile bottlenecks and get optimisation recommendations
- **Audit accessibility** — Check UI code against WCAG standards
- **Ensure compliance** — Verify code and processes meet regulatory requirements
- **Assess test coverage** — Identify gaps in your testing strategy
- **Measure code health** — Quantify complexity, coupling, and maintainability

## Available Subagents

### [**accessibility-tester**](accessibility-tester.md) — Audit UI code for WCAG compliance
Reviews UI components, HTML, and CSS for accessibility violations and WCAG 2.1/2.2 compliance. Identifies missing ARIA attributes, colour contrast failures, keyboard navigation issues, and screen reader compatibility problems.

**Use when:** Before shipping UI changes, during accessibility audits, or when you need to understand your a11y posture.

### [**code-reviewer**](code-reviewer.md) — Review PRs and diffs for quality
Provides comprehensive code review feedback covering correctness, style, maintainability, naming conventions, design patterns, and potential bugs. Mimics a senior engineer's PR review.

**Use when:** You want a thorough code review before merging a PR, or need feedback on a code change without a human reviewer available.

### [**complexity-analyzer**](complexity-analyzer.md) — Measure code health metrics
Calculates cyclomatic complexity, coupling metrics, cohesion scores, and other code health indicators. Identifies the most complex and risky modules and produces prioritised refactoring recommendations.

**Use when:** Planning a refactoring initiative, assessing technical debt, or tracking code health trends over time.

### [**compliance-auditor**](compliance-auditor.md) — Audit for regulatory compliance
Reviews code, configurations, and processes against regulatory frameworks (GDPR, HIPAA, SOC 2, PCI-DSS, etc.). Identifies gaps and produces audit-ready compliance reports.

**Use when:** Preparing for a compliance audit, onboarding to a regulated industry, or verifying that data handling practices meet legal requirements.

### [**dependency-auditor**](dependency-auditor.md) — Audit dependencies for security and compliance
Scans project dependencies for known CVEs, deprecated packages, licence incompatibilities, and supply-chain risks. Produces a prioritised list of issues with remediation recommendations.

**Use when:** Before a release, after a `npm audit` / `pip-audit` alert, or as part of regular security hygiene.

### [**performance-engineer**](performance-engineer.md) — Profile and identify bottlenecks
Analyses code for performance issues including algorithmic complexity, database query patterns, memory usage, and caching opportunities. Produces specific, actionable optimisation recommendations.

**Use when:** Users report slow performance, before scaling infrastructure, or when profiling data shows unexpected hotspots.

### [**qa-expert**](qa-expert.md) — Assess overall quality and test gaps
Evaluates overall software quality including test coverage, error handling, edge case coverage, and risk areas. Identifies where the highest-value tests should be added.

**Use when:** Starting a testing initiative, assessing quality before a major release, or auditing a legacy codebase for test gaps.

### [**security-auditor**](security-auditor.md) — Identify security vulnerabilities
Reviews code for security vulnerabilities including OWASP Top 10, injection attacks, authentication issues, secrets in code, and insecure cryptography. Produces findings with severity ratings and remediation guidance.

**Use when:** Before shipping security-sensitive features, during security reviews, or as part of a shift-left security practice.

## Quick Selection Guide

| Task | Subagent | Notes |
|------|----------|-------|
| Pre-merge code review | **code-reviewer** | Covers correctness, style, patterns, and maintainability |
| Find security vulnerabilities | **security-auditor** | OWASP Top 10, injection, auth issues |
| Check package CVEs and licences | **dependency-auditor** | Supply-chain risk, deprecated deps |
| Audit WCAG/a11y compliance | **accessibility-tester** | WCAG 2.1/2.2, ARIA, colour contrast |
| Regulatory compliance check | **compliance-auditor** | GDPR, HIPAA, SOC 2, PCI-DSS |
| Profile performance bottlenecks | **performance-engineer** | Algorithm complexity, query patterns, caching |
| Measure cyclomatic complexity | **complexity-analyzer** | Code health metrics, refactoring priorities |
| Identify test gaps | **qa-expert** | Coverage analysis, edge cases, risk areas |

## Common Combinations

**"Pre-release quality gate"**
- **security-auditor** + **dependency-auditor** + **code-reviewer** + **qa-expert** — Run in parallel for a comprehensive quality and security check before any major release.

**"Technical debt assessment"**
- **complexity-analyzer** → measures code health → **code-reviewer** → identifies patterns causing debt → **performance-engineer** → finds bottlenecks to address first.

**"Accessibility compliance audit"**
- **accessibility-tester** → WCAG findings → **compliance-auditor** → maps to legal requirements (ADA, EN 301 549) → combined report for stakeholders.

**"Security review for a new feature"**
- **security-auditor** → code-level vulnerabilities → **dependency-auditor** → new dependency risks → **compliance-auditor** → data handling compliance.

## Getting Started

1. **Pick your focus area** — Security, quality, performance, accessibility, or compliance; use the Quick Selection Guide to find your agent.
2. **Provide the right context** — Share the relevant code files, PR diffs, or package manifest as applicable.
3. **Combine for completeness** — Run multiple review agents in parallel for a thorough pre-release check.
4. **Act on findings** — Route issues to the appropriate Tier 2 agents (bug-fixer, refactoring-specialist) for remediation.
5. **Track over time** — Re-run regularly to measure improvement in code health and security posture.
