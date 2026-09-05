"""The operator board — `python papanoel.py serve` then open the browser.

A local web app over the SAME store and gates as the CLI: every action goes
through the state machine, so the board can't do anything the gates forbid —
a refused action shows the gate's own message. Binds to 127.0.0.1 only;
nothing is exposed to the network. Later, Mrs. Claus's inbound webhook
mounts on this same server.
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import store
import reservation_agent
import logistics_agent
import operator_review as operator_lane
import content_agent
import health as health_lane
from rates import RATE_CARD
from zones import zone_map

PORT_DEFAULT = 8225


def _content_adapter():
    if os.environ.get("OPENAI_API_KEY"):
        from openai_adapter import OpenAIContentAdapter
        return OpenAIContentAdapter()
    return None


def _drafts():
    out = []
    qd = content_agent.QUEUE_DIR
    if os.path.isdir(qd):
        for rid in sorted(os.listdir(qd)):
            p = os.path.join(qd, rid, "draft.json")
            if os.path.exists(p):
                with open(p, encoding="utf-8") as f:
                    out.append(json.load(f))
    return out


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/":
            self._send(200, PAGE.encode("utf-8"), "text/html")
        elif self.path == "/api/state":
            records = store.load()
            for d in sorted({r["date"] for r in records if r.get("date")}):
                logistics_agent.check_date(records, d)
            store.save(records)
            self._send(200, {
                "reservations": records,
                "drafts": _drafts(),
                "rates": {k: v["label_en"] for k, v in RATE_CARD.items()},
                "zones": zone_map(),
                "openai": bool(os.environ.get("OPENAI_API_KEY")),
            })
        elif self.path == "/api/health":
            records = store.load()
            self._send(200, health_lane.run(records))
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(n).decode("utf-8")) if n else {}
        except ValueError:
            return self._send(400, {"error": "bad json"})
        records = store.load()
        try:
            if self.path == "/api/new":
                rec = reservation_agent.create(records, **{
                    k: v for k, v in body.items()
                    if k in reservation_agent.FIELDS and v not in (None, "")})
                out = {"created": rec["id"], "status": rec["status"]}
            elif self.path == "/api/update":
                rec = reservation_agent.update(records, body.pop("id"), **{
                    k: v for k, v in body.items()
                    if k in reservation_agent.FIELDS and v not in (None, "")})
                out = {"updated": rec["id"], "status": rec["status"]}
            elif self.path == "/api/verify-deposit":
                rec = operator_lane.verify_deposit(
                    records, body["id"], body.get("amount"), body.get("memo"))
                reservation_agent.advance(records, body["id"])
                out = {"status": rec["status"], "deposit": rec["deposit"]}
            elif self.path == "/api/approve":
                rec = operator_lane.approve(records, body["id"])
                out = {"confirmed": rec["id"]}
            elif self.path == "/api/reject":
                rec = operator_lane.reject(records, body["id"], body.get("reason", ""))
                out = {"id": rec["id"], "status": rec["status"]}
            elif self.path == "/api/complete":
                rec = operator_lane.complete(records, body["id"])
                out = {"id": rec["id"], "status": rec["status"]}
            elif self.path == "/api/content":
                made = content_agent.draft_for_all(records, _content_adapter())
                out = {"drafts_made": len(made)}
            elif self.path == "/api/approve-post":
                out = content_agent.approve_draft(body["id"], store.OPERATOR)
            else:
                return self._send(404, {"error": "not found"})
        except (store.TransitionError, content_agent.ContentGateError) as e:
            store.save(records)
            return self._send(409, {"refused": str(e)})
        except KeyError as e:
            return self._send(400, {"error": "missing field %s" % e})
        store.save(records)
        self._send(200, out)


def serve(port=PORT_DEFAULT):
    srv = HTTPServer(("127.0.0.1", port), Handler)
    print("Operator board: http://127.0.0.1:%d  (Ctrl+C to stop)" % port)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


PAGE = r"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Papa Noel Operator Board</title>
<style>
:root{--bg:#141816;--card:#1B211E;--ink:#E8EAE6;--mut:#98A29C;--line:#3A423E;
--pine:#4CAF82;--red:#E06055;--gold:#D8A93F;--chip:#232A26}
body{background:var(--bg);color:var(--ink);font:14px/1.45 "Segoe UI",system-ui,sans-serif;margin:0;padding:18px}
h1{font-size:20px;margin:0 0 2px}.mut{color:var(--mut)}
.top{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:14px}
.badge{border:1px solid var(--line);border-radius:20px;padding:3px 12px;font-size:12px;color:var(--mut)}
.badge.on{border-color:var(--pine);color:var(--pine)}
button{background:var(--chip);color:var(--ink);border:1px solid var(--line);border-radius:6px;
padding:6px 12px;cursor:pointer;font-size:13px}
button:hover{border-color:var(--pine)}
button.primary{background:var(--pine);border-color:var(--pine);color:#10231A;font-weight:600}
button.danger{border-color:var(--red);color:var(--red)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px}
.col h2{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--mut);margin:0 0 8px}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 12px;margin-bottom:10px}
.card b{font-size:14px}.row{color:var(--mut);font-size:12.5px;margin:2px 0}
.lg-ok{color:var(--pine)}.lg-tight{color:var(--gold)}.lg-impossible{color:var(--red)}
.dep-verified{color:var(--pine)}.dep-unpaid{color:var(--red)}.dep-claimed{color:var(--gold)}
.acts{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}
form#new{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px;
display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:8px;margin-bottom:16px}
input,select{background:var(--chip);color:var(--ink);border:1px solid var(--line);border-radius:6px;padding:6px 8px;font-size:13px}
#toast{position:fixed;bottom:16px;left:50%;transform:translateX(-50%);background:var(--card);
border:1px solid var(--line);border-radius:8px;padding:10px 16px;max-width:80%;display:none}
#toast.err{border-color:var(--red)}
.draft{border-left:3px solid var(--gold);padding-left:10px}
.draft.approved{border-left-color:var(--pine)}
.cap{font-size:12.5px;margin:4px 0;color:var(--ink)}
</style></head><body>
<div class="top">
  <div><h1>🎅 Papa Noel Operator Board</h1><div class="mut">every action runs through the gates — refused means the gate spoke</div></div>
  <div style="display:flex;gap:8px;align-items:center">
    <span id="oai" class="badge">OpenAI: off</span>
    <button onclick="runContent()">Draft content</button>
    <button onclick="health()">Health check</button>
  </div>
</div>
<form id="new" onsubmit="return newRes(event)">
  <input name="client_name" placeholder="Client name" required>
  <input name="phone" placeholder="Phone" required>
  <select name="package" id="pkg" required></select>
  <input name="date" type="date" required>
  <input name="start_time" type="time" required>
  <select name="zone" id="zone" required></select>
  <input name="duration_min" type="number" placeholder="Minutes" value="60">
  <input name="address" placeholder="Address (for review)">
  <input name="guest_count" type="number" placeholder="Guests">
  <button class="primary">Add booking</button>
</form>
<div class="grid" id="cols"></div>
<h2 style="font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--mut)">Content queue</h2>
<div id="drafts" class="grid"></div>
<div id="toast"></div>
<script>
let S={reservations:[],drafts:[],rates:{},zones:{}};
const COLS=[["inquiry","Inquiries"],["hold","Holds"],["pending_review","Your review"],["confirmed","Confirmed"],["completed","Done"]];
function toast(m,err){const t=document.getElementById('toast');t.textContent=m;
t.className=err?'err':'';t.style.display='block';setTimeout(()=>t.style.display='none',4200)}
async function api(p,b){const r=await fetch(p,b?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)}:undefined);
const j=await r.json();if(!r.ok){toast(j.refused||j.error||'error',true);throw j}return j}
async function load(){S=await api('/api/state');
document.getElementById('oai').textContent='OpenAI: '+(S.openai?'live':'off');
document.getElementById('oai').className='badge'+(S.openai?' on':'');
const pk=document.getElementById('pkg');pk.innerHTML=Object.entries(S.rates).map(([k,v])=>`<option value="${k}">${v}</option>`).join('');
const zn=document.getElementById('zone');zn.innerHTML=Object.entries(S.zones).map(([k,v])=>`<option value="${k}">${v}</option>`).join('');
render()}
function card(r){
const lg=r.logistics?`<div class="row lg-${r.logistics.result}">route: ${r.logistics.result}${r.logistics.estimates?' (est.)':''}</div>`:'';
const dep=`<span class="dep-${r.deposit.status}">deposit ${r.deposit.status}</span>`;
let acts='';
if(['inquiry','hold'].includes(r.status)){
 acts+=`<button onclick="verify('${r.id}')">Verify deposit</button>`;
 if(!r.address)acts+=`<button onclick="fill('${r.id}')">Add address/guests</button>`;}
if(r.status==='pending_review')acts+=`<button class="primary" onclick="act('approve','${r.id}')">Approve ✓</button>
<button class="danger" onclick="reject('${r.id}')">Reject</button>`;
if(r.status==='confirmed')acts+=`<button onclick="act('complete','${r.id}')">Mark done</button>`;
return `<div class="card"><b>${r.client_name||'—'}</b>
<div class="row">${r.date||'no date'} · ${r.start_time||''} · ${S.zones[r.zone]||r.zone||'no zone'}</div>
<div class="row">${S.rates[r.package]||r.package||'no package'} · $${r.price_quoted??'—'}</div>
<div class="row">${dep}</div>${lg}<div class="acts">${acts}</div></div>`}
function render(){
document.getElementById('cols').innerHTML=COLS.map(([s,t])=>{
const rs=S.reservations.filter(r=>r.status===s);
return `<div class="col"><h2>${t} (${rs.length})</h2>${rs.map(card).join('')||'<div class="mut">—</div>'}</div>`}).join('');
document.getElementById('drafts').innerHTML=S.drafts.map(d=>`<div class="card draft ${d.status}">
<b>${d.status.toUpperCase()}</b> · ${d.reservation}
<div class="cap">EN: ${d.caption_en}</div><div class="cap">ES: ${d.caption_es}</div>
${d.status==='draft'?`<div class="acts"><button class="primary" onclick="approvePost('${d.reservation}')">Approve post</button></div>`:''}
</div>`).join('')||'<div class="mut">no drafts — content is made from confirmed bookings only</div>'}
async function newRes(e){e.preventDefault();const f=Object.fromEntries(new FormData(e.target));
['duration_min','guest_count'].forEach(k=>{if(f[k])f[k]=+f[k];else delete f[k]});
await api('/api/new',f);e.target.reset();toast('booking added');load();return false}
async function act(a,id){await api('/api/'+a,{id});toast(a+' done');load()}
async function verify(id){const amount=+prompt('Zelle amount received?')||null;
const memo=prompt('Memo (event date + client name)?')||null;
await api('/api/verify-deposit',{id,amount,memo});toast('deposit verified');load()}
async function reject(id){const reason=prompt('Reason?')||'';await api('/api/reject',{id,reason});load()}
async function fill(id){const address=prompt('Full address?');const guest_count=+prompt('Guests?')||null;
await api('/api/update',{id,address,guest_count});load()}
async function runContent(){const r=await api('/api/content',{});toast(r.drafts_made+' draft(s) made');load()}
async function approvePost(id){await api('/api/approve-post',{id});toast('post approved — you publish it');load()}
async function health(){const h=await api('/api/health');
toast(h.needs_operator?'needs you: '+(h.stale_holds.length+' stale holds, '+h.route_regressions.length+' route issues, '+h.drafts_pending_approval.length+' drafts waiting'):'all clean — logged')}
load();
</script></body></html>"""


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT_DEFAULT
    serve(port)
