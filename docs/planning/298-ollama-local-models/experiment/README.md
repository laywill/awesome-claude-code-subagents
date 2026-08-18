# Experiment: does an agent definition improve a small local model?

Reproduces the A/B/C test cited in `../notes.md` §2 and `../local-model-strategy.md`.

## Method

- **Agent under test:** `categories/03-analysis-and-review/code-reviewer.md`
- **Task:** `task.txt` — a 12-line Python function with 5 seeded defects:
  1. SQL injection via string concatenation
  2. Off-by-one — `range(len(rows) + 1)`
  3. Bare `except: pass`
  4. Connection never closed
  5. Magic column index `rows[i][3]`
- **Conditions:**
  - `A_none` — no system prompt (baseline)
  - `B_full` — agent file, YAML frontmatter stripped, everything else kept
  - `C_stripped` — B minus `## Communication Protocol` onwards, minus "Query context manager"
- **Settings:** `temperature=0.2`, `seed=42`, `num_ctx=8192`, Ollama 0.32.13

## Run

```bash
python run.py gemma3:4b            # add more model tags as extra args
```

Outputs are written as `out_<model>_<condition>.md` with a metadata comment on line 1.
The runner skips conditions whose output file already exists, so it resumes safely —
generation takes ~3-4 min per condition on a 4B model.

## Results (gemma3:4b)

| condition | prompt tok | output tok | secs | defects found |
|---|---|---|---|---|
| A_none | 162 | 1206 | 259 | 4/5 (missed off-by-one) |
| B_full | 1505 | 1145 | 180 | 4/5 (missed unclosed connection) |
| C_stripped | 707 | 1339 | 210 | **5/5** |

**C beat B on coverage using less than half the prompt.** See `../notes.md` for the full
reading, including the significant caveat that C also recommended an f-string SQL query —
re-introducing the injection it had flagged as critical two sections earlier.

## Limitations

n=1 agent, n=1 task, n=1 model, single seed. Directional signal only. A real harness needs
multiple agents, multiple seeded-defect fixtures, several models, and repeated seeds.
