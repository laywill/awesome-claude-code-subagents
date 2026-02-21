# Testing & Quality Assurance Subagents

Testing & QA subagents write and maintain automated tests across all testing levels — from unit tests to end-to-end scenarios. They help you build confidence in your code by increasing coverage, generating realistic test data, and maintaining test suites as your application evolves. All changes are limited to test files and fixtures in the working directory.

**Risk Tier: 🟡 Tier 2 — Medium** — Creates and modifies test files in the working directory; changes are local and reviewable via git diff.

## When to Use Testing & QA Agents

Use these subagents when you need to:
- **Add test coverage** — Write tests for existing untested code paths
- **Implement tests for new features** — Add unit, integration, or E2E tests alongside new code
- **Set up test infrastructure** — Build test frameworks, fixtures, and data factories
- **Maintain test suites** — Update snapshots and fix tests after intentional changes
- **Test system resilience** — Design chaos experiments to verify fault tolerance
- **Fill coverage gaps** — Identify and address the highest-risk untested areas

## Available Subagents

### [**chaos-engineer**](chaos-engineer.md) — Design and run chaos experiments
Designs chaos experiments to test system resilience — network partitions, instance failures, latency injection, and resource exhaustion. Produces chaos test plans with hypothesis, blast radius, and success criteria.

**Use when:** Validating that your system handles failures gracefully, preparing for high-stakes events, or maturing your reliability engineering practice.

### [**coverage-gap-filler**](coverage-gap-filler.md) — Identify and fill test coverage gaps
Analyses code coverage reports to find untested paths, identifies the highest-value gaps based on risk and complexity, and writes tests to close them.

**Use when:** Coverage is below target, before a major release, or after a bug is found in untested code (to prevent regression).

### [**e2e-test-writer**](e2e-test-writer.md) — Write end-to-end tests
Creates end-to-end tests using Playwright, Cypress, or Selenium that simulate real user journeys through the application. Handles authentication, data setup, and cross-browser scenarios.

**Use when:** Testing critical user flows (signup, checkout, core workflows) that must work correctly across browsers and environments.

### [**integration-test-writer**](integration-test-writer.md) — Write integration tests
Writes tests that verify interactions between components, services, or layers — API contracts, database operations, external service integrations, and event-driven flows.

**Use when:** Testing boundaries between services, verifying API contracts, or ensuring components work together correctly in realistic scenarios.

### [**snapshot-updater**](snapshot-updater.md) — Update snapshot tests after intentional changes
Reviews and updates snapshot tests after intentional UI or output changes. Validates that changes are expected and correct before approving snapshot updates.

**Use when:** You've made deliberate UI or output changes that caused snapshot failures and need to update the baseline thoughtfully.

### [**test-automator**](test-automator.md) — Build and maintain test suites and frameworks
Sets up and maintains automated test infrastructure — test frameworks, CI integration, test runners, reporting, and test organisation patterns. Builds the foundation for a scalable testing practice.

**Use when:** Establishing a new testing strategy, migrating to a new testing framework, or improving test infrastructure organisation and performance.

### [**test-fixture-generator**](test-fixture-generator.md) — Generate test data, factories, and fixtures
Creates realistic test data using factory patterns, faker libraries, and domain-appropriate generators. Produces fixtures for databases, API mocks, and file-based test inputs.

**Use when:** Tests need realistic data, you're setting up factories for a new model or entity, or existing test data is too simplistic to catch real bugs.

### [**unit-test-writer**](unit-test-writer.md) — Write unit tests for functions and classes
Writes focused unit tests covering happy paths, edge cases, error conditions, and boundary values for individual functions, methods, and classes.

**Use when:** A function or class lacks tests, after implementing new logic, or when fixing a bug and adding a regression test.

## Quick Selection Guide

| Task | Subagent | Notes |
|------|----------|-------|
| Write tests for a new function | **unit-test-writer** | Happy paths, edge cases, error conditions |
| Test API contracts and service boundaries | **integration-test-writer** | Database, API, and event-driven flow tests |
| Test end-to-end user journeys | **e2e-test-writer** | Playwright/Cypress, multi-browser, auth flows |
| Generate realistic test data | **test-fixture-generator** | Factories, faker data, database seeds |
| Update snapshot test baselines | **snapshot-updater** | After intentional UI or output changes |
| Improve coverage metrics | **coverage-gap-filler** | Risk-based gap prioritisation |
| Set up test infrastructure | **test-automator** | Framework setup, CI integration, organisation |
| Validate resilience to failures | **chaos-engineer** | Network partitions, failure injection |

## Common Combinations

**"Test a new feature thoroughly"**
- **unit-test-writer** → unit tests for business logic → **integration-test-writer** → API and DB boundary tests → **e2e-test-writer** → critical user flows → **test-fixture-generator** → shared test data.

**"Increase test coverage before a release"**
- **coverage-gap-filler** → identifies highest-risk gaps → **unit-test-writer** → fills unit-level gaps → **integration-test-writer** → fills integration gaps.

**"Build a testing foundation for a new project"**
- **test-automator** → framework and CI setup → **test-fixture-generator** → data factories → **unit-test-writer** → first test suite.

**"Validate production resilience"**
- **chaos-engineer** → design experiments → **integration-test-writer** → test failure-mode handling → **sre-engineer** (Production Ops category) → observe in staging.

## Getting Started

1. **Match the test type to the concern** — Unit for logic correctness, integration for boundaries, E2E for user flows, chaos for resilience.
2. **Provide implementation context** — Share the code under test, existing test patterns, and testing framework in use.
3. **Generate fixtures first** — If tests need realistic data, set up **test-fixture-generator** before writing tests.
4. **Integrate with CI** — Use **test-automator** to ensure new tests run automatically on every PR.
5. **Track coverage trends** — Use **coverage-gap-filler** regularly to keep coverage growing in the highest-risk areas.
