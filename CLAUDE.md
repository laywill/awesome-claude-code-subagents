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
- `AGENT_SECURITY_GUIDELINES.md` — authoritative rules for the Security Safeguards section (read before writing one)
- `docs/planning/` — design notes and experiments, not shipped content

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
  - `opus`: only when both of these hold, stated in the PR. First, the output is a judgement that is costly to get wrong (architecture decisions, security or threat assessment, compliance or financial-risk findings). Second, no tool run can check it: the value comes from reasoning, not from running commands and reading their output. 18 agents are pinned to `opus` today. Each per-category issue re-tests them against these criteria.

| Role type | `tools` | `disallowedTools` |
| --- | --- | --- |
| Read-only (reviewers, auditors) | `Read, Grep, Glob` | `Write, Edit, NotebookEdit`, plus `Bash` in Tier 1 |
| Research (analysts) | `Read, Grep, Glob, WebFetch, WebSearch` | as read-only |
| Documentation | `Read, Write, Edit, Glob, Grep` | `Bash` |
| Code writers / infrastructure | `Read, Write, Edit, Bash, Glob, Grep` | — |

A **read-only role** is one whose deliverable is findings returned to the conversation, so its job is done with the file tree unchanged. `disallowedTools` is applied before `tools`, and it wins when a tool appears in both. That makes it a lock: it survives someone later adding `Write` to `tools`, and it gives the validator an explicit read-only marker. Listing a tool in both fields is an error. A specifier such as `Bash(git push *)` removes the whole tool, so don't use one.

### Optional fields by tier

| Field | Tier 1 🟢 | Tier 2 🟡 | Tier 3 🟠 | Tier 4 🔴 | Tier 5 ⛔ |
| --- | --- | --- | --- | --- | --- |
| `color` | `green` | `yellow` | `orange` | `red` | `purple` |
| `disallowedTools` | `Bash` always; read-only roles add `Write, Edit, NotebookEdit` | read-only roles: `Write, Edit, NotebookEdit` | same | same | same |
| `effort` | omit | omit | omit | `high` | `high` |
| `maxTurns` | omit | omit | omit | `40` | `25` |
| `isolation` | omit | omit, unless it qualifies (below) | same | same | omit |
| `model` | by the criteria above | same | same | same | same |

- **`color`**: the tier, so it is visible while the agent runs. The eight valid values are `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan`.
- **`effort`**: omit it so the user's session level applies, with three exceptions. Tier 4–5 agents get `high`, except on `haiku`. Every `opus` agent gets `high`, which pins its behaviour; otherwise the default varies by version, `medium` on Opus 5.5 but `xhigh` on Opus 4.7. A `sonnet` agent that fails only the second `opus` criterion also gets `high`. Don't use `low` or `medium` (a task that cheap belongs on `haiku`), or `xhigh` or `max`.
- **`maxTurns`**: a hard stop. The output comes back marked partial and Claude can resume the agent, so treat the cap as a checkpoint where a human sees progress against external or production systems. A normal task fits well inside it; a retry or polling loop hits it. Override it per agent only with a reason.
- **`isolation: worktree`**: the worktree branches from the **default branch**, not the caller's `HEAD`, unless the user has set `worktree.baseRef: "head"`. An agent that edits the user's in-progress work would silently work on stale code, so leave it to the caller, which can pass `isolation` per invocation. A file qualifies only if it edits the repo, its task is complete from a clean default-branch checkout, and its result is reviewed as a branch rather than applied in place (for example, a dependency-upgrade trial). Tier 5 work isn't in the repo.

### Frontmatter fields

Claude Code recognises 18 fields and silently ignores unknown or misspelled ones.

| Field | Values | Policy |
| --- | --- | --- |
| `name`, `description`, `tools`, `model` | see above | required |
| `color`, `disallowedTools`, `effort`, `maxTurns`, `isolation` | `effort`: `low`, `medium`, `high`, `xhigh`, `max`; `maxTurns`: integer; `isolation`: `worktree` | per the tier table |
| `memory` | `user`, `project`, `local` | not used. It writes into the user's home or repo, and it enables `Read, Write, Edit` automatically, which breaks a read-only role's tool restriction |
| `skills` | skill names | not used. The catalog ships no skills, and preloading a user's skills by name isn't portable. Revisit in a spike |
| `background` | `true` | not used. Foreground or background is the caller's choice |
| `omitClaudeMd` | `true` | not used. The project's conventions matter to almost every agent here |
| `experimental` | `cacheTtl: 5m \| 1h` | not used. The cache TTL is a billing choice for the user |
| `permissionMode`, `hooks`, `mcpServers`, `initialPrompt` | — | **forbidden**. Ignored in plugin agents, so they would ship as dead config |

## Security Safeguards

`AGENT_SECURITY_GUIDELINES.md` is the source of truth; the essentials:

Classify by capability, not by category number — no Bash → LOW; Bash but development-scope → MEDIUM; production-adjacent (databases, deploys, cloud) → HIGH; direct production infrastructure → CRITICAL.

| Section | LOW | MEDIUM | HIGH | CRITICAL |
| --- | :-: | :-: | :-: | :-: |
| Environment Note | — | ✓ | ✓ | ✓ |
| Input Validation (prose only) | — | ✓ | ✓ | ✓ |
| Approval Gates | — | — | ✓ | ✓ |
| Rollback Procedures | — | ✓ | ✓ | ✓ |
| Emergency Stop | — | — | — | ✓ |
| Blast Radius Controls | — | — | — | ✓ |
| Audit Logging | — | — | — | — |

Two rules that get violated repeatedly:

- **Never add Audit Logging.** Claude Code Hooks handle it at the platform level. Code-level logging follows the user's requirements, not agent-file mandates.
- **Never embed implementation code** for validation or logging (validator classes, logger setup). The agent is an expert in its domain and writes that at runtime; embedding it just bloats the definition. Rollback *CLI commands* are the exception — those are operational and belong in the file.

`chaos-engineer` and `penetration-tester` are the reference examples for safeguard design: specific, measurable, minimally-tooled.

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

Adding an agent therefore means updating the count in the README badge and in `.claude-plugin/marketplace.json`, not just the four places.

## GitHub Actions

`.github/workflows/validate.yml` is currently the only workflow. It and any that get added must pin every action to a full 40-character commit SHA, with a trailing comment naming the semantic version that SHA corresponds to:

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
