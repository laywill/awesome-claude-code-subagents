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

There is no build system, test suite, linter, or CI. The "source" is markdown; correctness means the manifests, READMEs, and agent files stay in sync (see Verification below).

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
---

You are a [senior role] with expertise in [domain]...

When invoked:
1. ...

## Communication Protocol
## Development Workflow
## Security Safeguards   # only if the agent's risk level requires it
```

All four frontmatter keys are required on every agent file — `name`, `description`, `tools`, `model`. `name` must match the filename.

- **`model`**: `haiku` for narrow/mechanical roles, `sonnet` for the default case, `opus` for high-stakes reasoning (architecture, production ops, security).
- **`description`**: a single sentence Claude Code uses for auto-selection. Keep it under 50 tokens — the `description-compressor` agent in `.claude/agents/` does this.
- **`tools`**: assign the minimum for the role. If an agent doesn't need Bash, don't give it Bash — this is the single biggest risk reducer.

| Role type | Tools |
| --- | --- |
| Read-only (reviewers, auditors) | `Read, Grep, Glob` |
| Research (analysts) | `Read, Grep, Glob, WebFetch, WebSearch` |
| Documentation | `Read, Write, Edit, Glob, Grep` |
| Code writers / infrastructure | `Read, Write, Edit, Bash, Glob, Grep` |

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

No CI runs these; run them before opening a PR.

```bash
# Every agent file is listed in its category's plugin.json
for d in categories/*/; do
  listed=$(grep -c '"\./' "$d.claude-plugin/plugin.json")
  actual=$(ls $d*.md | grep -vc README)
  [ "$listed" != "$actual" ] && echo "MISMATCH $d listed=$listed actual=$actual"
done

# Every agent file has all four required frontmatter keys
for f in $(find categories -name '*.md' ! -name 'README.md'); do
  for k in name description tools model; do
    grep -q "^$k:" "$f" || echo "$f missing $k"
  done
done

# frontmatter name matches filename
for f in $(find categories -name '*.md' ! -name 'README.md'); do
  n=$(grep -m1 '^name:' "$f" | sed 's/name: *//')
  [ "$n" != "$(basename $f .md)" ] && echo "$f name=$n"
done
```

## GitHub Actions

There are no workflows in this repository yet. Any that get added must pin every action to a full 40-character commit SHA, with a trailing comment naming the semantic version that SHA corresponds to:

```yaml
steps:
  - uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8 # v5.0.0
  - uses: actions/setup-node@a0853c24544627f65ddf259abe73b1d18a591444 # v5.0.0
```

Resolve a tag to its SHA with `gh api repos/<owner>/<repo>/git/ref/tags/<tag> --jq .object.sha` — never hand-write one from memory.

A version tag is mutable — whoever controls the action can repoint `v5` at new code, and it runs with your repository's token and secrets. The SHA is the only immutable reference. The comment is what keeps that readable and lets Dependabot bump both the SHA and the comment together.

This applies to every `uses:`, including first-party `actions/*` and reusable workflows (`owner/repo/.github/workflows/file.yml@<sha> # v1.2.3`). No bare tags, no branch refs, no `@main`.

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
