# CLAUDE.md

## Role & Communication Style

You are a senior software engineer collaborating with a peer. Prioritize thorough planning and alignment before implementation. Approach conversations as technical discussions, not as an assistant serving requests.

- **Plan first**: discuss the approach, surface the implementation choices, present options with trade-offs, confirm alignment, *then* write code.
- If you discover an unforeseen issue mid-implementation, stop and discuss.
- Push back on flawed logic. Don't open with praise, don't validate every decision as "absolutely right", don't agree just to be agreeable.
- When a change is purely stylistic or preferential, say so ("Sure, I'll use that approach") rather than dressing it as an objective improvement.
- Assume common programming concepts are understood. Be direct with feedback rather than couching it in niceties.

## Project Overview

This is a curated collection of Claude Code subagent definitions — specialized AI assistants for specific development tasks. Subagents are markdown files with YAML frontmatter that Claude Code loads as agents.

There is no build system. The "source" is markdown; correctness means the manifests, READMEs, and agent files stay in sync, which `scripts/validate-catalog.sh` checks and CI enforces (see Verification below). The Python under `scripts/` that does the checking has its own tests and lint (see Linting).

## Repository Structure

24 risk-tiered categories under `categories/`:

```text
01-research-and-discovery/              # 🟢 Tier 1 | Research & exploration
02-architecture-and-design/             # 🟢 Tier 1 | System design
03-analysis-and-review/                 # 🟢 Tier 1 | Code analysis & audit
04-documentation/                       # 🟢 Tier 1 | Docs & guides
05-planning-and-estimation/             # 🟢 Tier 1 | Project planning
06-business-and-product/                # 🟢 Tier 1 | Business strategy
07-language-and-framework-specialists/  # 🟡 Tier 2 | Language experts
08-general-development/                 # 🟡 Tier 2 | Core development roles
09-testing-and-qa/                      # 🟡 Tier 2 | Testing & QA
10-refactoring-and-modernization/       # 🟡 Tier 2 | Code improvement
11-bug-fixing-and-debugging/            # 🟡 Tier 2 | Debugging & diagnostics
12-frontend-and-ui/                     # 🟡 Tier 2 | Frontend specialization
13-developer-experience-and-tooling/    # 🟡 Tier 2 | DX & tools
14-data-and-database/                   # 🟠 Tier 3 | Data layer
15-data-science-and-ai/                 # 🟠 Tier 3 | ML & AI
16-dependency-and-package-management/   # 🟠 Tier 3 | Dependency management
17-build-and-ci-cd/                     # 🟠 Tier 3 | Build automation
18-api-and-service-integration/         # 🔴 Tier 4 | API integration
19-infrastructure-as-code/              # 🔴 Tier 4 | IaC & cloud
20-security-and-secrets/                # 🔴 Tier 4 | Security hardening
21-specialized-domains/                 # 🔴 Tier 4 | Niche domains
22-deployment-and-release/              # ⛔ Tier 5 | Production deployment
23-production-ops-and-observability/    # ⛔ Tier 5 | Production operations
24-production-data-ops/                 # ⛔ Tier 5 | Production data
```

**Risk Tier Guide:** Tier 1 (🟢) read-only/advisory · Tier 2 (🟡) local code changes · Tier 3 (🟠) data/dependencies/build · Tier 4 (🔴) external systems & infrastructure · Tier 5 (⛔) production changes.

Other top-level pieces:

- `.claude-plugin/marketplace.json` — marketplace manifest; one entry per category, each pointing at `./categories/NN-.../`
- `categories/NN-*/.claude-plugin/plugin.json` — per-category plugin manifest listing every agent file explicitly
- `.claude/agents/` — repo-maintenance agents used *on* this repo. `agent-uplifter` applies the v3 template to one agent file end to end, stamps it and lints it clean; the per-category uplifts run one per file, and the calling session owns everything outside the file (four places, allowlist, ratchet, version bump). For bulk description rewrites without Claude tokens, use `scripts/compress-descriptions.py`.
- `install-agents.sh` — interactive installer; works from a clone (local mode) or standalone via the GitHub API (remote mode)
- `tools/` — Claude Code skills that browse/fetch the catalog, installed to `~/.claude/commands/`
- `AGENT_SECURITY_GUIDELINES.md` — authoritative keep/delete policy for safety content in agent files (read before writing any)

## A New Agent Must Beat the Built-ins

Claude Code ships its own subagents: `Explore` (read-only codebase search, skips CLAUDE.md and git status), `Plan` (read-only research in plan mode), `general-purpose` (every tool, loads CLAUDE.md and git status) and `claude` (the catch-all). An agent that restates one of them is not free: its description sits in every session's context, and it is one more near-match for delegation to pick wrongly.

- A new agent's PR states in a sentence or two what it does that `Explore` and plain Claude with the same tools do not: domain method, a checkable output, a tool restriction that matters. If that comes out empty, don't add the agent. #322 records this test applied to category 01.
- Apply the same test against the catalog. `validate-catalog.sh` catches two agents with the same name, not two agents with the same job under different names.
- Don't reuse a built-in name (`Explore`, `Plan`, `general-purpose`, `claude`) unless the agent is deliberately replacing that built-in. A user or project agent with the same name overrides it; the docs don't say a plugin agent does, so a replacement only works when installed as a file. Say so in the PR when that is the intent.

## Every Agent Exists in Four Places

Adding, renaming, moving, or deleting an agent means updating all four, or the plugin ships broken:

1. `categories/NN-category/agent-name.md` — the definition itself
2. `categories/NN-category/.claude-plugin/plugin.json` — add `"./agent-name.md"` to the `agents` array (this list is explicit, not a glob)
3. `categories/NN-category/README.md` — description under "Available Subagents", plus the "Quick Selection Guide" table row
4. Root `README.md` — `- [**agent-name**](categories/NN-category/agent-name.md) - Brief description`, alphabetical within the category

Exception to 4: category 07 is summarised in the root README with a "View all 34 language specialists →" link rather than itemised, so a new language specialist adds nothing there — update the count and the inline list instead.

Bump versions when publishing changes: the category's `plugin.json` `version`, and `.claude-plugin/marketplace.json` `metadata.version`. The exception is work on an open release train (see Git Workflow), where the train sets every version once and PRs into it change none.

## Agent File Format

`templates/agent-template.md` is the v3 agent file for every tier. Copy it, fill it in, and delete its `TEMPLATE:` guidance. Its shape:

```markdown
---
name: agent-name
description: "Task type first, then the nouns a user types; one sentence, at most 250 characters"
tools: Read, Grep, Glob
model: sonnet
color: green                                # optional fields per the tier table below
disallowedTools: Write, Edit, NotebookEdit, Bash
---

You are a <senior role> who <does what, in one line>.

## Scope
## How you work                             # numbered list
## <Domain section>                         # optional, any number, only here
## Expert practice
## Output
<!-- BEGIN GENERATED: operating-notes tier=N -->
## Operating notes
<!-- END GENERATED: operating-notes -->
## Rollback                                 # conditional, see Body skeleton
## Approval gates                           # conditional, see Body skeleton
```

All four frontmatter keys are required on every agent file — `name`, `description`, `tools`, `model` — although Claude Code itself requires only the first two. `name` must match the filename.

- **`description`**: a single sentence Claude Code uses for auto-selection. At most 250 characters; see Description style.
- **`tools`**: assign the minimum for the role. If an agent doesn't need Bash, don't give it Bash — this is the single biggest risk reducer. Always set it: an explicit list already excludes every MCP tool, so `mcp__*` in `disallowedTools` is redundant here. Omitting `tools` inherits everything, MCP included. The rows in the table below are starting points, not entitlements: `WebFetch` and `WebSearch` stay only where a step in `## How you work` uses them.
- **`model`**: an alias — `haiku`, `sonnet` or `opus`. No full model IDs (they go stale), no `fable` or `inherit`. Frontmatter outranks the user's `CLAUDE_CODE_SUBAGENT_MODEL`, so an `opus` pin overrides a user who set a cheaper model:
  - `haiku`: narrow, mechanical roles where the output follows from the input with little judgement (formatting, lookup, changelogs). Never set `effort` on it; Haiku doesn't support effort.
  - `sonnet`: the default. When a mistake would be costly but tools, tests or a plan output can check the result, use `sonnet` + `effort: high` rather than `opus`.
  - `opus`: only when both of these hold, stated in the PR. First, the output is a judgement that is costly to get wrong (architecture decisions, security or threat assessment, compliance or financial-risk findings). Second, a wrong answer would pass every check the agent or its caller can run (tests, linters, scanners, plan output), because the error is in the reasoning (a bad trade-off, a missed threat), not in anything a command reports.
  - Test the second criterion against the error the first names, not against incidental errors a tool happens to catch. `oasdiff` catching a breaking change doesn't rescue a wrong service boundary, so `microservices-architect` is `opus`; `spectral` and `oasdiff` do check most of what `api-designer` hands back, so it is `sonnet` + `effort: high`. "A human reviews it" is not a check: every output is reviewed. "Each finding cites a file the caller can open" is one. Every uplift PR states the model argument in one line per agent.

| Role type | `tools` |
| --- | --- |
| Read-only (reviewers, auditors) | `Read, Grep, Glob` |
| Research (analysts) | `Read, Grep, Glob, WebFetch, WebSearch` |
| Documentation | `Read, Write, Edit, Glob, Grep` |
| Code writers / infrastructure | `Read, Write, Edit, Bash, Glob, Grep` |

A **read-only role** is one whose deliverable is findings returned to the conversation, so its job is done with the file tree unchanged. Declare it with `disallowedTools: Write, Edit, NotebookEdit`: that is the explicit read-only marker the validator checks, since a role can't be inferred from a name. Listing a tool in both `tools` and `disallowedTools` is an error. A specifier such as `Bash(git push *)` removes the whole tool, so don't use one.

### Optional fields by tier

Tier here is the **category tier**, from Repository Structure. Frontmatter always follows it; stamp overrides never change it (see Category tier and stamp tier, below).

| Field | Tier 1 🟢 | Tier 2 🟡 | Tier 3 🟠 | Tier 4 🔴 | Tier 5 ⛔ |
| --- | --- | --- | --- | --- | --- |
| `color` | `green` | `yellow` | `orange` | `red` | `purple` |
| `disallowedTools` | `Bash`, unless the role must run commands to produce its findings (tests, profilers, `git log`); read-only roles add `Write, Edit, NotebookEdit` | read-only roles: `Write, Edit, NotebookEdit` | same | same | same |
| `effort` | omit | omit | omit | `high` on `sonnet` | `high` on `sonnet` |
| `maxTurns` | omit | omit | omit | `40` | `25` |

- **`color`**: the tier, so it is visible while the agent runs. The eight valid values are `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan`.
- **`effort`**: omit it so the user's session level applies, with two exceptions, each set to `high` and each on `sonnet` only: Tier 4–5 agents, and a `sonnet` agent that fails only the second `opus` criterion. On `sonnet`, `high` is already the model default, so its effect is to override a user who lowered session effort. Never set it on `opus`: the session default is effective, and `high` on Opus burns tokens that only a particularly hard task justifies, which is the caller's call. Never set it on `haiku`, and don't use `low`, `medium`, `xhigh` or `max`.
- **`maxTurns`**: a hard stop. The output comes back marked partial and Claude can resume the agent, so treat the cap as a checkpoint where a human sees progress against external or production systems. The cap can fire between any two tool calls, so Tier 4–5 bodies must leave the target system consistent after each step and say what state it is in. A normal task fits well inside it; a retry or polling loop hits it. Override it per agent only with a reason.

### Frontmatter fields

Claude Code recognises 18 fields and silently ignores unknown or misspelled ones.

| Field | Values | Policy |
| --- | --- | --- |
| `name`, `description`, `tools`, `model` | see above | required |
| `color`, `disallowedTools`, `effort`, `maxTurns` | `effort`: `low`, `medium`, `high`, `xhigh`, `max`; `maxTurns`: integer | per the tier table |
| `isolation` | `worktree` | not used. Subagent worktrees branch from the **default branch**, not the caller's `HEAD`, unless the user set `worktree.baseRef: "head"`, so a pinned agent silently works on stale code when invoked on in-progress work. Whether a clean checkout is safe depends on the invocation, so the caller passes `isolation` per call |
| `memory` | `user`, `project`, `local` | not used. It writes into the user's home or repo, and it adds `Read, Write, Edit` automatically, which undermines a read-only role |
| `skills` | skill names | not used. The catalog ships no skills, and preloading a user's skills by name isn't portable. Revisit in a spike |
| `background` | `true` | not used. Foreground or background is the caller's choice |
| `omitClaudeMd` | `true` | not used. The project's conventions matter to almost every agent here |
| `experimental` | `cacheTtl: 5m \| 1h` | not used. The cache TTL is a billing choice for the user |
| `permissionMode`, `hooks`, `mcpServers`, `initialPrompt` | — | **forbidden**. Ignored in plugin agents, so they would ship as dead config |

### Description style

Interim, until #316 measures a better one.

- One sentence, **at most 250 characters**, with no line breaks and no `<example>` blocks.
- The task type first, as an imperative verb ("Review…", "Migrate…", "Write…", not "Reviews…"), then the concrete nouns a user types: languages, frameworks, tools, file types.
- Start with `Use proactively when…` only for an agent that should fire without being named. Everything else leaves it out.
- `scripts/compress-descriptions.py` (#362) rewrites a description to this style with a local model.

### Category tier and stamp tier

Two tiers apply to every agent file, and they drive different things:

- **Category tier** comes from the category directory (Repository Structure) and nothing else. It drives the **frontmatter**: `color`, `effort`, `maxTurns`, and the Tier 1 `Bash` rule in `disallowedTools`. No override changes it.
- **Stamp tier** is the `N` in the stamped block. It drives the **body**: which operating notes are stamped, and whether Expert practice, Rollback and Approval gates are required, optional or absent. It equals the category tier except for two overrides:
  - **Read-only override:** a Tier 2–5 agent whose `tools` hold none of `Bash`, `Write`, `Edit` or `NotebookEdit` takes `tier=1`, and has no Rollback. The test is on `tools` alone. The `disallowedTools` read-only marker plays no part in choosing the stamp, so `penetration-tester` (`Read, Grep, Glob, Bash`) keeps its category's stamp.
  - **Per-file override:** where the category is right but the stamp isn't, an entry in `scripts/lint-allowlist.txt` maps the file to another stamp tier with a one-line reason, e.g. `chaos-engineer: tier=5 # injects faults into running systems, not local code`. The uplift PR that needs an override adds the entry.

**What a Tier 1 agent writes.** The tier-1 notes allow "the documents you were asked for" and hand "code or config changes" back. A specification that *is* the design counts as a document: prose docs, ADRs, plans, diagrams, OpenAPI or AsyncAPI, GraphQL SDL, a schema expressed as DDL or an ERD. Implementation and operational config are returned as proposals in the report: resolvers, tests, migrations, Kubernetes manifests, mesh config, mock servers, docs-site generator config, CI config. Don't reach for a `tier=2` override to let a Tier 1 agent write them; an agent whose job is implementation belongs in a Tier 2 category.

### Body skeleton

Everything after the frontmatter follows this skeleton. `scripts/validate-catalog.sh` lints it, so the rules are exact:

| # | Heading, exact and case-sensitive | Status | Content |
| --- | --- | --- | --- |
| 0 | none: the opening paragraph | required | `You are a <role> who <scope>` |
| 1 | `## Scope` | required | what the agent does, and what it hands back to its caller instead |
| 2 | `## How you work` | required | a numbered list and nothing else (below) |
| 3 | any other H2 | optional, zero or more | domain depth: the agent's method, knowledge and checkable criteria |
| 4 | `## Expert practice` | required; optional where the stamp is `tier=1` | what a senior practitioner does that a generalist forgets, in the domain's own commands |
| 5 | `## Output` | required | what the final report contains |
| 6 | `## Operating notes`, inside the stamped block | required, exactly one | generated, never hand-edited (below) |
| 7 | `## Rollback` | required where the stamp is `tier=3`, `4` or `5`; optional at `tier=2`; absent at `tier=1` | real CLI commands that undo this agent's changes |
| 8 | `## Approval gates` | optional; absent at `tier=1` | one line per real domain process: *trigger → who confirms* |

Lint rules. Every rule applies outside fenced code blocks only:

- **Fences:** a fence opens on a line whose first non-space characters are three or more backticks or three or more tildes, at any indent, so fences inside list items count. It closes on a line holding only the same character, repeated at least as many times as the opener. Four-backtick fences occur, so track the character and the length.
- **Opening paragraph (row 0):** the first non-blank line after the closing `---` of the frontmatter matches `^You are an?[ ]`. It starts the only paragraph before `## Scope`; nothing else precedes `## Scope`, not even an H3. The wording after "You are a" ("who …") is checked in review.
- **Headings:** ATX only: `##` plus one space for H2, `###` plus one space for H3. Setext headings (a line of `=` or `-` under text) are banned. H1 and H4 or deeper are banned.
- **Fixed headings** (rows 1, 2 and 4–8) match exactly, case-sensitively, with a single space after `##` and no trailing text. Each appears at most once, in the table's order. An H2 that equals a fixed heading once case and whitespace are ignored, but not exactly (`## Expert Practice`, `##  Scope`), is an error, not a domain section.
- **Domain H2s** (row 3) sit between `## How you work` and `## Expert practice`, or `## Output` where Expert practice is absent. Nowhere else. A domain H2 may not use a banned heading (Banned content, below), including `## Development Workflow`.
- **H3** is allowed under any H2 except `## How you work` (its list rule excludes it) and inside the stamped block.
- **`## How you work`:** after the heading, only blank lines, then a line matching `^1\.[ ]`. From there to the next H2, every non-blank line either matches `^[0-9]+\.[ ]` or starts with at least 3 spaces (a continuation line, a nested list or an indented fence). `1)` items and unindented (lazy) continuation lines are not allowed.
- **Stamped block:** the `BEGIN` line comes after the `## Output` section's content, and only blank lines sit between the `END` line and the next H2 or the end of the file. The region between the markers is compared byte for byte with `templates/operating-notes-tierN.md`.

Review rules, not linted:

- **Rollback in Tier 2** is for state git doesn't track: a local database migration, an installed toolchain, artifacts outside the repo. Working-tree changes are undone with git, and every model knows how, so they get no section.
- **Approval gates** only where the domain has a real human process the agent can't satisfy alone (a DBA, a data owner, a maintenance window, rules of engagement). `AGENT_SECURITY_GUIDELINES.md` §3 has the three tests.
- **Output** should end with the recommended sentence "Report only what you did and observed. Never report a count, percentage, score or duration you did not measure." It is recommended, not required, and not linted.
- **Body length is not the enemy; generic text is.** The body costs nothing until the agent runs. A sentence that would read the same in `content-marketer` and in `kubernetes-specialist` goes.
- **No bare keyword lists.** A list of the domain's own named technologies (frameworks, CLIs, services) is domain depth and stays. A bullet that is only an abstract noun phrase ("Caching strategies", "DRY/KISS/YAGNI", "Radar charts") with no criterion, evidence source or command is rewritten into a checkable criterion ("every cache names its invalidation trigger") or cut. The Markup conversion below changes the shape of a list, not whether it earns its place.
- **Say each point once.** Expert practice doesn't repeat a bullet from a domain section; keep it where it fits best.
- **Never ask for what the tools can't do.** A step or an Output line that needs Bash (a build, a link check, `git log`) in an agent without Bash names the command for the caller to run instead of running it or reporting its output. An agent without Bash or web tools doesn't source from "the issue tracker" or "git history"; it reads the repo and what the caller passes in.
- **Say where a document goes.** Every agent that writes a document writes it at the path the task gives, or, with no path, returns it in the report.

### Agents report to their caller

A subagent can't talk to the user. It runs to the end and returns one final message to the session that called it; nothing it writes before then reaches anyone, and it can't wait for an answer. Write every agent file for that:

- **Never "ask the user" or "confirm with the user".** When something needed is missing, the agent proceeds on a stated default where a wrong guess is cheap to redo (local, uncommitted work, or a read-only answer). Otherwise it stops and returns what it needs: an external or production target, an irreversible step, or work a wrong guess would waste. The caller answers, from the conversation or by asking the user, and resumes it.
- **Hard-to-reverse design choices are the job, not a stop trigger.** A design agent choosing a resource shape, an entity key, a service boundary or a partition key doesn't stop at it: it proposes the choice, what reversing it would cost and the alternative it rejected, and lists it in Output as needing the caller's confirmation. It stops only when an input that choice depends on is missing. For a Tier 1 agent a wrong guess usually costs a rerun, so a stated default is usually right.
- **Write "the caller", not "the user"**, wherever the agent file means whoever invoked it, and don't explain the mechanism in the file ("You can't ask the user mid-task"); state the behaviour.
- **Anything the user must see is named in `## Output`.** An assumption, a default chosen, a warning about the user's choice, a risk found along the way: if Output doesn't list it, the final report can drop it.
- **Approval gates stop and hand back.** At a gate's trigger the agent stops and returns the operation and who must confirm it, unless the task already says it is confirmed or that no such process exists.

The stamped operating notes already follow this ("stop and report what you need", "return the plan"). #370 records how the template got it wrong.

### How you work

- Required in every file, and always a numbered list, per the lint rule above.
- No inline `When invoked: (1)… (2)…` sentences, no `When invoked:` or `On invocation:` labels anywhere in the file. The heading replaces them. Domain-specific phases from an old `## Development Workflow` fold into these steps or into Expert practice.
- Step 1 says where the context comes from (the conversation, the codebase, the issue tracker) and what to do when something needed is missing: proceed on a stated default, or stop and return what's needed (Agents report to their caller, above). Nothing else supplies it: the context-manager query that the upstream "gather context" step relied on is gone (#315). Checked in review.
- The remaining steps are domain-specific and use the domain's own commands and file names. Checked in review.

### Markup

Linted:

- The heading rules above: ATX only, H2 and H3 only, no setext.
- No line that is only bold text: `**Label**` or `**Label**:` alone on a line (markdownlint MD036). Use an H3.
- The only HTML comments are the stamp markers. Every `TEMPLATE:` line from the template is deleted.

Review only:

- `**Label:** text` inside a list item is fine.
- Plain `Label:` lines and `**Label:** text` paragraphs outside a list, the main form of domain depth in the upstream files, are converted during uplift: `Label: a, b, c` becomes `### Label` with one bullet per item, under a domain H2.
- Fenced code blocks name their language (markdownlint MD040, report-only).

### Operating notes (stamped)

- The block is exactly this, between `## Output` and `## Rollback`:

  ```markdown
  <!-- BEGIN GENERATED: operating-notes tier=N -->
  ## Operating notes

  <wording for tier N>
  <!-- END GENERATED: operating-notes -->
  ```

- The `END` marker names its block, so that other stamp kinds can coexist later without ambiguity.
- The wording is `AGENT_SECURITY_GUIDELINES.md` §7, stamped from `templates/operating-notes-tierN.md` by `python3 scripts/stamp_sections.py <file...>`. It is never hand-edited, and the validator fails on drift, and on a template that no longer matches §7.
- `N` is the stamp tier (see Category tier and stamp tier, above).
- The block **replaces** hand-written `Environment Note`, `Environment adaptability` and `Environment adaptability & scope` preambles. Delete them; don't keep them alongside.

### Banned content

`scripts/validate-catalog.sh` is the enforcing copy of everything here except the Review line.

- **Enforced in every category:** the headings `Communication Protocol`, `Progress Tracking`, `Integration with Other Agents` and `Audit Logging`, at any level; the phrases `requesting_agent`, `request_type`, `Delivery notification`, `Progress tracking:`, `integration with other agents`, `query context manager` and `context manager for`.
- **Retired by #354, linted through the ratchet:** the `Security Safeguards` heading and its subsections (`Input Validation`, `Rollback Procedures`, `Approval Gates`, `Emergency Stop`, `Blast Radius Controls`); `EMERGENCY_STOP` stop-file checks; the generic gate phrases `Change ticket` and `read -p`; `-auto-approve` in a rollback section; hand-written `Environment Note` and `Environment adaptability` preambles (above). Generic on-call or peer-review gates are caught in review.
- **Structural, linted through the ratchet:** the heading `## Development Workflow`; `When invoked:` and `On invocation:`; any breach of the Body skeleton lint rules; leftover `TEMPLATE:` guidance; and descriptions over 250 characters or holding `<example>` blocks.
- **Review:** invented metrics (counts, percentages, scores, durations or thresholds the agent can't measure or that have no source, such as "coverage > 80% confirmed"), embedded validation or logging code, and inter-agent coordination prose.

## Security Safeguards

`AGENT_SECURITY_GUIDELINES.md` is the source of truth. It has a keep/delete test for any piece of safeguard content, with worked examples. The essentials:

What protects a user is the permission mode, not agent prose. In Manual mode the user approves each command. In auto mode, the built-in default on Pro, Max and Team, a classifier blocks force pushes, production deploys, `terraform destroy`, IAM grants, secret-manager writes and similar actions. Deny rules apply in every mode. So agent files carry what makes the agent competent, not warnings.

| Content | Tier 1 | Tier 2 | Tier 3 | Tier 4 | Tier 5 |
| --- | :-: | :-: | :-: | :-: | :-: |
| Operating notes (stamped from template, never hand-edited) | ✓ | ✓ | ✓ | ✓ | ✓ |
| Expert practice (dry-run, plan before apply, backup, confirm target, pin versions) | if relevant | ✓ | ✓ | ✓ | ✓ |
| Rollback (real CLI commands for the domain) | — | state outside git only | ✓ | ✓ | ✓ |
| Domain approval gates (a real human process, e.g. DBA sign-off) | — | rarely | if real | if real | if real |

The tiers in this table are stamp tiers: a Tier 2–5 agent whose `tools` hold none of `Bash`, `Write`, `Edit` or `NotebookEdit` takes the Tier 1 notes and has no Rollback section (see Category tier and stamp tier).

**Delete on sight:** generic Emergency Stop (stop-file checks), generic Blast Radius Controls, generic Approval Gates (change ticket, on-call, `read -p CONFIRM`), Input Validation that amounts to "validate inputs", and invented thresholds ("rollback in < 5 min").

**Enforce through frontmatter, not prose:** `tools`, `disallowedTools`, `maxTurns`. (`isolation` is not set in agent files; see Frontmatter fields.) Plugin agents ignore `permissionMode`, `hooks`, `mcpServers` and `initialPrompt`, and `permissionMode` can't tighten a session that's already in auto, acceptEdits or bypass mode. Never use any of the four.

Two rules that get violated repeatedly:

- **Never add Audit Logging.** Audit trails belong to the platform and the user's own hooks. Code-level logging follows the user's requirements, not agent-file mandates.
- **Never embed implementation code** for validation, logging, gates or stop checks. The agent writes that at runtime, and embedded code bloats the definition without enforcing anything. Rollback *CLI commands* are the exception: they are operational and belong in the file.

## Verification

```bash
./scripts/validate-catalog.sh
```

One script, checked in, run by both humans and CI — `.github/workflows/validate.yml` invokes it on every pull request and on pushes to `main`. Keep the checks in the script; do not re-inline them here, or the documented copy becomes the stale one.

It reports every failure it finds rather than stopping at the first, and exits non-zero if any fired. What it enforces everywhere, regardless of category:

| Check | Catches |
| --- | --- |
| plugin.json lists exactly the category's agent files | step 2 of "Four Places" — compared by name, so a typo'd entry is caught even though the counts still match |
| All four frontmatter keys present | a missing `name`, `description`, `tools` or `model` |
| Frontmatter `name` matches the filename | an agent Claude Code cannot resolve |
| `name` is unique across all 24 categories | one agent silently shadowing another once both plugins are installed |
| Every agent documented in its category README | step 3 of "Four Places" |
| Every agent linked from the root README | step 4 of "Four Places" — category 07 is skipped, per the exception above |
| Root README `categories/...` links resolve | a link to a moved or deleted file |
| marketplace.json covers each category exactly once | a category that ships unreachable |
| Badge and marketplace counts match the real file count | the advertised subagent total drifting from reality |
| Agent files carry no banned scaffolding headings or phrases | `## Communication Protocol`, context-manager queries, progress JSON and delivery notifications creeping back in (removed in #315) |
| `templates/operating-notes-tierN.md` match `AGENT_SECURITY_GUIDELINES.md` §7 | the stamped wording drifting from the policy it comes from |
| A stamped operating-notes block, where one exists, matches its template | a hand-edited block, a wrong `tier=N`, or a missing or repeated marker |
| `scripts/lint-enforced-categories.txt` and `scripts/lint-allowlist.txt` are well-formed | a misspelt category that silently enforces nothing; an allowlist entry with no reason, an unknown rule, or an agent that no longer exists |

Adding an agent therefore means updating the count in the README badge and in `.claude-plugin/marketplace.json`, not just the four places.

### Content lint and the per-category ratchet

The rules marked as linted under Agent File Format (frontmatter keys, values and tier rules; Body skeleton; Markup; Operating notes; the Retired and Structural lines of Banned content) are checked by `scripts/agent_lint.py`, one file at a time. It parses each file once into `scripts/lint_model.py`'s immutable model, then runs the rules in `scripts/lint_frontmatter.py`, `scripts/lint_body.py` and `scripts/lint_content.py`, which are functions over that model and never re-parse text. `scripts/catalog_lint.py` runs it over the catalog and applies the ratchet, and `validate-catalog.sh` runs that. The stamper reads files through the same model, so the two can't disagree about a heading, a fence or a stamp marker. Most agent files predate v3, so these findings are ratcheted:

- **`scripts/lint-enforced-categories.txt`** lists category directories. In a listed category every content finding fails the build; elsewhere it is a warning. Each category's v3 uplift adds its category as its last step; #328 requires all 24 and removes the ratchet.
- Two exceptions to the ratchet: a stamped block that exists but has drifted or is malformed always fails, and the invented-metric heuristic (`metric-invented`) only ever warns.
- Warnings print as counts by rule and by category. `./scripts/validate-catalog.sh --verbose` lists every one; `./scripts/validate-catalog.sh 03-analysis-and-review` lists that category's. Arguments change what is printed, never what fails.
- **`scripts/lint-allowlist.txt`** holds the reviewed per-file exceptions, one per line as `<agent-name>: <rule> # <reason>`: `tier=N` (stamp override), `tier1-bash`, and `sonnet-instead-of-opus`. The reason is mandatory.
- **`python3 scripts/catalog_lint.py --file <path>`** (repeatable) lints only the named agent files, reading no other agent file, and prints every finding for them in full, warnings included, then a count. The ratchet still decides FAIL or WARN. Unlike the arguments above, it changes what fails, so `validate-catalog.sh` refuses it. `agent-uplifter` uses it, since parallel uplifts are editing the sibling files.
- **`python3 scripts/stamp_sections.py <file...>`** writes or refreshes a file's stamped block, choosing the stamp tier as the validator does. It needs explicit paths, and a second run changes nothing.
- **`scripts/lint-enforced-markdown.sh`** runs markdownlint and cspell, blocking, over the listed categories only.
- **Cutover (#328):** once all 24 categories are listed, delete the ratchet file, `scripts/lint-enforced-markdown.sh` and the `enforced-markdown` job in `validate.yml`; make content findings fail everywhere; and remove `MARKDOWN_MARKDOWNLINT` and `SPELL_CSPELL` from `DISABLE_ERRORS_LINTERS` in `.mega-linter.yml`, so MegaLinter blocks on them directly.

The Python scripts use the standard library only. `tests/` covers them with pytest (`python3 -m pytest`, configured in `pyproject.toml`), and CI runs the tests in `validate.yml` before the catalog check. Change a lint rule by changing its test first. Tests that need a real local Ollama server (`compress-descriptions.py`'s contract with its API) are marked `ollama` and deselected by default; run `python3 -m pytest -m ollama` after changing how the script talks to Ollama.

### Linting

MegaLinter (`.mega-linter.yml`, `.github/workflows/mega-linter.yml`) covers generic file hygiene; `validate-catalog.sh` covers what is specific to this catalog; `scripts/lint-python.sh` covers Python. Don't duplicate a check across them.

**Python** is not linted by MegaLinter (`DISABLE: PYTHON`). `scripts/lint-python.sh` runs ruff, black, isort, flake8, pylint, `mypy --strict`, bandit and radon over all of `scripts/` and `tests/`, from the `python-lint` job in `validate.yml`, on every run. Tool versions are pinned in `requirements-dev.txt` (Dependabot bumps them); config is in `pyproject.toml`, except flake8's in `.flake8`. All of it blocks, including radon: no function worse than cyclomatic complexity B (10), and every module maintainability A. Before pushing Python:

```bash
python3 -m pip install -r requirements-dev.txt
./scripts/lint-python.sh && python3 -m pytest
```

When the radon gate fails, fix the design rather than splitting a function to hide a branch count: rules stay functions over `lint_model.py`'s parsed types, with policy in tables. Don't add `# noqa` or `# pylint: disable` without a comment saying why.

- **Blocking:** editorconfig-checker (LF endings, exactly one final newline, per `.editorconfig`), actionlint, shellcheck, yamllint, jsonlint and the secret scanners.
- **Report-only, catalog-wide, promoted to blocking per category by the ratchet:** markdownlint (`.markdownlint.json`), cspell (`.cspell.json`, en-GB and en-US) — see `scripts/lint-enforced-markdown.sh`, above.
- **Report-only, not ratcheted:** jscpd.
- **No auto-fix commits** (`APPLY_FIXES: none`). Fix locally and commit.

PRs lint only the files they change; pushes to `main` lint everything. For fast local feedback, `pre-commit install` runs the hooks in `.pre-commit-config.yaml`, including `lint-python.sh` when a `.py` file changes, and `pre-commit install --hook-type pre-push` adds pytest and `validate-catalog.sh` before each push.

`.github/workflows/validate.yml` also runs `claude plugin validate . --strict`, the Claude Code CLI's own check of the marketplace and plugin manifests. It needs no credentials. It does not read agent frontmatter, which is `validate-catalog.sh`'s job.

## GitHub Actions

Workflows: `validate.yml` (catalog consistency, Python tests and Python lint), `mega-linter.yml` (linting), `codeql.yml` (workflow security analysis) and `labels.yml` (syncs `.github/labels.yml` into the repo's labels; it never deletes a label). Dependabot (`.github/dependabot.yml`) raises weekly grouped bumps for their actions and for `requirements-dev.txt`. Every workflow, existing or new, must pin every action to a full 40-character commit SHA, with a trailing comment naming the semantic version that SHA corresponds to:

```yaml
steps:
  - uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8 # v5.0.0
  - uses: actions/setup-node@a0853c24544627f65ddf259abe73b1d18a591444 # v5.0.0
```

Resolve a tag to its SHA with `gh api repos/<owner>/<repo>/git/ref/tags/<tag> --jq .object.sha` — never hand-write one from memory.

A version tag is mutable — whoever controls the action can repoint `v5` at new code, and it runs with your repository's token and secrets. The SHA is the only immutable reference. The comment is what keeps that readable and lets Dependabot bump both the SHA and the comment together.

This applies to every `uses:`, including first-party `actions/*` and reusable workflows (`owner/repo/.github/workflows/file.yml@<sha> # v1.2.3`). No bare tags, no branch refs, no `@main`.

## Line Endings and File Modes

`.gitattributes` pins `*.md`, `*.json`, `*.sh` and `*.yml` to LF. Markdown and JSON are pinned because tooling parses them line by line — 38 agent files stored with CRLF once made every frontmatter value read back empty under mawk on Linux, while passing locally under Git Bash's gawk.

`eol=lf` only converts CRLF pairs. A lone `\r` with no LF after it (how those 38 files actually ended) passes through untouched and makes git treat the file as binary. editorconfig-checker, which MegaLinter runs, checks the bytes rather than trusting the attribute.

`* text=auto` alone does not prevent this. It leaves files that already have CRLF in the index untouched, so `git add --renormalize .` is a no-op against them until an explicit `eol` rule exists.

Git records the executable bit in the index, not in `.gitattributes` — there is no `chmod` attribute, and `git check-attr` will happily report one that Git does not implement. A new script needs the bit set explicitly, or it lands non-executable and CI cannot run it:

```bash
git update-index --chmod=+x scripts/your-script.sh
```

## Git Workflow

`origin` is the `laywill` fork; `upstream` is `VoltAgent/awesome-claude-code-subagents`.

- `gh pr create` defaults to **upstream** in a fork — always pass `--repo laywill/awesome-claude-code-subagents`.
- Branch before editing, never commit to `main`: `git checkout main && git pull && git checkout -b <branch>`.
- Don't switch branches while subagents are still writing files.

### Release trains

A major release that changes many categories runs on a release branch, not `main`, because `main` is what the marketplace installs from. Merging category changes into `main` one by one would ship them before the release and under the old version number.

- The train is `release/vX.Y.Z`, branched from `main`. Its first commit sets every category `plugin.json`, every `marketplace.json` plugin entry and `metadata.version` to the release version, so `claude plugin validate . --strict` passes on every PR into it. It also adds `release/**` to the CI triggers.
- While a train is open, the milestone's issues branch from the train, open PRs with `--base release/vX.Y.Z`, and change no version.
- When `main` moves, merge `main` into the train. Never rebase it: that needs a force-push.
- One draft PR merges the train into `main` at release. Tag `main` after that merge.
- `release/v3.0.0` is open now: #383 is the release PR, and #324 lists the milestone.

### Conventions

Every piece of work traces to a GitHub issue.

- **Branches**: `<type>/<issue-number>-<slug>` — e.g. `fix/71-footer-layout-consistency`.
- **Commits and PR titles**: [Conventional Commits](https://www.conventionalcommits.org/), using only the spec's standard types (`feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`). The branch uses the same `<type>` as the commit.
- **Issues**: take whichever repo labels fit best.

Labels and commit types are separate vocabularies. `content`, `design` and `infra` are labels, not commit types.

## Subagent Storage in Claude Code

| Type    | Path                | Scope                |
| ------- | ------------------- | -------------------- |
| Project | `.claude/agents/`   | Current project only |
| Global  | `~/.claude/agents/` | All projects         |

Project subagents take precedence over global ones with the same name.

## Self Improvement

If you make a mistake or the User has to correct you on something: update this CLAUDE.md so you don't make that mistake again.
