# Task Plan: Repository Organisation Restructure

## Goal
Reorganise the repository so every category provides a clear, cohesive set of capabilities. Standardise agent naming conventions. Eliminate duplicates. Update all references.

## Decisions Made
- All language/framework agents in cat 02 → use `-specialist` suffix
- Create new "Architecture & Design" category
- Merge duplicate agents (pick best, consolidate)
- Full restructure scope: new categories + renames + moves + dedup + README updates

---

## Phase 1: Create New Category - Architecture & Design

Create `categories/XX-architecture-design/` (number TBD based on ordering preference).

### Agents to move INTO this category:
| Agent | Current Location | Rationale |
|-------|-----------------|-----------|
| microservices-architect | 01-core-development | System design, not implementation |
| graphql-architect | 01-core-development | API architecture, not implementation |
| api-designer | 01-core-development | API design/specs, not implementation |
| ui-designer | 01-core-development | Visual/interaction design, not coding |
| architect-reviewer | 04-quality-security | Architecture review fits with architects |
| cloud-architect | 03-infrastructure | System design role |
| wordpress-master | 08-business-product | Line 8 says "WordPress architect" - rename to `wordpress-architect` |
| embedded-systems-architect | NEW (split from embedded-systems) | Firmware architecture, system design for embedded platforms |

### Tasks:
- [ ] 1.1 Create `categories/11-architecture-design/` directory
- [ ] 1.2 Move agent files to new category
- [ ] 1.3 Create category README.md
- [ ] 1.4 Create `.claude-plugin/plugin.json`
- [ ] 1.5 Update main README.md with new category section
- [ ] 1.6 Remove moved agents from old category READMEs
- [ ] 1.7 Update frontmatter in moved agent files if needed

---

## Phase 2: Rename 01-core-development → 01-general-development

After removing architecture/design agents, cat 01 becomes focused on hands-on development.

### Remaining agents after moves:
- frontend-developer
- backend-developer
- fullstack-developer
- mobile-developer
- websocket-engineer (keep - it's an implementation role)

### Agents moved OUT:
- electron-pro → `electron-specialist` in cat 02 (it's a framework specialist like Laravel, React, etc.)

### Tasks:
- [ ] 2.1 Move `electron-pro` → cat 02 as `electron-specialist` (file + frontmatter)
- [ ] 2.2 Update category README title/description to "General Development"
- [ ] 2.3 Update main README.md references

---

## Phase 3: Standardise Category 02 Naming (Language Specialists)

All agents get `-specialist` suffix.

### Renames needed:
| Current Name | New Name |
|-------------|----------|
| python-pro | python-specialist |
| typescript-pro | typescript-specialist |
| javascript-pro | javascript-specialist |
| golang-pro | golang-specialist |
| php-pro | php-specialist |
| sql-pro | sql-specialist |
| cpp-pro | cpp-specialist |
| java-architect | java-specialist |
| angular-architect | angular-specialist |
| rust-engineer | rust-specialist |
| spring-boot-engineer | spring-boot-specialist |
| csharp-developer | csharp-specialist |
| django-developer | django-specialist |
| nextjs-developer | nextjs-specialist |
| dotnet-core-expert | dotnet-core-specialist |
| dotnet-framework-4.8-expert | dotnet-framework-specialist |
| elixir-expert | elixir-specialist |
| flutter-expert | flutter-specialist |
| swift-expert | swift-specialist |
| powershell-5.1-expert | powershell-5.1-specialist |
| powershell-7-expert | powershell-7-specialist |
| haskell-expert | haskell-specialist |
| vue-expert | vue-specialist |
| rails-expert | rails-specialist |
| laravel-specialist | (no change) |
| react-specialist | (no change) |
| kotlin-specialist | (no change) |

### Tasks:
- [ ] 3.1 Rename all 24 agent files (filename + `name:` in frontmatter)
- [ ] 3.2 Update category 02 README.md with new names/links
- [ ] 3.3 Update main README.md with new names/links

---

## Phase 4: Standardise Category 03 Naming (Infrastructure)

### Renames:
| Current | New | Rationale |
|---------|-----|-----------|
| kubernetes-specialist | kubernetes-engineer | Align with rest of category |
| database-administrator | database-admin | Shorten to match windows-infra-admin |

### Note: `cloud-architect` moved to architecture category in Phase 1

### Tasks:
- [ ] 4.1 Rename kubernetes-specialist → kubernetes-engineer
- [ ] 4.2 Rename database-administrator → database-admin
- [ ] 4.3 Update category 03 README.md
- [ ] 4.4 Update main README.md

---

## Phase 5: Fix Category 04 Naming (Quality & Security)

### Renames:
| Current | New | Rationale |
|---------|-----|-----------|
| powershell-security-hardening | powershell-security-reviewer | Follow naming convention |

### Note: `architect-reviewer` moved to architecture category in Phase 1

### Tasks:
- [ ] 5.1 Rename powershell-security-hardening → powershell-security-reviewer
- [ ] 5.2 Update category 04 README.md (remove architect-reviewer, update rename)
- [ ] 5.3 Update main README.md

---

## Phase 5b: Split embedded-systems Agent

The current `embedded-systems` agent (cat 07) covers too much ground. Split into:

### New agents for cat 02 (Language Specialists):
| New Agent | Focus |
|-----------|-------|
| vhdl-specialist | VHDL hardware description language for FPGA/ASIC design |
| verilog-specialist | Verilog HDL for digital circuit design and simulation |
| systemverilog-specialist | SystemVerilog for verification and advanced hardware design |

### New agent for cat 11 (Architecture & Design):
| New Agent | Focus |
|-----------|-------|
| embedded-systems-architect | Firmware architecture, RTOS design, hardware abstraction, power management strategy |

### Tasks:
- [ ] 5b.1 Create `vhdl-specialist.md` in cat 02 (extract HDL content from embedded-systems)
- [ ] 5b.2 Create `verilog-specialist.md` in cat 02
- [ ] 5b.3 Create `systemverilog-specialist.md` in cat 02
- [ ] 5b.4 Create `embedded-systems-architect.md` in cat 11 (architecture/design content)
- [ ] 5b.5 Delete original `embedded-systems.md` from cat 07
- [ ] 5b.6 Update cat 02, cat 07, cat 11 READMEs and main README

---

## Phase 6: Merge Duplicate Agents

### 6a: ml-engineer + machine-learning-engineer → ml-engineer (cat 05)
- Merge best content from both into single `ml-engineer.md`
- Delete `machine-learning-engineer.md`

### 6b: mobile-developer (cat 01) + mobile-app-developer (cat 07) → mobile-developer (cat 01)
- Merge best content into `mobile-developer.md`
- Delete `mobile-app-developer.md` from cat 07

### 6c: incident-responder + devops-incident-responder → incident-responder (cat 03)
- Merge DevOps-specific content into `incident-responder.md`
- Delete `devops-incident-responder.md`

### Tasks:
- [ ] 6.1 Merge ml-engineer + machine-learning-engineer → ml-engineer
- [ ] 6.2 Merge mobile-developer + mobile-app-developer → mobile-developer
- [ ] 6.3 Merge incident-responder + devops-incident-responder → incident-responder
- [ ] 6.4 Update all affected READMEs (cat 01, 03, 05, 07, main)

---

## Phase 7: Move Misplaced Agents

| Agent | From | To | Rationale |
|-------|------|----|-----------|
| m365-admin | 07-specialized-domains | 03-infrastructure | It's infra admin, not a "specialised domain" |
| postgres-pro | 05-data-ai | 03-infrastructure | Database belongs with infra; rename to `postgresql-specialist` |
| api-documenter | 07-specialized-domains | 06-developer-experience | Docs tooling belongs with DX; consolidate scope with documentation-engineer |
| slack-expert | 06-developer-experience | 07-specialized-domains | Integration platform, not DX; rename to `slack-specialist` |

Note: `wordpress-master` → `wordpress-architect` already handled in Phase 1 (moved to cat 11).
Note: `electron-pro` → `electron-specialist` already handled in Phase 2 (moved to cat 02).

### Tasks:
- [ ] 7.1 Move + rename postgres-pro → postgresql-specialist (to cat 03)
- [ ] 7.2 Move m365-admin → cat 03
- [ ] 7.3 Move api-documenter → cat 06
- [ ] 7.4 Move + rename slack-expert → slack-specialist (to cat 07)
- [ ] 7.5 Update all affected READMEs

---

## Phase 8: Fix Remaining Naming Oddities

| Current | New | Category | Rationale |
|---------|-----|----------|-----------|
| error-detective | error-analyst | 04 | Consistent with analyst pattern |
| postgres-pro | (handled in Phase 7) | | |

### Tasks:
- [ ] 8.1 Rename error-detective → error-analyst (cat 04)
- [ ] 8.2 Update cat 04 README and main README

---

## Phase 9: Update All Plugin JSON Files

Each category has `.claude-plugin/plugin.json` that lists agents. These must be updated for any category that had agents added, removed, or renamed.

### Affected categories:
- 01 (agents removed + added + renamed)
- 03 (agents removed + added + renamed)
- 04 (agents removed + renamed)
- 05 (agent merged)
- 06 (agent added)
- 07 (agents removed + added + renamed)
- 08 (agent removed)
- 11 (new category)

### Tasks:
- [ ] 9.1 Update all affected plugin.json files

---

## Phase 10: Final Validation

- [ ] 10.1 Verify all agent files have correct `name:` in frontmatter matching filename
- [ ] 10.2 Verify all README links resolve correctly
- [ ] 10.3 Verify main README lists all agents in correct categories
- [ ] 10.4 Verify no orphaned files
- [ ] 10.5 Run a grep for old agent names to catch stale references

---

## Summary of Changes

| Metric | Count |
|--------|-------|
| New categories created | 1 (11-architecture-design) |
| Agents renamed | ~36 |
| Agents moved between categories | ~13 |
| Agents split | 1 (embedded-systems → 3 language specialists + 1 architect) |
| Duplicate agents merged | 3 pairs → 3 agents removed |
| Net new agent files | +3 (split) - 3 (merges) = 0 |
| READMEs updated | 12 (10 category + 1 main + 1 new) |
| Plugin JSONs updated | 9 |

## Execution Order
Phases 1-5 can be done somewhat independently. Phase 6-7 depend on category structure being settled. Phase 8-9 are cleanup. Phase 10 is validation.

Recommended: Execute in numbered order. Each phase should be a separate commit or PR for reviewability.
