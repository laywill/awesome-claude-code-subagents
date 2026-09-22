"""Is C's content as substantive as B's, or has the grammar hollowed it out?"""
import json, glob, re, statistics as st
from scorer import extract

DOMAIN = ["saml","idp","metadata","jit","provision","tenant","organisation","organization",
          "session","drf","token","mobile","xml","django","migration","admin","password",
          "sso","assertion","acs","certificate"]

def load(c):
    out=[]
    for f in sorted(glob.glob("out/%s_*.json"%c)):
        d=extract(json.load(open(f))["response"])
        if isinstance(d,dict) and isinstance(d.get("tasks"),list): out.append(d)
    return out

for c in ("B","C"):
    ds=load(c); tasks=[t for d in ds for t in d["tasks"] if isinstance(t,dict)]
    ac=[a for t in tasks for a in t.get("acceptance_criteria",[])]
    scopes=[t.get("scope","") for t in tasks]
    titles=[t.get("title","") for t in tasks]
    blob=" ".join(scopes+titles+ac).lower()
    empty_ac=sum(1 for t in tasks if not t.get("acceptance_criteria"))
    nodep=sum(1 for t in tasks if not t.get("dependencies"))
    print("--- %s  (n_docs=%d, n_tasks=%d)" % (c,len(ds),len(tasks)))
    print("  mean words/scope      %.1f" % st.mean(len(s.split()) for s in scopes))
    print("  mean words/criterion  %.1f" % st.mean(len(a.split()) for a in ac))
    print("  mean criteria/task    %.2f" % (len(ac)/len(tasks)))
    print("  tasks w/ 0 criteria   %d (%.0f%%)" % (empty_ac,100*empty_ac/len(tasks)))
    print("  tasks w/ 0 deps       %d (%.0f%%)" % (nodep,100*nodep/len(tasks)))
    print("  distinct titles       %d / %d" % (len(set(titles)),len(titles)))
    print("  domain terms hit      %d / %d" % (sum(1 for k in DOMAIN if k in blob),len(DOMAIN)))
    print("  complexity spread     %s" % json.dumps(
        {k:sum(1 for t in tasks if t.get("complexity")==k)
         for k in ("trivial","small","medium","large","spike")}))
    dep_edges=sum(len(t.get("dependencies",[])) for t in tasks)
    print("  dep edges/task        %.2f" % (dep_edges/len(tasks)))
