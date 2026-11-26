"""Ubah data batas wilayah cahyadsn (wilayah_level_1_2.sql) menjadi GeoJSON untuk peta.

Hasil:
    data/geo/provinsi.geojson   (38 provinsi)
    data/geo/kabupaten.geojson  (514 kabupaten/kota)

Properti tiap fitur: kode, nama, ibukota, lat, lng, luas_km2, penduduk.
Kode sama formatnya dengan kolom kode_provinsi ("11") dan kode_kabupaten ("11.01")
di data/processed/desa_clean.parquet, jadi bisa langsung digabung.

Catatan data:
- Koordinat di sumber ditulis [lat, lng]. GeoJSON memakai [lng, lat], jadi ditukar.
- Satu wilayah bisa terdiri dari banyak pulau, jadi semua fitur disimpan sebagai MultiPolygon.
- Koordinat dibulatkan ke 3 desimal (sekitar 100 meter) supaya file kecil. Untuk peta
  tingkat provinsi dan kabupaten ini sudah lebih dari cukup.
- Dua kesalahan format di sumber diperbaiki otomatis: Kota Banjar (32.79) kurang satu
  kurung tutup, dan sebagian ring Kota Semarang (33.74) tidak diberi kurung pembuka.

File SQL (24 MB) tidak ikut di-commit. Kalau belum ada, script ini mengunduhnya sendiri.

Cara pakai (dari folder root repo):
    python src/convert_geo.py
"""

import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SQL_PATH = ROOT / "data" / "raw" / "wilayah_level_1_2.sql"
SQL_URL = "https://raw.githubusercontent.com/cahyadsn/wilayah/master/db/wilayah_level_1_2.sql"
OUT_DIR = ROOT / "data" / "geo"
DESIMAL = 3

_BARIS = re.compile(
    r"^\('([0-9.]+)','((?:[^']|'')*)','((?:[^']|'')*)',\s*([-0-9.eE]+|NULL),\s*([-0-9.eE]+|NULL),"
    r"\s*([-0-9.eE]+|NULL),\s*([-0-9.eE]+|NULL),\s*([-0-9.eE]+|NULL),\s*([-0-9.eE]+|NULL),"
    r"\s*'(\[.*?\])',\s*(\w+)\)",
    re.M,
)


def _angka(x):
    return None if x == "NULL" else float(x)


def _baca_path(teks):
    """Parse string poligon. Kalau kurung tutup kurang, tambahkan sampai valid."""
    for tambahan in range(4):
        try:
            return json.loads(teks + "]" * tambahan)
        except json.JSONDecodeError:
            continue
    raise ValueError("poligon tidak bisa dibaca")


def _ring(titik):
    """[[lat, lng], ...] menjadi [[lng, lat], ...], dibulatkan, tanpa titik berurutan yang sama."""
    hasil = []
    for lat, lng in titik:
        p = [round(lng, DESIMAL), round(lat, DESIMAL)]
        if not hasil or hasil[-1] != p:
            hasil.append(p)
    if len(hasil) < 3:
        return None
    if hasil[0] != hasil[-1]:
        hasil.append(hasil[0])
    return hasil if len(hasil) >= 4 else None


def _titik(x):
    return isinstance(x, list) and len(x) == 2 and all(isinstance(v, (int, float)) for v in x)


def _kumpulkan_ring(x, hasil):
    """Sumber mencampur beberapa tingkat kurung. Ambil semua ring ([[lat, lng], ...]) di dalamnya.

    Titik-titik yang berurutan dalam satu daftar dianggap satu ring. Ini juga menangani
    Kota Semarang (33.74), yang sebagian ringnya di sumber tidak diberi kurung pembuka.
    """
    sekarang = []
    for y in x:
        if _titik(y):
            sekarang.append(y)
            continue
        if sekarang:
            hasil.append(sekarang)
            sekarang = []
        _kumpulkan_ring(y, hasil)
    if sekarang:
        hasil.append(sekarang)


def _multipolygon(path):
    """Setiap ring dijadikan satu poligon (satu pulau)."""
    rings = []
    _kumpulkan_ring(path, rings)
    return [[r] for r in (_ring(x) for x in rings) if r]


def main():
    if not SQL_PATH.exists():
        print(f"Mengunduh {SQL_URL} ...")
        SQL_PATH.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(SQL_URL, SQL_PATH)

    teks = SQL_PATH.read_text(encoding="utf-8")
    fitur = {"provinsi": [], "kabupaten": []}
    for kode, nama, ibukota, lat, lng, _elv, _tz, luas, penduduk, path, _status in _BARIS.findall(teks):
        level = "provinsi" if "." not in kode else "kabupaten"
        fitur[level].append(
            {
                "type": "Feature",
                "id": kode,
                "properties": {
                    "kode": kode,
                    "nama": nama.replace("''", "'"),
                    "ibukota": ibukota.replace("''", "'"),
                    "lat": _angka(lat),
                    "lng": _angka(lng),
                    "luas_km2": _angka(luas),
                    "penduduk": _angka(penduduk),
                },
                "geometry": {"type": "MultiPolygon", "coordinates": _multipolygon(_baca_path(path))},
            }
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for level, daftar in fitur.items():
        out = OUT_DIR / f"{level}.geojson"
        with open(out, "w", encoding="utf-8") as f:
            json.dump({"type": "FeatureCollection", "features": daftar}, f, ensure_ascii=False, separators=(",", ":"))
        print(f"{out.relative_to(ROOT)}: {len(daftar)} wilayah, {out.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
