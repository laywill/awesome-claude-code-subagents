import json, urllib.request, pathlib, sys, time

MODEL = "gemma3:4b"
N = 10
epic = pathlib.Path("epic.txt").read_text(encoding="utf-8")
prompts = {"A": pathlib.Path("prompt_A.txt").read_text(encoding="utf-8"),
           "B": pathlib.Path("prompt_B.txt").read_text(encoding="utf-8")}
prompts["C"] = prompts["B"]
fmt = json.loads(pathlib.Path("format_schema.json").read_text(encoding="utf-8"))
out = pathlib.Path("out")

def call(system, prompt, seed, schema=None):
    body = {"model": MODEL, "stream": False, "system": system, "prompt": prompt,
            "options": {"seed": seed, "temperature": 0.7, "num_ctx": 4096}}
    if schema: body["format"] = schema
    last = None
    for attempt in range(5):
        try:
            req = urllib.request.Request("http://localhost:11434/api/generate",
                    json.dumps(body).encode(), {"Content-Type": "application/json"})
            return json.load(urllib.request.urlopen(req, timeout=1800))
        except Exception as e:                    # transient 500s on model load
            last = e
            print("  retry %d after %r" % (attempt, e), flush=True)
            time.sleep(10 * (attempt + 1))
    raise last

for cond in ("A", "B", "C"):
    for seed in range(N):
        f = out / ("%s_%02d.json" % (cond, seed))
        if f.exists():
            continue                      # resume-safe
        t = time.time()
        r = call(prompts[cond], epic, seed, fmt if cond == "C" else None)
        rec = {"cond": cond, "seed": seed, "elapsed": round(time.time()-t, 1),
               "response": r.get("response", ""), "thinking": r.get("thinking", ""),
               "prompt_eval_count": r.get("prompt_eval_count"),
               "eval_count": r.get("eval_count"),
               "done_reason": r.get("done_reason")}
        f.write_text(json.dumps(rec), encoding="utf-8")
        print("%s seed=%d %.0fs %d tok %s" % (cond, seed, rec["elapsed"],
              rec["eval_count"] or 0, rec["done_reason"]), flush=True)
print("DONE")
