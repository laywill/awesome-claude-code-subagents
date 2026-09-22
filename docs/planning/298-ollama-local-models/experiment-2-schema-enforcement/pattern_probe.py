import json,urllib.request,time,sys
base={"date":{"type":"string"},"vendor":{"type":"string"},
 "document_type":{"type":"string"},
 "confidence":{"type":"string","enum":["high","medium","low"]}}
def run(pattern,n=3):
    props=json.loads(json.dumps(base))
    if pattern: props["date"]["pattern"]="^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
    schema={"type":"object","properties":props,"required":list(props)}
    out=[]
    for i in range(n):
        body={"model":"gemma3:4b","stream":False,"options":{"seed":i},
          "prompt":"Invoice from Acme Widgets Ltd dated 3rd March 2024. What is this document?",
          "format":schema}
        r=json.load(urllib.request.urlopen(urllib.request.Request(
          "http://localhost:11434/api/generate",json.dumps(body).encode(),
          {"Content-Type":"application/json"})))
        try: d=json.loads(r["response"])["date"]
        except Exception as e: d="PARSE_FAIL:"+r["response"][:60]
        out.append(d); print(("pattern " if pattern else "no-pattern "),i,repr(d),flush=True)
    return out
print("=== WITH pattern");  a=run(True)
print("=== WITHOUT pattern"); b=run(False)
json.dump({"with_pattern":a,"without_pattern":b},open("pattern_probe.json","w"),indent=2)
