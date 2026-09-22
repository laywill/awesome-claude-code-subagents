# Task Plan: Agent definitions as system prompts for local Ollama models

Issue: https://github.com/laywill/awesome-claude-code-subagents/issues/298
Branch: `298-explore-ollama-local-model-prompts`

## Goal
Produce a written, evidence-grounded assessment of whether (and how) this repo's 203
agent definitions can be repurposed as system prompts for small local models served by
Ollama — ending in a recommendation and a set of follow-up issues, not an implementation.

## Phases
- [x] Phase 1: Plan and setup
- [x] Phase 2: Characterise the corpus (measured — see notes.md §1)
- [x] Phase 3: Assess local-model suitability per category (strategy §2)
- [x] Phase 4: Identify genuine opportunities (strategy §3)
- [x] Phase 5: Design options + recommendation (strategy §5)
- [x] Phase 6: Write deliverable, commit, open PR, propose follow-up issues

## Key Questions
1. Which of the 24 categories suit a 4B-30B local model, and what is the actual
   discriminator? (Hypothesis: it's agentic tool-loop depth, not subject matter.)
2. What are the real use cases where local wins — privacy, cost, offline, bulk, latency?
3. What has to change mechanically? Frontmatter stripping, Claude-Code tool references,
   the "context manager" idiom (128 files), JSON inter-agent protocols.
4. Does a ~1,000-word dense system prompt help or *hurt* a 4B model? How would we know?
5. What is the smallest useful deliverable — docs only, a converter script, or Modelfiles?

## Extra phase added mid-flight
- [x] Phase 2b: **Run a real experiment.** Ollama turned out to be installed locally with the
  user's actual models, so the "does this help or hurt?" question was answered by measurement
  rather than argument. This changed two conclusions (see below).
- [x] Phase 7 (2026-08-18): **Experiment 2 — schema enforcement.** Triggered by the
  observation that local models need far stricter output contracts than frontier models, and
  by the question of whether deterministic quality gates (the pre-commit / linting model)
  transfer to loosely-defined tasks. See `notes.md` §4 and
  `experiment-2-schema-enforcement/`. **This produced a correction to the §5 converter
  design that has not yet been applied.**

## Decisions Made
- (2026-08-18) Exploration output lives in `docs/planning/298-ollama-local-models/`,
  committed to the branch, so the reasoning is reviewable in the PR rather than lost in chat.
- (2026-08-18) Treat the user's brief as rambling thoughts to be shaped: the deliverable
  must push back where the idea is weak, not just execute it.
- (2026-08-18) **Measure, don't assert.** Ran an A/B/C test on gemma3:4b before writing
  conclusions. Two prior assumptions were overturned:
  (a) "long prompts will be too expensive for small models" — false, generation dominates;
  (b) "stripping is a token-saving compromise" — false, the stripped prompt scored *better*.
- (2026-08-18) Recommend a converter script, not a committed Modelfile registry — the repo is
  a curated collection and 203 derived artefacts would drift from their sources immediately.
- (2026-08-18) The converter should **hard-gate Tier 4-5 categories**, not merely warn. The
  tier is in the directory name, so enforcement is free.
- (2026-08-18) Category 05 chosen as the experiment-2 testbed. `model: haiku` on all its
  agents is *not* evidence of local suitability — it is a Claude-side cost knob. The real
  reason 05 works as a testbed is that its outputs are rigidly structured, so **schema
  compliance is mechanically scoreable even though plan quality is not**. That separates
  "did it follow instructions" from "was it right".
- (2026-08-18) **Deferred:** whether to fold experiment 2's findings into
  `local-model-strategy.md` as a §8 and amend the §5 converter spec. Maintainer has not
  decided. Findings are parked in `notes.md` §0/§4/§5 so nothing is lost.

## Errors Encountered
- Bash heredoc failed on the long deliverable (unmatched quote in prose). Resolution: used
  the Write tool for the long document; heredocs kept for short files.
  **Recurred in the 2026-08-18 session on the notes.md rewrite — same resolution. Treat
  "long markdown prose via heredoc" as a known-bad pattern in this repo.**
- First background experiment run died on fork (`nohup ... &` inside a backgrounded Bash
  call). Resolution: invoke the script directly as the background command.
- gemma3:4b takes ~3-4 min per generation on this machine; the 3-condition sweep exceeds the
  10-minute foreground tool limit. Resolution: added skip-if-output-exists to the runner so
  it resumes rather than repeating work.
- (Experiment 2) Ollama returned a transient HTTP 500 on the first call of a sweep, while a
  previously-resident model was being evicted. Resolution: retry with backoff in the runner.
  Do not interpret a single 500 as a broken request.
- (Experiment 2) `num_ctx: 8192` silently pushed gemma3:4b out of VRAM into a 54%/46%
  CPU/GPU split, roughly halving throughput. `ollama ps` shows the split. Resolution: size
  `num_ctx` to actual need (4096 was ample for a ~800-token prompt and ~1,900-token output).

## Key findings (short version)
1. The agent files help small models via **checklist + output schema**, not knowledge transfer.
2. **46% of the corpus is strippable** multi-agent orchestration prose, and stripping it
   *improved* measured quality (5/5 seeded defects vs 4/5) at half the tokens.
3. Prompt length costs nothing in latency; generation dominates.
4. The best-scoring run still re-introduced a critical SQL injection as a "style tip" —
   human filtering of output is a load-bearing constraint, not a disclaimer.
5. Suitability is decided by loop depth / blast radius / verifiability / knowledge
   specificity — **not** by subject matter.
6. **(Experiment 2)** The recommended strip **deletes the output contract** — in category 05
   every schema lives inside `## Communication Protocol`. Stripped-only output was 0/10
   machine-parseable. The converter must *unwrap* the schema, not discard it.
7. **(Experiment 2)** *Enforcing* a schema via Ollama `format` beat *stating* it in the
   prompt (10/10 vs 0/10 fully valid) at **no latency cost**, and did not degrade content.
8. **(Experiment 2)** But constrained decoding is only safe when the grammar agrees with what
   the model wanted to emit. A regex `pattern` on a date field gave 0/3 correct dates.
9. **(Experiment 2)** No gate of any kind caught the most obvious content defect: zero spike
   tasks across 266 tasks, for a team explicitly described as having no SAML experience.

## Next steps

Ordered. Nothing here is started.

1. **Decide the deferred question** (blocks 2 and 3): fold experiment 2 into
   `local-model-strategy.md` as §8 + amend §5 from a 2-behaviour to a 4-behaviour converter?
   Everything needed to make the call is in `notes.md` §5. If yes, this is a ~1 hour edit.
2. **Build `tools/ollama-export/export.py`** per the amended spec — strip, **unwrap**,
   epilogue, **emit `format` schema**, tier gate. `experiment-2-schema-enforcement/build_prompts.py`
   is a working prototype of the first four for a single agent; generalising the unwrap across
   188 files with a `requesting_agent` envelope is the real work.
   - Open sub-question: 188 files have an envelope, but the `payload` shapes are not uniform.
     Sample ~20 across categories before assuming one extraction rule fits all.
3. **Build the validator layer** (`tools/ollama-export/validate.py`) for cross-field checks
   JSON Schema cannot express. `experiment-2-schema-enforcement/scorer.py` is the prototype.
   Per-agent rules, so start with the 05 set and see how much generalises.
4. **Eval harness** (already agreed as a follow-up issue, now more clearly needed).
   Experiment 2 gives it a concrete shape: seeded fixtures + mechanically-scoreable
   conformance checks + a content control like `quality.py` to catch schema-valid hollowing.
5. **Per-agent gating for 07, 11, 14** — still guesswork without the harness. Unchanged.
6. **Re-run experiment 2 on `qwen3-coder:30b`** to see whether the B/C gap closes with model
   size. If a 30B model complies with a stated schema reliably, constrained decoding becomes
   an optimisation rather than a requirement, and that changes the converter's priorities.

## Open questions for follow-up
- Per-agent (not per-category) gating for 07, 11, 14 — needs the eval harness, not guesswork.
- Does qwen3-coder:30b close the gap on the long-tail languages, or just on mainstream ones?
- Would a `local_model:` frontmatter field be worth the maintenance cost across 203 files?
- Does the B→C gap shrink with model size? (See next step 6.)
- Are the `payload` shapes across the 188 enveloped files regular enough for one unwrap rule?
- Is there a category where the model does *not* already want to emit the schema's shape —
  i.e. where constrained decoding would do damage the way the date `pattern` did?

## Status
**Exploration complete; one decision outstanding.** Deliverable: `local-model-strategy.md`.
Evidence: `notes.md` (start at §0) plus `experiment/` and `experiment-2-schema-enforcement/`.

**Picking this up fresh?** Read `notes.md` §0 first — five make-or-break results in one page.
Then §5 for the converter design change awaiting a decision, then "Next steps" above.
