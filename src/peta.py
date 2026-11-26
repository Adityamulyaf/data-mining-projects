"""Gambar peta Indonesia (provinsi atau kabupaten) dengan matplotlib, tanpa geopandas.

Contoh:
    from src.peta import gambar_peta
    nilai = df.groupby("kode_kabupaten")["kolom"].mean()   # index = kode kabupaten
    fig, ax = plt.subplots(figsize=(14, 6))
    gambar_peta(ax, nilai, level="kabupaten", cmap="Blues", label="persen")

GeoJSON dibuat oleh src/convert_geo.py. Kode wilayah yang tidak ada di `nilai`
digambar abu-abu.
"""

import json
from functools import lru_cache
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.colors import Normalize

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "data" / "geo"
ABU = "#e7e7e7"


@lru_cache(maxsize=2)
def baca_geo(level):
    """Kembalikan list (kode, nama, daftar_poligon) untuk level "provinsi" atau "kabupaten"."""
    with open(GEO / f"{level}.geojson", encoding="utf-8") as f:
        g = json.load(f)
    return [(ft["id"], ft["properties"]["nama"], [pol[0] for pol in ft["geometry"]["coordinates"]]) for ft in g["features"]]


def gambar_peta(ax, nilai=None, level="kabupaten", cmap="Blues", vmin=None, vmax=None, warna=None, label=None):
    """Isi peta.

    nilai : pandas Series berindeks kode wilayah, untuk peta bergradasi (pakai cmap).
    warna : dict kode -> warna, untuk peta kategori (misalnya klaster). Dipakai kalau nilai None.
    """
    norm = None
    if nilai is not None:
        norm = Normalize(vmin=nilai.min() if vmin is None else vmin, vmax=nilai.max() if vmax is None else vmax)
        peta_warna = plt.get_cmap(cmap)

    polys, cols = [], []
    for kode, _nama, poligon in baca_geo(level):
        if nilai is not None:
            c = peta_warna(norm(nilai[kode])) if kode in nilai.index else ABU
        else:
            c = (warna or {}).get(kode, ABU)
        polys.extend(poligon)
        cols.extend([c] * len(poligon))

    ax.add_collection(PolyCollection(polys, facecolors=cols, edgecolors="white", linewidths=0.15))
    ax.set_xlim(94.5, 141.5)
    ax.set_ylim(-11.3, 6.3)
    ax.set_aspect("equal")
    ax.axis("off")

    if norm is not None:
        sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
        cb = plt.colorbar(sm, ax=ax, fraction=0.025, pad=0.01)
        cb.outline.set_visible(False)
        if label:
            cb.set_label(label)
    return ax
