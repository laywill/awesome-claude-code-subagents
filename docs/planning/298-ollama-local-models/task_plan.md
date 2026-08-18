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

## Errors Encountered
- Bash heredoc failed on the long deliverable (unmatched quote in prose). Resolution: used
  the Write tool for the long document; heredocs kept for short files.
- First background experiment run died on fork (`nohup ... &` inside a backgrounded Bash
  call). Resolution: invoke the script directly as the background command.
- gemma3:4b takes ~3-4 min per generation on this machine; the 3-condition sweep exceeds the
  10-minute foreground tool limit. Resolution: added skip-if-output-exists to the runner so
  it resumes rather than repeating work.

## Key findings (short version)
1. The agent files help small models via **checklist + output schema**, not knowledge transfer.
2. **46% of the corpus is strippable** multi-agent orchestration prose, and stripping it
   *improved* measured quality (5/5 seeded defects vs 4/5) at half the tokens.
3. Prompt length costs nothing in latency; generation dominates.
4. The best-scoring run still re-introduced a critical SQL injection as a "style tip" —
   human filtering of output is a load-bearing constraint, not a disclaimer.
5. Suitability is decided by loop depth / blast radius / verifiability / knowledge
   specificity — **not** by subject matter.

## Open questions for follow-up
- Per-agent (not per-category) gating for 07, 11, 14 — needs the eval harness, not guesswork.
- Does qwen3-coder:30b close the gap on the long-tail languages, or just on mainstream ones?
- Would a `local_model:` frontmatter field be worth the maintenance cost across 203 files?

## Status
**Complete.** All phases done. Deliverable: `local-model-strategy.md`. Evidence: `notes.md`
plus raw model outputs in `experiment/`. Follow-up issues proposed in the PR.
