# Production Operations & Observability Subagents

Production Operations & Observability subagents monitor, alert, and respond to production issues. They manage production databases, configure observability infrastructure, run incident response, and ensure systems meet SLA commitments. Every action in this category has immediate impact on live users — proceed with care, escalate when uncertain, and always have rollback plans ready.

**Risk Tier: ⛔ Tier 5 — Critical** — Direct impact on live users and production systems. Changes to production configurations, incident response actions, and database operations are often irreversible in real time. Maximum caution required.

## When to Use Production Operations Agents

Use these subagents when you need to:
- **Respond to incidents** — Triage, investigate, and resolve production outages
- **Configure alerting** — Set up alerting rules, thresholds, and escalation policies
- **Build observability dashboards** — Create dashboards in Grafana, Datadog, or similar tools
- **Manage production databases** — Handle replication, backups, and production DB administration
- **Configure log pipelines** — Set up log aggregation, filtering, and retention
- **Monitor SLA/SLO compliance** — Track error budgets and service level objectives
- **Manage scaling** — Configure auto-scaling and capacity planning

## Available Subagents

### [**alert-configurator**](alert-configurator.md) — Configure alerting rules and escalation policies
Configures alerting rules, thresholds, and on-call escalation policies in PagerDuty, OpsGenie, Grafana Alertmanager, and cloud-native alerting. Designs alert fatigue reduction strategies.

**Use when:** Setting up alerting for new services, tuning noisy alerts, or implementing a new on-call rotation structure.

### [**dashboard-builder**](dashboard-builder.md) — Build observability dashboards
Creates monitoring dashboards in Grafana, Datadog, New Relic, and cloud-native tools. Implements golden signal dashboards (latency, traffic, errors, saturation) and service-specific observability views.

**Use when:** Setting up observability for a new service, building executive SLA dashboards, or creating runbook-linked dashboards for incident response.

### [**database-administrator**](database-administrator.md) — Manage production databases
Administers production databases — schema changes with zero-downtime migrations, replication setup, backup verification, connection pooling, and performance incident response.

**Use when:** Performing production database maintenance, investigating DB performance incidents, or setting up database replication and failover.

### [**devops-incident-responder**](devops-incident-responder.md) — DevOps-focused incident response
Responds to infrastructure and platform incidents — Kubernetes pod failures, deployment rollbacks, infrastructure capacity issues, and CI/CD pipeline incidents. Expert in DevOps-layer troubleshooting.

**Use when:** Infrastructure or platform-level incidents that require DevOps expertise — not application-layer bugs.

### [**incident-responder**](incident-responder.md) — Triage and respond to production incidents
Leads structured incident response — establishing severity, coordinating response, updating stakeholders, executing mitigation steps, and conducting post-incident reviews. Follows ICS/ITIL frameworks.

**Use when:** A production incident requires coordinated response, stakeholder communication, and structured mitigation execution.

### [**log-pipeline-manager**](log-pipeline-manager.md) — Configure log aggregation and retention
Sets up and manages log pipelines — Fluentd/Logstash/Vector configuration, Elasticsearch/OpenSearch indexing, log retention policies, and log-based alerting. Implements structured logging standards.

**Use when:** Setting up centralised logging, managing log storage costs, or implementing log-based monitoring and alerting.

### [**scaling-manager**](scaling-manager.md) — Configure auto-scaling and capacity planning
Configures horizontal and vertical auto-scaling for cloud services and Kubernetes workloads. Conducts capacity planning, load testing analysis, and scaling policy optimisation.

**Use when:** Services are under-provisioned or over-provisioned, setting up auto-scaling for a new service, or planning capacity for anticipated traffic growth.

### [**sla-monitor**](sla-monitor.md) — Track SLA/SLO compliance and error budgets
Implements SLO tracking with error budget calculations, compliance reporting, and alerting on budget burn rate. Integrates with Prometheus, Datadog SLOs, and Google Cloud Monitoring.

**Use when:** Establishing SLOs for a service, tracking compliance for contractual SLAs, or building error budget reporting for engineering teams.

### [**sre-engineer**](sre-engineer.md) — Site reliability engineering and error budgets
Applies SRE practices — defining SLIs/SLOs, implementing error budget policies, building reliability-improving features, and leading capacity planning. Balances reliability work with feature velocity.

**Use when:** Establishing an SRE function, improving service reliability, conducting reliability reviews, or designing systems for higher availability targets.

## Quick Selection Guide

| Task | Subagent | Notes |
|------|----------|-------|
| Respond to a production incident | **incident-responder** | Triage, coordination, stakeholder comms |
| Infrastructure/platform incident | **devops-incident-responder** | Kubernetes, deployments, CI/CD incidents |
| Configure alerting and on-call | **alert-configurator** | Thresholds, escalation, alert fatigue reduction |
| Build monitoring dashboards | **dashboard-builder** | Grafana, Datadog, golden signals |
| Manage production databases | **database-administrator** | Zero-downtime migrations, replication, backup |
| Set up centralised logging | **log-pipeline-manager** | Aggregation, indexing, retention policies |
| Configure auto-scaling | **scaling-manager** | HPA, cloud auto-scaling, capacity planning |
| Track SLO/error budgets | **sla-monitor** | SLO compliance, burn rate alerting |
| Establish SRE practices | **sre-engineer** | SLI/SLO definition, reliability strategy |

## Common Combinations

**"Set up observability for a new service"**
- **sre-engineer** → SLI/SLO definition → **dashboard-builder** → golden signals dashboards → **alert-configurator** → alerting rules → **sla-monitor** → error budget tracking.

**"Respond to a major production incident"**
- **incident-responder** → leads response → **devops-incident-responder** → infrastructure triage → **database-administrator** → DB investigation if needed → **log-pipeline-manager** → log analysis.

**"Prepare for high-traffic event"**
- **scaling-manager** → capacity plan and auto-scaling config → **sre-engineer** → error budget review → **dashboard-builder** → event monitoring dashboard → **alert-configurator** → tightened alerting thresholds.

**"Post-incident improvements"**
- **incident-responder** → post-mortem → **alert-configurator** → improve detection → **dashboard-builder** → add missing visibility → **sre-engineer** → reliability improvements backlog.

## Getting Started

> **These agents operate on production systems with live user impact. Always confirm the blast radius before taking any action.**

1. **Declare incidents clearly** — Use **incident-responder** to establish a clear incident structure before taking action; ad-hoc responses cause confusion.
2. **Have rollback plans ready** — Before any production change, know exactly how to reverse it.
3. **Communicate proactively** — Keep stakeholders informed during incidents; silence is worse than bad news.
4. **Follow runbooks** — Use the runbooks from **runbook-writer** (Documentation category) during incidents rather than improvising.
5. **Conduct post-incident reviews** — Every significant incident should result in documented learnings and reliability improvements.
