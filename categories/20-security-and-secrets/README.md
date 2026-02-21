# Security & Secrets Subagents

Security & Secrets subagents manage credentials, access policies, security configurations, and vulnerability testing. These agents touch cloud resources, credentials, and security boundaries — mistakes can expose sensitive data, lock out systems, or create security gaps. Always work in non-production environments first, and ensure proper authorisation before running penetration tests.

**Risk Tier: 🔴 Tier 4 — High** — Manages credentials, access policies, and security configurations affecting shared systems. Penetration testing requires explicit written authorisation. Never rotate production credentials without a tested rollback plan.

## When to Use Security & Secrets Agents

Use these subagents when you need to:
- **Implement security controls** — Add security tooling, scanning, and hardening
- **Test for vulnerabilities** — Assess systems for exploitable weaknesses (authorised only)
- **Manage credentials** — Rotate API keys, tokens, and certificates safely
- **Author IAM policies** — Write least-privilege access policies for cloud resources
- **Configure secrets management** — Set up Vault, AWS Secrets Manager, or Azure Key Vault
- **Harden environments** — Secure Windows, PowerShell, and AD configurations

## Available Subagents

### [**ad-security-reviewer**](ad-security-reviewer.md) — Review Active Directory security
Reviews Active Directory configurations for security misconfigurations — weak password policies, over-privileged accounts, dangerous ACLs, and common AD attack paths (Kerberoasting, DCSync, etc.).

**Use when:** Auditing Active Directory security posture, preparing for a red team exercise, or hardening on-premises or hybrid identity infrastructure.

### [**certificate-manager**](certificate-manager.md) — Manage TLS certificates and trust chains
Manages TLS certificate lifecycle — provisioning, renewal automation (Let's Encrypt, ACME), trust chain validation, and certificate pinning. Prevents certificate expiry incidents.

**Use when:** Setting up TLS for services, automating certificate renewal, troubleshooting certificate validation errors, or implementing certificate pinning.

### [**cors-policy-manager**](cors-policy-manager.md) — Configure CORS, CSP, and security headers
Configures HTTP security headers — CORS policies, Content Security Policy (CSP), HSTS, X-Frame-Options, and other security-relevant headers. Balances security restrictions with legitimate cross-origin requirements.

**Use when:** Hardening web application security headers, troubleshooting CORS errors, or implementing a strict Content Security Policy.

### [**iam-policy-author**](iam-policy-author.md) — Write least-privilege IAM and RBAC policies
Creates IAM policies (AWS IAM, Azure RBAC, GCP IAM) and Kubernetes RBAC configurations following least-privilege principles. Analyses existing policies for over-permissive access.

**Use when:** Creating or reviewing cloud IAM policies, setting up service account permissions, or auditing existing roles for excessive permissions.

### [**penetration-tester**](penetration-tester.md) — Test systems for exploitable vulnerabilities
Conducts structured penetration tests against authorised systems — web application testing (OWASP Top 10), network scanning, API security testing, and privilege escalation assessment.

**Use when:** Running an authorised penetration test against your own systems, validating security fixes, or assessing a new application before launch. **Requires explicit written authorisation.**

### [**powershell-security-hardening**](powershell-security-hardening.md) — Harden Windows and PowerShell environments
Implements PowerShell security controls — Constrained Language Mode, script block logging, AMSI integration, execution policy hardening, and JEA (Just Enough Administration) configurations.

**Use when:** Hardening Windows environments against PowerShell-based attacks, implementing audit logging, or meeting CIS benchmarks for Windows.

### [**secret-rotator**](secret-rotator.md) — Rotate credentials safely
Safely rotates API keys, database passwords, tokens, and other credentials — updating all dependent systems, verifying the new credentials work, and revoking the old ones. Prevents credential rotation outages.

**Use when:** Rotating credentials as part of regular security hygiene, after a suspected credential exposure, or implementing automated rotation.

### [**security-engineer**](security-engineer.md) — Implement security controls and tooling
Implements security controls across the stack — dependency scanning, SAST/DAST integration, secrets detection, security testing in CI/CD, and security monitoring configuration.

**Use when:** Adding security tooling to a project, implementing security scanning in a CI/CD pipeline, or building a shift-left security practice.

### [**vault-configurator**](vault-configurator.md) — Configure secrets managers
Configures secrets management platforms — HashiCorp Vault policies and auth methods, AWS Secrets Manager rotation, Azure Key Vault access policies, and GCP Secret Manager IAM.

**Use when:** Setting up a secrets management solution, configuring dynamic secrets, or migrating from environment variables to a dedicated secrets manager.

## Quick Selection Guide

| Task | Subagent | Notes |
|------|----------|-------|
| Add security scanning to CI/CD | **security-engineer** | SAST, DAST, secrets detection, dependency scanning |
| Authorised penetration test | **penetration-tester** | **Requires written authorisation** |
| Review Active Directory security | **ad-security-reviewer** | AD misconfigurations, attack paths |
| Manage TLS certificates | **certificate-manager** | Provisioning, renewal, trust chain |
| Configure CORS and security headers | **cors-policy-manager** | CSP, HSTS, CORS, X-Frame-Options |
| Write IAM / RBAC policies | **iam-policy-author** | Least-privilege AWS, Azure, GCP, Kubernetes |
| Rotate credentials safely | **secret-rotator** | Zero-downtime rotation with verification |
| Set up Vault or AWS SM | **vault-configurator** | Dynamic secrets, policies, auth methods |
| Harden Windows and PowerShell | **powershell-security-hardening** | CLM, AMSI, JEA, audit logging |

## Common Combinations

**"Harden a new cloud deployment"**
- **iam-policy-author** → least-privilege roles → **vault-configurator** → secrets management → **security-engineer** → CI/CD scanning → **cors-policy-manager** → web security headers.

**"Security review before launch"**
- **security-auditor** (Analysis category) → code review → **dependency-auditor** (Analysis category) → supply chain → **penetration-tester** → authorised pentest → **secret-rotator** → rotate any exposed secrets.

**"Set up zero-trust secrets management"**
- **vault-configurator** → Vault policies and auth → **iam-policy-author** → cloud IAM for Vault → **secret-rotator** → automated rotation schedules → **security-engineer** → audit logging.

**"Harden Windows AD environment"**
- **ad-security-reviewer** → findings → **powershell-security-hardening** → PowerShell controls → **iam-policy-author** → least-privilege AD delegation → **certificate-manager** → internal PKI.

## Getting Started

> **Security agents work on real systems — proceed with care.**

1. **Authorise before testing** — Never run penetration tests against systems without explicit written authorisation from the system owner.
2. **Rotate credentials safely** — Always use **secret-rotator** for credential rotation; never just delete old credentials before updating all dependents.
3. **Test IAM changes in staging** — Apply **iam-policy-author** changes in a non-production account first to verify access is correct.
4. **Back up before hardening** — Ensure you can restore system state before applying hardening changes that could lock out access.
5. **Log all security changes** — Security configuration changes should always be in version control and review-tracked.
