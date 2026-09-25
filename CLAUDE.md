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

There is no build system or test suite. The "source" is markdown; correctness means the manifests, READMEs, and agent files stay in sync, which `scripts/validate-catalog.sh` checks and CI enforces (see Verification below).

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
- `.claude/agents/` — repo-maintenance agents used *on* this repo (description compression, security remediation, token optimization, gold-standard enhancement). Check these first before doing bulk edits by hand.
- `install-agents.sh` — interactive installer; works from a clone (local mode) or standalone via the GitHub API (remote mode)
- `tools/` — Claude Code skills that browse/fetch the catalog, installed to `~/.claude/commands/`
- `AGENT_SECURITY_GUIDELINES.md` — authoritative keep/delete policy for safety content in agent files (read before writing any)
- `docs/planning/` — design notes and experiments, not shipped content

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

Bump versions when publishing changes: the category's `plugin.json` `version`, and `.claude-plugin/marketplace.json` `metadata.version`.

## Agent File Format

```markdown
---
name: agent-name
description: "When this agent should be invoked — one sentence, under ~50 tokens"
tools: Read, Grep, Glob
model: sonnet
color: green                                # optional fields per the tier table below
disallowedTools: Write, Edit, NotebookEdit, Bash
---

You are a [senior role] with expertise in [domain]...

When invoked:
1. ...

## Communication Protocol
## Development Workflow
## Security Safeguards   # only if the agent's risk level requires it
```

All four frontmatter keys are required on every agent file — `name`, `description`, `tools`, `model` — although Claude Code itself requires only the first two. `name` must match the filename.

- **`description`**: a single sentence Claude Code uses for auto-selection. Keep it under 50 tokens — the `description-compressor` agent in `.claude/agents/` does this.
- **`tools`**: assign the minimum for the role. If an agent doesn't need Bash, don't give it Bash — this is the single biggest risk reducer. Always set it: an explicit list already excludes every MCP tool, so `mcp__*` in `disallowedTools` is redundant here. Omitting `tools` inherits everything, MCP included.
- **`model`**: an alias — `haiku`, `sonnet` or `opus`. No full model IDs (they go stale), no `fable` or `inherit`. Frontmatter outranks the user's `CLAUDE_CODE_SUBAGENT_MODEL`, so an `opus` pin overrides a user who set a cheaper model:
  - `haiku`: narrow, mechanical roles where the output follows from the input with little judgement (formatting, lookup, changelogs). Never set `effort` on it; Haiku doesn't support effort.
  - `sonnet`: the default. When a mistake would be costly but tools, tests or a plan output can check the result, use `sonnet` + `effort: high` rather than `opus`.
  - `opus`: only when both of these hold, stated in the PR. First, the output is a judgement that is costly to get wrong (architecture decisions, security or threat assessment, compliance or financial-risk findings). Second, a wrong answer would pass every check the agent or its caller can run (tests, linters, scanners, plan output), because the error is in the reasoning (a bad trade-off, a missed threat), not in anything a command reports.

| Role type | `tools` |
| --- | --- |
| Read-only (reviewers, auditors) | `Read, Grep, Glob` |
| Research (analysts) | `Read, Grep, Glob, WebFetch, WebSearch` |
| Documentation | `Read, Write, Edit, Glob, Grep` |
| Code writers / infrastructure | `Read, Write, Edit, Bash, Glob, Grep` |

A **read-only role** is one whose deliverable is findings returned to the conversation, so its job is done with the file tree unchanged. Declare it with `disallowedTools: Write, Edit, NotebookEdit`: that is the explicit read-only marker the validator checks, since a role can't be inferred from a name. Listing a tool in both `tools` and `disallowedTools` is an error. A specifier such as `Bash(git push *)` removes the whole tool, so don't use one.

### Optional fields by tier

Tier here is the category's tier from Repository Structure, the same tier Security Safeguards keys its content by.

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

## Security Safeguards

`AGENT_SECURITY_GUIDELINES.md` is the source of truth. It has a keep/delete test for any piece of safeguard content, with worked examples. The essentials:

What protects a user is the permission mode, not agent prose. In Manual mode the user approves each command. In auto mode, the built-in default on Pro, Max and Team, a classifier blocks force pushes, production deploys, `terraform destroy`, IAM grants, secret-manager writes and similar actions. Deny rules apply in every mode. So agent files carry what makes the agent competent, not warnings.

| Content | Tier 1 | Tier 2 | Tier 3 | Tier 4 | Tier 5 |
| --- | :-: | :-: | :-: | :-: | :-: |
| Operating notes (stamped from template, never hand-edited) | ✓ | ✓ | ✓ | ✓ | ✓ |
| Expert practice (dry-run, plan before apply, backup, confirm target, pin versions) | if relevant | ✓ | ✓ | ✓ | ✓ |
| Rollback (real CLI commands for the domain) | — | state outside git only | ✓ | ✓ | ✓ |
| Domain approval gates (a real human process, e.g. DBA sign-off) | — | rarely | if real | if real | if real |

A Tier 3–5 agent with none of `Bash`, `Write` or `Edit` takes the Tier 1 notes and has no Rollback section.

**Delete on sight:** generic Emergency Stop (stop-file checks), generic Blast Radius Controls, generic Approval Gates (change ticket, on-call, `read -p CONFIRM`), Input Validation that amounts to "validate inputs", and invented thresholds ("rollback in < 5 min").

**Enforce through frontmatter, not prose:** `tools`, `disallowedTools`, `isolation`, `maxTurns`. Plugin agents ignore `permissionMode`, `hooks`, `mcpServers` and `initialPrompt`, and `permissionMode` can't tighten a session that's already in auto, acceptEdits or bypass mode. Never use any of the four.

Two rules that get violated repeatedly:

- **Never add Audit Logging.** Audit trails belong to the platform and the user's own hooks. Code-level logging follows the user's requirements, not agent-file mandates.
- **Never embed implementation code** for validation, logging, gates or stop checks. The agent writes that at runtime, and embedded code bloats the definition without enforcing anything. Rollback *CLI commands* are the exception: they are operational and belong in the file.

## Verification

```bash
./scripts/validate-catalog.sh
```

One script, checked in, run by both humans and CI — `.github/workflows/validate.yml` invokes it on every pull request and on pushes to `main`. Keep the checks in the script; do not re-inline them here, or the documented copy becomes the stale one.

It reports every failure it finds rather than stopping at the first, and exits non-zero if any fired. What it enforces:

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

Adding an agent therefore means updating the count in the README badge and in `.claude-plugin/marketplace.json`, not just the four places.

### Linting

MegaLinter (`.mega-linter.yml`, `.github/workflows/mega-linter.yml`) covers generic file hygiene; `validate-catalog.sh` covers what is specific to this catalog. Don't duplicate a check across the two.

- **Blocking:** editorconfig-checker (LF endings, exactly one final newline, per `.editorconfig`), actionlint, shellcheck, yamllint, jsonlint and the secret scanners.
- **Report-only:** markdownlint (`.markdownlint.json`), cspell (`.cspell.json`, en-GB and en-US) and jscpd. The agent files predate linting, and #318's per-category ratchet makes these blocking as each category is uplifted.
- **No auto-fix commits** (`APPLY_FIXES: none`). Fix locally and commit.

PRs lint only the files they change; pushes to `main` lint everything. For fast local feedback, `pre-commit install` runs the hooks in `.pre-commit-config.yaml`, and `pre-commit install --hook-type pre-push` adds `validate-catalog.sh` before each push.

## GitHub Actions

Workflows: `validate.yml` (catalog consistency), `mega-linter.yml` (linting), `codeql.yml` (workflow security analysis) and `labels.yml` (syncs `.github/labels.yml` into the repo's labels; it never deletes a label). Dependabot (`.github/dependabot.yml`) raises weekly grouped bumps for them. Every workflow, existing or new, must pin every action to a full 40-character commit SHA, with a trailing comment naming the semantic version that SHA corresponds to:

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

### Conventions

Every piece of work traces to a GitHub issue.

- **Branches**: `<type>/<issue-number>-<slug>` — e.g. `fix/71-footer-layout-consistency`.
- **Commits and PR titles**: [Conventional Commits](https://www.conventionalcommits.org/), using only the spec's standard types (`feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`). The branch uses the same `<type>` as the commit.
- **Issues**: take whichever repo labels fit best.

Labels and commit types are separate vocabularies. `content`, `design` and `infra` are labels, not commit types.

## Subagent Storage in Claude Code

| Type    | Path              | Scope                |
| ------- | ----------------- | -------------------- |
| Project | `.claude/agents/` | Current project only |
| Global  | `~/.claude/agents/` | All projects       |

Project subagents take precedence over global ones with the same name.

## Self Improvement

If you make a mistake or the User has to correct you on something: update this CLAUDE.md so you don't make that mistake again.
