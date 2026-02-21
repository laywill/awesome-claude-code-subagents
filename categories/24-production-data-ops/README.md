# Production Data Operations Subagents

Production Data Operations subagents perform direct operations on live production data — migrations, backups, anonymisation, replication, and retention enforcement. These operations often have irreversible consequences: a failed migration may corrupt live data, and retention enforcement permanently deletes records. This is the highest-risk category — use maximum caution, always backup first, and always test in a staging environment with production-like data.

**Risk Tier: ⛔ Tier 5 — Critical** — Direct operations on live production data with potentially irreversible consequences. Always backup first, test in staging, and have explicit rollback plans. Some actions (data deletion under GDPR) cannot be undone.

## When to Use Production Data Operations Agents

Use these subagents when you need to:
- **Run data migrations** — Apply schema or data migrations to production databases
- **Manage backups** — Orchestrate backups, verify integrity, and perform restores
- **Anonymise PII** — Redact or pseudonymise personal data for compliance
- **Enforce retention** — Apply data deletion policies under GDPR, CCPA, or internal policies
- **Configure replication** — Set up or modify database replication and failover

## Available Subagents

### [**backup-restore-manager**](backup-restore-manager.md) — Manage backups and perform restores
Manages database backup schedules, verifies backup integrity through test restores, and performs production restores when needed. Handles point-in-time recovery, cross-region backup replication, and backup retention policies.

**Use when:** Setting up automated backups, verifying backup integrity before a risky operation, or performing a production database restore.

### [**data-anonymizer**](data-anonymizer.md) — Anonymise PII in production data
Anonymises or pseudonymises personally identifiable information in production datasets — email addresses, names, phone numbers, and other PII. Implements GDPR/CCPA-compliant anonymisation techniques while preserving referential integrity.

**Use when:** Creating anonymised copies of production data for development/testing, complying with data subject rights requests, or preparing datasets for sharing with third parties.

### [**data-migrator**](data-migrator.md) — Run data migrations against production databases
Executes data migrations on production databases — schema changes, data transformations, and large-scale data moves. Implements zero-downtime migration patterns (expand/contract, dual-write, shadow tables).

**Use when:** Applying a migration to production that involves significant data transformation, large-volume data moves, or high-risk schema changes.

### [**replication-configurator**](replication-configurator.md) — Configure database replication and failover
Sets up and modifies database replication — PostgreSQL streaming replication, MySQL binlog replication, read replica configuration, and failover procedures. Manages replication lag and consistency guarantees.

**Use when:** Setting up read replicas, configuring replication for a new database cluster, or modifying failover configuration in a production environment.

### [**retention-policy-enforcer**](retention-policy-enforcer.md) — Apply data retention and deletion policies
Implements and executes data retention and deletion policies in compliance with GDPR, CCPA, HIPAA, and internal data governance requirements. Manages scheduled deletion jobs, audit trails, and deletion verification.

**Use when:** Implementing a data retention policy, responding to GDPR right-to-erasure requests, or setting up automated data lifecycle management.

## Quick Selection Guide

| Task | Subagent | Notes |
|------|----------|-------|
| Set up or verify backups | **backup-restore-manager** | Scheduling, integrity verification, restore procedures |
| Restore from backup | **backup-restore-manager** | Point-in-time recovery, cross-region restore |
| Anonymise PII for dev/testing | **data-anonymizer** | GDPR-compliant anonymisation, referential integrity |
| Run a production data migration | **data-migrator** | Zero-downtime patterns, large-volume transforms |
| Configure database replication | **replication-configurator** | Streaming replication, read replicas, failover |
| Enforce GDPR/CCPA deletion policies | **retention-policy-enforcer** | Automated deletion, audit trails, compliance verification |

## Common Combinations

**"Before a risky production migration"**
- **backup-restore-manager** → verify backup and test restore → **data-migrator** → plan migration with rollback → **database-administrator** (Production Ops category) → monitor during execution.

**"GDPR compliance for a new market"**
- **data-anonymizer** → anonymise dev/test databases → **retention-policy-enforcer** → implement deletion policies → **compliance-auditor** (Analysis category) → verify compliance posture.

**"Set up a new production database cluster"**
- **backup-restore-manager** → backup configuration → **replication-configurator** → replication and failover → **data-migrator** → initial data load → **sre-engineer** (Production Ops category) → SLO definition.

**"Respond to a data subject erasure request"**
- **retention-policy-enforcer** → execute deletion → **data-anonymizer** → anonymise remaining references → **backup-restore-manager** → verify deleted data not in accessible backups.

## Getting Started

> **There is no undo for data deletion. Treat every operation here as irreversible until proven otherwise.**

1. **Backup before anything** — Always run **backup-restore-manager** to verify a tested backup exists before any production data operation.
2. **Test with production-like data in staging** — Anonymise production data with **data-anonymizer** to create a realistic staging dataset, then test operations there first.
3. **Use zero-downtime patterns** — **data-migrator** should always use expand/contract or dual-write patterns for production; never lock tables on a live database.
4. **Document everything** — Log all production data operations with timestamps, operators, and scope; this is critical for audit trails and incident recovery.
5. **Plan the rollback** — Before executing any operation, define exactly what rollback looks like and verify it's feasible given your backup state.
