import json, urllib.request, sys, time, os
SP = os.path.dirname(os.path.abspath(__file__))
task = open(os.path.join(SP,"task.txt"), encoding="utf-8").read()
conds = {
 "A_none": None,
 "B_full": open(os.path.join(SP,"sys_B_full.txt"), encoding="utf-8").read(),
 "C_stripped": open(os.path.join(SP,"sys_C_stripped.txt"), encoding="utf-8").read(),
}
models = sys.argv[1:] or ["gemma3:4b"]
for m in models:
    for cname, sp in conds.items():
        fn0 = os.path.join(SP, f"out_{m.replace(':','-').replace('/','-')}_{cname}.md")
        if os.path.exists(fn0):
            print(f"SKIP {m} {cname}", flush=True); continue
        msgs = ([{"role":"system","content":sp}] if sp else []) + [{"role":"user","content":task}]
        body = json.dumps({"model":m,"messages":msgs,"stream":False,
                           "options":{"temperature":0.2,"seed":42,"num_ctx":8192}}).encode()
        req = urllib.request.Request("http://localhost:11434/api/chat", body,
                                     {"Content-Type":"application/json"})
        t0=time.time()
        try:
            r = json.load(urllib.request.urlopen(req, timeout=900))
            out = r["message"]["content"]
            meta = f"eval_tokens={r.get('eval_count')} prompt_tokens={r.get('prompt_eval_count')} secs={time.time()-t0:.1f}"
        except Exception as e:
            out = f"ERROR: {e}"; meta = f"secs={time.time()-t0:.1f}"
        fn = os.path.join(SP, f"out_{m.replace(':','-').replace('/','-')}_{cname}.md")
        open(fn,"w",encoding="utf-8").write(f"<!-- {m} | {cname} | {meta} -->\n\n{out}")
        print(f"DONE {m} {cname} :: {meta}", flush=True)
