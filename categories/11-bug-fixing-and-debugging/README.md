# Bug Fixing & Debugging Subagents

Bug Fixing & Debugging subagents diagnose and fix defects in application code. They specialise in tracing errors through complex call chains, interpreting stack traces, analysing logs, and identifying regression-introducing commits. These agents can both diagnose problems (read-only) and fix them (write), always pairing fixes with regression tests to prevent recurrence.

**Risk Tier: 🟡 Tier 2 — Medium** — Modifies source code to fix defects; changes are local and reviewable. Fixes include regression tests.

## When to Use Bug Fixing & Debugging Agents

Use these subagents when you need to:
- **Diagnose a bug** — Systematically trace the root cause of a defect
- **Fix a reported issue** — Implement a fix with a corresponding regression test
- **Interpret stack traces** — Understand complex error output and identify the offending code
- **Analyse log output** — Extract root cause from application or system logs
- **Find regression commits** — Identify which commit introduced a bug
- **Trace errors through layers** — Follow errors through complex call chains and service boundaries

## Available Subagents

### [**bug-fixer**](bug-fixer.md) — Diagnose and fix bugs with regression tests
Takes a bug report, diagnoses the root cause, implements a fix, and writes a regression test to prevent recurrence. Follows a systematic investigation approach before writing any code.

**Use when:** You have a confirmed bug and want both a fix and a test in a single operation.

### [**debugger**](debugger.md) — Systematically diagnose code defects
Works methodically through a defect — reproducing it, isolating variables, testing hypotheses, and identifying the root cause. Produces a diagnosis report before recommending a fix.

**Use when:** A bug is complex or non-obvious and you need systematic investigation before implementing a fix.

### [**error-detective**](error-detective.md) — Trace errors through complex call chains
Follows error propagation through call stacks, async chains, event loops, and service-to-service calls to identify where an error originates. Expert in distinguishing symptoms from root causes.

**Use when:** An error manifests far from its source (e.g. a cryptic exception in middleware caused by bad data in a controller).

### [**log-analyzer**](log-analyzer.md) — Analyse application logs to identify root causes
Parses and analyses application, system, or infrastructure logs to identify error patterns, anomalies, and root causes. Correlates events across log sources and timelines.

**Use when:** A problem is visible in logs but the pattern or cause isn't immediately clear, especially in distributed systems.

### [**regression-hunter**](regression-hunter.md) — Find the commit that introduced a bug
Uses git bisect, blame, and history analysis to identify which commit introduced a regression. Produces a commit reference and explanation of the change that caused the issue.

**Use when:** A bug wasn't present in a previous version and you need to find exactly when and how it was introduced.

### [**stack-trace-interpreter**](stack-trace-interpreter.md) — Parse and explain stack traces
Interprets stack traces from any language or runtime, explains what each frame means, identifies the likely root cause, and suggests fixes. Handles minified JS, async stack traces, and multi-language stacks.

**Use when:** You have a stack trace that's hard to interpret — minified code, unfamiliar framework internals, or async/promise chains.

## Quick Selection Guide

| Task | Subagent | Notes |
|------|----------|-------|
| Fix a known bug with a test | **bug-fixer** | Diagnose + fix + regression test in one pass |
| Systematically investigate a complex bug | **debugger** | Methodical diagnosis before implementing a fix |
| Error manifests far from its source | **error-detective** | Traces propagation through call chains and layers |
| Parse confusing logs | **log-analyzer** | Pattern extraction, anomaly detection, correlation |
| Find which commit broke something | **regression-hunter** | Git bisect, blame, history analysis |
| Understand a cryptic stack trace | **stack-trace-interpreter** | Any language, minified JS, async chains |

## Common Combinations

**"Production incident — find and fix the cause"**
- **log-analyzer** → identify error pattern from logs → **error-detective** → trace to root cause → **bug-fixer** → implement fix and regression test.

**"A test started failing after recent changes"**
- **regression-hunter** → identify offending commit → **debugger** → confirm root cause → **bug-fixer** → fix with test.

**"Cryptic error in a complex system"**
- **stack-trace-interpreter** → explain the stack trace → **error-detective** → trace through layers → **debugger** → systematic diagnosis → **bug-fixer** → fix.

**"Intermittent bug in production"**
- **log-analyzer** → find patterns in log history → **error-detective** → identify race condition or state issue → **debugger** → reproduce and confirm → **bug-fixer** → fix.

## Getting Started

1. **Share the error information** — Provide stack traces, error messages, logs, and steps to reproduce.
2. **Start with diagnosis** — Use **debugger** or **error-detective** before jumping to fixes; understanding the root cause prevents recurring issues.
3. **Always add a regression test** — After fixing a bug, ensure **bug-fixer** or **unit-test-writer** adds a test that would have caught the bug.
4. **Check for related issues** — After fixing, run **code-reviewer** (Analysis category) on the affected area to spot similar patterns.
5. **Document the fix** — Use **adr-author** (Documentation category) for significant architectural issues uncovered during debugging.
