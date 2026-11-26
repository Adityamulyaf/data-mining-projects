# Jejak Budaya dalam Nama

Klasifikasi, klastering, dan generasi nama desa di Indonesia berbasis n-gram karakter. Team-Based Project mata kuliah Data Mining.

Rencana kerja lengkap, pembagian tugas, dan tahapan ada di [PLAN.md](PLAN.md). Baca itu dulu.

## Setup

Butuh Python 3.12 atau lebih baru.

```bash
git clone https://github.com/Adityamulyaf/data-mining-projects.git
cd data-mining-projects

python -m venv .venv
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Windows (Git Bash)
source .venv/Scripts/activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
python -c "import sklearn, pandas, streamlit; print('siap')"
```

Kalau repo ini ada di dalam folder OneDrive, buat virtual environment di luar OneDrive supaya ribuan file library tidak ikut tersinkron. Contoh: `python -m venv %USERPROFILE%\.venvs\datmin`.

## Menjalankan

- Notebook: buka folder `notebooks/` dan jalankan berurutan dari `01` sampai `05`.
- Dashboard: `streamlit run app/streamlit_app.py`

## Struktur folder

| Folder              | Isi                                                |
| ------------------- | -------------------------------------------------- |
| `data/raw/`       | data asli, tidak boleh diubah                      |
| `data/processed/` | data hasil olahan                                  |
| `data/geo/`       | GeoJSON untuk peta                                 |
| `notebooks/`      | analisis, dijalankan berurutan                     |
| `src/`            | fungsi bersama yang dipakai notebook dan dashboard |
| `models/`         | model terbaik (joblib)                             |
| `app/`            | dashboard Streamlit                                |
| `reports/`        | laporan, slide, dan `figures/` untuk grafik      |
| `docs/`           | bahan dari dosen                                   |

## Data

Sumber: kode wilayah Kepmendagri No 300.2.2-2138 Tahun 2025 dari https://github.com/cahyadsn/wilayah (file `db/wilayah.sql`, lisensi MIT).

Data asli disimpan di `data/raw/wilayah.sql`, lalu diubah ke CSV dengan:

```bash
python src/convert_wilayah.py
```

Hasil pengecekan `data/raw/wilayah_2025.csv`:

- Encoding: UTF-8.
- Kolom: `kode_desa`, `nama_desa`, `jenis`, `kode_kecamatan`, `nama_kecamatan`, `kode_kabupaten`, `nama_kabupaten`, `kode_provinsi`, `nama_provinsi`.
- Jumlah baris: 83.762 desa/kelurahan (75.252 desa, 8.496 kelurahan, 14 desa adat), dari 38 provinsi, 514 kabupaten/kota, dan 7.285 kecamatan. Cocok dengan angka resmi Kepmendagri.
