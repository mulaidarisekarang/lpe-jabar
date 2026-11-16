# Dashboard LPE Jawa Barat

Isi: `index.html` (dashboard), `data.json` (data dari Excel Anda), `scripts/` (konversi + updater BPS), `.github/workflows/update.yml` (jadwal harian).

## Coba lokal
    python3 -m http.server 8000   # lalu buka http://localhost:8000

## Auto-update (GitHub Pages)
1. Buat repo GitHub, upload semua isi folder ini, aktifkan Settings > Pages (branch main).
2. Daftar API key gratis di https://webapi.bps.go.id/developer/ , simpan di repo: Settings > Secrets > Actions > `BPS_API_KEY`.
3. Cari ID variabel tabel LPE di WebAPI BPS (domain 3200 = Jawa Barat):
   `https://webapi.bps.go.id/v1/api/list/model/var/lang/ind/domain/3200/key/KEY_ANDA/keyword/pertumbuhan`
   lalu isi angka `var` di `scripts/bps_vars.json` (lu.y, lu.q, pg.y, pg.q, kab.y, kab.q).
4. Jalankan manual sekali: tab Actions > "Update data BPS" > Run workflow. Setelah itu otomatis tiap hari 08:00 WIB; commit hanya terjadi bila ada angka baru.

## Mengganti data awal dari Excel
    python3 scripts/excel_to_json.py file.xlsx data.json
