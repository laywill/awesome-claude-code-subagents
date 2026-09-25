# Agent Safeguards Policy

This document decides which safety content belongs in an agent file and which does not. It is written for maintainers reviewing agent files and for agent sessions applying the policy during the v3 uplift (#329–#352).

It is policy only. The v3 agent template (#327) says where each kept item goes in the file; #318 stamps the shared operating notes and lints for banned content; the frontmatter tier table (#319) lives in CLAUDE.md under Agent File Format.

Platform facts below were checked against the Claude Code docs on 2026-09-25 (sources at the end). If the docs change, update this file first; don't let agent files drift from it.

---

## The policy in brief

1. **Keep expert practice.** Dry-run, plan before apply, back up before a destructive change, confirm the target, pin versions, operate on one unit at a time. It is written as how a senior practitioner works, and it improves results in every permission mode.
2. **Keep rollback CLI commands** for the domain: real commands that undo what this agent changes.
3. **Keep domain approval gates**, but only where they encode a real human process in this domain, such as DBA sign-off for production DDL or a pentest's rules of engagement.
4. **Stamp one operating-notes block per tier**, generated from a template, never hand-written.
5. **Delete** generic Emergency Stop, generic Blast Radius Controls, generic Approval Gates, Input Validation that amounts to "validate inputs", Audit Logging, embedded implementation code, and invented thresholds.
6. **Enforce through frontmatter, not prose.** `tools`, `disallowedTools`, `isolation` and `maxTurns` are the only controls an agent file really enforces.

The `## Security Safeguards` heading and its LOW/MEDIUM/HIGH/CRITICAL matrix are retired. Content that survives moves into the #327 template's sections: **Expert practice**, the stamped **Operating notes**, **Rollback** and **Approval gates**.

---

## 1. What actually protects a user

### Permission modes

| Mode | What runs without asking | What stops a damaging command | Does agent prose add a control? |
| --- | --- | --- | --- |
| `default` (Manual) | Reads only | The user approves every edit and every non-read-only command | No. A prose "approval gate" repeats the permission prompt. |
| `acceptEdits` | Reads, file edits, and common filesystem commands (`mkdir`, `touch`, `mv`, `cp`) | Other Bash still prompts | No. The dangerous operations are Bash commands, and those still prompt. |
| `plan` | Reads, plus classifier-approved commands when auto mode is available | No edits; commands prompt or go to the classifier | No. |
| `auto` | Everything, subject to the classifier | Deny and ask rules first, then the classifier model reviewing each action | Marginal. See below. |
| `dontAsk` | Reads and pre-approved tools; anything else is denied | The allowlist | No. |
| `bypassPermissions` | Everything | Deny rules, explicit ask rules, critical-path `rm` checks, and whatever contains the process | It's the only in-agent layer, but the docs restrict this mode to isolated containers and VMs and say it "offers no protection against prompt injection or unintended actions". |

Consequences:

- **Auto mode is the built-in starting mode on Pro, Max and Team plans.** It is the mode most of our users are in, so the classifier is the control most of them actually have.
- Subagents inherit the session's mode. Under auto mode, the classifier evaluates the subagent's tool calls against the main conversation's block and allow rules.
- **Prose is the last line of defence only in bypass mode run outside a container**, which is an unsupported setup, and a paragraph asking the model to be careful is a weak control there. The honest response is to state the supported setups in the README (#323), not to spread warnings across 149 files.
- **Deny rules apply in every mode**, including `bypassPermissions`. A user who needs a hard guarantee writes a `permissions.deny` rule. An agent file cannot supply one.
- The docs say the classifier reads the user's messages, the commands Claude runs, and the CLAUDE.md files Claude loads. They don't say it reads subagent definitions. Don't write agent prose on the assumption that it steers the classifier.

### What the auto-mode classifier blocks by default

The classifier trusts the working directory and the repo's configured remotes. It treats everything else as external until the user configures `autoMode.environment`. Out of the box it blocks, among other things:

- **Git:** force push; `git reset --hard`, `git checkout -- .`, `git restore .`, `git clean -fd`, `git stash drop`/`clear`; amending a commit that was pushed or that the session didn't create; changing remotes the user didn't name.
- **Deploys and infrastructure:** production deploys and migrations; `terraform`/`pulumi`/`cdk`/`terragrunt destroy` and applying a plan that destroys resources; changes to protected IaC scopes; modifying shared infrastructure; toggling, ramping or deleting production feature flags; posting commands to automation such as `atlantis apply` or `/deploy`.
- **Cloud and clusters:** mass deletion on cloud storage; deleting stateful resources the session didn't create; draining and removing nodes; DaemonSets and admission webhooks; cluster writes that reach beyond the named resource (`--all`, broad selectors); shells or port-forwards into sensitive remote targets.
- **Identity and secrets:** granting IAM or repo permissions; writing to a secret manager; DNS and TLS certificate changes; printing a live credential; reading host credentials or the instance-metadata endpoint.
- **Supply chain and exfiltration:** `curl | bash`; routing installs around the internal registry; sending sensitive data to external endpoints; committing or pushing changes that send secrets outside the repo; public tunnels and reverse shells.
- **Review bypass:** merging an unapproved PR; approving Claude's own PR; disabling CI checks; deleting or force-passing tests that guard security behaviour; flags that disarm a safety guard, such as `--insecure`.

Run `claude auto-mode defaults` for the current full list. Several rules are version-gated, and several (production targets, protected IaC scopes) fall back to name heuristics such as `prod` until the user configures them.

**This covers most of what our CRITICAL and HIGH prose tried to cover**, and it does so by checking the actual tool call rather than asking the model to remember a paragraph.

### What the classifier correctly allows, and why expert practice still matters

By default the classifier allows local file operations, installing dependencies declared in manifests, read-only HTTP, pushes to any branch of the working repo (including the default branch), and anything inside the trust boundary. A migration against a dev database, a lockfile regeneration, or a `kubectl apply` against a cluster the classifier doesn't recognise as production are not blocked. Some of those are still mistakes. A competent engineer dry-runs the migration, diffs the manifest, and checks `kubectl config current-context` first. That competence is what agent files are for.

---

## 2. What an agent file can enforce

| Field | Effect | Status for this catalog |
| --- | --- | --- |
| `tools` | Allowlist of tools the agent can call | **Primary lever.** Minimum for the role. |
| `disallowedTools` | Removes tools, including `mcp__*` patterns; applied to inherited or listed tools | Use on read-only roles so they don't inherit MCP write tools. |
| `isolation: worktree` | Runs the agent in a temporary git worktree | For agents that build, migrate or refactor locally. |
| `maxTurns` | Hard stop; output is returned marked partial | For Tier 4 and 5. |
| `permissionMode` | **Ignored in plugin agents.** Elsewhere it is ignored whenever the parent session is in `auto`, `acceptEdits` or `bypassPermissions`, and a subagent that declares `bypassPermissions` keeps the parent's mode. | **Never use.** |
| `hooks` | **Ignored in plugin agents** | **Never use.** Hooks are a separate question (#325). |
| `mcpServers` | **Ignored in plugin agents** | **Never use.** |
| `initialPrompt` | **Ignored in plugin agents**; applies only when the agent runs as the main session agent | **Never use.** |

Which tier gets which of `disallowedTools`, `isolation`, `maxTurns`, `effort` and `color` is decided by #319. That table is in CLAUDE.md under Agent File Format; this document doesn't restate it.

Two consequences:

- **`permissionMode` cannot tighten a permissive session.** Even in an agent copied into `~/.claude/agents/` (which is how `install-agents.sh` installs), `permissionMode: default` does nothing while the user is in auto mode. The same file ships in plugins, where the field is ignored outright, and we don't maintain two variants.
- **A mismatch between an agent's tier and its tools is fixed in `tools`, not with prose.** A Tier 1 reviewer holding `Bash` loses `Bash`; it doesn't gain a paragraph about being careful with `Bash`. #318 lints for this.

---

## 3. Keep and delete

### Keep

**Expert practice.** This is operating technique specific to the domain, of the kind a senior practitioner uses and a generalist forgets. Write it as how the agent works, not as a warning. Examples:

- plan or diff before apply: `terraform plan`, `kubectl diff`, `helm upgrade --dry-run`, `EXPLAIN`
- dry-run first: `kubectl apply --dry-run=server`, `--check` modes, generating into a temporary directory
- back up before a destructive schema or data change, and confirm that the backup restores
- confirm the target environment with the domain's own command: `kubectl config current-context`, `SELECT current_database()`, `az account show`, `aws sts get-caller-identity`
- pin versions and image tags or digests; no `latest` in anything deployed
- operate on one unit at a time (one namespace, one node, one batch), verify it, then continue
- the domain's real supply-chain checks, such as typosquatting, registry source and lockfile integrity

This goes under **Expert practice** in the #327 template.

**Rollback CLI commands.** Real, targeted commands that undo what this agent changes: `kubectl rollout undo`, `helm rollback`, `alembic downgrade -1`, `flyway undo`, restoring a lockfile from git, restoring a Grafana dashboard version. Placeholders such as `<release>` are fine. This goes under **Rollback**. Rules:

- The commands must undo *this agent's* changes. `git revert <sha>` alone is not domain rollback. Every agent can do that, so it fails the swap test (§4).
- Prefer targeted commands (`git restore --source=<sha> -- <path>`) over blanket ones (`git checkout .`, `git reset --hard`), which the classifier blocks anyway.
- No `-auto-approve`, `--force` or `--yes` in a rollback path that runs against shared infrastructure.

**Domain approval gates.** A gate is kept only if it passes all three tests:

1. **It names a human role or process that really exists in this domain:** a DBA, a data owner, a change advisory board, a maintenance window, rules of engagement, a security team for privilege grants.
2. **It names the operation that triggers it:** production DDL, `TRUNCATE`, a `GRANT`, active exploitation of a host.
3. **The agent can't satisfy it alone.** If the agent could do it itself (run a dry-run, check a context), it is expert practice, not a gate.

Write it as one line: *what triggers it → who confirms*. Where the user has no such process, the agent says so and continues; it doesn't invent one. This goes under **Approval gates**.

**Operating notes (stamped).** One short block per tier, generated from `templates/operating-notes-tier{1..5}.md` by #318. The agent can't infer from the conversation whether it is pointed at production, so the note tells it what to establish first. The wording is drafted in §7. Never hand-edit a stamped block.

### Delete

| Content | Why it goes |
| --- | --- |
| **Generic Emergency Stop** (a `/tmp/..._EMERGENCY_STOP` file check) | Nobody creates the file, and the agent only checks it between commands. The user already has Esc and Ctrl+C, deny rules, and the classifier. Where a *domain* has a real halt mechanism (a chaos tool's abort command, pausing a rollout), keep it as a rollback or expert-practice command. |
| **Generic Blast Radius Controls** ("start small", "canary first", invented per-environment caps) | Either it restates the classifier's rules about broad selectors and shared infrastructure, or it's a number nobody measured. Domain-specific scoping ("one namespace at a time", a progressive traffic schedule) is expert practice; keep it there. |
| **Generic Approval Gates** (change ticket, on-call notified, peer review, "rollback tested within 7 days", `read -p "Type CONFIRM"`) | The same checklist in 46 files encodes no specific process. In manual mode it repeats the permission prompt; in auto mode the classifier is the gate. A `read -p` prompt can't even run: Claude's Bash has no interactive stdin. |
| **Input Validation that amounts to "validate inputs"** (shell metacharacter lists, `../` traversal, identifier regexes, "reject `;` in package names") | The agent composes its own commands; there is no untrusted user string being interpolated. The swap test fails: the same bullets appear in `python-pro` and `lockfile-resolver`. Domain-specific checks (typosquatting, registry source, `kube-system` as a write target) are expert practice. |
| **Audit Logging** | Audit trails belong to the platform and the user's own hooks or telemetry, not to agent prose. Code-level logging in the user's project follows the user's requirements. |
| **Embedded implementation code** (validator classes, logger setup, bash scripts that enforce a gate or check a stop file) | The agent writes code at runtime. Embedded enforcement code bloats the definition, and it isn't enforcement: nothing runs it. Rollback CLI commands are the exception. |
| **Invented thresholds** ("rollback in < 5 minutes", "max 3 namespaces", "retention 30 days", "< 10K rows per transaction") | The agent can't measure them, and they came from nowhere. Replace them with a checkable practice ("batch large DML and verify each batch") or with the user's own number, or delete them. |
| **"Environment adaptability" preambles** hand-written into individual files | Replaced by the stamped operating notes. |

### Content by tier

Tier is the category's tier (CLAUDE.md, Repository Structure). This replaces the old LOW/MEDIUM/HIGH/CRITICAL matrix.

| Content | Tier 1 🟢 | Tier 2 🟡 | Tier 3 🟠 | Tier 4 🔴 | Tier 5 ⛔ |
| --- | :-: | :-: | :-: | :-: | :-: |
| Operating notes (stamped) | ✓ | ✓ | ✓ | ✓ | ✓ |
| Expert practice | where the domain has it | ✓ | ✓ | ✓ | ✓ |
| Rollback (CLI commands) | — | only for state outside git | ✓ | ✓ | ✓ |
| Domain approval gates | — | rarely | where a real process exists | where a real process exists | where a real process exists |
| Emergency Stop, generic Blast Radius, generic Approval Gates, generic Input Validation, Audit Logging, embedded code | never | never | never | never | never |

**Read-only override:** an agent in Tier 3–5 that holds none of `Bash`, `Write` or `Edit` gets the Tier 1 operating notes and no Rollback section. It changes nothing, so there is nothing to roll back. #318 can derive this from `tools` mechanically.

**Tier 2 rollback:** changes in the working tree are undone with git, and every model knows how. A Tier 2 agent gets a Rollback section only when it changes state that git doesn't track: a local database migration, an installed toolchain, generated artifacts outside the repo.

---

## 4. Classifying safeguard content

Take each paragraph, bullet or checklist item on its own and apply these tests in order. The first test that matches decides.

| # | Test | Verdict |
| --- | --- | --- |
| 1 | Is it Audit Logging, or code that implements validation, logging, a gate or a stop check? | **Delete.** |
| 2 | Is it a stop-file or kill-switch-file check? | **Delete.** Keep a domain halt *command*, such as `kubectl argo rollouts abort`, under Rollback. |
| 3 | Does it restate a permission prompt or a classifier rule? ("confirm before destructive actions", "never force push", "type CONFIRM for production", "don't `--all` in production") | **Delete.** |
| 4 | **Swap test:** would the sentence be equally true pasted into an unrelated agent, such as `content-marketer`, `python-pro` or `kubernetes-specialist`? (metacharacter lists, `../` traversal, "change ticket linked", "peer review completed", "rollback tested") | **Delete.** |
| 5 | Is it a number the agent can't measure, or one with no source? ("rollback < 5 min", "max 3 namespaces", "retention 30 days") | **Delete**, or rewrite it as a checkable practice. A domain default that is presented as a default for the user to tune, such as a canary step schedule or analysis thresholds, is not caught here; it goes to test 8. |
| 6 | Does it name a real human role or process in this domain, triggered by a specific operation, that the agent can't satisfy alone? | **Keep → Approval gates**, as one line: *trigger → who confirms*. |
| 7 | Is it a command that undoes this agent's changes? | **Keep → Rollback.** Make it targeted, with no auto-approve flags. |
| 8 | Is it a domain technique: plan, diff, dry-run, backup, target check, version pin, one unit at a time, domain supply-chain check? | **Keep → Expert practice**, written as how the agent works, without MUST and without warnings. |
| 9 | None of the above | **Delete.** If it seems valuable, it is probably domain knowledge; move it to the body and tell the reviewer. |

Rewrite tone as you move content. "All inputs MUST be validated before use in any kubectl operation" becomes "Check `kubectl config current-context` before the first change." Short, specific, and in the domain's own commands.

---

## 5. Worked examples

These are real excerpts from the catalog before the v3 uplift. They are trimmed, and each "after" shows the destination section.

### A. `dashboard-builder` (Tier 5): a generic gate and generic controls, mostly deleted

**Before:**

```markdown
### Approval Gates
- [ ] **Change ticket referenced** *(if available)*
- [ ] **Dashboard reviewed** — diff reviewed by at least one team member *(if available)*
- [ ] **Query performance validated** — no queries exceeding 30s execution time
- [ ] **Environment confirmed** — Target Grafana org/Datadog account explicitly confirmed
- [ ] **Rollback plan documented** — Previous dashboard version ID or JSON backup captured before overwrite
Enforcement: (bash script with `read CONFIRM`)

### Emergency Stop
[[ -f /tmp/DASHBOARD_EMERGENCY_STOP ]] && echo "EMERGENCY STOP ACTIVE" && exit 1

### Blast Radius Controls
| production | Max 5 dashboards | Max 30 panels | Max 5 new alerts |
```

**Verdicts:** change ticket and peer review → test 4, delete. The 30s query limit → test 5, delete. Enforcement script → test 1, delete. Emergency Stop → test 2, delete. Per-environment caps → test 5, delete. "Environment confirmed" and "back up before overwrite" → test 8, keep. The Grafana and Datadog restore commands → test 7, keep. `terraform apply -auto-approve` in the rollback path → rewrite without the flag.

**After:**

```markdown
## Expert practice
- Confirm the target Grafana org or Datadog account before writing; never default to production.
- Export the current dashboard JSON (or note its version number) before overwriting it.
- Run each panel query over the dashboard's default time range before saving it.

## Rollback
curl -X POST -H "Authorization: Bearer $GRAFANA_TOKEN" \
  "$GRAFANA_URL/api/dashboards/uid/<uid>/restore" -d '{"version": <n>}'
```

No approval gate survives, because dashboards have no real human process that is specific to this domain.

### B. `database-administrator` (Tier 5): domain gates kept

**Before:**

```markdown
- [ ] **Change ticket** *(if available)*
- [ ] **DBA approval for DDL** *(if available)*: All DDL require senior DBA sign-off
- [ ] **Change window confirmed**: Operation scheduled within approved maintenance window
- [ ] **Rollback plan tested**: Rollback script executed on staging replica within 24 hours
- [ ] **Environment confirmed**: `SELECT current_database()` or `SELECT @@hostname, @@port`
- [ ] **Backup verified**: Fresh backup completed and verified restorable before destructive operations
- `DROP TABLE/DATABASE`: Requires 2 DBA approvals + engineering manager sign-off
- `TRUNCATE` on production: Data owner confirmation + backup verification
- `DELETE` without `WHERE`: Blocked unconditionally
- Privilege grants (`GRANT`, `REVOKE`): Security team approval
```

**Verdicts:** DBA sign-off for production DDL, the maintenance window, data-owner confirmation for `TRUNCATE`, and security-team approval for grants → test 6, keep as gates. "2 DBA approvals + engineering manager" → test 5 (an invented count); keep the gate and drop the count. Environment check, backup, and no unbounded `DELETE` → test 8, keep. Change ticket and "tested within 24 hours" → tests 4 and 5, delete.

**After:**

```markdown
## Approval gates
- Production DDL (`CREATE`, `ALTER`, `DROP`) → the user confirms DBA sign-off and the maintenance window.
- `TRUNCATE` or bulk `DELETE` on production → the data owner confirms.
- `GRANT` / `REVOKE` → the security team confirms.
If the user's organisation has no such role, say so and continue.

## Expert practice
- Identify the target with `SELECT current_database(), inet_server_addr();` before any change.
- Take a backup before destructive DDL/DML and confirm it restores.
- Never run `UPDATE`/`DELETE` without a `WHERE`; snapshot affected rows into a rollback table first.
```

### C. `kubernetes-specialist` (Tier 4): Blast Radius split between keep and delete

**Before (abridged):** an Emergency Stop function checking `/etc/kubernetes/agent-emergency-stop` before every `kubectl apply`; a gate script with `read -p "Type 'CONFIRM'"`; namespace regexes; then under Blast Radius: "One namespace at a time", "Always scope commands to specific resources by name; avoid `--all`", "Run `kubectl apply --dry-run=server` … before any mutating operation", "When draining nodes, operate on one node at a time".

**Verdicts:** the stop file and the gate script → tests 1 and 2, delete. The namespace regex → test 4, delete. "Avoid `--all`" and draining → test 3; the classifier already blocks broad cluster writes and node drains, so delete them as rules. "One namespace at a time", server-side dry-run, `kubectl diff`, and checking the current context → test 8, keep. Rolling-update `maxUnavailable: 0` is domain knowledge that stays in the body.

**After:**

```markdown
## Expert practice
- Check `kubectl config current-context` and the target namespace before the first change.
- `kubectl diff -f` and `kubectl apply --dry-run=server -f` before applying.
- Change one namespace, verify rollout status, then move to the next.
- Pin images by tag or digest; never `latest`.

## Rollback
kubectl rollout undo deployment/<name> -n <ns> [--to-revision=<n>]
helm rollback <release> <revision> -n <ns> --wait
```

### D. `dependency-manager` vs `dependency-upgrader` (Tier 3): same heading, opposite verdicts

**`dependency-upgrader`, before:**

```markdown
- **Package names**: Allow alphanumeric characters, dots, dashes, underscores, `@`, and `/` only.
  Reject shell metacharacters (`;`, `|`, `&`, `$`, backticks, `>`, `<`).
- **File and directory paths**: Resolve against the project root. Reject `../` traversal.
```

**Verdict:** test 4, delete all of it. This is the template text from the old MEDIUM section, and it appears nearly verbatim in `lockfile-resolver` and `python-pro`.

**`dependency-manager`, before:**

```markdown
- **Package name hygiene**: Flag names that differ from well-known packages by one character
  (`lodahs` vs `lodash`) as potential typosquatting.
- **Registry source**: Only install from the project's declared registry.
- **Checksum and integrity verification**: confirm lockfile integrity fields are present and match.
- **Transitive dependency changes**: surface net-new transitive dependencies before applying.
```

**Verdict:** test 8, keep all of it under **Expert practice**. These are supply-chain checks that a senior dependency engineer does and a generalist skips. The classifier catches routing around an internal registry, but not a typosquatted name from the right registry.

### E. `data-migrator` (Tier 5): an Emergency Stop hiding real practice

**Before:**

```markdown
### Emergency Stop
[[ -f /tmp/DATAMIGRATOR_EMERGENCY_STOP ]] && echo "EMERGENCY STOP ACTIVE" && exit 1
When emergency stop activates: record current checkpoint, skip remaining batches, report last
successfully committed batch ID, and preserve rollback artifacts.

### Blast Radius Controls
| 1 | Single table, 1,000 rows | Row count + checksum match |
| 2 | Single table, full backfill | Checksum + referential integrity |
...
Limit concurrent migration workers to 2 per database host. Cap batch throughput to 50% of I/O headroom.
```

**Verdicts:** the stop-file check → test 2, delete. But "checkpoint, report last committed batch, preserve rollback artifacts" → test 8, keep; resumable batches are real migration practice. The phased scope table → test 8, keep; progressive validation is the method. "2 workers" and "50% of I/O" → test 5, delete.

**After:**

```markdown
## Expert practice
- Migrate in resumable batches; after each, record the last committed batch ID.
- Widen scope in stages — a 1,000-row sample, one full table, one schema, everything —
  checking row counts and checksums at each stage before the next.
- On any mismatch, stop and report the last good batch; keep the rollback snapshot tables.
```

### F. `python-pro` (Tier 2): Input Validation that belongs in the body, or nowhere

**Before:**

```markdown
### Input Validation
Validate all user inputs, external data, API requests before processing.
**Path Traversal Prevention**: Resolve the user path … verify it `is_relative_to(allowed_base)`.
**SQL Injection Prevention**: Always use parameterized queries.
**Command Injection Prevention**: Pass arguments as a list to `subprocess.run()`. Never use `shell=True`.

### Rollback Procedures
**Constraints**: All operations MUST have <5min rollback path. …
1. **Source Code**: Git revert commits …
```

**Verdicts:** these bullets aren't safeguards on the agent. They describe the Python code it writes. "Validate all user inputs" → test 4, delete. The `subprocess` list-args and parameterised-query rules → test 8, keep as secure-coding expert practice in the body, one line each. "<5min" → test 5, delete. Git-based rollback → test 4, and Tier 2 changes are in git, so delete it. `alembic downgrade -1` for local migrations is state outside git; keep it under Rollback.

---

## 6. The old reference agents, reassessed

`chaos-engineer` and `penetration-tester` were the "gold standard" for safeguard design. Neither has a `## Security Safeguards` section; their safety content is in the body.

- **`penetration-tester`**: its design survives, and it remains the reference for *tool minimisation*: `Read, Grep, Glob, Bash`, with no `Write` or `Edit`, in a high-risk domain. Its authorisation-first stance is the model of a **domain approval gate**: rules of engagement are a real, specific, external process that the agent cannot satisfy alone, and the classifier can't know which hosts are in scope. In v3, promote the keyword bullets ("Legal authorization", "Verify authorization") to one explicit gate: *any active test against a host → the user confirms written authorisation and that the host is on the in-scope list; stop at the scope boundary.* Delete the "Ethical considerations" keyword list, which the gate covers.
- **`chaos-engineer`**: this is the reference for **blast radius as domain method**. In chaos engineering, limiting the blast radius is the craft itself, not a generic control, so its "Blast radius control" content (traffic percentage, user segmentation, feature flags, kill switches) is expert practice. But its checklist fails test 5: "Rollback automated < 30s" and "No customer impact" are claims the agent can't verify. In v3: *define the abort condition and the halt command before injecting; start in non-production or at the smallest traffic share; stop when the abort condition fires.* Keep a game-day sign-off with service owners as a gate. It holds `Write`/`Edit`/`Bash`, which suits Tier 2, and its category's `isolation` rule comes from #319.

Neither agent is a template to copy. The principle they illustrate survives: **specific to the domain, checkable, minimally tooled.**

---

## 7. Stamped operating notes

Drafted here for #318, which owns `templates/operating-notes-tier{1..5}.md` and the stamping script. The block includes its own heading, so the stamped region is self-contained.

**Keyed by tier, not by capability class.** Tier comes from the category directory, so the stamper and the validator can choose the block without judgment. Capability (Bash or not) is enforced separately through `tools` and the #319 lint, and the one case where it must override the tier is handled mechanically by the read-only override in §3. Keying by capability class would mean re-classifying 203 files by hand, and a file would change class whenever its `tools` changed.

### Tier 1 🟢 (and any read-only agent)

```markdown
<!-- BEGIN GENERATED: operating-notes tier=1 -->
## Operating notes

You are advisory. Read, analyse and recommend; don't edit files or run commands that change state. Hand proposed changes back to the main conversation.
<!-- END GENERATED -->
```

### Tier 2 🟡

```markdown
<!-- BEGIN GENERATED: operating-notes tier=2 -->
## Operating notes

You change code in the local working tree. Keep each change reviewable, and leave committing and pushing to the user unless they ask. Deploys, remote databases and cloud resources are out of scope: say so and stop.
<!-- END GENERATED -->
```

### Tier 3 🟠

```markdown
<!-- BEGIN GENERATED: operating-notes tier=3 -->
## Operating notes

Your work can change dependencies, builds or data. Before the first command that changes state, establish which environment it runs against (local, CI, shared dev or staging) and name it in your reply. If it could be production, stop and ask. Undo steps are under Rollback.
<!-- END GENERATED -->
```

### Tier 4 🔴

```markdown
<!-- BEGIN GENERATED: operating-notes tier=4 -->
## Operating notes

You change external systems: cloud accounts, clusters, networks, identity and third-party services. Before the first change, establish the exact target (account or subscription, project, cluster context, region) and whether it is production; if you can't tell, ask. Show the plan, diff or dry-run before you apply. Follow the user's change process where one exists; don't invent one where it doesn't. Undo steps are under Rollback.
<!-- END GENERATED -->
```

### Tier 5 ⛔

```markdown
<!-- BEGIN GENERATED: operating-notes tier=5 -->
## Operating notes

Treat the target as production unless the user says otherwise. Before the first change, confirm the exact target and that now is an acceptable time to change it. Make the smallest change you can verify and reverse, verify it, then continue. If what you observe differs from what you expected, stop and report before doing anything else. Follow the user's change process where one exists; don't invent one where it doesn't. Undo steps are under Rollback.
<!-- END GENERATED -->
```

The Tier 3–5 notes refer to a Rollback section, so #318 should require one wherever those blocks are stamped. The read-only override takes the Tier 1 block and needs none.

---

## 8. Writing rules

**Do:**

- Use the domain's own commands: "Run `terraform plan`", not "Review changes".
- Write practice as how the agent works: "Diff before applying", not "MUST validate before any operation".
- Keep gates to one line each: *trigger → who confirms*.
- Keep rollback commands targeted and free of auto-approve flags.
- Put numbers in only when the user supplies them or the domain defines them (a canary schedule the user can adjust, a `revisionHistoryLimit`).

**Don't:**

- Use `permissionMode`, `hooks`, `mcpServers` or `initialPrompt` in frontmatter.
- Write Emergency Stop, generic Blast Radius, generic Approval Gates or generic Input Validation sections.
- Add Audit Logging.
- Embed implementation code for validation, logging, gates or stop checks.
- Restate what the permission prompt or the classifier already enforces.
- Hand-edit a stamped block.
- Add safety prose to an agent to compensate for tools it shouldn't have. Fix `tools` instead.

---

## Sources

Checked 2026-09-25:

- [Subagents](https://code.claude.com/docs/en/sub-agents): frontmatter fields; plugin subagents ignore `hooks`, `mcpServers` and `permissionMode`; parent `auto`/`acceptEdits`/`bypassPermissions` overrides a subagent's `permissionMode`; the classifier evaluates subagent calls with the main conversation's rules.
- [Plugin components](https://code.claude.com/docs/en/plugins/components): plugin agents ignore `permissionMode`, `hooks`, `mcpServers` and `initialPrompt`.
- [Permission modes](https://code.claude.com/docs/en/permission-modes): the mode table, the classifier's default block and allow lists, auto mode as the starting mode on Pro/Max/Team, and `bypassPermissions` restricted to isolated containers and VMs.
- [Configure permissions](https://code.claude.com/docs/en/permissions): deny rules apply in every mode.
- [Configure auto mode](https://code.claude.com/docs/en/auto-mode-config): deny and ask rules are evaluated before the classifier; `claude auto-mode defaults`; environment trust slots.
