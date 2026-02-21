# Deployment & Release Subagents

These subagents manage the critical process of shipping code to production environments. They handle automated deployments, blue-green switches, canary releases, feature flag toggles, and rollback procedures. This category covers the entire spectrum of deployment strategies, from safe progressive rollouts to emergency recovery operations.

**Risk Tier: ⛔ Tier 5 — Critical** — These agents directly control production deployments and traffic. Every action affects live users immediately. Failures can cause service outages, data loss, or security incidents. Always test in staging first, maintain a rollback plan, and have monitoring in place before execution.

## When to Use Deployment & Release Subagents

Use these subagents when you need to:
- **Execute deployments** to staging or production with automated pre/post checks and validation
- **Implement safe rollout strategies** using blue-green deployments or canary releases with traffic management
- **Manage feature flags** to control feature visibility, perform A/B testing, or execute gradual rollouts
- **Perform emergency rollbacks** to revert failed deployments and restore service quickly
- **Orchestrate complex release workflows** combining multiple deployment strategies and validation gates

## Available Subagents

### [**blue-green-switcher**](blue-green-switcher.md) — Switch traffic between deployment slots

Executes traffic switches between blue (current) and green (new) deployment slots with minimal downtime. Manages DNS updates, load balancer configuration, and traffic routing to ensure smooth transitions. Includes health checks and quick switch-back capabilities for rapid rollback if issues are detected post-switch.

**Use when:** You need to perform a blue-green deployment and switch production traffic from the current version to a new version already running in a separate slot.

### [**canary-release-controller**](canary-release-controller.md) — Manage canary releases with traffic shifting and metrics gates

Orchestrates progressive canary releases by gradually shifting traffic to a new version while monitoring error rates, latency, and custom metrics. Implements automated rollback if configured thresholds are exceeded during the canary phase. Coordinates multiple deployments across infrastructure while maintaining full observability and control.

**Use when:** You want to safely roll out a new version to a small subset of traffic first, verify it performs well, then gradually increase exposure before full deployment.

### [**deployer**](deployer.md) — Automated deployment execution with pre/post checks

Executes automated deployments to staging or production environments with comprehensive validation. Runs pre-deployment checks (health, configuration, dependencies), performs the deployment, and validates post-deployment with smoke tests and health checks. Logs all operations for audit trails and supports automatic rollback on validation failures.

**Use when:** You need a straightforward, fully automated deployment to a target environment with built-in safety checks and validation.

### [**deployment-engineer**](deployment-engineer.md) — Execute deployments to staging and production environments

Manages end-to-end deployment workflows to staging and production with orchestrated pre/post deployment procedures. Coordinates container updates, service restarts, database migrations, and configuration changes. Provides detailed progress reporting and handles environment-specific deployment logic while maintaining deployment history.

**Use when:** You're performing complex deployments requiring orchestration of multiple components, configuration management, and environment-specific handling.

### [**feature-flag-manager**](feature-flag-manager.md) — Toggle feature flags in LaunchDarkly, Unleash, etc.

Manages feature flags across major platforms (LaunchDarkly, Unleash, Flags.ai, ConfigCat) to control feature visibility and enable A/B testing. Supports creating, enabling, disabling, and targeting specific user segments or percentage-based rollouts. Allows decoupling feature deployment from code deployment for safer, more flexible release strategies.

**Use when:** You need to toggle features on/off in production, run experiments, or control feature visibility to specific user groups without redeploying code.

### [**rollback-manager**](rollback-manager.md) — Roll back failed deployments to last known good state

Executes rapid rollback procedures to restore the previous known-good version when a deployment fails or causes production issues. Coordinates infrastructure rollback (container/service reversion), data state restoration, and verification steps. Provides detailed rollback status and post-rollback validation to ensure service stability.

**Use when:** A deployment has failed or is causing production incidents, and you need to quickly revert to the last stable version and restore service.

## Quick Selection Guide

| Task | Subagent | Notes |
|------|----------|-------|
| Switch production traffic to a new version already deployed in parallel | **blue-green-switcher** | Minimal downtime; requires blue/green infrastructure |
| Gradually roll out a new version with traffic shifting and metrics monitoring | **canary-release-controller** | Safest for risky changes; automated rollback if metrics degrade |
| Deploy code with automated validation and health checks | **deployer** | Best for straightforward, atomic deployments |
| Orchestrate multi-component deployment with config and database changes | **deployment-engineer** | Complex deployments with multiple moving parts |
| Enable/disable features without redeploying code | **feature-flag-manager** | Fastest way to toggle production behavior; supports user targeting |
| Revert a failed deployment to the previous version | **rollback-manager** | Emergency recovery; always have a rollback plan |
| Test a new version with a subset of users before full rollout | **canary-release-controller** or **feature-flag-manager** | Canary for infrastructure changes; feature flags for code features |
| Perform A/B testing with different code versions | **feature-flag-manager** | Simplest approach; supports segment-based targeting |

## Common Combinations

**Safe Production Rollout (Recommended for Critical Services):**
- **canary-release-controller** + **deployment-engineer** + **feature-flag-manager** — Deploy new version using canary strategy with deployment orchestration, enable features gradually via flags, monitor metrics, and scale up traffic as confidence builds.

**Blue-Green Deployment with Feature Control:**
- **deployment-engineer** + **blue-green-switcher** + **rollback-manager** — Deploy new version to green slot with full orchestration, perform health checks, switch traffic with blue-green switcher, keep rollback-manager on standby for instant reversion if issues arise.

**Feature Release Without Redeployment:**
- **feature-flag-manager** — Code already deployed; toggle features on/off for different user segments, run A/B tests, and adjust visibility without infrastructure changes. Fastest path to production when code is ready.

**Emergency Rollback and Recovery:**
- **rollback-manager** + **deployment-engineer** — Immediately revert to previous version with rollback-manager, then use deployment-engineer for detailed post-rollback verification and state restoration.

## Getting Started

1. **Understand your deployment infrastructure** — Identify whether you use blue-green slots, container orchestration, or load balancers. Know your service's pre/post-deployment requirements.

2. **Start with feature flags** — If you're deploying code that's feature-gated, use **feature-flag-manager** to control visibility without infrastructure changes.

3. **Use canary releases for significant changes** — For high-risk deployments (database schema changes, major algorithm changes), use **canary-release-controller** with appropriate metrics gates.

4. **Have a rollback plan** — Before running any deployment subagent, ensure you understand how to roll back. Test your rollback procedure in staging first.

5. **Integrate monitoring** — Deployment subagents can monitor metrics and health checks. Configure your observability platform to provide real-time feedback during deployments.

6. **Test in staging first** — Always validate your entire deployment workflow in a staging environment before production execution.

7. **Enable audit logging** — Deployments affect all users. Ensure all deployment actions are logged for compliance, incident investigation, and operational learning.

## Critical Risk Warnings

- **Every deployment affects live users** — Test thoroughly in staging environments before production execution. A failed deployment can cause service outages.

- **Always maintain a rollback capability** — Have the previous version readily available and test rollback procedures. Use **rollback-manager** if you need rapid recovery.

- **Validate before and after** — Both pre-deployment checks and post-deployment validation are essential. Don't skip health checks or smoke tests.

- **Monitor during deployments** — Watch metrics, error rates, and user-impacting signals during canary releases or traffic switches. Be ready to rollback immediately if anomalies appear.

- **Coordinate with observability** — Ensure your monitoring, logging, and alerting systems are active before initiating deployments. Deployment failures are much easier to detect with real-time telemetry.

- **Use appropriate strategies for risk level** — Low-risk changes can use direct deployments; high-risk changes should use canary releases or blue-green deployments with extensive validation.

- **Communicate with stakeholders** — For critical production deployments, inform relevant teams. Coordinate maintenance windows if necessary.
