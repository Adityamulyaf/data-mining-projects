"""Ubah data/raw/wilayah.sql (cahyadsn/wilayah) menjadi data/raw/wilayah_2025.csv.

Sumber: https://github.com/cahyadsn/wilayah (MIT), Kepmendagri No 300.2.2-2138 Tahun 2025.

File SQL hanya punya dua kolom, `kode` dan `nama`, untuk semua tingkat wilayah.
Tingkat wilayah dibaca dari jumlah bagian kode:
    11             provinsi
    11.01          kabupaten/kota
    11.01.01       kecamatan
    11.01.01.2001  kelurahan (bagian terakhir diawali 1), desa (diawali 2), atau desa adat (diawali 3)

Hasilnya satu baris per desa/kelurahan, lengkap dengan nama kecamatan, kabupaten, dan provinsinya.
Skrip ini hanya mengubah format, tidak membersihkan nama. Pembersihan ada di src/clean.py.

Cara pakai (dari folder root repo):
    python src/convert_wilayah.py
"""

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SQL_PATH = ROOT / "data" / "raw" / "wilayah.sql"
CSV_PATH = ROOT / "data" / "raw" / "wilayah_2025.csv"

# Baris data berbentuk ('kode','nama'), dengan petik di dalam nama ditulis dobel ('')
ROW_RE = re.compile(r"\('([0-9.]+)','((?:[^']|'')*)'\)")

COLUMNS = [
    "kode_desa",
    "nama_desa",
    "jenis",
    "kode_kecamatan",
    "nama_kecamatan",
    "kode_kabupaten",
    "nama_kabupaten",
    "kode_provinsi",
    "nama_provinsi",
]


def read_sql(path):
    text = path.read_text(encoding="utf-8")
    return {kode: nama.replace("''", "'") for kode, nama in ROW_RE.findall(text)}


def build_rows(names):
    rows = []
    for kode, nama in names.items():
        parts = kode.split(".")
        if len(parts) != 4:
            continue
        prov, kab, kec = parts[0], ".".join(parts[:2]), ".".join(parts[:3])
        jenis = {"1": "kelurahan", "2": "desa", "3": "desa_adat"}.get(parts[3][0], "lainnya")
        rows.append(
            {
                "kode_desa": kode,
                "nama_desa": nama,
                "jenis": jenis,
                "kode_kecamatan": kec,
                "nama_kecamatan": names.get(kec, ""),
                "kode_kabupaten": kab,
                "nama_kabupaten": names.get(kab, ""),
                "kode_provinsi": prov,
                "nama_provinsi": names.get(prov, ""),
            }
        )
    rows.sort(key=lambda r: r["kode_desa"])
    return rows


def main():
    names = read_sql(SQL_PATH)
    rows = build_rows(names)
    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    levels = {1: 0, 2: 0, 3: 0, 4: 0}
    for kode in names:
        levels[len(kode.split("."))] = levels.get(len(kode.split(".")), 0) + 1
    jenis = {}
    for r in rows:
        jenis[r["jenis"]] = jenis.get(r["jenis"], 0) + 1
    missing = sum(1 for r in rows if not (r["nama_kecamatan"] and r["nama_kabupaten"] and r["nama_provinsi"]))

    print(f"Provinsi       : {levels[1]}")
    print(f"Kabupaten/kota : {levels[2]}")
    print(f"Kecamatan      : {levels[3]}")
    print(f"Desa/kelurahan : {levels[4]} {jenis}")
    print(f"Induk kosong   : {missing}")
    print(f"Tersimpan di   : {CSV_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
