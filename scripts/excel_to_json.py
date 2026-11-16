"""Konversi Excel LPE Jabar -> data.json (jalankan sekali untuk data awal)."""
import json, re, sys, datetime
from openpyxl import load_workbook

ROM = {"I": 1, "II": 2, "III": 3, "IV": 4}
def num(v):
    return round(float(v), 2) if isinstance(v, (int, float)) else None

def pkey(label, year):
    """'Triw II-2019 (q-to-q)' / '2024 Triwulan I' / 'Tahunan' -> (key, year)"""
    s = str(label)
    y = re.search(r"(20\d\d)", s)
    year = int(y.group(1)) if y else year
    if "ahunan" in s: return f"{year}-T", year
    q = re.search(r"\b(IV|III|II|I)\b", s)
    return (f"{year}-Q{ROM[q.group(1)]}", year) if q else (None, year)

def main_sheet(ws):
    rows = list(ws.iter_rows(values_only=True))
    keys, year = [], None
    for c in rows[1][2:]:
        if c is None: keys.append(None); continue
        k, year = pkey(c, year); keys.append(k)
    out = []
    for r in rows[2:]:
        if r[1] is None: break
        out.append({"kode": str(r[0] or ""), "nama": str(r[1]).strip(),
                    "v": [num(x) for x in r[2:2 + len(keys)]]})
        if "PDRB" in str(r[1]): break
    keep = [i for i, k in enumerate(keys) if k]
    for r in out: r["v"] = [r["v"][i] if i < len(r["v"]) else None for i in keep]
    return {"periods": [keys[i] for i in keep], "rows": out}

def kab_sheet(ws):
    rows = list(ws.iter_rows(values_only=True))
    keys, year = [], None
    for c in rows[2][1:]:
        if c is None or "Keterangan" in str(c): break
        k, year = pkey(c, year); keys.append(k)
    out = []
    for r in rows[3:]:
        if r[0] is None: break
        out.append({"kode": "", "nama": str(r[0]).strip(),
                    "v": [num(x) for x in r[1:1 + len(keys)]]})
    return {"periods": keys, "rows": out}

def build(path):
    wb = load_workbook(path, read_only=True, data_only=True)
    return {
        "updated": datetime.date.today().isoformat(),
        "sumber": "BPS Provinsi Jawa Barat (jabar.bps.go.id)",
        "lu": {"q": main_sheet(wb["Q-to-Q (Lapangan Usaha)"]), "y": main_sheet(wb["Y-to-Y (Lapangan Usaha)"])},
        "pg": {"q": main_sheet(wb["Q-to-Q (Pengeluaran)"]), "y": main_sheet(wb["Y-to-Y (Pengeluaran)"])},
        "kab": {"q": kab_sheet(wb["Q-to-Q KabupatenKota"]), "y": kab_sheet(wb["Y-to-Y KabupatenKota"])},
    }

if __name__ == "__main__":
    d = build(sys.argv[1])
    json.dump(d, open(sys.argv[2] if len(sys.argv) > 2 else "data.json", "w"), ensure_ascii=False, separators=(",", ":"))
    for g in ("lu", "pg", "kab"):
        for m in "qy":
            s = d[g][m]; print(g, m, len(s["rows"]), "baris", len(s["periods"]), "periode", s["periods"][-3:])
