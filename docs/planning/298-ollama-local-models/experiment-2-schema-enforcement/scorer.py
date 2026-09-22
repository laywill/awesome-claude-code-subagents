"""Score task-planner outputs. Checks split into those a JSON Schema CAN express
(constrained decoding should make them free) and those it structurally CANNOT
(cross-field / graph properties -- these need a validator hook)."""
import json, re, pathlib, collections

VALID_COMPLEXITY = {"trivial","small","medium","large","spike"}
TASK_KEYS = ["id","title","workstream","scope","acceptance_criteria",
             "dependencies","complexity","notes"]

def extract(text):
    """Recover JSON from raw model output: fences, prose wrappers, trailing junk."""
    if not text or not text.strip(): return None
    t = text.strip()
    m = re.search(r"```(?:json)?\s*\n(.*?)```", t, flags=re.S)
    if m: t = m.group(1).strip()
    try: return json.loads(t)
    except Exception: pass
    i, j = t.find("{"), t.rfind("}")
    if i != -1 and j > i:
        try: return json.loads(t[i:j+1])
        except Exception: return None
    return None

def acyclic(tasks):
    g = {t.get("id"): [d for d in t.get("dependencies",[]) if isinstance(d,str)]
         for t in tasks if isinstance(t, dict)}
    colour = {}
    def visit(n):
        if colour.get(n) == 1: return False
        if colour.get(n) == 2: return True
        colour[n] = 1
        for m in g.get(n, []):
            if m in g and not visit(m): return False
        colour[n] = 2
        return True
    return all(visit(n) for n in g)

def score(rec):
    raw = rec["response"] or rec.get("thinking") or ""
    d = extract(raw)
    r = {"cond": rec["cond"], "seed": rec["seed"], "elapsed": rec["elapsed"],
         "eval_count": rec["eval_count"], "chars": len(raw)}

    # --- clean parse: did it emit bare JSON with no wrapper? (schema-expressible)
    r["parses"] = d is not None
    r["clean_json"] = False
    if raw.strip():
        try:
            json.loads(raw.strip()); r["clean_json"] = True
        except Exception: pass
    if not r["parses"]:
        for k in ("top_keys","tasks_array","task_keys","complexity_enum","array_types",
                  "total_matches","ids_unique","deps_resolve","ws_valid","dag"):
            r[k] = False
        r["n_tasks"] = 0
        return r

    tasks = d.get("tasks") if isinstance(d, dict) else None
    tasks = tasks if isinstance(tasks, list) else []
    dicts = [t for t in tasks if isinstance(t, dict)]
    r["n_tasks"] = len(tasks)

    # ---- SCHEMA-EXPRESSIBLE ----
    r["top_keys"] = isinstance(d, dict) and all(
        k in d for k in ("epic","workstreams","total_tasks","tasks"))
    r["tasks_array"] = len(tasks) > 0 and len(dicts) == len(tasks)
    r["task_keys"] = bool(dicts) and all(
        all(k in t for k in TASK_KEYS) for t in dicts)
    r["complexity_enum"] = bool(dicts) and all(
        t.get("complexity") in VALID_COMPLEXITY for t in dicts)
    r["array_types"] = bool(dicts) and all(
        isinstance(t.get("acceptance_criteria"), list)
        and isinstance(t.get("dependencies"), list)
        and all(isinstance(x, str) for x in t.get("acceptance_criteria", []))
        and all(isinstance(x, str) for x in t.get("dependencies", []))
        for t in dicts)

    # ---- NOT SCHEMA-EXPRESSIBLE (needs a validator hook) ----
    ids = [t.get("id") for t in dicts]
    r["total_matches"] = d.get("total_tasks") == len(tasks)
    r["ids_unique"] = bool(ids) and len(set(ids)) == len(ids)
    idset = set(ids)
    r["deps_resolve"] = bool(dicts) and all(
        all(dep in idset for dep in t.get("dependencies", []) if isinstance(dep, str))
        for t in dicts)
    ws = d.get("workstreams")
    r["ws_valid"] = isinstance(ws, list) and bool(dicts) and all(
        t.get("workstream") in ws for t in dicts)
    r["dag"] = bool(dicts) and acyclic(dicts)
    return r

SCHEMA = ["clean_json","top_keys","tasks_array","task_keys","complexity_enum","array_types"]
HOOK   = ["total_matches","ids_unique","deps_resolve","ws_valid","dag"]

if __name__ == "__main__":
    rows = [score(json.loads(f.read_text(encoding="utf-8")))
            for f in sorted(pathlib.Path("out").glob("*.json"))]
    json.dump(rows, open("scores.json","w"), indent=2)

    by = collections.defaultdict(list)
    for r in rows: by[r["cond"]].append(r)

    def pct(rs, k): return "%d/%d" % (sum(1 for r in rs if r[k]), len(rs))
    print("n per condition:", {c: len(v) for c, v in sorted(by.items())})
    print()
    hdr = ["check"] + sorted(by)
    print("%-18s %s" % ("SCHEMA-EXPRESSIBLE", "  ".join("%6s" % c for c in sorted(by))))
    for k in ["parses"] + SCHEMA:
        print("%-18s %s" % (k, "  ".join("%6s" % pct(by[c], k) for c in sorted(by))))
    print()
    print("%-18s %s" % ("NEEDS-A-HOOK", ""))
    for k in HOOK:
        print("%-18s %s" % (k, "  ".join("%6s" % pct(by[c], k) for c in sorted(by))))
    print()
    for k in ("elapsed","eval_count","n_tasks"):
        print("%-18s %s" % ("mean "+k, "  ".join(
            "%6.1f" % (sum(r[k] or 0 for r in by[c])/len(by[c])) for c in sorted(by))))
    print()
    print("%-18s %s" % ("ALL SCHEMA pass", "  ".join("%6s" % (
        "%d/%d" % (sum(1 for r in by[c] if all(r[k] for k in SCHEMA)), len(by[c])))
        for c in sorted(by))))
    print("%-18s %s" % ("ALL HOOK pass", "  ".join("%6s" % (
        "%d/%d" % (sum(1 for r in by[c] if all(r[k] for k in HOOK)), len(by[c])))
        for c in sorted(by))))
    print("%-18s %s" % ("FULLY VALID", "  ".join("%6s" % (
        "%d/%d" % (sum(1 for r in by[c] if all(r[k] for k in SCHEMA+HOOK)), len(by[c])))
        for c in sorted(by))))
