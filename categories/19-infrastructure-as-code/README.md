# Infrastructure as Code Subagents

Infrastructure as Code subagents author cloud infrastructure definitions, Kubernetes manifests, Docker configurations, and platform tooling. These agents define real cloud resources that incur costs and affect team infrastructure when applied. Always review `plan`/`dry-run` output before applying changes, and test in non-production environments first.

**Risk Tier: 🔴 Tier 4 — High** — Authors cloud infrastructure definitions that affect shared resources and may incur costs when applied. Always review plans before applying; use separate environments for testing.

## When to Use Infrastructure as Code Agents

Use these subagents when you need to:
- **Provision cloud resources** — Define AWS, Azure, or GCP infrastructure as Terraform, CloudFormation, or Bicep
- **Manage Kubernetes** — Author manifests, Helm charts, and cluster configurations
- **Containerise applications** — Write Dockerfiles and docker-compose configurations
- **Build internal platforms** — Create self-service infrastructure and golden path templates
- **Configure networking** — Define VPCs, subnets, security groups, and load balancers
- **Manage Windows infrastructure** — Configure Windows Server and Active Directory

## Available Subagents

### [**azure-infra-engineer**](azure-infra-engineer.md) — Azure infrastructure specialist
Designs and implements Azure infrastructure using Bicep, ARM templates, or Terraform. Expert in Azure networking (VNets, NSGs), AKS, Azure Functions, App Service, and Azure-specific security patterns.

**Use when:** Building or managing infrastructure on Microsoft Azure, especially when Azure-specific services (AKS, APIM, Azure AD) are involved.

### [**cloud-architect**](cloud-architect.md) — Cloud infrastructure design and implementation
Designs multi-cloud or single-cloud infrastructure architectures for scalability, reliability, and cost efficiency. Works across AWS, Azure, and GCP with well-architected framework principles.

**Use when:** Designing cloud infrastructure from scratch, migrating on-premises systems to cloud, or reviewing existing cloud architectures for improvement.

### [**cloudformation-builder**](cloudformation-builder.md) — Author CloudFormation and SAM templates
Creates AWS CloudFormation stacks and SAM templates for serverless applications. Handles nested stacks, StackSets, custom resources, and CDK comparisons.

**Use when:** Building AWS-native infrastructure with CloudFormation or deploying serverless applications with AWS SAM.

### [**devops-engineer**](devops-engineer.md) — DevOps automation and toolchain
Builds and maintains CI/CD pipelines, infrastructure automation scripts, deployment tooling, and DevOps platform configurations. Bridges development and operations with automation.

**Use when:** Setting up the DevOps toolchain for a project — combining CI/CD, IaC, monitoring, and deployment automation.

### [**docker-composer**](docker-composer.md) — Write Dockerfiles and docker-compose configurations
Creates optimised Dockerfiles with multi-stage builds, minimal base images, and layer caching. Writes docker-compose configurations for local development and service orchestration.

**Use when:** Containerising an application, setting up a local development environment with multiple services, or optimising existing Docker images.

### [**helm-chart-builder**](helm-chart-builder.md) — Create and maintain Helm charts
Builds Helm charts with configurable values, templating, hooks, and sub-chart dependencies. Creates charts for both application deployment and shared infrastructure components.

**Use when:** Packaging a Kubernetes application for reuse, managing Kubernetes deployments with versioned releases, or creating charts for a Helm repository.

### [**kubernetes-specialist**](kubernetes-specialist.md) — Kubernetes manifests and cluster configuration
Authors and manages Kubernetes manifests — Deployments, Services, ConfigMaps, RBAC, NetworkPolicies, HPA, and custom resources. Handles cluster configuration and operator deployment.

**Use when:** Deploying applications to Kubernetes, configuring cluster policies, or troubleshooting Kubernetes workloads.

### [**network-engineer**](network-engineer.md) — Network infrastructure configuration
Configures cloud networking — VPCs, subnets, route tables, security groups, NAT gateways, load balancers, and DNS. Designs secure, segmented network topologies.

**Use when:** Setting up cloud networking for a new environment, troubleshooting connectivity issues, or hardening network security.

### [**platform-engineer**](platform-engineer.md) — Build and maintain internal developer platforms
Creates internal developer platforms — self-service infrastructure provisioning, golden path templates, internal portals, and developer tooling that abstracts cloud complexity.

**Use when:** Building a platform engineering capability, creating self-service infrastructure for development teams, or implementing golden path templates.

### [**terraform-engineer**](terraform-engineer.md) — Write Terraform modules and configurations
Authors Terraform modules, provider configurations, state management setups, and workspace strategies. Works across all major cloud providers and third-party Terraform providers.

**Use when:** Managing infrastructure with Terraform — from single-resource configurations to complex multi-module, multi-environment setups.

### [**windows-infra-admin**](windows-infra-admin.md) — Windows Server and Active Directory
Configures Windows Server infrastructure — Active Directory, Group Policy, RSAT management, Windows services, and IIS. Automates administration with PowerShell and DSC.

**Use when:** Managing Windows Server environments, configuring Active Directory, or automating Windows infrastructure tasks.

## Quick Selection Guide

| Task | Subagent | Notes |
|------|----------|-------|
| Multi-cloud infrastructure design | **cloud-architect** | Well-architected, cost-efficient, scalable |
| Terraform modules and state | **terraform-engineer** | All providers, modules, workspace strategy |
| AWS CloudFormation or SAM | **cloudformation-builder** | AWS-native IaC, serverless apps |
| Azure-specific infrastructure | **azure-infra-engineer** | Bicep, ARM, Azure-specific services |
| Kubernetes manifests and RBAC | **kubernetes-specialist** | Deployments, Services, NetworkPolicies, HPA |
| Helm chart creation | **helm-chart-builder** | Packaged Kubernetes deployments |
| Containerise an application | **docker-composer** | Dockerfiles, multi-stage builds, compose |
| Cloud networking design | **network-engineer** | VPCs, subnets, security groups, load balancers |
| Internal developer platform | **platform-engineer** | Self-service IaC, golden paths |
| Full DevOps toolchain | **devops-engineer** | CI/CD + IaC + monitoring integration |
| Windows Server / Active Directory | **windows-infra-admin** | PowerShell automation, GPO, AD management |

## Common Combinations

**"Deploy a new application to Kubernetes"**
- **docker-composer** → Dockerfiles and images → **kubernetes-specialist** → manifests → **helm-chart-builder** → Helm chart → **terraform-engineer** → cluster infrastructure.

**"Set up a new cloud environment"**
- **cloud-architect** → architecture design → **terraform-engineer** → infrastructure provisioning → **network-engineer** → networking → **kubernetes-specialist** → cluster configuration.

**"Build an internal platform"**
- **platform-engineer** → platform design → **terraform-engineer** → self-service modules → **helm-chart-builder** → application templates → **devops-engineer** → CI/CD integration.

**"Migrate to microservices on cloud"**
- **cloud-architect** → target architecture → **network-engineer** → network topology → **kubernetes-specialist** → workload manifests → **terraform-engineer** → infrastructure code.

## Getting Started

> **Always run `plan` before `apply`.** Review Terraform plans and kubectl dry-runs before making any changes to cloud resources.

1. **Test in a separate environment first** — Use a dev or staging account/namespace before applying to production.
2. **Version control all IaC** — Every infrastructure change should go through code review in git.
3. **Use remote state** — Configure Terraform remote state (S3, GCS, Azure Blob) for team collaboration.
4. **Apply least privilege** — Ensure IaC roles have minimum necessary permissions; use **iam-policy-author** (Security category) to review IAM policies.
5. **Review cost before provisioning** — Check resource costs before creating cloud resources, especially databases, load balancers, and compute instances.
