import sys, json, tempfile, importlib
from datetime import date
from pathlib import Path
root = sys.argv[1]; sys.path.insert(0, root)
from fastapi.testclient import TestClient
from todo_api.app import create_app
c = TestClient(create_app(today=lambda: date(2026,12,10), db_path=Path(tempfile.mkdtemp())/"t.db"))
reqs = [("post","/todos",{"title":"a"}),("post","/todos",{"title":"  b  ","due_date":"2026-12-01"}),
 ("post","/todos",{"title":""}),("post","/todos",{"title":"x"*100000}),("post","/todos",{"title":"\ud800"}),
 ("post","/todos",{"title":"c","due_date":"20261201"}),("post","/todos",{}),("post","/todos",{"title":1}),
 ("post","/todos/1/complete",None),("post","/todos/99999999999999999999/complete",None),("post","/todos/-1/complete",None),
 ("get","/todos",None),("get","/todos?overdue=true",None),("get","/todos?overdue=maybe",None)]
out=[]
for m,p,b in reqs:
    try:
        r = c.post(p,json=b) if m=="post" else c.get(p)
        body = r.json()
        def strip(x):
            if isinstance(x,dict): return {k:v for k,v in x.items() if k!="priority"}
            if isinstance(x,list): return [strip(i) for i in x]
            return x
        out.append((p, r.status_code, json.dumps(strip(body),ensure_ascii=False)[:200]))
    except Exception as e: out.append((p,"EXC",type(e).__name__))
print(json.dumps(out,ensure_ascii=False))
