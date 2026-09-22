# Experiment 2: does enforcing an output schema beat asking for one?

Follows experiment 1 (`../experiment/`), which asked *does an agent definition help a small
model at all?* This one asks the next question: **once you have a stripped agent prompt, what
does it take to get output a deterministic gate can actually check?**

Cited by `../notes.md` §4 and §5.

## Why this experiment exists

Experiment 1 recommended stripping `## Communication Protocol` onwards. In
`categories/05-planning-and-estimation/`, **every output schema in the category lives inside
that section** — there are zero JSON blocks before it in all five agents. So the recommended
strip deletes the only description of the output shape and leaves prose behind.

## Method

- **Agent under test:** `categories/05-planning-and-estimation/task-planner.md`
- **Model:** `gemma3:4b`, Ollama 0.32.14, `temperature=0.7`, `num_ctx=4096`, seeds 0-9
- **Task:** `epic.txt` — decompose a SAML 2.0 SSO epic for a multi-tenant Django monolith
- **Conditions** (10 runs each, 30 total):
  - **A** (`prompt_A.txt`) — stripped + grounding epilogue. The current recommendation in
    `../local-model-strategy.md` §4-5.
  - **B** (`prompt_B.txt`) — A, plus the `payload` schema **unwrapped** from the
    Communication Protocol JSON envelope and re-presented as an explicit output contract.
  - **C** — prompt B *plus* `format_schema.json` passed as Ollama `format` (constrained
    decoding).

`build_prompts.py` performs the strip and the unwrap mechanically — it is a prototype of the
`export.py` change this experiment argues for.

## Scoring

`scorer.py` deliberately splits the checks into two groups:

- **Schema-expressible** — field set, types, enum membership. A JSON Schema can state these,
  so constrained decoding should make them free.
- **Needs-a-hook** — cross-field and graph properties a JSON Schema *structurally cannot*
  express: `total_tasks` equals `len(tasks)`, ids unique, every dependency id resolves, every
  `workstream` was declared in the top-level array, dependency graph is acyclic.

`quality.py` is the control: it checks whether constrained decoding hollowed out the
*content* while the form got better.

## Results

| check | A | B | C |
|---|---|---|---|
| parses at all | 0/10 | 9/10 | **10/10** |
| bare JSON, no fences | 0/10 | 0/10 | **10/10** |
| all top-level keys | 0/10 | 9/10 | 10/10 |
| all 8 task fields | 0/10 | 9/10 | 10/10 |
| `complexity` in vocabulary | 0/10 | 9/10 | 10/10 |
| `total_tasks` matches | 0/10 | 9/10 | 10/10 |
| dependency ids resolve | 0/10 | 9/10 | 10/10 |
| workstream was declared | 0/10 | **8/10** | 10/10 |
| dependency graph acyclic | 0/10 | 9/10 | 10/10 |
| **fully valid** | **0/10** | **0/10** | **10/10** |
| mean secs / output tokens | 195 / 1114 | 338 / 1873 | 325 / 1872 |

### The two B failures, one per layer

- **seed 8 — grammar.** Drifted into typographic smart quotes mid-document
  (`“title”: “Implement Admin UI”`) after two correctly-quoted tasks. Unparseable.
- **seed 5 — semantics.** Declared four workstreams, then assigned a task to a fifth,
  `"All"`, that it invented. Parses perfectly. Only the hook layer can catch this — "must be
  one of the values in that other array" is not expressible in JSON Schema.

Constrained decoding eliminates the first class structurally. It cannot touch the second.

### Content control (`quality.py`)

C is not hollowed out — it is marginally *richer* than B:

| | B | C |
|---|---|---|
| acceptance criteria / task | 1.94 | 2.26 |
| dependency edges / task | 1.46 | 1.90 |
| domain terms hit (of 21) | 19 | 20 |
| distinct titles | 92/126 | 107/140 |

## Side probe: when constrained decoding goes wrong

`pattern_probe.py` / `intfields_probe.py`. Same model, extracting a date from
`"Invoice from Acme Widgets Ltd dated 3rd March 2024"`, 3 seeds each:

| `date` field schema | outputs | correct |
|---|---|---|
| `{"type":"string","pattern":"^[0-9]{4}-[0-9]{2}-[0-9]{2}$"}` | `3150-03-03`, `3024-03-03`, `3153-03-03` | **0/3** |
| `{"type":"string"}` | `3rd March 2024`, `March 3rd, 2024`, `3rd March 2024` | 3/3 semantically, 0/3 formatted |
| separate `{"year":int,"month":int,"day":int}` | `2024-03-03` x3 | **3/3** |

The pattern *is* enforced — every output matches the regex. That is the problem. The model
wants to emit `3` (starting "3rd March"), the grammar then demands three more digits, and
constrained decoding **cannot backtrack**, so it confabulates a plausible remainder. A wrong
date that passes every syntactic check.

## Reproducing

```bash
python build_prompts.py     # regenerate prompt_A.txt, prompt_B.txt, format_schema.json
python runner.py            # 30 runs, ~100 min on gemma3:4b; resume-safe
python scorer.py            # writes scores.json, prints the table
python quality.py           # content control
```

`runner.py` skips any run whose output file already exists, so it resumes after an
interruption rather than repeating work.

## Caveats

n=1 agent, n=1 epic, n=1 model, 10 seeds. Enough to justify the `export.py` design change;
not enough to publish quality claims. Condition A is not "bad planning" — its prose is
reasonable. It is **unlintable**, which is a different and narrower finding.
