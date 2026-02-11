# Repository Organisation Analysis

## Current State Summary

128+ agents across 10 categories. Several categories lack cohesion, naming is inconsistent, and some agents are clearly miscategorized.

---

## Category-by-Category Analysis

### 01-core-development (11 agents) - PROBLEMATIC
**Stated purpose:** Essential development tasks
**Actual contents:**
- **Implementation roles:** frontend-developer, backend-developer, fullstack-developer, mobile-developer, electron-pro, websocket-engineer
- **Architecture/Design roles:** microservices-architect, graphql-architect, api-designer, ui-designer

**Problems:**
1. Mixes hands-on coding agents with architecture/design agents
2. `api-designer` is really API architecture, not implementation
3. `ui-designer` is visual design, not code development
4. `microservices-architect` and `graphql-architect` are system design, not "core development"
5. `electron-pro` and `websocket-engineer` are specialised tech, not "core"

**Naming inconsistency:** Uses 5 different suffixes: -developer, -designer, -architect, -pro, -engineer

### 02-language-specialists (26+ agents) - MOSTLY COHERENT
**Stated purpose:** Language/framework experts
**Actual contents:** All language or framework specialists - good cohesion

**Problems:**
1. **Naming chaos** - 6 different suffixes for the same role type:
   - `-pro`: python, typescript, javascript, golang, php, sql, cpp
   - `-specialist`: react, kotlin, laravel
   - `-expert`: dotnet-core, dotnet-framework-4.8, elixir, flutter, swift, powershell-5.1, powershell-7, haskell, vue
   - `-developer`: csharp, django, nextjs
   - `-architect`: java, angular
   - `-engineer`: rust, spring-boot
2. No logic to suffix choice - why is Python "pro" but Java "architect"? Why is React "specialist" but Angular "architect"?

### 03-infrastructure (14 agents) - MOSTLY COHERENT
**Stated purpose:** DevOps, cloud, Kubernetes, etc.
**Actual contents:** All infrastructure-related - good cohesion

**Problems:**
1. `kubernetes-specialist` is the ONLY `-specialist` - everything else is `-engineer`, `-architect`, `-administrator`, or `-admin`
2. `incident-responder` and `devops-incident-responder` overlap significantly
3. `database-administrator` vs `database-optimizer` (in cat 05) - split across categories
4. `security-engineer` straddles infra security and app security

### 04-quality-security (14 agents) - REASONABLE
**Stated purpose:** Testing, security auditing, code review
**Actual contents:** Mix of quality assurance and security agents

**Problems:**
1. `architect-reviewer` does system design review - belongs with architecture agents
2. `performance-engineer` and `chaos-engineer` could be infrastructure
3. `debugger` and `error-detective` - unclear differentiation
4. `powershell-security-hardening` doesn't follow naming convention (should be `powershell-security-specialist` or similar)
5. `ad-security-reviewer` is very niche (Active Directory specific)

### 05-data-ai (12 agents) - REASONABLE
**Stated purpose:** ML, data engineering, AI specialists

**Problems:**
1. `ml-engineer` and `machine-learning-engineer` - essentially duplicates
2. `postgres-pro` belongs in infrastructure (database), not data-ai
3. `database-optimizer` overlaps with `postgres-pro` and `database-administrator` (cat 03)

### 06-developer-experience (13 agents) - GOOD COHESION
**Stated purpose:** Tooling, documentation, DX optimization

**Problems:**
1. `powershell-module-architect` and `powershell-ui-architect` are language-specific - could be in cat 02
2. `slack-expert` feels out of place - it's integration development, not DX
3. `mcp-developer` is very specific to Claude ecosystem

### 07-specialized-domains (12 agents) - CATCH-ALL
**Stated purpose:** Blockchain, IoT, fintech, gaming

**Problems:**
1. This is a "miscellaneous" bucket - no unifying theme beyond "specialised"
2. `api-documenter` overlaps with `documentation-engineer` (cat 06) and `technical-writer` (cat 08)
3. `mobile-app-developer` overlaps with `mobile-developer` (cat 01)
4. `quant-analyst` and `risk-manager` are finance-specific - belong together
5. `m365-admin` is infrastructure, not a "specialised domain"
6. `seo-specialist` is marketing-adjacent

### 08-business-product (11 agents) - REASONABLE
**Stated purpose:** Product management, business analysis

**Problems:**
1. `wordpress-master` is development, not business/product
2. `technical-writer` overlaps with documentation agents elsewhere
3. Naming: `wordpress-master` is unique suffix

### 09-meta-orchestration (11 agents) - GOOD COHESION
**Stated purpose:** Multi-agent coordination

**Problems:**
1. `it-ops-orchestrator` feels more like infrastructure
2. `agent-installer` is a utility, not orchestration

### 10-research-analysis (6 agents) - GOOD COHESION
**Stated purpose:** Research and analysis specialists
**Minimal issues** - well-defined and consistent

---

## Cross-Cutting Issues

### 1. Documentation Agent Sprawl
Three agents across three categories all write documentation:
- `documentation-engineer` (06)
- `api-documenter` (07)
- `technical-writer` (08)

### 2. Database Agent Sprawl
Three database agents across two categories:
- `database-administrator` (03)
- `database-optimizer` (05)
- `postgres-pro` (05)

### 3. Mobile Developer Duplication
- `mobile-developer` (01) - cross-platform mobile
- `mobile-app-developer` (07) - also mobile apps

### 4. Incident Response Duplication
- `incident-responder` (03)
- `devops-incident-responder` (03)

### 5. ML Engineer Duplication
- `ml-engineer` (05)
- `machine-learning-engineer` (05)

---

## Proposed New Category Structure

### Option A: Minimal Reorganisation (recommended)
Keep most categories, but create 1-2 new ones and move misplaced agents.

**New category: `XX-architecture-design`**
Move from 01: `microservices-architect`, `graphql-architect`, `api-designer`
Move from 04: `architect-reviewer`
Move from 01: `ui-designer`

**Rename 01 to `01-general-development`**
Keep: `frontend-developer`, `backend-developer`, `fullstack-developer`, `mobile-developer`
Move in: `wordpress-master` (from 08)?

**Clean up 07-specialized-domains**
Move `m365-admin` → 03-infrastructure
Move `mobile-app-developer` → consolidate with `mobile-developer` or delete
Move `api-documenter` → 06-developer-experience (with other docs agents)

### Option B: Larger Reorganisation
More aggressive restructuring - potentially disruptive but cleaner.

---

## Naming Convention Proposal

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

### Specific Renames Needed (cat 02 - Language Specialists)
All should use `-specialist`:
- python-pro → python-specialist
- typescript-pro → typescript-specialist
- javascript-pro → javascript-specialist
- golang-pro → golang-specialist
- php-pro → php-specialist
- sql-pro → sql-specialist
- cpp-pro → cpp-specialist
- java-architect → java-specialist
- angular-architect → angular-specialist
- rust-engineer → rust-specialist
- spring-boot-engineer → spring-boot-specialist
- csharp-developer → csharp-specialist
- django-developer → django-specialist
- nextjs-developer → nextjs-specialist
- dotnet-core-expert → dotnet-core-specialist
- dotnet-framework-4.8-expert → dotnet-framework-specialist
- elixir-expert → elixir-specialist
- flutter-expert → flutter-specialist
- swift-expert → swift-specialist
- powershell-5.1-expert → powershell-5.1-specialist
- powershell-7-expert → powershell-7-specialist
- haskell-expert → haskell-specialist
- vue-expert → vue-specialist

### Specific Renames Needed (cat 03 - Infrastructure)
- `kubernetes-specialist` → `kubernetes-engineer` (align with rest of category)

### Specific Renames Needed (cat 04 - Quality & Security)
- `powershell-security-hardening` → `powershell-security-reviewer`

### Specific Renames Needed (cat 05 - Data & AI)
- `postgres-pro` → move to infrastructure OR rename `postgresql-specialist`

### Specific Renames Needed (cat 07)
- `embedded-systems` → `embedded-systems-engineer`

### Specific Renames Needed (cat 08)
- `wordpress-master` → `wordpress-specialist` (and consider moving)

---

## Impact Assessment

Each rename/move requires updating:
1. The agent `.md` file (filename + `name:` in frontmatter)
2. The category `README.md` (remove from old, add to new)
3. The main `README.md` (update link path and description)
4. Any cross-references in other agent files
5. Plugin JSON files if category changes

This is a significant undertaking but will dramatically improve discoverability and consistency.
