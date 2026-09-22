import json,urllib.request
schema={"type":"object","properties":{
 "year":{"type":"integer"},"month":{"type":"integer"},"day":{"type":"integer"},
 "vendor":{"type":"string"},"document_type":{"type":"string"},
 "confidence":{"type":"string","enum":["high","medium","low"]}},
 "required":["year","month","day","vendor","document_type","confidence"]}
res=[]
for i in range(3):
    body={"model":"gemma3:4b","stream":False,"options":{"seed":i},
      "prompt":"Invoice from Acme Widgets Ltd dated 3rd March 2024. What is this document?",
      "format":schema}
    r=json.load(urllib.request.urlopen(urllib.request.Request(
      "http://localhost:11434/api/generate",json.dumps(body).encode(),
      {"Content-Type":"application/json"})))
    d=json.loads(r["response"])
    s="%04d-%02d-%02d"%(d["year"],d["month"],d["day"])
    res.append(s); print("int-fields",i,s,flush=True)
json.dump(res,open("intfields_probe.json","w"))
