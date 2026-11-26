"""Buat gambar khusus laporan IEEE (reports/figures/laporan_*.png).

Ukurannya sudah pas dengan kolom IEEE (1 kolom 3,5 inci, 2 kolom 7,16 inci), huruf Times,
dan tanpa judul di dalam gambar karena judul ada di caption LaTeX.

Cara pakai (dari folder root repo):
    python reports/buat_gambar_laporan.py
"""

import sys
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.collections import PolyCollection  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from sklearn.metrics import confusion_matrix  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.peta import baca_geo  # noqa: E402
from src.regions import WILAYAH, wilayah_dari_provinsi  # noqa: E402

PROCESSED = ROOT / "data" / "processed"
FIGS = ROOT / "reports" / "figures"
SATU_KOLOM, DUA_KOLOM = 3.5, 7.16
BIRU, ABU, TEKS2 = "#257de0", "#c2c2c2", "#444444"
WARNA_KLASTER = ["#257de0", "#f47230", "#00b894", "#f2a600", "#ee7fac", "#008a17", "#6a4ce2"]

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8, "xtick.labelsize": 7, "ytick.labelsize": 7,
    "legend.fontsize": 7, "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": ABU, "axes.labelcolor": TEKS2, "xtick.color": TEKS2, "ytick.color": TEKS2,
    "savefig.dpi": 300, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
})


def simpan(fig, nama):
    fig.savefig(FIGS / nama)
    plt.close(fig)
    print("tersimpan", nama)


def peta(ax, warna_per_kode, abu=ABU):
    polys, cols = [], []
    for kode, _, poligon in baca_geo("kabupaten"):
        c = warna_per_kode.get(kode, abu)
        polys.extend(poligon)
        cols.extend([c] * len(poligon))
    ax.add_collection(PolyCollection(polys, facecolors=cols, edgecolors="white", linewidths=0.1))
    ax.set_xlim(95, 141.1)
    ax.set_ylim(-11.1, 6.1)
    ax.set_aspect("equal")
    ax.axis("off")


def main():
    df = pd.read_parquet(PROCESSED / "desa_clean.parquet")
    oof = pd.read_parquet(PROCESSED / "prediksi_oof.parquet")
    assert (oof["kode_desa"].values == df["kode_desa"].values).all()
    kelas = oof.columns[1:].values
    df["tebakan"] = kelas[oof[kelas].values.argmax(axis=1)]
    df["tebakan_wilayah"] = df["tebakan"].map(wilayah_dari_provinsi)

    # 1. n-gram khas: 6 provinsi, 6 n-gram, dua kolom
    ng = pd.read_csv(ROOT / "reports" / "ngram_khas_provinsi.csv")
    pilihan = ["Jawa Barat", "Aceh", "Sumatera Utara", "Lampung", "Sulawesi Selatan", "Nusa Tenggara Timur"]
    fig, axes = plt.subplots(2, 3, figsize=(DUA_KOLOM, 3.0))
    for ax, prov in zip(axes.ravel(), pilihan):
        d = ng[ng["provinsi"] == prov].head(6).iloc[::-1]
        ax.barh(d["ngram"], d["koefisien"], color=BIRU, height=0.65)
        for y, (v, p) in enumerate(zip(d["koefisien"], d["persen_di_provinsi"])):
            ax.text(v, y, f" {p:.0f}%", va="center", fontsize=6.5, color=TEKS2)
        ax.set_xlim(0, d["koefisien"].max() * 1.3)
        ax.set_title(prov, loc="left")
        ax.tick_params(axis="y", labelsize=7.5)
    for ax in axes[1]:
        ax.set_xlabel("koefisien LR")
    fig.tight_layout(w_pad=1.2, h_pad=0.8)
    simpan(fig, "laporan_ngram.png")

    # 2. confusion matrix wilayah, satu kolom
    urut = list(WILAYAH.keys())
    singkat = ["Sumatera", "Jawa", "Bali-NT", "Kalimantan", "Sulawesi", "Maluku", "Papua"]
    cm = confusion_matrix(df["wilayah"], df["tebakan_wilayah"], labels=urut, normalize="true") * 100
    fig, ax = plt.subplots(figsize=(SATU_KOLOM, 3.0))
    ax.imshow(cm, cmap="Blues", vmin=0, vmax=100)
    ax.set_xticks(range(7), singkat, rotation=40, ha="right")
    ax.set_yticks(range(7), singkat)
    for i in range(7):
        for j in range(7):
            ax.text(j, i, f"{cm[i, j]:.0f}", ha="center", va="center", fontsize=7,
                    color="white" if cm[i, j] > 50 else "#191919")
    ax.set_xlabel("ditebak sebagai")
    ax.set_ylabel("wilayah sebenarnya")
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
    simpan(fig, "laporan_confusion.png")

    # 3. peta jejak Jawa, dua kolom
    luar = df[df["wilayah"] != "Jawa"]
    per_kab = luar.groupby("kode_kabupaten")["tebakan_wilayah"].apply(lambda s: (s == "Jawa").mean() * 100)
    cmap = plt.get_cmap("Blues")
    norm = plt.Normalize(0, 40)
    fig, ax = plt.subplots(figsize=(DUA_KOLOM, 2.5))
    peta(ax, {k: cmap(norm(v)) for k, v in per_kab.items()}, abu="#dddddd")
    sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    cax = ax.inset_axes([0.03, 0.12, 0.22, 0.035])
    cb = fig.colorbar(sm, cax=cax, orientation="horizontal", ticks=[0, 10, 20, 30, 40])
    cb.ax.set_xticklabels(["0", "10", "20", "30", "40+"])
    cb.outline.set_visible(False)
    cb.set_label("% desa ditebak Jawa", fontsize=7)
    cb.ax.tick_params(labelsize=6.5)
    simpan(fig, "laporan_jejak_jawa.png")

    # 4. peta klaster K-Means, dua kolom, legenda di bawah
    kl = pd.read_csv(PROCESSED / "klaster_kabupaten.csv", dtype={"kode_kabupaten": str})
    nama = kl.drop_duplicates("klaster").set_index("klaster")["nama_klaster"].sort_index()
    fig, ax = plt.subplots(figsize=(DUA_KOLOM, 2.75))
    peta(ax, {k: WARNA_KLASTER[c] for k, c in zip(kl["kode_kabupaten"], kl["klaster"])})
    ax.legend(handles=[Patch(color=WARNA_KLASTER[c], label=n) for c, n in nama.items()],
              loc="upper center", bbox_to_anchor=(0.5, 0.02), ncol=3, frameon=False,
              handlelength=1.2, columnspacing=1.2, fontsize=7)
    simpan(fig, "laporan_klaster.png")

    # 5. tabel kata pertama (dicetak, untuk disalin ke LaTeX)
    kata1 = df["nama_bersih"].str.split().str[0]
    print("\nKata pertama teratas per wilayah:")
    for w in urut:
        vc = kata1[df["wilayah"] == w].value_counts(normalize=True).head(3) * 100
        print(w, " | ".join(f"{k} ({v:.1f})" for k, v in vc.items()))


if __name__ == "__main__":
    main()
