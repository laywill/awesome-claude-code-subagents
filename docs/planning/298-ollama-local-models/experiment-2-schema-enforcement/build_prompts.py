"""Build the three prompt conditions from the agent .md (prototype of export.py)."""
import re, json, pathlib

SRC = pathlib.Path(r"c:/Users/laywi/Documents/repos/awesome-claude-code-subagents/categories/05-planning-and-estimation/task-planner.md")
raw = SRC.read_text(encoding="utf-8")

# 1. strip YAML frontmatter
body = re.sub(r"^---\n.*?\n---\n", "", raw, flags=re.S)

# 2. capture the payload schema from the Communication Protocol BEFORE cutting it
blocks = re.findall(r"```json\n(.*?)\n```", body, flags=re.S)
payload = None
for b in blocks:
    try: d = json.loads(b)
    except Exception: continue
    if d.get("request_type") == "task_breakdown":
        payload = d["payload"]; break
assert payload, "task_breakdown payload not found"

# 3. cut Communication Protocol -> EOF
stripped = body.split("\n## Communication Protocol")[0].rstrip()

EPILOGUE = """

You have no tools. You cannot read files, run commands, or query other agents. Work only
from what the user gives you in the conversation. If you need to see a file, ask for it.
Answer directly - do not emit status objects or plans to hand off work."""

# Condition A: stripped + epilogue (current strategy-doc recommendation)
A = stripped + EPILOGUE

# Condition B: A + the payload schema promoted into an explicit output contract ("unwrap")
SCHEMA_INSTRUCTION = """

## Required output format

Reply with a single JSON object and nothing else. No prose before or after it, no markdown
code fences. It must have exactly this shape:

```json
%s
```

Field rules:
- "total_tasks" must equal the number of entries in "tasks".
- Every task "id" must be unique.
- Every string in a task's "dependencies" must be the "id" of another task in "tasks".
- "complexity" must be exactly one of: trivial, small, medium, large, spike.
- "acceptance_criteria" and "dependencies" are arrays of strings (may be empty).
- "workstream" must be one of the names listed in the top-level "workstreams" array.
""" % json.dumps(payload, indent=2)

B = stripped + SCHEMA_INSTRUCTION + EPILOGUE

pathlib.Path("prompt_A.txt").write_text(A, encoding="utf-8")
pathlib.Path("prompt_B.txt").write_text(B, encoding="utf-8")

# Condition C uses prompt B + an Ollama JSON Schema for constrained decoding
FORMAT_SCHEMA = {
  "type": "object",
  "properties": {
    "epic": {"type": "string"},
    "workstreams": {"type": "array", "items": {"type": "string"}},
    "total_tasks": {"type": "integer"},
    "critical_path_length": {"type": "integer"},
    "parallel_tracks": {"type": "integer"},
    "tasks": {"type": "array", "items": {
        "type": "object",
        "properties": {
          "id": {"type": "string"},
          "title": {"type": "string"},
          "workstream": {"type": "string"},
          "scope": {"type": "string"},
          "acceptance_criteria": {"type": "array", "items": {"type": "string"}},
          "dependencies": {"type": "array", "items": {"type": "string"}},
          "complexity": {"type": "string", "enum": ["trivial","small","medium","large","spike"]},
          "notes": {"type": "string"}
        },
        "required": ["id","title","workstream","scope","acceptance_criteria",
                     "dependencies","complexity","notes"]
    }}
  },
  "required": ["epic","workstreams","total_tasks","tasks"]
}
pathlib.Path("format_schema.json").write_text(json.dumps(FORMAT_SCHEMA, indent=2), encoding="utf-8")

for n, p in (("A", A), ("B", B)):
    print("prompt_%s.txt  %d words" % (n, len(p.split())))
print("payload keys:", list(payload))
