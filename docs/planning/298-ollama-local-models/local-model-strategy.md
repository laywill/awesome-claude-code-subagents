# Using these agent definitions with local models (Ollama)

**Status:** exploration / proposal — issue #298
**Audience:** maintainers deciding whether this is worth building

---

## TL;DR

The idea works, but not for the reason it looks like it works.

These files do **not** make a 4B model smarter about a domain. In a controlled local test
(`gemma3:4b`, `code-reviewer`, 5 seeded defects) the bare model already knew what SQL
injection was. What it lacked was the discipline to look systematically and report
consistently. The agent prompt supplied exactly that — and caught the subtlest defect
(an off-by-one) that the bare model silently missed.

**So the value is checklist + output schema, not knowledge transfer.** That reframing
should drive everything else:

- **Do it** — for Tier 1–2 advisory and drafting roles, where output is human-filtered.
- **Don't do it** — for Tier 4–5. Not a prompt problem; a "don't give a 4B model prod
  credentials" problem.
- **Build one small converter**, not a registry of 203 Modelfiles.
- **Strip aggressively.** 46% of the corpus is multi-agent orchestration prose that is
  actively harmful to a standalone model — it instructs it to do things it cannot do.
  Measured: the stripped prompt **beat** the full one — 5/5 seeded defects vs 4/5, on less
  than half the tokens. Stripping is a quality improvement, not just a saving.
- **Prompt length is a non-issue.** Measured: 162 → 1,505 prompt tokens changed latency
  not at all (generation dominates). Drop the "too long for small models" worry.
- **Never ship the output unread.** The best-scoring run also re-introduced the SQL
  injection it had just flagged as critical, disguised as a style tip (§6.1).

---

## 1. What actually decides suitability

Not subject matter. Four axes:

| Axis | Question | Why small models fail |
|---|---|---|
| **Loop depth** | How many tool-call → observe → adjust cycles before the output is useful? | Degrade sharply past ~3 cycles; lose the thread, hallucinate tool results, cannot recover from errors |
| **Blast radius** | What happens when it is confidently wrong? | Confidence is uncorrelated with correctness at 4B |
| **Verifiability** | Is there a cheap oracle — compiler, test suite, linter, schema validator? | An oracle converts "unreliable" into "unreliable but self-correcting" |
| **Knowledge specificity** | Does it need exact, current API/CLI/version facts, or transferable principles? | Niche API surface is where small models hallucinate most confidently |

**Sweet spot: shallow loop + low blast radius + (verifiable OR human-filtered) + principle-driven.**

Two consequences that cut against intuition:

- **"It is just code" does not mean "safe for a local model."**
  `07-language-and-framework-specialists` is only Tier 2, but it is one of the *worst* fits —
  it demands exact framework API recall. A hallucinated `terraform` flag gets caught by
  `terraform plan`; a hallucinated Elixir stdlib function gets caught by nothing until it
  fails to compile, and a hallucinated *idiom* never gets caught at all.
- **Documentation is one of the best fits** despite being "writing," because blast radius is
  near zero and a human reads every word before it lands.

### A fortunate accident

Prompt length in this repo correlates almost perfectly with risk tier — Tier 1 agents average
~630–970 words, Tier 5 average ~1,760–1,890. The agents best suited to local models are also
the cheapest to load. Prompt budget pressure and safety point the same direction.

---

## 2. Category-by-category assessment

**Legend:** ✅ good fit · 🟨 partial / with caveats · ❌ do not

| # | Category | Tier | Fit | Reasoning |
|---|---|---|---|---|
| 01 | research-and-discovery | 🟢1 | 🟨 | `codebase-explorer` needs repo-wide context a 4B cannot hold. But `feasibility-assessor` and `research-analyst` are single-turn framing tasks — good. Market/trend/competitive analysts need *current* facts and will confabulate; those need web search, so they belong to Claude Code. |
| 02 | architecture-and-design | 🟢1 | ✅ | Shortest prompts in the repo (mean 634w). Principle-driven, human-filtered, single-turn. `schema-designer`, `api-designer`, `data-flow-designer` produce reviewable artefacts. Strong starting point. |
| 03 | analysis-and-review | 🟢1 | ✅ **best** | Where the experiment ran and where the checklist effect is strongest. Read-only, low blast radius, self-contained inputs. `code-reviewer`, `complexity-analyzer`, `accessibility-tester` all work on a pasted snippet. Caveat: findings must be read, never applied wholesale — see §6.1. |
| 04 | documentation | 🟢1 | ✅ **best** | Near-zero blast radius, always human-reviewed, output shape matters more than knowledge depth — exactly what these prompts supply. `readme-generator`, `changelog-generator`, `adr-author`, `runbook-writer`. Also the highest-volume, most tedious work, so the best ROI. |
| 05 | planning-and-estimation | 🟢1 | ✅ | Structured-output tasks over user-supplied context. `task-planner`, `effort-estimator`, `risk-assessor`. Nobody ships an estimate unreviewed. |
| 06 | business-and-product | 🟢1 | 🟨 | Fine mechanically. But `legal-advisor`, `quant-analyst` and `risk-manager` invite acting on confabulated specifics. Prefer the drafting ones (`content-marketer`, `ux-researcher`). |
| 07 | language-and-framework-specialists | 🟡2 | 🟨 **splits hard** | Depends entirely on the language's training-data mass *and* the model. `qwen3-coder:30b` is credible on Python/TS/SQL/Go/Java. The long tail — Elixir, OCaml, Haskell, F#, Lua, dotnet-framework-4.8, the PowerShell family, WordPress — is where confident hallucination lives. Gate per-language, not per-category. |
| 08 | general-development | 🟡2 | 🟨 | Scaffolding and boilerplate: yes. Anything spanning many files: no. Verifiable via compiler and tests, which helps a lot. |
| 09 | testing-and-qa | 🟡2 | ✅ | **Underrated.** Test generation is the one place with a *free automatic oracle*: the test runs or it does not. `unit-test-writer`, `test-fixture-generator`, `coverage-gap-filler` are near-ideal — bulk, repetitive, self-verifying. (Not `chaos-engineer` — that touches live systems.) |
| 10 | refactoring-and-modernization | 🟡2 | 🟨 | `linter-fixer` and mechanical `pattern-migrator` work — narrow, verifiable, diff-reviewable. `legacy-modernizer` needs whole-system context; do not. |
| 11 | bug-fixing-and-debugging | 🟡2 | 🟨 | `stack-trace-interpreter` and `log-analyzer` are excellent — single-turn, self-contained input, pure interpretation. `bug-fixer` and `regression-hunter` need long investigative loops; do not. **This category should be split by loop depth.** |
| 12 | frontend-and-ui | 🟡2 | ✅ | `i18n-extractor`, `style-refactorer`, `theme-generator` are mechanical, bounded transformations over supplied input. Good bulk local work. |
| 13 | developer-experience-and-tooling | 🟡2 | 🟨 | `prompt-engineer` is a fun self-referential fit. `build-engineer` and `tooling-engineer` need environment-specific facts. |
| 14 | data-and-database | 🟠3 | 🟨 | `seed-data-generator` ✅ (generative, harmless, bulk). `schema-migrator` and `database-optimizer` ❌ — touching data. |
| 15 | data-science-and-ai | 🟠3 | 🟨 | Analysis and explanation yes; anything running pipelines no. |
| 16 | dependency-and-package-management | 🟠3 | ❌ | Needs exact current version and CVE facts. Confabulation here is dangerous and invisible. Use real tooling, not a language model. |
| 17 | build-and-ci-cd | 🟠3 | ❌ | Needs exact CI YAML schemas and current action versions — high hallucination, and unverifiable until it fails in CI. |
| 18 | api-and-service-integration | 🔴4 | ❌ | Exact third-party API surface. The worst possible hallucination profile. |
| 19 | infrastructure-as-code | 🔴4 | ❌ | Real infrastructure, exact provider schemas. |
| 20 | security-and-secrets | 🔴4 | ❌ *with one carve-out* | Never for acting. **But** read-only *review* of code that legally cannot leave the building is the single strongest local-model use case in this repo — see §3. Use the `03/security-auditor` framing, not `20/secret-rotator`. |
| 21 | specialized-domains | 🔴4 | ❌ | Niche and high-consequence (fintech, payments, embedded). |
| 22 | deployment-and-release | ⛔5 | ❌ | Absolutely not. |
| 23 | production-ops-and-observability | ⛔5 | ❌ | Absolutely not. |
| 24 | production-data-ops | ⛔5 | ❌ | Absolutely not. |

### Summary

- **Start here (✅):** 02, 03, 04, 05, 09, 12 — roughly 45 agents
- **Selectively (🟨):** 01, 06, 07, 08, 10, 11, 13, 14, 15 — per-agent gating needed
- **Never (❌):** 16–24 — and the converter should enforce this, not merely document it

The line is **Tier 1–2, minus anything needing exact current API facts, plus anything with a
free oracle.**

---

## 3. Where local genuinely beats reaching for Claude Code

Ordered by how real the advantage is.

1. **Work that cannot leave the network.** Client code under NDA, regulated environments,
   air-gapped sites. Here local is not cheaper — it is *the only option*. A checklist-driven
   `code-reviewer` or `security-auditor` on a 30B local model is infinitely better than no
   review at all. **This is the strongest case and it should lead the docs.**
2. **Bulk, repetitive, low-stakes volume.** Changelogs across 200 commits; READMEs across 40
   monorepo packages; docstrings; i18n extraction; test fixtures. Per-item quality matters
   less than getting a consistent first draft across the whole set, and latency is irrelevant
   when it runs overnight.
3. **Draft-then-refine.** The local model produces the structured skeleton (which is what
   these prompts are good at); Claude Code refines the substance. Cuts expensive tokens
   substantially on long-form output.
4. **Independent second opinion.** A different model with a different checklist catches
   different things — the test showed the 4B finding a defect *because* it was checklisted.
   Cheap enough to run on every commit as a pre-filter that escalates only on findings.
5. **Offline.** Planes, trains, bad hotel wifi.
6. **Dogfooding this repo.** 203 files needing consistency audits, description-length checks
   and frontmatter validation. The repo already has `description-compressor` and
   `token-efficiency-optimizer` project agents doing exactly this kind of bulk pass.
7. **Learning.** Unlimited free practice with role framings, no token anxiety.

**Where local does *not* win:** anything needing current facts, deep multi-file reasoning,
long tool loops, or a correct answer first time.

---

## 4. What would have to change

### 4.1 The frontmatter must go — but it is not the interesting part

`name`, `description` and `model` are Claude Code registry metadata. The `tools:` line is
worse than useless: it tells the model it has `Read, Write, Edit, Bash` when it has none,
inviting it to role-play tool calls instead of answering.

### 4.2 The actually harmful content is the multi-agent fiction

Measured across 203 files:

| Idiom | Files |
|---|---|
| `## Communication Protocol` | 192 |
| `requesting_agent` JSON envelope | 188 |
| `## Development Workflow` phases | 181 |
| "Query context manager for …" | 128 |
| references other named subagents | 132 |
| names a Claude Code tool *in prose* | **2** |

Note the last row: Claude-Code-specific *tool* coupling is almost nonexistent in the body.
The coupling that matters is **orchestration** — a context manager to query, siblings to hand
off to, a JSON status protocol nobody is listening to. To a standalone Ollama model these are
**unsatisfiable instructions**, and a small model's failure mode when given one is to fake
compliance: hallucinate a context-manager reply, or emit status JSON instead of the answer.

**46% of all corpus words sit at or after `## Communication Protocol`.** On the tested agent,
stripping cut 872 → 376 words. This is the single highest-value transformation, and it is
purely mechanical.

**It is also, measurably, a quality win.** In the A/B/C test the stripped prompt found
**5/5** seeded defects against **4/5** for the full prompt, on 707 vs 1,505 prompt tokens.
The orchestration sections are not inert filler being carried along for free — they are
active distraction that costs a small model real accuracy.

### 4.3 Something must be *added*: a grounding epilogue

The most important addition, appended after stripping:

> You have no tools. You cannot read files, run commands, or query other agents. Work only
> from what the user gives you in the conversation. If you need to see a file, ask for it.
> Answer directly — do not emit status objects or plans to hand off work.

This closes exactly the hole that stripping the protocol sections opens.

### 4.4 Prompt length is *not* a problem

Measured on `gemma3:4b`: 162 → 1,505 prompt tokens produced **no latency penalty** (the
long-prompt run was in fact faster, because generation dominates and it emitted fewer
tokens). Strip for *behavioural* reasons — unsatisfiable instructions — not for budget. The
"1,000-word prompts will overload a 4B model" worry is unfounded on the cost axis. It is
*not* unfounded on the instruction-following axis: the full-protocol prompt scored *worse*
than the stripped one. More prompt does not mean better — but the reason is attention and
instruction conflict, not context budget.

---

## 5. Design options

| | Approach | Verdict |
|---|---|---|
| **1** | Docs only — a "using these with Ollama" guide | Too thin. The stripping is fiddly enough that everyone would do it differently and badly. |
| **2** | **Converter script** — read agent `.md`, strip, emit system prompt or `Modelfile` | ✅ **Recommended** |
| **3** | Committed registry of 203 pre-built Modelfiles | ❌ 203 derived artefacts to keep in sync with their sources, plus coupling to specific model tags. Guaranteed drift. |
| **4** | Full runtime CLI wrapper (`ollama-agent code-reviewer file.py`) | ❌ Turns a curated *collection* into a *tool product*. Real maintenance burden and scope creep. Possible later, on evidence of demand. |

### Recommended: Option 2 plus a short doc

One script under `tools/ollama-export/`, generating on demand. The single source of truth
stays the agent `.md`; nothing derived is committed; no coupling to model versions.

```
tools/ollama-export/
  export.py            # agent .md -> system prompt (.txt) or Modelfile
  README.md            # usage plus the honest caveats from §2
```

Behaviour:

- Strip YAML frontmatter (always).
- Drop `## Communication Protocol` through EOF by default; `--keep-protocol` to override.
- Drop `Query context manager…` bullets and neutralise sibling-agent handoff references.
- Append the §4.3 grounding epilogue.
- `--format modelfile` emits `SYSTEM """…"""` (escaping embedded triple quotes) with a sane
  `num_ctx`.
- **Risk gate:** refuse Tier 4–5 categories (16–24) unless an explicit override flag is
  passed, and print the reason. The tier is derivable from the directory name, so this is
  free to implement — and it is the difference between a helpful tool and one that helps
  someone point a 4B model at production.

### Not now, but worth an issue

- An eval harness (`tools/ollama-export/eval/`) — seeded-defect fixtures, A/B/C conditions,
  scoring. Everything in §2 is currently reasoned from first principles plus **one** data point.
- An optional frontmatter field (e.g. `local_model: good|partial|unsuitable`) so the
  per-agent gating in 07, 11 and 14 lives next to the agent rather than in a table that rots.

---

## 6. Honest risks

1. **Confidently-wrong output that looks authoritative. (Observed, not hypothetical.)**
   The best-scoring run — stripped prompt, all 5 defects found, neatly severity-graded —
   correctly stated under *Security* that user data must never be embedded in SQL and that
   parameterized queries are required. Three paragraphs later, under *Code Style*, it
   recommended:

   > Use f-strings for cleaner formatting:
   > `q = f"SELECT * FROM orders WHERE user_id = '{user_id}' LIMIT {limit}"`

   That is the identical SQL injection, re-introduced as a style improvement. A reader
   skimming section headings and applying the suggestions would reinstate the vulnerability
   the same tool had just flagged as critical.

   The lesson is not "small models are bad." It is that a **better-structured output raises
   the credibility of the wrong parts along with the right ones.** The agent prompt makes
   output look like a professional review, which makes it *harder* to stay sceptical of.
   Every recommendation in §2 and §3 is therefore conditional on **human-filtered output**,
   and the docs must say so in the first paragraph, not a footnote.

2. **The evidence base is one test.** n=1 agent, n=1 task, n=1 model, one seed. It justifies
   building; it does not justify publishing quality claims. Fix with the eval harness.
3. **Instruction overload is real.** The full-protocol prompt produced a spurious finding
   ("hardcoded limit" — it was a parameter) and demoted a real one from a finding to a silent
   fix, while scoring below the stripped prompt. Longer does not mean better.
4. **Encouraging unsafe use.** The clearest failure mode for this whole idea is someone
   running `terraform-engineer` on a 4B model against real infrastructure. Hence the hard
   risk gate in the converter, not just a warning in a README.
5. **Scope creep.** This repo is a curated collection. One script and one doc is
   proportionate; a CLI product is not.

---

## 7. Recommendation

Proceed, scoped tightly:

1. Build `tools/ollama-export/export.py` (strip, epilogue, Modelfile, tier gate).
2. Write `tools/ollama-export/README.md` leading with the privacy and air-gapped case,
   carrying §2's honest table, and opening with the §6.1 warning — output from these is a
   *checklist-driven first draft for a human to filter*, never a verdict to apply.
3. Open a follow-up issue for the eval harness before making any quality claims publicly.
4. Leave per-agent gating (07, 11, 14) to the eval work rather than guessing now.
