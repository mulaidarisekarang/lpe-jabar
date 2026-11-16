"""Tarik data terbaru dari WebAPI BPS -> gabungkan ke data.json.
Butuh env BPS_API_KEY (gratis: https://webapi.bps.go.id/developer/)."""
import json, os, re, sys, datetime, urllib.request
sys.path.insert(0, os.path.dirname(__file__))
from excel_to_json import pkey

KEY = os.environ["BPS_API_KEY"]
ROOT = os.path.join(os.path.dirname(__file__), "..")
cfg = json.load(open(os.path.join(ROOT, "scripts/bps_vars.json")))
data = json.load(open(os.path.join(ROOT, "data.json")))
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())

def fetch(var):
    url = (f"https://webapi.bps.go.id/v1/api/list/model/data/lang/ind/domain/{cfg['domain']}"
           f"/var/{var}/key/{KEY}/")
    return json.load(urllib.request.urlopen(url, timeout=60))

def parse(res):
    """Balikkan datacontent BPS -> {nama_baris: {period_key: nilai}}"""
    var = str(res["var"][0]["val"])
    vervar = {str(v["val"]): v["label"] for v in res["vervar"]}
    turvar = {str(v["val"]): v["label"] for v in res.get("turvar", [])} or {"0": ""}
    tahun = {str(v["val"]): int(v["label"]) for v in res["tahun"]}
    turth = {str(v["val"]): v["label"] for v in res["turtahun"]}
    out = {}
    for k, val in res["datacontent"].items():
        for vv, vl in vervar.items():
            if not k.startswith(vv + var): continue
            rest = k[len(vv) + len(var):]
            for tv in turvar:
                if not rest.startswith(tv): continue
                for th, yr in tahun.items():
                    if rest[len(tv):].startswith(th):
                        tt = rest[len(tv) + len(th):]
                        if tt in turth:
                            pk, _ = pkey(f"{yr} {turth[tt]}", yr)
                            if pk and isinstance(val, (int, float)):
                                out.setdefault(vl, {})[pk] = round(val, 2)
    return out

def order(k): y, q = k.split("-"); return (int(y), 5 if q == "T" else int(q[1]))

changed = 0
for name, c in cfg["datasets"].items():
    if not c["var"]: continue
    grp, mode = name.split(".")
    blk = data[grp][mode]
    fresh = parse(fetch(c["var"]))
    lookup = {norm(r["nama"]): r for r in blk["rows"]}
    cur = dict(zip(blk["periods"], range(len(blk["periods"]))))
    newp = sorted({p for d in fresh.values() for p in d} | set(blk["periods"]), key=order)
    for r in blk["rows"]:
        old = dict(zip(blk["periods"], r["v"]))
        for lab, d in fresh.items():
            if norm(lab) == norm(r["nama"]):
                for p, v in d.items():
                    if old.get(p) != v: changed += 1
                old.update(d)
        r["v"] = [old.get(p) for p in newp]
    blk["periods"] = newp

if changed:
    data["updated"] = datetime.date.today().isoformat()
    json.dump(data, open(os.path.join(ROOT, "data.json"), "w"), ensure_ascii=False, separators=(",", ":"))
print(f"{changed} nilai diperbarui")
