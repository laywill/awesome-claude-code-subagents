# Refactoring & Modernisation Subagents

Refactoring & Modernisation subagents restructure and improve existing code without changing observable behaviour. They help you reduce technical debt, migrate to modern patterns, upgrade framework versions, and improve code quality systematically. All changes stay in the local working tree and should be verified by tests before merging.

**Risk Tier: 🟡 Tier 2 — Medium** — Modifies existing source code; changes are local and reviewable. Always run tests after refactoring to verify behaviour is preserved.

## When to Use Refactoring & Modernisation Agents

Use these subagents when you need to:
- **Reduce technical debt** — Systematically address accumulated code quality issues
- **Migrate patterns** — Move from callbacks to async/await, class components to hooks, etc.
- **Upgrade frameworks** — Update to new major versions with breaking changes
- **Modernise language** — Adopt new language features like type hints, generics, or pattern matching
- **Fix lint violations** — Automatically resolve style and formatting issues at scale
- **Modernise legacy systems** — Incrementally improve old codebases toward current standards

## Available Subagents

### [**framework-upgrader**](framework-upgrader.md) — Upgrade framework versions
Upgrades framework dependencies to new major versions, adapts code for breaking API changes, updates configuration, and verifies compatibility. Works with React, Django, Spring, Rails, Angular, and others.

**Use when:** Upgrading to a new major version of a framework that has breaking changes, deprecations, or significant API shifts.

### [**language-modernizer**](language-modernizer.md) — Adopt modern language features
Updates existing code to use modern language features — optional chaining, nullish coalescing, structural pattern matching, type annotations, generics, and more. Improves readability and safety without changing behaviour.

**Use when:** Your codebase uses outdated syntax or missed new language features in an upgrade, and you want to modernise it incrementally.

### [**legacy-modernizer**](legacy-modernizer.md) — Modernise legacy codebases
Takes a holistic approach to modernising legacy systems — updating dependencies, replacing deprecated APIs, improving structure, and incrementally applying modern practices. Prioritises changes by risk and value.

**Use when:** Working with an older codebase that needs broad improvement across multiple dimensions (language version, frameworks, patterns, testing).

### [**linter-fixer**](linter-fixer.md) — Auto-fix lint and formatter violations
Applies automatic fixes for ESLint, Pylint, RuboCop, golangci-lint, and other linter violations across the codebase. Handles both auto-fixable rules and more complex manual fixes.

**Use when:** Onboarding a linter to an existing codebase, cleaning up accumulated violations, or enforcing a consistent code style.

### [**pattern-migrator**](pattern-migrator.md) — Migrate code between patterns
Systematically migrates code from one pattern to another — callbacks to async/await, class components to function components, mutable to immutable data patterns, synchronous to event-driven, etc.

**Use when:** You want to standardise on a new pattern across a large codebase, replacing an old approach that's scattered through many files.

### [**refactoring-specialist**](refactoring-specialist.md) — Apply targeted refactorings
Applies specific refactoring techniques — extract method, rename variable, introduce parameter object, replace conditional with polymorphism, and other Fowler-style refactorings — with precision and care.

**Use when:** A specific piece of code needs structural improvement (too long, too complex, poorly named) and you want targeted, safe changes.

### [**tech-debt-reducer**](tech-debt-reducer.md) — Identify and resolve tech debt systematically
Surveys a codebase for tech debt (duplicated code, magic numbers, poor abstractions, missing error handling), prioritises items by impact and risk, and systematically works through the backlog.

**Use when:** Starting a tech debt initiative, preparing a codebase for a new feature, or when code quality is slowing development velocity.

## Quick Selection Guide

| Task | Subagent | Notes |
|------|----------|-------|
| Upgrade to a new major framework version | **framework-upgrader** | Handles breaking API changes and config updates |
| Adopt new language syntax features | **language-modernizer** | Optional chaining, type hints, pattern matching, etc. |
| Broadly improve a legacy codebase | **legacy-modernizer** | Holistic, prioritised modernisation approach |
| Fix linter/formatter violations at scale | **linter-fixer** | ESLint, Pylint, golangci-lint, RuboCop |
| Replace callbacks with async/await | **pattern-migrator** | Systematic pattern replacement across files |
| Refactor a specific complex function | **refactoring-specialist** | Targeted Fowler-style refactoring techniques |
| Tackle accumulated technical debt | **tech-debt-reducer** | Prioritised debt inventory and systematic resolution |

## Common Combinations

**"Upgrade a major framework and clean up the codebase"**
- **framework-upgrader** → API changes → **language-modernizer** → adopt new idioms → **linter-fixer** → style cleanup → **unit-test-writer** (Testing category) → verify behaviour.

**"Modernise a legacy codebase incrementally"**
- **legacy-modernizer** → assessment and priorities → **pattern-migrator** → key pattern migrations → **tech-debt-reducer** → systematic debt reduction → **complexity-analyzer** (Analysis category) → measure improvement.

**"Prepare a codebase for a new feature"**
- **tech-debt-reducer** → clean up affected areas → **refactoring-specialist** → targeted improvements → **coverage-gap-filler** (Testing category) → add tests before new work.

**"Standardise async patterns across codebase"**
- **pattern-migrator** → callbacks → async/await → **linter-fixer** → enforce no-promise-return-in-callbacks rule → **code-reviewer** (Analysis category) → verify correctness.

## Getting Started

1. **Run tests first** — Before refactoring, ensure you have adequate test coverage so you can verify behaviour is preserved.
2. **Choose your scope** — Targeted refactoring (single function/class) vs. broad modernisation (whole codebase) call for different agents.
3. **Work incrementally** — Break large refactoring efforts into smaller PRs; each should pass tests independently.
4. **Use complexity-analyzer** — Run the Analysis & Review complexity agent before and after to measure improvement.
5. **Commit at safe points** — Commit after each logical refactoring step so you can revert to any known-good state.
