# Task Plan: Repository Organisation Restructure

## Goal
Reorganise the repository so every category provides a clear, cohesive set of capabilities. Standardise agent naming conventions. Eliminate duplicates. Update all references including cross-references and install scripts.

## Decisions Locked In
1. **graphql-architect** → move to `00-architecture-design` (pure design agent)
2. **microservices-architect** → stays in `01-general-development` (tightly coupled to implementation agents)
3. **cloud-architect** → stays in `03-infrastructure` (infra teams expect it)
4. **wordpress-master** → `wordpress-specialist` in cat 02 (framework specialist, NOT architect)
5. **powershell-module-architect** → `powershell-module-specialist` in cat 02 (writes code, framework dev agent)
6. **powershell-ui-architect** → `powershell-ui-specialist` in cat 02 (writes code, framework dev agent)
7. **embedded-systems** → rename to `embedded-systems-engineer`, keep in cat 07 (no split — zero HDL content)
8. **error-detective** → `error-diagnostics-engineer` (distinct from debugger — keep both)
9. **postgres-pro** → `postgresql-admin` in cat 03 (naming consistent with cat 03 convention)
10. **database-optimizer** → `database-performance-engineer` in cat 03 (was missing from plan)
11. Cross-references and install scripts get dedicated execution phases

---

## Phase 1: Create `00-architecture-design`

### Agents (4):
| Agent | Source | Action |
|-------|--------|--------|
| api-designer | 01-core-development | Move |
| ui-designer | 01-core-development | Move |
| graphql-architect | 01-core-development | Move |
| architect-reviewer | 04-quality-security | Move |

### Tasks:
- [ ] 1.1 Create `categories/00-architecture-design/` directory
- [ ] 1.2 Move 4 agent files to new category
- [ ] 1.3 Create category `README.md`
- [ ] 1.4 Create `.claude-plugin/plugin.json`
- [ ] 1.5 Update cat 01 README (remove 3 agents)
- [ ] 1.6 Update cat 04 README (remove architect-reviewer)
- [ ] 1.7 Update main README.md with new category section
- [ ] 1.8 Update frontmatter `name:` in moved agent files if needed

---

## Phase 2: Reorganise `01-core-development` → `01-general-development`

### After Phase 1 removals, cat 01 has 7 agents. Move out 1 more:
| Agent | Action | Destination |
|-------|--------|-------------|
| electron-pro | Move + rename → `electron-specialist` | 02-language-specialists |

### Also fix pre-existing discrepancy:
| Agent | Action | Notes |
|-------|--------|-------|
| wordpress-master | Move + rename → `wordpress-specialist` | Physically in cat 08, listed in cat 01 README. Move file from cat 08 to cat 02. |

### Remaining agents (6):
frontend-developer, backend-developer, fullstack-developer, mobile-developer, microservices-architect, websocket-engineer

### Tasks:
- [ ] 2.1 Move `electron-pro` → cat 02 as `electron-specialist` (file + frontmatter)
- [ ] 2.2 Move `wordpress-master` from cat 08 → cat 02 as `wordpress-specialist` (file + frontmatter)
- [ ] 2.3 Rename category directory `01-core-development` → `01-general-development`
- [ ] 2.4 Update cat 01 README title/description
- [ ] 2.5 Update cat 08 README (remove wordpress-master)
- [ ] 2.6 Update main README.md references

---

## Phase 3: Standardise cat 02 naming + additions

### All 23 renames (existing agents → `-specialist`):
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

**Already `-specialist` (no change):** rails-expert → rails-specialist (was missed — needs rename), laravel-specialist, react-specialist, kotlin-specialist

### Additions from other phases:
| Agent | Source | New Name |
|-------|--------|----------|
| electron-pro | cat 01 (Phase 2) | electron-specialist |
| wordpress-master | cat 08 (Phase 2) | wordpress-specialist |
| powershell-module-architect | cat 06 | powershell-module-specialist |
| powershell-ui-architect | cat 06 | powershell-ui-specialist |

### Tasks:
- [ ] 3.1 Rename all 24 agent files (filename + `name:` in frontmatter) — 23 existing + rails-expert
- [ ] 3.2 Move powershell-module-architect from cat 06 → cat 02 as `powershell-module-specialist`
- [ ] 3.3 Move powershell-ui-architect from cat 06 → cat 02 as `powershell-ui-specialist`
- [ ] 3.4 Update cat 02 README.md with all new names/links
- [ ] 3.5 Update cat 06 README.md (remove 2 powershell agents)
- [ ] 3.6 Update main README.md with new names/links

---

## Phase 4: Standardise cat 03 + add database agents

### Renames:
| Current | New | Rationale |
|---------|-----|-----------|
| kubernetes-specialist | kubernetes-engineer | Align with rest of category |
| database-administrator | database-admin | Match windows-infra-admin pattern |

### Moves IN:
| Agent | Source | New Name |
|-------|--------|----------|
| m365-admin | 07-specialized-domains | m365-admin (no rename) |
| postgres-pro | 05-data-ai | postgresql-admin |
| database-optimizer | 05-data-ai | database-performance-engineer |

### Tasks:
- [ ] 4.1 Rename kubernetes-specialist → kubernetes-engineer
- [ ] 4.2 Rename database-administrator → database-admin
- [ ] 4.3 Move m365-admin from cat 07 → cat 03
- [ ] 4.4 Move postgres-pro → cat 03 as `postgresql-admin`
- [ ] 4.5 Move database-optimizer → cat 03 as `database-performance-engineer`
- [ ] 4.6 Update cat 03 README.md
- [ ] 4.7 Update cat 05 README.md (remove 2 agents)
- [ ] 4.8 Update cat 07 README.md (remove m365-admin)
- [ ] 4.9 Update main README.md

---

## Phase 5: Fix cat 04 naming

### Renames:
| Current | New | Rationale |
|---------|-----|-----------|
| powershell-security-hardening | powershell-security-reviewer | Follow naming convention |

### Already handled in Phase 1:
- `architect-reviewer` moved to cat 00

### Tasks:
- [ ] 5.1 Rename powershell-security-hardening → powershell-security-reviewer
- [ ] 5.2 Update cat 04 README.md (rename + confirm architect-reviewer removed)
- [ ] 5.3 Update main README.md

---

## Phase 6: Merge duplicate agents

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

## Phase 7: Move remaining misplaced agents

| Agent | From | To | Rename? |
|-------|------|----|---------|
| api-documenter | 07-specialized-domains | 06-developer-experience | No |
| slack-expert | 06-developer-experience | 07-specialized-domains | → slack-specialist |
| seo-specialist | 07-specialized-domains | 08-business-product | No |

### Tasks:
- [ ] 7.1 Move api-documenter → cat 06
- [ ] 7.2 Move + rename slack-expert → slack-specialist (to cat 07)
- [ ] 7.3 Move seo-specialist → cat 08
- [ ] 7.4 Update all affected READMEs (cat 06, 07, 08, main)

---

## Phase 8: Remaining renames

| Current | New | Category |
|---------|-----|----------|
| error-detective | error-diagnostics-engineer | 04 |
| embedded-systems | embedded-systems-engineer | 07 |

### Also:
- Add `unreal-specialist` to cat 07 README and plugin.json (already exists on branch as untracked file)

### Tasks:
- [ ] 8.1 Rename error-detective → error-diagnostics-engineer
- [ ] 8.2 Rename embedded-systems → embedded-systems-engineer
- [ ] 8.3 Add unreal-specialist to cat 07 README and plugin.json
- [ ] 8.4 Update cat 04, cat 07 READMEs and main README

---

## Phase 9: Cross-reference updates

Dedicated phase — grep for every old agent name across ALL `.md` files and update references.

### High-priority cross-references (agents referenced by many others):
- it-ops-orchestrator (referenced by infra agents)
- azure-infra-engineer, platform-engineer, terraform-engineer
- fullstack-developer (referenced by cat 01 agents)
- All renamed cat 02 agents (referenced in collaboration sections)

### Tasks:
- [ ] 9.1 Grep for ALL old agent names across all `.md` files
- [ ] 9.2 Update references in agent collaboration/integration sections
- [ ] 9.3 Verify zero stale references remain

---

## Phase 10: Install script & README example updates

### Files to update:
- `install-agents.sh` — GitHub raw URLs with category paths and agent filenames
- `agent-installer.md` (cat 09) — URL patterns and templates
- Main `README.md` — install examples (e.g., "php-pro" → "php-specialist")

### Tasks:
- [ ] 10.1 Update `install-agents.sh` URLs for renamed categories and agents
- [ ] 10.2 Update `agent-installer.md` URL patterns
- [ ] 10.3 Update main README install examples

---

## Phase 11: Update all plugin.json files

### Affected categories:
| Category | Changes |
|----------|---------|
| 00 (NEW) | Create new plugin.json |
| 01 | Agents removed + category renamed |
| 02 | 24 renames + 4 additions |
| 03 | 2 renames + 3 additions |
| 04 | 1 rename + 1 removal |
| 05 | 2 removals + 1 merge |
| 06 | 2 removals + 1 addition |
| 07 | 3 removals + 1 addition + 1 rename + unreal-specialist |
| 08 | 1 removal + 1 addition |

### Fix pre-existing discrepancies:
- wordpress-master dual listing (will be resolved by moves)
- m365-admin missing from cat 07 README (will be moot after move)
- Cat 06 Quick Selection Guide missing agents (fix during update)

### Tasks:
- [ ] 11.1 Update all affected plugin.json files (categories 00-08)
- [ ] 11.2 Fix any remaining pre-existing discrepancies in READMEs

---

## Phase 12: Final validation

- [ ] 12.1 Verify all agent `.md` filenames match `name:` in frontmatter
- [ ] 12.2 Verify all README links resolve correctly
- [ ] 12.3 Verify main README lists all agents in correct categories
- [ ] 12.4 Verify no orphaned files (agent files not listed in any README)
- [ ] 12.5 Grep for ALL old agent names — zero matches expected
- [ ] 12.6 Verify install-agents.sh URLs match actual file paths
- [ ] 12.7 Document decisions on agent-installer and it-ops-orchestrator placement
- [ ] 12.8 Verify agent count: should be 126 (129 - 3 merges)

---

## Summary of Changes

| Metric | Count |
|--------|-------|
| New categories created | 1 (00-architecture-design) |
| Categories renamed | 1 (01-core-development → 01-general-development) |
| Agents renamed | ~30 |
| Agents moved between categories | ~12 |
| Agents split | 0 |
| Duplicate agents merged | 3 pairs → 3 removed |
| Net new agent files | -3 |
| READMEs updated | 12 (10 category + 1 main + 1 new) |
| Plugin JSONs updated | 10 |
| Cross-references updated | TBD (grep-driven) |
| Install scripts updated | 2 |

## Execution Order

Phases 1-5 establish the new structure and can be executed sequentially as a batch. Phase 6 (merges) depends on category structure being settled. Phases 7-8 are remaining moves/renames. Phases 9-10 are cross-cutting updates that must happen after all renames are complete. Phase 11 is plugin.json cleanup. Phase 12 is validation.

Recommended: Execute in numbered order. Each phase (or batch of related phases) should be a separate commit for reviewability.
