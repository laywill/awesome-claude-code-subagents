# Repository Organisation Analysis

## Current State Summary

129 agent files across 10 categories (10 + 26 + 14 + 14 + 12 + 13 + 13 + 11 + 10 + 6). Several categories lack cohesion, naming is inconsistent, and some agents are miscategorized. Three duplicate pairs exist.

---

## Category-by-Category Analysis

### 01-core-development (10 agents) — PROBLEMATIC
**Stated purpose:** Essential development tasks
**Actual contents:**
- **Implementation roles:** frontend-developer, backend-developer, fullstack-developer, mobile-developer, electron-pro, websocket-engineer
- **Architecture/Design roles:** microservices-architect, graphql-architect, api-designer, ui-designer

**Problems:**
1. Mixes hands-on coding agents with architecture/design agents
2. `api-designer` is API architecture, not implementation
3. `ui-designer` is visual design, not code development
4. `graphql-architect` is pure API design — no implementation
5. `electron-pro` is a framework specialist — belongs in cat 02
6. `wordpress-master` appears in cat 01 README but physically lives in cat 08 (pre-existing discrepancy)

**Naming inconsistency:** 5 different suffixes: -developer, -designer, -architect, -pro, -engineer

**Decision:** `microservices-architect` stays here — tightly coupled to cat 01 implementation agents (frontend, backend, fullstack). `graphql-architect` moves to architecture category (pure design).

### 02-language-specialists (26 agents) — MOSTLY COHERENT
**Stated purpose:** Language/framework experts
**Actual contents:** All language or framework specialists — good cohesion

**Problems:**
1. **Naming chaos** — 6 different suffixes for the same role type:
   - `-pro`: python, typescript, javascript, golang, php, sql, cpp (7)
   - `-specialist`: react, kotlin, laravel (3)
   - `-expert`: dotnet-core, dotnet-framework-4.8, elixir, flutter, swift, powershell-5.1, powershell-7, haskell, vue, rails (10)
   - `-developer`: csharp, django, nextjs (3)
   - `-architect`: java, angular (2)
   - `-engineer`: rust, spring-boot (2)
2. No logic to suffix choice — Python is "pro" but Java is "architect"; React is "specialist" but Angular is "architect"

### 03-infrastructure (14 agents) — MOSTLY COHERENT
**Stated purpose:** DevOps, cloud, Kubernetes, etc.
**Actual contents:** All infrastructure-related — good cohesion

**Problems:**
1. `kubernetes-specialist` is the ONLY `-specialist` — everything else is `-engineer`, `-architect`, `-administrator`, or `-admin`
2. `incident-responder` and `devops-incident-responder` overlap significantly
3. `database-administrator` vs `database-optimizer` (in cat 05) and `postgres-pro` (in cat 05) — database agents split across categories
4. `security-engineer` straddles infra security and app security

**Decision:** `cloud-architect` stays here — infra teams expect it; the architecture category is for cross-cutting design agents, not cloud-specific infra design.

### 04-quality-security (14 agents) — REASONABLE
**Stated purpose:** Testing, security auditing, code review
**Actual contents:** Mix of quality assurance and security agents

**Problems:**
1. `architect-reviewer` does system design review — belongs with architecture agents
2. `performance-engineer` and `chaos-engineer` could be infrastructure (but testing-focused, so keep)
3. `debugger` and `error-detective` — **distinct roles**: debugger handles single-service/local debugging; error-detective analyses distributed cascade failures and multi-service error propagation
4. `powershell-security-hardening` doesn't follow naming convention (should be `-reviewer`)
5. `ad-security-reviewer` is very niche (Active Directory specific)

### 05-data-ai (12 agents) — REASONABLE
**Stated purpose:** ML, data engineering, AI specialists

**Problems:**
1. `ml-engineer` and `machine-learning-engineer` — essentially duplicates
2. `postgres-pro` belongs in infrastructure (database), not data-ai
3. `database-optimizer` overlaps with `database-administrator` (cat 03) and should move there

### 06-developer-experience (13 agents) — GOOD COHESION
**Stated purpose:** Tooling, documentation, DX optimization

**Problems:**
1. `powershell-module-architect` and `powershell-ui-architect` are framework development agents — write code, belong in cat 02 as `-specialist`
2. `slack-expert` is integration development, not DX — belongs in cat 07
3. `mcp-developer` is very specific to Claude ecosystem (keep — it's tooling/DX)

**PowerShell scatter:** Currently 5 PowerShell agents across 3 categories (cat 02: 2, cat 04: 1, cat 06: 2). After reorganisation: cat 02: 4, cat 04: 1.

### 07-specialized-domains (13 agents) — CATCH-ALL
**Stated purpose:** Blockchain, IoT, fintech, gaming
**Includes:** unreal-specialist (untracked, on branch)

**Problems:**
1. This is a "miscellaneous" bucket — no unifying theme beyond "specialised"
2. `api-documenter` overlaps with `documentation-engineer` (cat 06) and `technical-writer` (cat 08) — move to cat 06
3. `mobile-app-developer` overlaps with `mobile-developer` (cat 01) — merge
4. `quant-analyst` and `risk-manager` are finance-specific — keep together, they belong here
5. `m365-admin` is infrastructure, not a "specialised domain" — move to cat 03
6. `seo-specialist` is business/marketing — move to cat 08

### 08-business-product (11 agents) — REASONABLE
**Stated purpose:** Product management, business analysis

**Problems:**
1. `wordpress-master` is development, not business/product — move to cat 02 as `wordpress-specialist`
2. `technical-writer` overlaps with documentation agents elsewhere (keep — different audience: business stakeholders vs developers)

### 09-meta-orchestration (10 agents) — GOOD COHESION
**Stated purpose:** Multi-agent coordination

**Problems:**
1. `it-ops-orchestrator` could be infrastructure, but its core purpose is orchestrating other agents — keep here
2. `agent-installer` is a utility, not orchestration — keep here (no better home; it installs agents)

**Cross-reference risk:** `it-ops-orchestrator` is referenced by many infrastructure agents. Renames in cat 03 will break these cross-references.

### 10-research-analysis (6 agents) — GOOD COHESION
**Stated purpose:** Research and analysis specialists
**Minimal issues** — well-defined and consistent

---

## Cross-Cutting Issues

### 1. Documentation Agent Boundaries
Three agents across three categories write documentation — but they serve different audiences:
- `documentation-engineer` (06) — developer-facing technical docs, API refs, READMEs
- `api-documenter` (07 → 06) — OpenAPI/Swagger specs, endpoint documentation
- `technical-writer` (08) — business/stakeholder-facing docs, user guides, release notes

**Decision:** Move `api-documenter` to cat 06 (developer docs tooling). Keep all three — they're distinct.

### 2. Database Agent Sprawl
Three database agents across two categories:
- `database-administrator` (03) → rename `database-admin`
- `database-optimizer` (05) → move to cat 03 as `database-performance-engineer`
- `postgres-pro` (05) → move to cat 03 as `postgresql-admin`

After reorganisation: all three in cat 03 (infrastructure), distinct roles.

### 3. Mobile Developer Duplication
- `mobile-developer` (01) — cross-platform mobile
- `mobile-app-developer` (07) — also mobile apps
**Decision:** Merge into `mobile-developer` (cat 01)

### 4. Incident Response Duplication
- `incident-responder` (03)
- `devops-incident-responder` (03)
**Decision:** Merge into `incident-responder` (cat 03)

### 5. ML Engineer Duplication
- `ml-engineer` (05)
- `machine-learning-engineer` (05)
**Decision:** Merge into `ml-engineer` (cat 05)

### 6. Cross-Reference Breakage Risk
Many agents reference other agents by name in collaboration/integration sections. Every rename risks breaking these. Key high-reference agents:
- `it-ops-orchestrator` (referenced by infra agents)
- `azure-infra-engineer`, `platform-engineer`, `terraform-engineer` (infrastructure cross-refs)
- `fullstack-developer` (referenced by many cat 01 agents)

**Mitigation:** Dedicated cross-reference update phase using grep.

### 7. Install Script URL Breakage
`install-agents.sh` and `agent-installer.md` contain GitHub raw URLs with category paths. Category renames (01-core-development → 01-core-development) and agent renames will break these URLs.

### 8. Pre-Existing Discrepancies
- `wordpress-master` listed in cat 01 README but physically in cat 08
- `m365-admin` missing from cat 07 README (but physically present)
- Cat 06 Quick Selection Guide missing several agents

---

## Proposed New Category Structure

### New category: `00-api-design` (slim — 4 agents)
Move from 01: `api-designer`, `ui-designer`, `graphql-architect`
Move from 04: `architect-reviewer`

**NOT moved** (decision rationale):
- `microservices-architect` — stays in 01 (tightly coupled to implementation agents)
- `cloud-architect` — stays in 03 (infra teams expect it; cloud-specific, not cross-cutting design)

### Rename 01 → `01-core-development` (6 agents remaining)
Keep: frontend-developer, backend-developer, fullstack-developer, mobile-developer, microservices-architect, websocket-engineer
Move out: electron-pro → cat 02, api-designer/ui-designer/graphql-architect → cat 00

### Cat 02 additions (4 new agents)
- `electron-specialist` (from cat 01, was electron-pro)
- `wordpress-specialist` (from cat 08, was wordpress-master)
- `powershell-module-specialist` (from cat 06, was powershell-module-architect)
- `powershell-ui-specialist` (from cat 06, was powershell-ui-architect)

### Cat 03 additions (3 agents moved in)
- `m365-admin` (from cat 07, no rename)
- `postgresql-admin` (from cat 05, was postgres-pro)
- `database-performance-engineer` (from cat 05, was database-optimizer)

### Cat 07 → cat 08 move
- `seo-specialist` → cat 08 (business/marketing, not specialised domain)

---

## Naming Convention

### By Role Type
| Role Type | Standard Suffix | Examples |
|-----------|----------------|----------|
| Language/framework coding | `-specialist` | python-specialist, react-specialist |
| System/solution design | `-architect` | microservices-architect, cloud-architect |
| Implementation/operations | `-engineer` | devops-engineer, sre-engineer |
| Review/audit | `-reviewer` or `-auditor` | code-reviewer, security-auditor |
| Testing | `-tester` | penetration-tester, accessibility-tester |
| Management/coordination | `-manager` | project-manager, dependency-manager |
| Research/analysis | `-analyst` | data-analyst, trend-analyst |
| Administration | `-admin` | database-admin, windows-infra-admin |

### Key Renames (non-cat-02)
| Current | New | Category | Rationale |
|---------|-----|----------|-----------|
| kubernetes-specialist | kubernetes-engineer | 03 | Align with rest of infra category |
| database-administrator | database-admin | 03 | Match windows-infra-admin pattern |
| postgres-pro | postgresql-admin | 03 | Admin role, consistent naming |
| database-optimizer | database-performance-engineer | 03 | Engineering role, descriptive |
| powershell-security-hardening | powershell-security-reviewer | 04 | Follow -reviewer convention |
| error-detective | error-diagnostics-engineer | 04 | Distinct from debugger; engineering role |
| embedded-systems | embedded-systems-engineer | 07 | No split (zero HDL content); -engineer suffix |
| wordpress-master | wordpress-specialist | 02 | Framework specialist, not architect |
| slack-expert | slack-specialist | 07 | Consistent with cat 07 naming |

---

## Installability Assessment

| Component | Breakage Risk | Notes |
|-----------|---------------|-------|
| install-agents.sh | HIGH | Contains hardcoded GitHub raw URLs with category paths |
| agent-installer.md | HIGH | Contains URL templates referencing category names |
| Main README examples | MEDIUM | Install examples reference agent names like "php-pro" |
| plugin.json files | LOW | Local to each category, straightforward update |
| Cross-references in agents | MEDIUM | ~30 agents reference other agents by name |

---

## Future Category Candidates

These could warrant their own categories if the agent count grows:
- **Fintech** — currently quant-analyst, risk-manager, fintech-engineer, payment-integration-specialist (4 agents in cat 07)
- **Gaming** — currently game-developer, unreal-specialist (2 agents in cat 07)
- **Compliance/Governance** — currently compliance-auditor (cat 04), legal-advisor (cat 08)

Not actionable now — too few agents per potential category.

---

## Impact Assessment

Each rename/move requires updating:
1. The agent `.md` file (filename + `name:` in frontmatter)
2. The source category `README.md` (remove agent)
3. The target category `README.md` (add agent)
4. The main `README.md` (update link path and description)
5. Cross-references in other agent `.md` files
6. Plugin JSON files for affected categories
7. Install script URLs (if category changed)

Estimated: ~30 renames, ~12 moves, 3 merges, 12 READMEs, 10 plugin.json files, 2 install scripts.
