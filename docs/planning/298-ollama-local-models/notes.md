# Notes: agent definitions as local-model system prompts

## 1. Corpus measurements (this repo, 2026-08-18)

203 agent files, 218,345 words total, mean 1,076 words (~1,400 tokens).

### Length correlates almost perfectly with risk tier

| Tier | Example categories | Mean words |
|---|---|---|
| 🟢 1 | 02-architecture (634), 05-planning (793), 06-business (878), 01-research (892) | ~630–970 |
| 🟡 2 | 09-testing (770), 08-general-dev (883), 07-language (960), 12-frontend (1073) | ~770–1090 |
| 🟠 3 | 14-data (1151), 16-dependency (1197), 17-build (1123) | ~1100–1200 |
| 🔴 4 | 18-api (1340), 19-iac (1360), 20-security (1140) | ~1100–1360 |
| ⛔ 5 | 22-deployment (1761), 23-prod-ops (1848), 24-prod-data (1892) | ~1760–1890 |

This is a **fortunate accident**: the categories most suitable for a small local model
(Tier 1, advisory) are the *shortest* prompts, and the least suitable (Tier 5, production
mutation) are the *longest*. Prompt budget pressure pushes the same way safety does.

### How much of each file is Claude-Code-specific machinery

| Idiom | Files affected (of 203) |
|---|---|
| `## Communication Protocol` section | 192 |
| `requesting_agent` JSON envelope | 188 |
| `## Development Workflow` phases | 181 |
| ` ```json ` fence | 186 |
| "Query context manager for …" | 128 |
| references other named subagents | 132 |
| names Claude Code tools (`Read`/`Grep`/…) in prose | **2** |

**Measured strippable fraction: 46% of all corpus words** sit at or after
`## Communication Protocol`. On the sample agent tested, stripping cut 872 → 376 words (-57%).

Important nuance: the tool names live almost entirely in *frontmatter* (`tools:`), not prose —
only 2 files name a Claude Code tool in the body. So the "Claude-Code-ness" that has to be
removed is **not** tool references. It is the multi-agent orchestration fiction:
a "context manager" agent to query, sibling agents to hand off to, and a JSON status
protocol nobody is listening to. For a standalone Ollama model these are *instructions it
cannot satisfy* — worst case it hallucinates a context-manager reply or emits status JSON
instead of the answer.

## 2. Empirical test (real, run locally)

Environment: Ollama 0.32.13, models present: `gemma3:4b`, `gemma4:latest`, `qwen3-coder:30b`,
`qwen2.5vl:7b`, `qwen3-vl:2b`.

Setup: `code-reviewer` (Tier 1, 03-analysis-and-review) as system prompt. Task: review a
12-line Python function seeded with 5 defects — SQL injection via string concat, an
off-by-one (`range(len(rows) + 1)`), a bare `except: pass`, a never-closed connection,
and a magic column index. `temperature=0.2, seed=42, num_ctx=8192`.

Conditions:
- **A_none** — no system prompt (baseline)
- **B_full** — agent file with YAML frontmatter stripped, everything else intact
- **C_stripped** — B minus `## Communication Protocol` onwards, minus the "Query context manager" line

### Results — gemma3:4b

| | prompt tok | output tok | secs | defects found (of 5) |
|---|---|---|---|---|
| A_none | 162 | 1206 | 259 | **4/5** — SQLi ✓, bare-except ✓, no-close ✓, magic-index ✓, **off-by-one ✗** |
| B_full | 1505 | 1145 | 180 | **4/5** — SQLi ✓, bare-except ✓, magic-index ✓, **off-by-one ✓**, no-close only silently fixed in the rewrite, never flagged |
| C_stripped | **707** | 1339 | 210 | **5/5** — all of the above, off-by-one named explicitly ("iterates one element too far"), plus naming and missing-docstring findings |

**C_stripped won on every axis: best coverage, smallest prompt, severity-graded output**
(Critical / Poor / Medium / Low / Minor). It was the only condition to find all five
seeded defects.

⚠️ **But C also produced the single most dangerous output of the three.** Having correctly
said "never embed user data in SQL, use parameterized queries" under *Security*, it then
said this under *Code Style*:

> Use f-strings for cleaner formatting: `q = f"SELECT * FROM orders WHERE user_id = '{user_id}' LIMIT {limit}"`

That is the *same SQL injection* it had just flagged as critical, re-introduced three
paragraphs later as a style improvement. A reader skimming the "Code Style" section and
applying the suggestion would reinstate the vulnerability.

This is the most important single result of the experiment. Broader checklist coverage
increased both the true findings **and** the confidently-wrong ones. The failure is not
random noise — it is a *locally* plausible suggestion that is globally wrong, which is
precisely the failure mode a human reviewer is least likely to catch. It confirms the
"human-filtered output only" constraint is load-bearing, not boilerplate.

### Observations that matter

1. **The agent prompt measurably improved coverage.** B caught the off-by-one that the
   bare model silently missed — and it is the subtlest defect of the five. It also flagged a
   naming issue A ignored.
2. **It improved structure more than coverage.** B grouped findings under
   Security / Code Quality / Error Handling / Naming with an explicit `Recommendation:` per
   item — traceable to the agent's own checklist headings. This is the clearest win:
   the prompt is acting as an **output schema and a coverage checklist**, not as knowledge
   transfer. The 4B model already *knew* about SQL injection; it needed to be told to look
   systematically and to report in a fixed shape.
3. **Stripping helped rather than hurt.** C outperformed B despite being less than half
   the prompt — evidence that the Communication Protocol / Development Workflow sections are
   not merely inert filler but active distraction for a small model.
4. **It was not free of harm.** B introduced a wrong finding ("Hardcoded Limit" — `limit` is a
   parameter, not hardcoded) and demoted the missing `conn.close()` from a finding to a silent
   fix. Small-model instruction load is real; more checklist ≠ strictly better.
5. **The long prompt cost nothing in latency.** 1,505 vs 162 prompt tokens, yet B finished
   *faster* (180s vs 259s) because prompt ingestion is cheap relative to generation and B
   generated slightly fewer tokens. **Prompt length is not the bottleneck; output length is.**
   This kills the "1,000-word prompts are too expensive for small models" objection.

### Caveat on this evidence
n=1 task, n=1 agent, n=1 model, single seed. This is a directional signal, not a benchmark.
It is enough to justify building a proper harness; it is not enough to publish claims.

## 3. Synthesised judgement

The idea works, but **not for the reason initially assumed**. The value is not that these
files make a small model *smarter* about a domain. It is that they supply the two things
small models are worst at supplying themselves:

- **Systematic coverage** — a checklist prevents the model stopping after the 3 obvious findings
- **Stable output shape** — headings and per-item recommendations, consistent across runs

That reframing changes what a good port looks like. If the value is checklist + schema, then
the parts worth keeping are exactly the enumerated checklists — and the parts worth cutting
are the multi-agent prose, which is 46% of the corpus.
