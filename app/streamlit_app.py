"""Dashboard "Jejak Budaya dalam Nama".

Jalankan dari folder root repo:
    streamlit run app/streamlit_app.py

Halaman:
1. Tebak nama desa      (models/best_provinsi.joblib)
2. Peta klaster         (data/processed/klaster_kabupaten.csv)
3. Fakta menarik        (reports/ngram_khas_provinsi.csv, data/processed/prediksi_oof.parquet, kandidat_salah_kode.csv)
4. Generator dan kuis   (src/generator.py, data/processed/kuis_*.csv)
"""

import html
import json
import re
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.clean import clean_nama  # noqa: E402
from src.generator import GeneratorNama, rapikan  # noqa: E402
from src.regions import WILAYAH, wilayah_dari_provinsi  # noqa: E402

PROCESSED = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"

# Warna halaman
TINTA, TINTA2, LAUT, MERAH, KONTUR, KERTAS = "#1E2A2F", "#5B6B70", "#1F5F7A", "#B8322A", "#C9D3CC", "#EDF1EC"
# Palet kategori untuk peta klaster (palet dataviz, sudah divalidasi untuk buta warna)
WARNA_KLASTER = ["#257de0", "#f47230", "#00b894", "#f2a600", "#ee7fac", "#008a17", "#6a4ce2"]
URUT_WILAYAH = list(WILAYAH.keys())

st.set_page_config(page_title="Jejak Budaya dalam Nama", page_icon=":material/map:", layout="wide")

st.html(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;500;600&family=Young+Serif&display=swap');
html, body, .stApp, .stMarkdown, p, label, input, textarea, button {{
  font-family: 'Public Sans', system-ui, sans-serif;
}}
[data-testid="stIconMaterial"], .material-symbols-rounded {{ font-family: 'Material Symbols Rounded' !important; }}
h1, h2, h3, .serif {{ font-family: 'Young Serif', Georgia, serif !important; font-weight: 400 !important; color: {TINTA}; }}
h1 {{ font-size: 2.6rem !important; line-height: 1.1 !important; letter-spacing: -0.01em; }}
h2 {{ font-size: 1.6rem !important; }}
h3 {{ font-size: 1.2rem !important; }}
.block-container {{ max-width: 1180px; padding-top: 2.2rem; }}
.lede {{ color: {TINTA2}; font-size: 1.05rem; max-width: 62ch; line-height: 1.55; margin-top: -0.4rem; }}
.nama-besar {{ font-family: 'Young Serif', Georgia, serif; font-size: clamp(2.2rem, 6vw, 4.2rem);
  line-height: 1.15; color: {TINTA}; margin: 0.8rem 0 0.5rem; word-break: break-word; }}
.nama-besar span {{ padding: 0 0.02em; }}
.keterangan {{ color: {TINTA2}; font-size: 0.88rem; }}
.baris-tebakan {{ display: grid; grid-template-columns: minmax(9rem, 16rem) 1fr 3.5rem; gap: 0.8rem;
  align-items: center; padding: 0.55rem 0; border-bottom: 1px solid {KONTUR}; }}
.baris-tebakan .prov {{ font-weight: 600; }}
.baris-tebakan .wil {{ display: block; font-weight: 400; color: {TINTA2}; font-size: 0.82rem; }}
.baris-tebakan .jalur {{ height: 10px; background: {KONTUR}; border-radius: 5px; overflow: hidden; }}
.baris-tebakan .isi {{ height: 100%; background: {LAUT}; border-radius: 5px; }}
.baris-tebakan.pertama .isi {{ background: {MERAH}; }}
.baris-tebakan .pct {{ text-align: right; font-variant-numeric: tabular-nums; font-weight: 600; }}
.chip {{ display: inline-block; font-family: 'Public Sans', sans-serif; background: #fff; border: 1px solid {KONTUR};
  border-radius: 4px; padding: 0.1rem 0.45rem; margin: 0 0.3rem 0.3rem 0; font-size: 0.9rem; }}
.chip b {{ color: {MERAH}; font-weight: 600; }}
.kartu-nama {{ font-family: 'Young Serif', Georgia, serif; font-size: 1.45rem; color: {TINTA}; }}
@media (max-width: 640px) {{
  .baris-tebakan {{ grid-template-columns: 1fr 3rem; }}
  .baris-tebakan .jalur {{ grid-column: 1 / -1; grid-row: 2; }}
}}
</style>
""")


# ---------------------------------------------------------------- data

@st.cache_resource(show_spinner="Memuat model...")
def muat_model():
    return joblib.load(ROOT / "models" / "best_provinsi.joblib"), joblib.load(ROOT / "models" / "best_wilayah.joblib")


@st.cache_data(show_spinner="Memuat data desa...")
def muat_desa():
    return pd.read_parquet(PROCESSED / "desa_clean.parquet")


@st.cache_data
def muat_geo(level):
    with open(ROOT / "data" / "geo" / f"{level}.geojson", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(show_spinner="Menghitung jejak transmigrasi...")
def muat_jejak_jawa():
    df = muat_desa()
    oof = pd.read_parquet(PROCESSED / "prediksi_oof.parquet")
    kelas = oof.columns[1:]
    tebakan = kelas.values[oof[kelas].values.argmax(axis=1)]
    df = df.assign(ditebak_jawa=[wilayah_dari_provinsi(t) == "Jawa" for t in tebakan])
    luar = df[df["wilayah"] != "Jawa"]
    per_kab = luar.groupby(["kode_kabupaten", "kabupaten", "provinsi"]).agg(
        jumlah_desa=("kode_desa", "size"), persen=("ditebak_jawa", "mean")).reset_index()
    per_kab["persen"] = (100 * per_kab["persen"]).round(1)
    return per_kab


@st.cache_resource(show_spinner="Melatih generator...")
def muat_generator():
    df = muat_desa()
    return {w: GeneratorNama(orde=3).latih(df.loc[df["wilayah"] == w, "nama_bersih"]) for w in URUT_WILAYAH}


def layout_plotly(fig, tinggi=520):
    fig.update_layout(
        height=tinggi, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor=KERTAS, plot_bgcolor=KERTAS,
        font=dict(family="Public Sans, sans-serif", color=TINTA, size=13),
        hoverlabel=dict(bgcolor="white", font_family="Public Sans, sans-serif"),
    )
    return fig


def peta(geo, kode, nilai, teks_hover, warna_diskret=None, skala=None, judul_skala="", tinggi=520):
    """Choropleth Indonesia. warna_diskret: dict kategori -> warna. skala: colorscale untuk nilai kontinu."""
    fig = go.Figure()
    if warna_diskret:
        # satu trace saja (GeoJSON hanya dikirim sekali), warna lewat skala bertingkat
        kategori = list(warna_diskret)
        n = len(kategori)
        skala_bertingkat = []
        for i, k in enumerate(kategori):
            skala_bertingkat += [[i / n, warna_diskret[k]], [(i + 1) / n, warna_diskret[k]]]
        posisi = {k: i for i, k in enumerate(kategori)}
        fig.add_trace(go.Choropleth(
            geojson=geo, locations=kode, featureidkey="id", z=[posisi[v] + 0.5 for v in nilai],
            zmin=0, zmax=n, colorscale=skala_bertingkat, showscale=False,
            text=teks_hover, hovertemplate="%{text}<extra></extra>",
            marker_line_color="white", marker_line_width=0.3))
    else:
        fig.add_trace(go.Choropleth(
            geojson=geo, locations=kode, featureidkey="id", z=nilai, colorscale=skala,
            text=teks_hover, hovertemplate="%{text}<extra></extra>",
            marker_line_color="white", marker_line_width=0.3,
            colorbar=dict(title=dict(text=judul_skala, side="top"), orientation="h", thickness=8, len=0.45,
                          x=0, xanchor="left", y=0, yanchor="top", outlinewidth=0)))
    fig.update_geos(visible=False, bgcolor=KERTAS, projection_type="mercator",
                    lonaxis_range=[94.5, 141.5], lataxis_range=[-11.3, 6.3])
    return layout_plotly(fig, tinggi)


def legenda(warna_diskret):
    """Legenda HTML untuk peta kategori."""
    isi = "".join(
        f'<span style="display:inline-flex;align-items:center;margin:0 1.1rem 0.4rem 0;font-size:0.9rem">'
        f'<span style="width:12px;height:12px;border-radius:2px;background:{w};margin-right:0.4rem"></span>'
        f'{html.escape(str(k))}</span>' for k, w in warna_diskret.items())
    st.html(f'<div style="margin-top:-0.4rem">{isi}</div>')


# ---------------------------------------------------------------- halaman 1

def sorot_nama(nama_tampil, nama_bersih, pipe, kelas_idx):
    """Warnai huruf yang paling mendorong tebakan ke kelas_idx, dan kembalikan n-gram terkuat."""
    vec, lr = pipe.named_steps["tfidf"], pipe.named_steps["model"]
    x = vec.transform([nama_bersih])
    vocab = vec.vocabulary_
    koef = lr.coef_[kelas_idx]

    # posisi setiap n-gram (char_wb: tiap kata diberi spasi di depan dan belakang)
    skor = np.zeros(len(nama_bersih))
    kontribusi = {}
    pos = 0
    for kata in nama_bersih.split(" "):
        pad = f" {kata} "
        for n in range(2, 5):
            for i in range(len(pad) - n + 1):
                g = pad[i:i + n]
                j = vocab.get(g)
                if j is None:
                    continue
                c = koef[j] * x[0, j]
                kontribusi[g] = c
                if c > 0:
                    a, b = max(i - 1, 0), min(i - 1 + n, len(kata))
                    skor[pos + a:pos + b] += c
        pos += len(kata) + 1

    maks = skor.max() if skor.max() > 0 else 1
    # nama yang ditampilkan memakai nama_bersih supaya posisi huruf cocok
    potong = []
    for h, s in zip(nama_bersih, skor):
        a = min(0.85, s / maks * 0.85)
        gaya = (f"background: linear-gradient(transparent 58%, rgba(184,50,42,{a:.2f}) 58%, rgba(184,50,42,{a:.2f}) 92%, transparent 92%);"
                if a > 0.08 else "")
        potong.append(f'<span style="{gaya}">{html.escape(h)}</span>')
    teratas = sorted(((g, c) for g, c in kontribusi.items() if c > 0), key=lambda t: -t[1])[:6]
    return "".join(potong), teratas


def halaman_tebak():
    st.title("Dari mana asal desa ini?")
    st.html(f'<p class="lede">Ketik nama desa, atau nama karanganmu sendiri. Model hanya melihat susunan hurufnya, '
            f'lalu menebak provinsinya. Dilatih dari 83.758 nama desa dan kelurahan Kepmendagri 2025.</p>')

    contoh = ["Cikalong Wetan", "Lumban Sitorus", "Gampong Meunasah Baro", "Sidorejo Kidul", "Bonto Marannu", "Oelnasi"]
    if "nama_input" not in st.session_state:
        st.session_state.nama_input = contoh[0]
    pilih = st.pills("Coba contoh", contoh, selection_mode="single", label_visibility="collapsed")
    if pilih and pilih != st.session_state.get("pilih_terakhir"):
        st.session_state.nama_input = pilih
        st.session_state.pilih_terakhir = pilih
    nama = st.text_input("Nama desa", key="nama_input", placeholder="misalnya Cikalong Wetan")

    bersih = clean_nama(nama)
    if len(bersih.replace(" ", "")) < 2:
        st.info("Ketik minimal dua huruf. Angka dan tanda baca diabaikan.")
        return

    pipe_prov, _ = muat_model()
    proba = pipe_prov.predict_proba([bersih])[0]
    urut = np.argsort(-proba)[:3]
    kelas = pipe_prov.classes_

    teks_sorot, teratas = sorot_nama(nama, bersih, pipe_prov, urut[0])
    st.html(f'<div class="nama-besar">{teks_sorot}</div>'
            f'<div class="keterangan">Huruf yang diwarnai paling mendorong tebakan ke {html.escape(kelas[urut[0]])}. '
            f'Makin gelap, makin kuat.</div>')

    kiri, kanan = st.columns([1.05, 1], gap="large")
    with kiri:
        st.subheader("Tiga tebakan teratas")
        baris = []
        for r, i in enumerate(urut):
            kelas_css = "baris-tebakan pertama" if r == 0 else "baris-tebakan"
            baris.append(
                f'<div class="{kelas_css}"><div class="prov">{html.escape(kelas[i])}'
                f'<span class="wil">{html.escape(wilayah_dari_provinsi(kelas[i]))}</span></div>'
                f'<div class="jalur"><div class="isi" style="width:{proba[i] * 100:.1f}%"></div></div>'
                f'<div class="pct">{proba[i]:.0%}</div></div>')
        st.html("".join(baris))
        if teratas:
            st.html('<p class="keterangan" style="margin-top:1rem">Potongan huruf terkuat '
                    '(tanda _ adalah batas kata):</p>'
                    + "".join(f'<span class="chip"><b>{html.escape(g.replace(" ", "_"))}</b></span>' for g, _ in teratas))

        df = muat_desa()
        sama = df[df["nama_bersih"] == bersih]
        if len(sama):
            prov = sama["provinsi"].value_counts()
            st.html(f'<p class="keterangan" style="margin-top:1rem">Nama ini ada di data: {len(sama)} desa, '
                    f'di {html.escape(", ".join(f"{p} ({n})" for p, n in prov.head(4).items()))}.</p>')
        else:
            st.html('<p class="keterangan" style="margin-top:1rem">Nama ini tidak ada di data, '
                    'jadi tebakannya murni dari pola huruf.</p>')

    with kanan:
        geo = muat_geo("provinsi")
        kode_prov = {ft["properties"]["nama"]: ft["id"] for ft in geo["features"]}
        nama_prov = np.array(list(kode_prov.keys()))
        idx = {k: i for i, k in enumerate(kelas)}
        nilai = np.array([proba[idx[p]] * 100 if p in idx else 0 for p in nama_prov])
        hover = np.array([f"{p}: {v:.1f}%" for p, v in zip(nama_prov, nilai)])
        skala = [[0, "#D5DFD8"], [0.1, "#A9C6D3"], [1, LAUT]]
        fig = peta(geo, np.array([kode_prov[p] for p in nama_prov]), nilai, hover, skala=skala,
                   judul_skala="peluang (%)", tinggi=380)
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    st.caption("Akurasi model pada nama yang belum pernah dilihat: sekitar 40 persen untuk provinsi (tebakan acak 2,6 persen) "
               "dan sekitar 65 persen untuk tujuh wilayah besar. Jawaban benar ada di tiga tebakan teratas pada sekitar 65 persen kasus.")


# ---------------------------------------------------------------- halaman 2

def halaman_klaster():
    st.title("Peta budaya dari nama desa")
    st.html('<p class="lede">Setiap kabupaten diwakili oleh rata-rata pola huruf nama desanya, lalu dikelompokkan '
            'tanpa diberi tahu provinsinya. Bandingkan hasilnya dengan pembagian wilayah resmi.</p>')

    kl = pd.read_csv(PROCESSED / "klaster_kabupaten.csv", dtype={"kode_kabupaten": str})
    ringkas = pd.read_csv(REPORTS / "ringkasan_klaster.csv")
    pilihan = st.segmented_control("Tampilkan", ["Klaster K-Means", "Klaster Ward", "7 wilayah resmi"],
                                   default="Klaster K-Means", label_visibility="collapsed")
    geo = muat_geo("kabupaten")

    if pilihan == "7 wilayah resmi":
        nilai = kl["wilayah"].values
        warna = {w: WARNA_KLASTER[i] for i, w in enumerate(URUT_WILAYAH)}
    else:
        kolom = "klaster_kmeans" if pilihan == "Klaster K-Means" else "klaster_ward"
        if kolom == "klaster_kmeans":
            nama = dict(zip(ringkas["klaster"], ringkas["nama_klaster"]))
            nilai = kl[kolom].map(lambda c: f"{c}: {nama.get(c, c)}").values
        else:
            nilai = kl[kolom].map(lambda c: f"Klaster {c}").values
        kategori = sorted(set(nilai), key=lambda s: int(re.findall(r"\d+", s)[0]))
        warna = {k: WARNA_KLASTER[i % len(WARNA_KLASTER)] for i, k in enumerate(kategori)}

    hover = (kl["kabupaten"] + "<br>" + kl["provinsi"] + "<br>" + pd.Series(nilai)).values
    fig = peta(geo, kl["kode_kabupaten"].values, nilai, hover, warna_diskret=warna, tinggi=470)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    legenda(warna)

    if pilihan == "Klaster K-Means":
        st.subheader("Isi tiap klaster")
        tabel = ringkas.rename(columns={
            "klaster": "Klaster", "nama_klaster": "Nama", "jumlah_kabupaten": "Kabupaten",
            "provinsi_terbanyak": "Provinsi terbanyak", "ngram_menonjol": "Potongan huruf menonjol",
            "nama_desa_tersering": "Nama desa tersering"})
        st.dataframe(tabel[["Klaster", "Nama", "Kabupaten", "Provinsi terbanyak", "Potongan huruf menonjol",
                            "Nama desa tersering"]], hide_index=True, width="stretch")
        st.markdown("""
**Yang patut dilihat**

- Pulau Jawa terbelah menjadi Sunda dan Jawa, mengikuti batas bahasa, bukan batas pulau.
- Aceh pesisir terpisah dari daerah Gayo dan Alas di pedalaman.
- Sumatera Utara terbelah menjadi tanah Batak, pesisir Melayu, dan Nias.
- Kota Metro dan Pringsewu di Lampung ikut klaster Jawa: jejak kolonisasi sejak awal abad ke-20.
""")


# ---------------------------------------------------------------- halaman 3

def halaman_fakta():
    st.title("Fakta dari 83 ribu nama desa")
    df = muat_desa()

    tab1, tab2, tab3, tab4 = st.tabs(["Potongan huruf khas", "Jejak transmigrasi", "Nama paling umum", "Nama yang nyasar"])

    with tab1:
        ng = pd.read_csv(REPORTS / "ngram_khas_provinsi.csv")
        prov = st.selectbox("Provinsi", sorted(ng["provinsi"].unique()),
                            index=sorted(ng["provinsi"].unique()).index("Jawa Barat"))
        d = ng[ng["provinsi"] == prov].sort_values("peringkat")
        st.html('<p class="keterangan">Tanda _ adalah batas kata: <b>_ci</b> berarti kata yang diawali "ci". '
                'Persentase = dari semua desa yang mengandung potongan itu, berapa yang berada di provinsi ini.</p>')
        fig = go.Figure(go.Bar(
            x=d["koefisien"][::-1], y=d["ngram"][::-1], orientation="h", marker_color=LAUT,
            text=[f"{p:.0f}% di {prov}" for p in d["persen_di_provinsi"][::-1]], textposition="outside",
            hovertemplate="%{y}: koefisien %{x:.2f}<extra></extra>"))
        fig.update_xaxes(title="seberapa kuat mendorong tebakan (koefisien)", gridcolor=KONTUR,
                         range=[0, d["koefisien"].max() * 1.35])
        st.plotly_chart(layout_plotly(fig, 420), width="stretch", config={"displayModeBar": False})

        contoh_ng = d.iloc[0]["ngram"].replace("_", " ")
        contoh_desa = df[(df["provinsi"] == prov) & (" " + df["nama_bersih"] + " ").str.contains(re.escape(contoh_ng))]
        if len(contoh_desa):
            st.html(f'<p class="keterangan">Contoh desa di {html.escape(prov)} dengan potongan '
                    f'<b>{html.escape(d.iloc[0]["ngram"])}</b>: '
                    f'{html.escape(", ".join(contoh_desa["nama_asli"].sample(min(8, len(contoh_desa)), random_state=1)))}</p>')

    with tab2:
        st.html('<p class="lede">Persentase desa di luar Jawa yang ditebak model sebagai provinsi di Jawa. '
                'Tebakan diambil dari model yang belum pernah melihat nama desa itu.</p>')
        per_kab = muat_jejak_jawa()
        hover = (per_kab["kabupaten"] + "<br>" + per_kab["provinsi"] + "<br>"
                 + per_kab["persen"].astype(str) + "% dari " + per_kab["jumlah_desa"].astype(str) + " desa").values
        skala = [[0, "#D5DFD8"], [0.25, "#A9C6D3"], [1, LAUT]]
        fig = peta(muat_geo("kabupaten"), per_kab["kode_kabupaten"].values, per_kab["persen"].clip(upper=40).values,
                   hover, skala=skala, judul_skala="% ditebak Jawa", tinggi=520)
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.dataframe(per_kab[per_kab["jumlah_desa"] >= 20].nlargest(10, "persen")
                     .rename(columns={"kabupaten": "Kabupaten", "provinsi": "Provinsi",
                                      "jumlah_desa": "Desa", "persen": "% ditebak Jawa"})
                     [["Kabupaten", "Provinsi", "Desa", "% ditebak Jawa"]],
                     hide_index=True, width="stretch")
        st.markdown("Contoh di Lampung: desa bernama **Purworejo**, **Sukoharjo**, **Banyumas**, **Klaten**, dan "
                    "**Sumbersari Bantul**. Para pendatang menamai desa barunya dengan nama kampung halamannya di Jawa.")

    with tab3:
        top = df["nama_bersih"].value_counts().head(20)
        fig = go.Figure(go.Bar(x=top.values[::-1], y=[rapikan(n) for n in top.index[::-1]], orientation="h",
                               marker_color=LAUT, hovertemplate="%{y}: %{x} desa<extra></extra>"))
        fig.update_xaxes(title="jumlah desa", gridcolor=KONTUR)
        st.plotly_chart(layout_plotly(fig, 560), width="stretch", config={"displayModeBar": False})
        kembar = df.groupby("nama_bersih")["provinsi"].nunique()
        st.html(f'<p class="keterangan">{(kembar > 1).sum():,} nama dipakai di lebih dari satu provinsi. '
                f'Nama-nama Jawa seperti Sidomulyo dan Sidorejo tersebar sampai ke Sumatera, Kalimantan, dan Sulawesi.</p>'
                .replace(",", "."))

    with tab4:
        st.html('<p class="lede">Desa yang namanya sangat yakin ditebak model berasal dari wilayah lain. '
                'Setelah dicek, sebagian besar adalah nama pendek yang kebetulan mirip pola daerah lain, '
                'bukan kesalahan kode wilayah.</p>')
        kand = pd.read_csv(PROCESSED / "kandidat_salah_kode.csv")
        st.dataframe(kand.rename(columns={"nama_asli": "Nama desa", "kabupaten": "Kabupaten", "provinsi": "Provinsi",
                                          "tebakan": "Ditebak", "keyakinan": "Keyakinan",
                                          "provinsi_lain_dengan_nama_sama": "Provinsi lain dengan nama sama"})
                     .drop(columns="kode_desa"), hide_index=True, width="stretch")


# ---------------------------------------------------------------- halaman 4

def halaman_generator():
    st.title("Mengarang nama desa")
    st.html('<p class="lede">Generator mempelajari huruf apa yang biasa muncul setelah setiap tiga huruf, '
            'lalu menyusun nama baru huruf demi huruf. Nama yang sudah ada di data dibuang, jadi semua nama di bawah '
            'belum pernah dipakai desa mana pun.</p>')

    tab1, tab2, tab3 = st.tabs(["Generator", "Kuis: asli atau palsu?", "Kuis: manusia vs mesin"])

    with tab1:
        kiri, kanan = st.columns([1, 2], gap="large")
        with kiri:
            wil = st.selectbox("Wilayah", URUT_WILAYAH, index=1)
            if st.button("Karang 6 nama", type="primary"):
                st.session_state.seed_gen = st.session_state.get("seed_gen", 0) + 1
        with kanan:
            df = muat_desa()
            gen = muat_generator()[wil]
            nama = gen.karang(6, dilarang=set(df["nama_bersih"]), seed=st.session_state.get("seed_gen", 0) * 97 + len(wil))
            _, pipe_wil = muat_model()
            proba = pipe_wil.predict_proba(nama)
            kartu = []
            for n, p in zip(nama, proba):
                i = p.argmax()
                tepat = pipe_wil.classes_[i] == wil
                tanda = f'<span style="color:{LAUT}">dikenali sebagai {html.escape(pipe_wil.classes_[i])} ({p[i]:.0%})</span>' if tepat \
                    else f'<span style="color:{MERAH}">ditebak {html.escape(pipe_wil.classes_[i])} ({p[i]:.0%})</span>'
                kartu.append(f'<div style="padding:0.55rem 0;border-bottom:1px solid {KONTUR}">'
                             f'<div class="kartu-nama">{html.escape(rapikan(n))}</div>'
                             f'<div class="keterangan">{tanda}</div></div>')
            st.html("".join(kartu))
        st.caption("Dari 350 nama karangan, 71 persen ditebak classifier sesuai wilayah asal generatornya (tebakan acak 14 persen).")

    with tab2:
        kuis = pd.read_csv(PROCESSED / "kuis_asli_palsu.csv")
        st.html('<p class="lede">Lima nama di bawah adalah desa sungguhan, lima lainnya karangan generator. '
                'Bisakah kamu membedakannya?</p>')
        jawaban = {}
        kol = st.columns(2, gap="large")
        for i, r in kuis.iterrows():
            with kol[i % 2]:
                st.html(f'<div class="kartu-nama" style="margin-top:0.6rem">{r["no"]}. {html.escape(r["nama"])}</div>')
                jawaban[r["no"]] = st.radio(f"Jawaban nomor {r['no']}", ["Asli", "Palsu"], horizontal=True,
                                            index=None, key=f"ap_{r['no']}", label_visibility="collapsed")
        if st.button("Periksa jawaban", type="primary", key="periksa_ap"):
            if any(v is None for v in jawaban.values()):
                st.warning("Masih ada nama yang belum dijawab.")
            else:
                benar = 0
                hasil = []
                for _, r in kuis.iterrows():
                    kunci_asli = r["kunci"].startswith("asli")
                    ok = (jawaban[r["no"]] == "Asli") == kunci_asli
                    benar += ok
                    hasil.append(f'<div style="padding:0.3rem 0"><b>{r["no"]}. {html.escape(r["nama"])}</b>: '
                                 f'{"benar" if ok else "salah"}, {html.escape(r["kunci"])}</div>')
                st.html(f'<div class="serif" style="font-size:1.6rem;margin:0.8rem 0">Skor kamu {benar} dari {len(kuis)}</div>'
                        + "".join(hasil))

    with tab3:
        kuis = pd.read_csv(PROCESSED / "kuis_manusia_vs_mesin.csv")
        st.html('<p class="lede">Tebak provinsi tiap desa, lalu bandingkan dengan tebakan model. '
                'Model belum pernah melihat nama-nama ini saat dilatih.</p>')
        provinsi = sorted(muat_desa()["provinsi"].unique())
        jawaban = {}
        for _, r in kuis.iterrows():
            a, b = st.columns([1, 1.3], vertical_alignment="center")
            a.html(f'<div class="kartu-nama">{r["no"]}. {html.escape(r["nama"])}</div>')
            jawaban[r["no"]] = b.selectbox(f"Provinsi untuk {r['nama']}", provinsi, index=None,
                                           placeholder="Pilih provinsi", key=f"mm_{r['no']}", label_visibility="collapsed")
        if st.button("Buka jawaban", type="primary", key="buka_mm"):
            skor_manusia = skor_mesin = 0
            baris = []
            for _, r in kuis.iterrows():
                prov_benar = r["jawaban"].split(", ")[-1]
                m = jawaban[r["no"]] == prov_benar
                skor_manusia += m
                skor_mesin += bool(r["mesin_benar"])
                baris.append({"Desa": r["nama"], "Jawaban": r["jawaban"], "Tebakanmu": jawaban[r["no"]] or "-",
                              "Tebakan mesin": f"{r['tebakan_mesin']} ({r['keyakinan_mesin']:.0%})",
                              "Tiga teratas mesin": r["top3_mesin"]})
            st.html(f'<div class="serif" style="font-size:1.6rem;margin:0.8rem 0">'
                    f'Kamu {skor_manusia}, mesin {skor_mesin}</div>')
            st.dataframe(pd.DataFrame(baris), hide_index=True, width="stretch")


# ---------------------------------------------------------------- navigasi

nav = st.navigation([
    st.Page(halaman_tebak, title="Tebak nama desa", icon=":material/search:", default=True),
    st.Page(halaman_klaster, title="Peta klaster", icon=":material/map:", url_path="klaster"),
    st.Page(halaman_fakta, title="Fakta menarik", icon=":material/insights:", url_path="fakta"),
    st.Page(halaman_generator, title="Generator dan kuis", icon=":material/casino:", url_path="generator"),
])
with st.sidebar:
    st.html(f'<div class="serif" style="font-size:1.25rem;line-height:1.2;margin-top:0.5rem">Jejak Budaya dalam Nama</div>'
            f'<p class="keterangan">Klasifikasi, klastering, dan generasi nama desa di Indonesia berbasis n-gram karakter. '
            f'Data: Kepmendagri No 300.2.2-2138 Tahun 2025.</p>')
nav.run()
