# 0001: Group by function, derive capability from `tools`

- **Status:** accepted by the owner in review on 2026-11-13 (#389); in force once PR #393 merges
- **Date:** 2026-11-13
- **Applies to:** v3.0.0, on `release/v3.0.0`
- **Reverses:** v2.0.0's risk-tier grouping (#285, PR #290), in part; #324's "Re-cutting the 24 categories" out-of-scope line; #318's "Keyed by tier, not capability class"

## Summary

v3 stops using risk tiers to organise the catalog or to decide what an agent may hold.

- Categories are grouped by function. v2's categories already were, underneath the tier ordering, so 23 of the 24 stay as they are. The numeric prefixes and tier labels go, `production-data-ops` merges into `data-and-database`, and two agents move.
- `tools` is sized to the job. An agent gets what its described work needs and nothing else. "Advisory" is not a reason to withhold Bash.
- Capability is computed from `tools` and never written by hand.
- One attribute is declared per agent: `live`, for an agent whose own commands change state outside the checkout. It replaces the five tiers as the thing that requires Rollback, a turn cap and `effort: high`.
- The user's permission mode is what protects them. The README says so, and agent files don't pose as a boundary.

This is a partial return to the functional grouping v1 and upstream use. v2 tried risk tiers as a control, the control turned out not to be one, and the tier got in the way of agents doing their jobs.

## Context

### What v2 decided, and why

v1.0.0 had ten functional categories, the same ten as `VoltAgent/awesome-claude-code-subagents`. Issue #285 ("Agents are badly categorised within the repo") led to PR #290, merged as `12863b3` on 2026-02-21 and tagged v2.0.0. It produced 25 categories in risk order; #295 removed category 00 for v2.2.0, leaving 24.

The reasoning was written down once, in `agents-restructure.md` at commit `f189a87`. The file was deleted before the merge and never reached `main`:

> **Risk-tiered categories.** Agents within a category share a similar blast radius. This lets you grant blanket permissions at the tier level: run Tier 1–2 autonomously, require PR review for Tier 3, and mandate manual approval for Tier 4–5.
>
> **Numbered prefixes enforce risk ordering.**
>
> **Task-based over role-based (mostly).** Categories are organised around *what an agent does* rather than *what job title it holds*

The v2.0.0 release notes added that users could "install only agents that have a level of risk you are comfortable with".

Two things about that decision matter now:

- **No mechanism for tier-level permissions was ever written.** `AGENT_SECURITY_GUIDELINES.md` at v2 did not contain the word "tier". Claude Code has no permission rule that can be scoped to one subagent or one plugin, so "run Tier 1–2 autonomously" could not be configured.
- **The categories were task-based already.** Risk supplied the order, the labels and, later, the rules. It supplied few of the boundaries.

### What changed

- **The permission mode became the control.** #317 (PR #354, `a28f667`, 2026-09-27) rewrote the guidelines: "Prose is the last line of defence only in bypass mode run outside a container". The current Claude Code docs go further than our notes did: from v2.1.283, auto mode is the starting permission mode on every plan. Its classifier blocks production deploys, force pushes, `terraform destroy`, IAM grants, writes to a secret manager and similar actions. Deny rules block in every mode. A subagent's actions go through the same decision order as its parent session's.
- **A subagent's restrictions bind only that subagent.** The session that calls it keeps every tool, so withholding Bash from `scrum-master` stops nothing the caller couldn't do anyway.
- **The tier started deciding grants.** v3's lint made Tier 1 mean "no Bash". #388 then codified "an agent without Bash or web tools doesn't source from 'the issue tracker'". PR #379 applied it to category 05, and the owner objected the same morning: "I would expect most of these agents to be given access to e.g. the GitHub command line tool and asked to manage a backlog that is tracked externally", and "if the caller has to do all the getting of the issue contents etc that bloats the caller's context horribly when the whole point of this is to have a specialist with disposable context".

### What we measured for this decision

- **Under-granted agents.** Of 47 agents checked (every agent without the full `Read, Write, Edit, Bash, Glob, Grep` set, plus the full-set agents in categories 01–06), 18 can't do their described job. All 18 are missing Bash. The uplift PRs widened the gap: #381 removed Bash from three architects whose bodies now tell the caller to run the linters, and #380 has two documentation agents say "you don't run them yourself" about building their own output.
- **The tier misdescribes what agents act on.** Of 78 agents in categories 14–24 (plus `chaos-engineer`), 31 change state in live systems and 47 don't. The directory tier demanded Rollback, or Rollback plus a turn cap, of 31 agents whose work stays in the checkout, and under-stated others: `postgres-pro` (Tier 3) administers running databases, the same job as `database-administrator` (Tier 5).
- **A binary flag fits.** 64 of the 78 were clearly live or local. Live predicted real Rollback content for 30 of 31. Of the 33 clearly local agents, 4 had any, all marginal. The other 14 author locally and sometimes apply; a third level would not help them.
- **The tier was already leaking.** The stamp tier needed a read-only override keyed on `tools`, and both allowlist entries on the train exist to correct a tier (`chaos-engineer: tier=5`, `license-auditor: tier1-bash`).

The Ollama measurements (#298, PR #300) still hold and are untouched by this decision: an agent file helps through its checklist and its output schema, and stripping protocol scaffolding improves quality. They are about a file's body. This record is about where the file lives and what it may hold.

## Criteria

1. **What actually protects the user**, per the current Claude Code docs.
2. **Agent effectiveness:** can each agent do its whole job with its grants?
3. **Discoverability and install granularity:** a category is a plugin, so it is what a user installs.
4. **Cost to deliver** on the release train.
5. **Cost to the user upgrading** from v2.x.

## Options

| Option | Protection | Effectiveness | Discoverability | Delivery cost | Upgrade cost |
| --- | --- | --- | --- | --- | --- |
| A. Keep risk tiers as the axis; fix the misfits by moving agents | none added | needs a tier with Bash that isn't "risky", which is the contradiction that started this | a user can read risk off the directory | lowest now; every future misfit is another move or allowlist entry | none |
| **B. Keep the functional categories, remove the tier layer, declare `live` per agent** | none added, none claimed | grants follow the job | unchanged, minus one category | policy, lint and three templates; one merge, two moves | one plugin rename, seven agents change plugin |
| C. Re-cut into about a dozen broad domains | none added | same as B | fewer, larger plugins; more descriptions loaded per install | B plus a move for most agents | most plugins renamed; most agents change scoped name |
| D. Return to upstream's ten | none added | same as B | easier to compare with upstream; categories of 30 or more | as C | as C |

**The case for A, argued properly.** It is the cheapest, it honours #324's promise that "no existing install breaks", and a tier read from a path can't drift. Its real benefit is install-by-risk: a user who never wants an agent that deploys simply doesn't install categories 22–24, so Claude never delegates a deploy to one. The owner's instinct on 2026-10-11 was to make the tier structure completely clear, not to drop it.

**Why it loses.** The install-by-risk benefit survives without tiers: the `live` flag is shown per agent, live agents cluster in a few categories, and `permissions.deny` with `Agent(name)` disables any single agent. Everything else A offers is a label. To keep tiers honest, `scrum-master` needs Bash, so it either moves to a "Tier 4" it doesn't belong in, or Tier 1 gains Bash and stops meaning anything. The audit found the directory wrong about what an agent touches for 31 of 78 agents. A tier that needs per-agent overrides to be right is a per-agent attribute stored in the wrong place.

**Why not C or D.** A plugin rename is cheap for marketplace users, because `marketplace.json` has a `renames` map. An agent changing plugin is not: its scoped name (`plugin:agent`) changes and nothing migrates it. C and D do that to most of the catalog. Nothing measured says the current functional boundaries make agents hard to find, and larger plugins put more descriptions into every session that installs one.

## Decision

### 1. Tools are sized to the job

- `tools` lists what the agent's described work needs. Bash is granted to run a tracker or VCS client (`gh`, `git log`), a linter, a test, a scanner or a build. `Write` and `Edit` are granted when the deliverable is a file. Web tools are granted when the job needs current external facts.
- A tool the job never uses is removed, because it now mislabels the agent (see 3).
- The Tier 1 Bash rule and the `tier1-bash` allowlist rule are deleted. So is #388's "What a Tier 1 agent writes".
- `disallowedTools` is no longer used. Every agent sets `tools`, and an explicit list already excludes everything else, so the read-only marker restated what `tools` said. The lint never read it. On an agent that holds Bash it was also untrue, since Bash can write files.

### 2. Categories are grouped by function

- 23 categories, each one plugin. See the list below.
- Directory names lose their numeric prefix: `categories/data-and-database/`. The prefix existed to enforce risk ordering.
- `24-production-data-ops` merges into `data-and-database`. It was the one boundary drawn only by risk: both sides hold database agents, split by whether the database is production.
- `database-administrator` moves from production ops to `data-and-database`. `chaos-engineer` moves from testing to `production-ops-and-observability`.
- No other category changes its membership or its plugin name. Build, provisioning, release and operations (old 17, 19, 22, 23) stay separate: they are different jobs, and the agents misfiled among them lose nothing once grants follow the job.
- Overlapping agents inside a category (for example `postgres-pro` and `database-administrator`, `mobile-app-developer` and `mobile-developer`) are tested against the catalog-overlap rule in that category's uplift, not here.

### 3. Capability is derived

Computed from `tools`, for display, the installer and the generated index (#314):

| `tools` holds | Label |
| --- | --- |
| none of `Write`, `Edit`, `NotebookEdit`, `Bash` | read-only |
| `Bash`, no `Write` or `Edit` | runs commands |
| `Write` or `Edit`, no `Bash` | writes files |
| `Write` or `Edit`, and `Bash` | writes files, runs commands |
| `WebFetch` or `WebSearch` as well | adds "web" |

"Read-only" is shown only for an agent that can't run a command. It is never typed into a file, a README or a manifest by hand.

### 4. One declared attribute: `live`

An agent is `live` when its own commands, doing its described job, change state outside the local checkout: a remote database, a cloud account, a cluster, a registry, a SaaS tenant, production.

- It is declared in the agent file's stamp marker: `<!-- BEGIN GENERATED: operating-notes profile=live -->`. `stamp_sections.py --live <file>` sets it, and a later re-stamp keeps it.
- An agent that authors locally and only sometimes applies (`package-publisher`, `webhook-configurator`) is not live. Its operating notes tell it to stop and hand the apply step back.
- No third level. "External but not production" would change what is required of almost no agent. Irreversible steps (a publish, a purge, a revoked key) are handled in that agent's Expert practice, not by a rank.

The 31 agents proposed as live are marked ● in the category list. Each category's uplift confirms its own.

### 5. Three profiles replace the five stamp tiers

| | `findings` | `local` | `live` |
| --- | --- | --- | --- |
| How it is chosen | derived: `tools` holds no `Write`, `Edit` or `NotebookEdit` | derived: it holds one | declared (see 4) |
| Operating notes template | `operating-notes-findings.md` | `operating-notes-local.md` | `operating-notes-live.md` |
| What the notes say | return findings; change nothing; with Bash, run only commands that read or measure | change files in the working tree; leave them uncommitted; anything beyond the checkout is handed back as commands | establish the exact target and whether it is production, and treat it as production if unsure; write a plan with a per-step undo; apply only when the task says to; leave the target consistent after each step |
| `## Expert practice` | required if `tools` holds `Bash` | required if `tools` holds `Bash` | required |
| `## Rollback` | absent | optional, for state git doesn't track | required |
| `## Approval gates` | absent | optional | optional |
| `color` | `green` | `yellow` | `red` |
| `effort` | omit | omit | `high` on `sonnet` |
| `maxTurns` | omit | omit | required, at most `40` |

- The stamp marker becomes `profile=<name>`. For `findings` and `local` the lint checks the marker against `tools`; `live` is accepted as declared.
- `scripts/lint-allowlist.txt` keeps one rule, `sonnet-instead-of-opus`, valid on agents that are not live. `tier=N` and `tier1-bash` go, with both current entries.
- `AGENT_SECURITY_GUIDELINES.md` §7 holds three source blocks under named headings, and `catalog_lint` reads them by heading, not by position.
- The final wording of the three notes is written in the policy change (#390), from the current Tier 1, 2 and 4–5 texts.
- Issue #387 (Tier 1 notes tell a read-only agent it may write documents) dissolves: an agent that writes documents is `local`.

### 6. The harness is the user's to secure

- The README states the operating assumptions: Manual or acceptEdits mode, auto mode, or a container for bypass mode. It says what auto mode's classifier blocks, that deny rules apply in every mode, and that `Agent(name)` in `permissions.deny` switches one agent off.
- Agent files carry no warnings and no posture. Expert practice stays: dry runs, confirming the target, plan before apply and backups are what a competent operator does.

## The v3 category list

● marks an agent proposed as `live`.

| Category (directory under `categories/`) | Plugin | Agents |
| --- | --- | --- |
| `analysis-and-review` (9) | `laywill-analysis-review` | `accessibility-tester`, `code-reviewer`, `complexity-analyzer`, `compliance-auditor`, `dependency-auditor`, `license-auditor`, `performance-engineer`, `qa-expert`, `security-auditor` |
| `api-and-service-integration` (5) | `laywill-api-service-integration` | `api-client-generator`, `message-queue-configurator` ●, `sdk-wrapper-builder`, `third-party-integrator`, `webhook-configurator` |
| `architecture-and-design` (8) | `laywill-architecture-design` | `api-designer`, `architect-reviewer`, `data-flow-designer`, `graphql-architect`, `microservices-architect`, `schema-designer`, `solution-architect`, `system-modeler` |
| `bug-fixing-and-debugging` (6) | `laywill-bug-fixing-debugging` | `bug-fixer`, `debugger`, `error-detective`, `log-analyzer`, `regression-hunter`, `stack-trace-interpreter` |
| `build-and-ci-cd` (5) | `laywill-build-ci-cd` | `artifact-publisher`, `build-optimizer`, `environment-configurator`, `pipeline-builder`, `workflow-author` |
| `business-and-product` (9) | `laywill-business-product` | `business-analyst`, `content-marketer`, `customer-success-manager`, `legal-advisor`, `quant-analyst`, `risk-manager`, `sales-engineer`, `seo-specialist`, `ux-researcher` |
| `data-and-database` (13) | `laywill-data-database` | `backup-restore-manager` ●, `data-anonymizer` ●, `data-engineer`, `data-migrator` ●, `data-validator`, `database-administrator` ●, `database-optimizer`, `orm-model-builder`, `postgres-pro` ●, `replication-configurator` ●, `retention-policy-enforcer` ●, `schema-migrator`, `seed-data-generator` |
| `data-science-and-ai` (8) | `laywill-data-science-ai` | `ai-engineer`, `data-analyst`, `data-scientist`, `llm-architect`, `machine-learning-engineer`, `ml-engineer`, `mlops-engineer` ●, `nlp-engineer` |
| `dependency-and-package-management` (6) | `laywill-dependency-management` | `dependency-manager`, `dependency-upgrader`, `lockfile-resolver`, `monorepo-manager`, `package-publisher`, `vulnerability-patcher` |
| `deployment-and-release` (6) | `laywill-deployment-release` | `blue-green-switcher` ●, `canary-release-controller` ●, `deployer` ●, `deployment-engineer`, `feature-flag-manager` ●, `rollback-manager` ● |
| `developer-experience-and-tooling` (6) | `laywill-developer-experience` | `build-engineer`, `dx-optimizer`, `git-workflow-manager`, `prompt-engineer`, `slack-expert`, `tooling-engineer` |
| `documentation` (7) | `laywill-documentation` | `adr-author`, `api-documenter`, `changelog-generator`, `documentation-engineer`, `readme-generator`, `runbook-writer`, `technical-writer` |
| `frontend-and-ui` (5) | `laywill-frontend-ui` | `i18n-extractor`, `responsive-adapter`, `style-refactorer`, `theme-generator`, `ui-component-builder` |
| `general-development` (11) | `laywill-general-development` | `backend-developer`, `cli-developer`, `electron-pro`, `frontend-developer`, `fullstack-developer`, `game-developer`, `mcp-developer`, `mobile-app-developer`, `mobile-developer`, `ui-designer`, `websocket-engineer` |
| `infrastructure-as-code` (11) | `laywill-infrastructure-code` | `azure-infra-engineer` ●, `cloud-architect`, `cloudformation-builder` ●, `devops-engineer` ●, `docker-composer`, `helm-chart-builder`, `kubernetes-specialist` ●, `network-engineer` ●, `platform-engineer`, `terraform-engineer` ●, `windows-infra-admin` ● |
| `language-and-framework-specialists` (29) | `laywill-language-specialists` | `angular-architect`, `cpp-pro`, `django-developer`, `dotnet-expert`, `elixir-expert`, `flutter-expert`, `fsharp-specialist`, `golang-pro`, `haskell-expert`, `java-architect`, `javascript-pro`, `kotlin-specialist`, `laravel-specialist`, `lua-specialist`, `nextjs-developer`, `ocaml-specialist`, `php-pro`, `powershell-expert`, `python-pro`, `r-specialist`, `rails-expert`, `react-specialist`, `rust-engineer`, `spring-boot-engineer`, `sql-pro`, `swift-expert`, `typescript-pro`, `vue-expert`, `wordpress-master` |
| `planning-and-estimation` (8) | `laywill-planning-estimation` | `effort-estimator`, `migration-planner`, `product-manager`, `project-manager`, `release-planner`, `risk-assessor`, `scrum-master`, `task-planner` |
| `production-ops-and-observability` (9) | `laywill-production-ops` | `alert-configurator` ●, `chaos-engineer` ●, `dashboard-builder`, `devops-incident-responder` ●, `incident-responder`, `log-pipeline-manager` ●, `scaling-manager` ●, `sla-monitor`, `sre-engineer` |
| `refactoring-and-modernization` (8) | `laywill-refactoring-modernization` | `dotnet-modernizer`, `framework-upgrader`, `language-modernizer`, `legacy-modernizer`, `linter-fixer`, `pattern-migrator`, `refactoring-specialist`, `tech-debt-reducer` |
| `research-and-discovery` (3) | `laywill-research-discovery` | `feasibility-assessor`, `research-analyst`, `technology-researcher` |
| `security-and-secrets` (9) | `laywill-security-secrets` | `ad-security-reviewer`, `certificate-manager` ●, `cors-policy-manager`, `iam-policy-author`, `penetration-tester` ●, `powershell-security-hardening`, `secret-rotator` ●, `security-engineer`, `vault-configurator` ● |
| `specialized-domains` (6) | `laywill-specialized-domains` | `blockchain-developer`, `embedded-systems`, `fintech-engineer`, `iot-engineer`, `m365-admin` ●, `payment-integration` |
| `testing-and-qa` (7) | `laywill-testing-qa` | `coverage-gap-filler`, `e2e-test-writer`, `integration-test-writer`, `snapshot-updater`, `test-automator`, `test-fixture-generator`, `unit-test-writer` |

## Before and after

| Agent | v2 / today on the train | v3 |
| --- | --- | --- |
| `scrum-master` | `05-planning-and-estimation`, Tier 1. `Read, Write, Edit, Glob, Grep, WebFetch, WebSearch`. PR #379 drops web and disallows Bash; stamp `tier=1`; reads tracker state "the caller passes in" | `planning-and-estimation`. `Read, Write, Edit, Bash, Glob, Grep`. Writes files, runs commands. Profile `local`, yellow. Queries the tracker itself with `gh`. Expert practice required |
| `penetration-tester` | `20-security-and-secrets`, Tier 4. `Read, Grep, Glob, Bash`, `opus`. Keeps the Tier 4 stamp because the read-only override looks at `tools`, and a read-only marker that Bash contradicts | `security-and-secrets`. Same tools. Runs commands. Profile `live`, red, `maxTurns: 40`. Rollback holds clean-up of test accounts and payloads. Approval gate: rules of engagement |
| `chaos-engineer` | `09-testing-and-qa`, Tier 2, with allowlist entry `tier=5` | `production-ops-and-observability`. Same tools. Profile `live` by its own marker; the allowlist entry is deleted. `effort: high`, `maxTurns` at most 40, Rollback required |
| `terraform-engineer` | `19-infrastructure-as-code`, Tier 4. Full set. Red, `effort: high`, `maxTurns: 40`, Rollback required | `infrastructure-as-code`. Unchanged in substance: profile `live` gives the same requirements |
| `code-reviewer` | `03-analysis-and-review`, Tier 1. Full set, `opus`. Would need a `tier1-bash` entry to keep Bash | `analysis-and-review`. `Read, Grep, Glob, Bash`: it returns feedback and reads PRs and history. Runs commands. Profile `findings`, green. No allowlist entry |
| `backup-restore-manager` | `24-production-data-ops`, Tier 5, plugin `laywill-production-data-ops`. Purple, `maxTurns: 25` | `data-and-database`, plugin `laywill-data-database`. Profile `live`, red, `maxTurns` at most 40 (25 is still allowed). Rollback required |
| `research-analyst` | `01-research-and-discovery`, Tier 1. `Read, Grep, Glob, WebFetch, WebSearch`. PR #378 adds `disallowedTools: Write, Edit, NotebookEdit, Bash`; stamp `tier=1` | `research-and-discovery`. Same tools; the `disallowedTools` line is removed. Read-only, web. Profile `findings`, green |

## Verdict on the working hypothesis

| Point | Verdict | Strongest counter-argument, and why it does or doesn't win |
| --- | --- | --- |
| 1. Agents must be able to do their jobs first | **Adopted, with one amendment** | *Counter:* a narrow grant is cheap insurance. *Loses:* it insured nothing, since the caller holds Bash, and it cost 18 agents their job. *Amendment:* the hypothesis kept `disallowedTools` as a read-only marker "where it describes the deliverable". It is dropped instead: it duplicates `tools`, the lint never read it, and the `findings` profile now describes the deliverable |
| 2. Group by domain or function, not by risk | **Amended** | *Counter:* #324 put a re-cut out of scope to protect installs. *Partly wins:* the regroup is much smaller than the hypothesis's examples. Only 14-vs-24 was a risk-only boundary. 19, 22 and 23 are distinct jobs and stay. One plugin name disappears |
| 3. Capability is derived, not declared | **Adopted** | *Counter:* a derived label can't say "this Bash agent only reads". *Accepted as a feature:* the owner's own rule is "If we grant Bash access, we cannot guarantee that an agent will only use it for reading". The label says "runs commands" |
| 4. At most one declared risk attribute | **Adopted: a binary `live` flag** | *Counter:* a three-level rank carries more. *Loses:* the audit found no agent whose requirements a middle level would change, and 14 agents it wouldn't classify any better. *Counter:* the domain implies it. *Loses:* `data-and-database` holds both `orm-model-builder` and `backup-restore-manager` |
| 5. Securing the harness is the user's job | **Adopted** | *Counter:* some users run bypass mode on a host, and prose is all they have. *Loses:* that setup is unsupported, and a paragraph is a weak control there (#317). Expert practice stays for competence |

## Migration from v2.x

### The map

Two levels, generated from git, not written by hand.

- **Agents:** `gen_migration_map.py <old-ref> <new-ref>` reads both trees and reports each agent as unchanged, moved, removed or added, with its old and new category, plugin, `tools` and model. Git records a merge of two agents as two deletions, so a reviewed overlay file names the successor of each removed agent and the PR that did it.
- **Plugins:** the same run reports each plugin's old and new name, directory and version.
- **Outputs:** a JSON file for tools (the installer reads it), and a table in the upgrade guide generated from the JSON. Delivered by #392.

Measured from `v2.2.0` to the train today: 203 agents become 194. 190 are unchanged, 12 were merged into another agent, 1 was deleted with no catalog successor (`codebase-explorer`, replaced by the built-in `Explore`), and 4 were added. This decision adds 7 agents that change plugin and 1 plugin rename. All of the agent changes so far are already on `main`, where plugins 01, 07 and 10 changed their agents while still at version 2.1.0.

### What breaks, per install route

| Route | What breaks | What fixes it |
| --- | --- | --- |
| Plugin marketplace | `laywill-production-data-ops` no longer exists. Seven agents have a new scoped name. Thirteen agent names are gone | `renames` in `marketplace.json` rewrites the `enabledPlugins` key to `laywill-data-database`. The user runs `/plugin marketplace update laywill-subagents`. A user who had production ops but not data-and-database installs the latter to keep `database-administrator` |
| `install-agents.sh`, local or remote | Copied files never update, and a file in `~/.claude/agents/` or `.claude/agents/` outranks the plugin agent of the same name. The 13 removed agents stay installed for ever | The installer reads the JSON map, lists the files whose names were removed or merged, names each replacement, and offers to delete them. It does not migrate silently, because it has no record of which files it installed (#320) |
| Copied by hand | The same shadowing and the same stale files | Commands in the upgrade guide, for bash and PowerShell, generated from the map |
| Any route | An agent name written into the user's `CLAUDE.md`, prompts or hooks. A hook matching `agent_type` sees the scoped name, which changes for the seven agents | The table in the upgrade guide |

**Changed grants.** The audit proposes Bash for 18 agents, and removing `Write` and `Edit` from up to six findings-only agents. No user's permission rule can have depended on the old grants, because a rule can't be scoped to a subagent. What changes is behaviour: in Manual mode a planning agent now prompts for `gh`, and in `dontAsk` mode it is denied unless the user allows it (`Bash(gh issue *)`, for example). The upgrade guide lists the agents whose grants widened.

### The upgrade guide

`UPGRADING.md` at the repo root, linked from the README and from the new `CHANGELOG.md` (#328). It is a file of its own because its commands are standing instructions for each route, not a release note. Its shape:

1. What changed and why, in a paragraph: the tiers went, and why v2 had them.
2. Marketplace: the update commands, and what `renames` does for you.
3. `install-agents.sh`: re-run it, and what it will offer to remove.
4. Hand copies: the removal commands.
5. The agent table: old name, what happened, new name, new plugin.
6. Agents whose tools changed.

## Consequences: what changes where

| Place | Change |
| --- | --- |
| `CLAUDE.md` | Repository Structure loses the tier column and numbers. "Optional fields by tier", "Category tier and stamp tier", the Body skeleton status column and the Security Safeguards table are re-keyed to profiles. The read-only and `disallowedTools` paragraphs go. #388's Tier 1 rules go. Auto mode's default is corrected. `scripts/agent_file.py` is named. A link to this record |
| `AGENT_SECURITY_GUIDELINES.md` | §1 updated to the current docs. §2 and §3 "Content by tier" re-keyed. §5 example titles. §7: three source blocks under named headings, and the "Keyed by tier" paragraph replaced |
| `templates/` | `operating-notes-findings.md`, `-local.md`, `-live.md` replace `tier1`–`tier5`. `agent-template.md` guidance re-keyed; `disallowedTools` removed |
| `scripts/agent_file.py` | `category_tier` and `stamp_tier` replaced by a profile function of `tools` and the marker. `TIER_OVERRIDE_RE` removed |
| `scripts/lint_frontmatter.py`, `lint_body.py` | `TIER_COLOR`, `TIER_MAX_TURNS`, `SECTION_RULES` re-keyed by profile. The Tier 1 Bash rule deleted. Effort rule takes the profile. A new finding for `disallowedTools` |
| `scripts/catalog_lint.py`, `stamp_sections.py` | Allowlist rules cut to one. §7 read by heading. `--live` on the stamper. No dependence on `NN-` |
| `tests/` | `builders.py` builds by profile. The tier-keyed tests in `test_agent_lint.py`, `test_catalog_lint.py` and `test_stamp_sections.py` are rewritten first, per the repo's rule |
| `scripts/lint-allowlist.txt` | Both entries removed; header rewritten |
| `scripts/lint-enforced-categories.txt` | Unchanged in purpose. Directory names without numbers |
| `scripts/validate-catalog.sh` | The literal `categories/07-language-and-framework-specialists/` path |
| `.claude/agents/agent-uplifter.md` | The lines that hard-code tier rules, in the same PR as the policy |
| `install-agents.sh` | Category discovery without the `^[0-9]*-` pattern; stale-file detection (#320) |
| `tools/subagent-catalog/` | Its README grep already fails on the current headings. Replaced by #314, whose index carries the derived capability and `live` |
| Root `README.md` | "Risk Tiers at a Glance" and the tier emoji go. Operating assumptions added. Links repointed |
| Category `README.md` files | The `**Risk Tier:**` line removed from 23 files. The merged category's README absorbs the five agents |
| `.claude-plugin/marketplace.json` | 23 entries with new `source` paths. `renames`. `metadata.description` loses "risk-tiered" |
| Category `plugin.json` files | `data-and-database` and `production-ops-and-observability` list their new agents; `testing-and-qa` drops one. The 24th is deleted |
| The four stamped agent files | Re-stamped with `profile=` |

## What survives of the uplift work

No category is enforced on the train yet. The four uplifts are open PRs (#378, #381, #380, #379), so nothing merged has to be redone.

- **Survives unchanged:** every body section that isn't about the tier. Scope, the domain sections, Expert practice, Output, the description, and the model changes.
- **Mechanical, scriptable:** the directory move, `color`, removing `disallowedTools`, and the re-stamp.
- **Rework:** the agents that regain Bash. Their step 1 and Output say "the caller passes in" and "for the caller to run". In the four PRs that is thirteen agents: `api-designer`, `graphql-architect`, `microservices-architect`, `schema-designer`, `system-modeler`, `api-documenter`, `documentation-engineer`, `effort-estimator`, `product-manager`, `project-manager`, `release-planner`, `scrum-master`, `task-planner`.
- **Per PR:** #378 is mechanical. #381 and #380 need rework on five and two agents. #379 needs rework on six of its eight.

The order that avoids doing work twice: policy, lint and templates first (#390); then the restructure (#391); then the four open PRs merge the train in and are corrected; then the remaining uplifts.

## Stack bundles (#313)

**Unblocked by this model. Not built in v3.0.0.**

No record was found that #313 was paused, or of a rule that a plugin must hold one risk tier. The rule was an implication of v2's premise that agents in a category share a blast radius. With tiers gone as a grouping axis, a bundle that mixes `terraform-engineer` with `architect-reviewer` breaks nothing. The docs confirm the mechanism: a symlink inside the marketplace is dereferenced.

What #313 now depends on:

- the restructure, so the paths bundles link to are stable;
- the uplift of every agent a bundle includes;
- a check that symlinks survive a Windows clone (`core.symlinks`);
- a rule for the validator's name-uniqueness check when one file ships in two plugins, and for the two scoped names that result.

The grouping leaves room for it: `categories/` stays the one home of every agent file, and nothing is derived from the directory any more.

## Evidence

- v2 origin: #285, PR #290 (`12863b3`), `agents-restructure.md` at `f189a87`, v2.0.0 release notes, #295 (`f22b563`).
- Policy history: #317 / PR #354 (`a28f667`); #318; #319; #327; #386 / PR #388.
- Owner statements: review comments on PR #379 (2026-09-30); sessions of 2026-10-11 and 2026-11-12.
- Claude Code docs, fetched 2026-11-13: `sub-agents`, `permission-modes`, `hooks`, `plugins/manifest-reference`, `plugins/marketplace-reference`, `plugins/host-marketplace`, `plugins/loading`.
- Audits run for this decision on `release/v3.0.0` at `55db4ac`: tier logic in code; tool grants against described jobs for 47 agents; live or local for 78 agents; `v2.2.0` to train diff.

Limits of the evidence:

- Categories 03 and 06 and most of 14–24 are pre-v3 files. Their audit read descriptions and excerpts, not every body in full.
- Categories 08–13 were judged from descriptions. Category 07 was not audited: all 29 are code writers.
- The docs quotes came through a fetch tool that may summarise. Exact wording is re-checked when the policy text is written.

Stale notes this decision corrects:

- `CLAUDE.md`: auto mode is "the built-in default on Pro, Max and Team". It is now the starting mode on every plan.
- Project memory: combined descriptions are "capped at 15,000 tokens". It is a startup warning.
- `CLAUDE.md`: the read-only marker is one "the validator checks". No rule reads it.
- #324, #328, #382: still describe per-PR version bumps that the release train replaced.

## Questions settled in review (2026-11-13)

| Question | Outcome |
| --- | --- |
| Drop the numeric directory prefixes? | **Yes** (owner). |
| Is one merge and two moves enough? | **Yes.** The owner is willing to break v2 installs where it materially improves v3. Nothing measured shows that merging build, provisioning, release and operations into fewer plugins would, so they stay separate. |
| Where is `live` declared? | **In the file's stamp marker.** The owner asked for the most standard place. Claude Code has no field for it, so neither option is standard. The marker travels with the file when someone copies it; a line in this repo's allowlist does not. |
| Remove `disallowedTools`? | **Yes** (owner). |
| One `maxTurns` ceiling of 40 for live agents? | **Yes** (owner), on the understanding that the cap must not stop a useful agent part-way through something critical. No live agent has been run under a cap, and there is no realistic test task to measure one with, so 40 ships unmeasured and is adjusted in a patch or minor release if agents hit it. A cap that is too tight is worse than none: the calling session then does the work itself with no operating notes at all. |
| Where was the one-tier-per-collection rule stated? | Nowhere in writing. The owner recalls it as a convention from the v2 restructure: a tier was treated as a natural grouping and kept to. It is what refused `scrum-master` its Bash, and that disruption led to this record. |
