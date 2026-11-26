"""Bangun data/processed/desa_clean.parquet dari data/raw/wilayah_2025.csv.

Kolom hasil (kontrak file, lihat PLAN.md bagian 7):
    kode_desa, nama_asli, nama_bersih, jenis,
    kode_kabupaten, kabupaten, kode_provinsi, provinsi, wilayah

Hanya nama yang layak dipakai (lihat src/clean.py: layak_dipakai) yang disimpan.

Cara pakai (dari folder root repo):
    python src/build_dataset.py
"""

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.clean import clean_nama, layak_dipakai  # noqa: E402
from src.regions import wilayah_dari_provinsi  # noqa: E402

RAW_PATH = ROOT / "data" / "raw" / "wilayah_2025.csv"
OUT_PATH = ROOT / "data" / "processed" / "desa_clean.parquet"


def main():
    raw = pd.read_csv(RAW_PATH, dtype=str, encoding="utf-8")

    df = pd.DataFrame(
        {
            "kode_desa": raw["kode_desa"],
            "nama_asli": raw["nama_desa"],
            "nama_bersih": raw["nama_desa"].map(clean_nama),
            "jenis": raw["jenis"],
            "kode_kabupaten": raw["kode_kabupaten"],
            "kabupaten": raw["nama_kabupaten"],
            "kode_provinsi": raw["kode_provinsi"],
            "provinsi": raw["nama_provinsi"],
        }
    )
    df["wilayah"] = df["provinsi"].map(wilayah_dari_provinsi)

    layak = [layak_dipakai(a, b) for a, b in zip(df["nama_asli"], df["nama_bersih"])]
    dibuang = df[[not x for x in layak]]
    df = df[layak].reset_index(drop=True)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT_PATH, index=False)

    print(f"Baris mentah        : {len(raw)}")
    print(f"Dibuang (tak layak) : {len(dibuang)} -> {dibuang['nama_asli'].tolist()}")
    print(f"Baris tersimpan     : {len(df)}")
    print(f"Nama bersih unik    : {df['nama_bersih'].nunique()}")
    print(f"Provinsi / wilayah  : {df['provinsi'].nunique()} / {df['wilayah'].nunique()}")
    print(f"Tersimpan di        : {OUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
