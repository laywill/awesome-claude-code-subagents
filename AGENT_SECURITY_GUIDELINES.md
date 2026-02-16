# Agent Definition Security Guidelines

Practical guidelines for creating or reviewing agent definition files. Based on the [Security Audit Report](SECURITY_AUDIT_REPORT.md).

---

## How to Classify an Agent

Use this decision tree to determine the risk level:

```
Agent has Bash access?
 NO  --> LOW RISK
 YES --> Can it modify production infrastructure directly?
          YES --> CRITICAL RISK
          NO  --> Does it affect production-adjacent systems (databases, deployments, cloud)?
                   YES --> HIGH RISK
                   NO  --> MEDIUM RISK (development scope)
```

**CRITICAL** = Direct production infrastructure access (k8s clusters, terraform, AD/DNS, security policies, production ML deployment, multi-domain orchestration)

**HIGH** = Production-adjacent systems (databases, deployment pipelines, cloud provisioning, M365 admin, payment processing)

**MEDIUM** = Development tooling with Bash (language specialists, build tools, test runners, local dev)

**LOW** = No Bash access, or Bash usage limited to read-only / UI-focused work

---

## What Each Risk Level Requires

### LOW RISK Agents

No security sections needed. Standard git workflows provide adequate safety.

**Examples**: read-only reviewers, research agents, frontend-only developers, documentation writers

**Tool assignment**: Typically `Read, Grep, Glob` or `Read, Write, Edit, Glob, Grep` (no Bash)

---

### MEDIUM RISK Agents

Add a `## Security Safeguards` section containing:

1. **Environment note** (standard preamble)
2. **Input Validation** (prose rules only)
3. **Rollback Procedures** (CLI commands appropriate to the agent's domain)

**Template:**

```markdown
## Security Safeguards

> **Environment Note**: Ask user about environment once at start. Homelabs/sandboxes
> skip change tickets/on-call notifications. Items marked *(if available)* skip when
> infrastructure missing. Never block on unavailable formal processes -- note skip
> and continue.

### Input Validation

Validate all user inputs before use in shell commands.

- **File/directory paths**: Resolve against project root; reject `../` traversal
  and paths outside the working directory
- **Package names**: Alphanumeric, dots, dashes, underscores, `@`, `/` only;
  reject shell metacharacters (`;`, `|`, `&`, `$`, backticks)
- **Branch names**: `^[a-zA-Z0-9._\-/]+$`; reject spaces and `..`
- [Add domain-specific rules here, e.g. table names for SQL, module names for Go]

### Rollback Procedures

- `git stash` / `git checkout .` for uncommitted file changes
- `git revert <commit>` for committed changes
- [Add domain-specific rollback, e.g. `pip install -r requirements.txt` to restore deps]
```

**What NOT to include:**
- No code blocks implementing validators (the agent knows how to code)
- No audit logging sections (handled by Claude Code Hooks at the platform level)
- No approval gates (not needed for development-scope agents)

---

### HIGH RISK Agents

Add a `## Security Safeguards` section containing:

1. **Environment note** (standard preamble)
2. **Input Validation** (prose rules, domain-specific)
3. **Approval Gates** (pre-execution checklist)
4. **Rollback Procedures** (specific CLI commands)

**Template additions beyond MEDIUM:**

```markdown
### Approval Gates

Pre-execution checklist for staging/production:
- [ ] **Change ticket linked** *(if available)* -- or document purpose in commit message
- [ ] **Dry-run completed** -- [agent-specific dry-run command]. **Always required.**
- [ ] **Rollback tested** -- in non-prod within 7 days
- [ ] **Blast radius estimated** -- affected services/users documented
- [ ] **On-call notified** *(if available)*
```

**Domain-specific approval examples:**
- **database-administrator**: Require `EXPLAIN` before DDL; no `DROP` without backup confirmation
- **deployment-engineer**: Require passing CI before deploy; canary/staged rollout for production
- **cloud-architect**: Require cost estimate before provisioning; tag all resources

**What NOT to include:**
- No audit logging sections (platform handles this)
- No emergency stop mechanisms (reserved for CRITICAL)
- No implementation code blocks for validation logic

---

### CRITICAL RISK Agents

Add a `## Security Safeguards` section containing:

1. **Environment adaptability note** (standard preamble)
2. **Input Validation** (prose rules with specific regex patterns for the domain)
3. **Approval Gates** (comprehensive pre-execution checklist)
4. **Rollback Procedures** (specific CLI commands with timeframes)
5. **Emergency Stop** (halt mechanism)
6. **Blast Radius Controls** (scope limits)

**Template additions beyond HIGH:**

```markdown
### Emergency Stop

Before every command execution, check for stop file:

```bash
[[ -f /tmp/AGENT_EMERGENCY_STOP ]] && echo "EMERGENCY STOP ACTIVE" && exit 1
```

If detected: stop all operations immediately, report current state, do not attempt cleanup.

### Blast Radius Controls

- Start with smallest scope (single instance/service before fleet-wide)
- Production changes: canary environment first
- Maximum affected scope must be documented before execution
- Never run destructive commands across all namespaces/regions simultaneously
```

**Critical-specific input validation examples by domain:**
- **kubernetes-specialist**: Verify context (`kubectl config current-context`) matches intended cluster; reject `--all-namespaces` on destructive commands
- **terraform-engineer**: Require `terraform plan` review before `apply`; never use `-auto-approve` in production
- **security-engineer**: Reject rules with `0.0.0.0/0` source unless explicitly confirmed; require security team sign-off
- **devops-engineer**: Validate image tags exist in registry before deployment; reject `latest` tag in production

**What NOT to include:**
- No audit logging sections (platform handles this via Claude Code Hooks)
- No implementation code for validators (keep prose rules; the agent codes at runtime)
- Avoid embedding full Python/JS validator classes -- they bloat context without adding value

---

## Style Rules for Security Sections

### DO

- Write validation rules as prose with regex patterns where helpful
- Include CLI commands for rollback (these are operational, not implementation code)
- Include the emergency stop bash snippet for CRITICAL agents (it's a 1-line operational check)
- Keep the environment adaptability preamble so agents don't block users unnecessarily
- Make checklist items concrete: "Run `terraform plan`" not "Review changes"
- Use `*(if available)*` for processes that may not exist in smaller setups

### DO NOT

- Embed implementation code blocks (Python validator classes, logging frameworks, etc.)
- Add audit logging requirements (Claude Code Hooks handle this at platform level)
- Add sections that duplicate Claude Code's built-in safety (the platform already confirms destructive commands)
- Over-specify: the agent is an expert in its domain and knows how to implement validation
- Add generic security boilerplate that doesn't relate to the agent's specific domain

---

## Quick Reference: Section Checklist

| Section | LOW | MEDIUM | HIGH | CRITICAL |
|---------|:---:|:------:|:----:|:--------:|
| Environment Note | -- | Yes | Yes | Yes |
| Input Validation | -- | Yes | Yes | Yes |
| Approval Gates | -- | -- | Yes | Yes |
| Rollback Procedures | -- | Yes | Yes | Yes |
| Emergency Stop | -- | -- | -- | Yes |
| Blast Radius Controls | -- | -- | -- | Yes |
| Audit Logging | -- | -- | -- | -- |

**Audit Logging is never included.** It is handled by Claude Code Hooks at the platform level. Code-level logging in the user's project follows user requirements, not agent-file mandates.

---

## Gold Standard Examples

Two agents in the repository demonstrate exemplary safety design:

- **`chaos-engineer`** -- Specific, measurable requirements ("< 30s rollback", "1% of users"), blast radius control, circuit breakers, kill switches
- **`penetration-tester`** -- Authorization-first design, intentionally restricted tools (read-only despite high-risk domain), ethical framework, emergency procedures

When in doubt, model new safeguard sections after these agents' approach: be specific, be measurable, and restrict tools to the minimum needed for the role.

---

## Tool Assignment Guidelines

Assign the minimum tools needed for the role:

| Role Type | Tools | Notes |
|-----------|-------|-------|
| Read-only (reviewers, auditors) | `Read, Grep, Glob` | No modification capability |
| Research (analysts) | `Read, Grep, Glob, WebFetch, WebSearch` | Web access, no file changes |
| Documentation | `Read, Write, Edit, Glob, Grep` | File changes, no shell |
| Code writers (developers) | `Read, Write, Edit, Bash, Glob, Grep` | Full dev capability |
| Infrastructure / Ops | `Read, Write, Edit, Bash, Glob, Grep` | Full capability; safeguards critical |

If an agent doesn't need Bash, don't give it Bash. This is the single most effective way to reduce risk.
