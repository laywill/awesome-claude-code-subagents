# Notes: agent definitions as local-model system prompts

## 0. Make-or-break learnings — read this first

Five results that will cost a new session a day if rediscovered the hard way. Each was
measured, not reasoned. Evidence in §2 (experiment 1) and §4 (experiment 2).

1. **Stripping `## Communication Protocol` deletes the output contract.** In
   `05-planning-and-estimation` all five agents have *zero* JSON blocks before that heading —
   the only description of the output shape sits inside the section experiment 1 told us to
   strip. Stripped-only prompts scored **0/10 parseable**. The converter must **unwrap** the
   `payload` schema and re-present it, not delete it. This is the single most important
   correction to `local-model-strategy.md` §5.

2. **Enforcing a schema costs nothing.** Ollama `format=<JSON Schema>` (constrained decoding)
   took 325s vs 338s for merely *asking* for the same schema in the prompt, at identical
   output volume. There is no latency argument for prompting over enforcing.

3. **But only constrain shapes the model already wants to emit.** Constraint is free when
   aligned with the model's intent and *destructive* when it fights it. A regex `pattern` on
   a date field produced 0/3 correct dates (`3153-03-03`) because the sampler cannot
   backtrack; separate integer `year`/`month`/`day` fields gave 3/3. **A gate that checks
   syntax can be satisfied by garbage.**

4. **Two failure layers, and they need different tools.** Grammar failures (smart quotes
   mid-JSON, markdown fences) are killed structurally by constrained decoding. Cross-field
   semantic failures (a task assigned to a workstream that was never declared) are
   *inexpressible* in JSON Schema and need a validator hook. Neither substitutes for the
   other — but the hook caught 2/10 in condition B and **0/10** in condition C, so it is
   cheap insurance, not the main event.

5. **No gate catches "well-formed, complete, and wrong."** Across 266 tasks in 19 valid plans,
   **zero spike tasks** — despite the agent prompt defining spikes for unknowns and the input
   epic stating "no prior SAML experience." Every run passed every check. Combined with
   experiment 1's SQL-injection-as-style-tip (§2), the human-filtering constraint is
   load-bearing at every level of enforcement.

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

⚠️ **Caveat added after experiment 2:** that 46% is strippable *content*, but the
`requesting_agent` envelope in 188 files also carries the only machine-readable description of
each agent's output. Strip the section wholesale and you lose it. See §0.1 and §5.

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

## 4. Experiment 2 — enforcing vs asking for an output schema (2026-08-18)

Full method, raw outputs and reproduction steps: `experiment-2-schema-enforcement/`.

**Question.** Experiment 1 said strip the protocol sections. But if the value of these files
is "checklist + output schema" (§3), and the schema lives inside the stripped section, what is
left? And is *stating* a schema in the prompt enough, or does it need *enforcing*?

**Setup.** `task-planner` (05-planning-and-estimation) on `gemma3:4b`, Ollama 0.32.14,
`temperature=0.7`, `num_ctx=4096`, seeds 0-9. Task: decompose a SAML 2.0 SSO epic for a
multi-tenant Django monolith. 3 conditions × 10 runs.

- **A** — stripped + grounding epilogue (the current §4–5 recommendation)
- **B** — A + the `payload` schema unwrapped from the JSON envelope into an explicit contract
- **C** — B + the same schema passed as Ollama `format` (constrained decoding)

### Results

| check | A | B | C |
|---|---|---|---|
| parses at all | 0/10 | 9/10 | **10/10** |
| bare JSON, no fences | 0/10 | 0/10 | **10/10** |
| all top-level keys | 0/10 | 9/10 | 10/10 |
| all 8 task fields present | 0/10 | 9/10 | 10/10 |
| `complexity` in vocabulary | 0/10 | 9/10 | 10/10 |
| *(hook layer)* `total_tasks` matches | 0/10 | 9/10 | 10/10 |
| *(hook layer)* dependency ids resolve | 0/10 | 9/10 | 10/10 |
| *(hook layer)* workstream was declared | 0/10 | **8/10** | 10/10 |
| *(hook layer)* graph acyclic | 0/10 | 9/10 | 10/10 |
| **fully valid** | **0/10** | **0/10** | **10/10** |
| mean secs / output tokens | 195 / 1114 | 338 / 1873 | 325 / 1872 |

### Observations that matter

1. **A is not bad planning — it is unlintable.** The prose decomposition is reasonable. But
   with no output contract there is nothing for any deterministic gate to grip. This is the
   finding that changes the converter design; it is *not* a claim that stripping was wrong.
2. **B gets the content right and the delivery wrong.** All 10 runs wrapped output in
   ` ```json ` fences despite the prompt saying, in those words, "no markdown code fences."
   Small models reliably follow positive instructions and drop negative ones — suppressing a
   strongly-learned habit is harder than following an instruction. Recoverable with a
   three-line fence-stripping parser, but it never complies on its own.
3. **The two B failures are one per layer.** Seed 8 drifted into typographic smart quotes
   mid-document (grammar); seed 5 invented an undeclared workstream `"All"` (semantics).
   Constrained decoding kills the first class outright — the grammar admits only `"` as a
   string delimiter. It cannot touch the second.
4. **Enforcement did not hollow out the content.** Checked deliberately, because of the date
   probe below. C is marginally *richer* than B: 2.26 vs 1.94 acceptance criteria per task,
   1.90 vs 1.46 dependency edges per task, 20/21 vs 19/21 domain terms hit, 107/140 vs 92/126
   distinct task titles.
5. **The `num_ctx` trap.** `num_ctx: 8192` pushed `gemma3:4b` out of VRAM into a 54%/46%
   CPU/GPU split. 4096 fits entirely on GPU. For local batch throughput, **context sizing is
   a far bigger lever than prompt length** — a second reason not to over-generalise
   experiment 1's "prompt length is free" result.

### Side probe — constrained decoding can produce schema-valid garbage

Extracting a date from `"Invoice from Acme Widgets Ltd dated 3rd March 2024"`, 3 seeds each:

| `date` field schema | outputs | correct |
|---|---|---|
| string + `pattern` `^[0-9]{4}-[0-9]{2}-[0-9]{2}$` | `3150-03-03`, `3024-03-03`, `3153-03-03` | **0/3** |
| string, unconstrained | `3rd March 2024`, `March 3rd, 2024`, `3rd March 2024` | 3/3 semantically, 0/3 formatted |
| integer `year`/`month`/`day` | `2024-03-03` ×3 | **3/3** |

The regex *is* enforced; every output matches it. The model's preferred next token is `3`
(beginning "3rd March"), the grammar then requires three more digits, and constrained decoding
**cannot backtrack** — so it commits and confabulates a plausible remainder. This is why §0.3
says constrain only what the model already wants to emit, and why syntactic validation is the
weakest kind of gate.

### Caveat on this evidence

n=1 agent, n=1 epic, n=1 model, 10 seeds. Enough to justify a specific design change to the
converter; not enough for published quality claims. The eval-harness follow-up still stands.

## 5. What this means for the converter (pending decision)

`local-model-strategy.md` §5 specifies a two-behaviour converter (strip, append epilogue).
The evidence above says it needs four:

1. **Strip** frontmatter and `## Communication Protocol` onwards — unchanged.
2. **Unwrap** the `payload` schema out of that section *before* discarding it, and re-present
   it as an explicit output contract. Without this, output is unlintable (0/10 parseable).
3. **Emit a matching JSON Schema** for Ollama `format`, so the shape is enforced rather than
   requested. Free in latency; removes the fence and smart-quote failure classes entirely.
4. **Ship a validator** for the cross-field checks a JSON Schema cannot express — id
   uniqueness, referential integrity of dependencies, acyclicity, declared-value membership.
   Cheap, deterministic, retryable, and the only thing that catches the seed-5 class.

Not yet applied to `local-model-strategy.md` — the maintainer has deferred that decision.
`build_prompts.py` in `experiment-2-schema-enforcement/` is a working prototype of steps 1–3,
and `scorer.py` of step 4.

### The general shape of it

Three gates, and they are not interchangeable:

| layer | enforces | example | cost |
|---|---|---|---|
| JSON Schema via `format` | grammar — field set, types, enums | `complexity ∈ {trivial…spike}` | free, structural |
| validator hook | semantics a schema cannot express | dependency ids resolve, graph acyclic | cheap code, deterministic |
| human | judgement | "there should be a SAML spike" | irreducible |

The analogy to linting a codebase holds, with one caveat: linting works because code already
has a grammar and a type system to grip. A loosely-defined task has neither, so forcing the
output into a schema is what *manufactures* the surface a gate can check. But code also has
tests, which check behaviour rather than form. A plan has no equivalent — which is why the
third row cannot be automated away here even though it partly can for code.
