"""Normalisasi nama desa. Dipakai bersama oleh semua notebook dan dashboard.

Prinsipnya: buang yang administratif, pertahankan yang mengandung petunjuk budaya.

Yang dibuang atau dirapikan:
- awalan "Desa Adat" (14 desa di Kabupaten Jayapura)
- penanda pemekaran: angka romawi berdiri sendiri (I sampai XX) dan potongan yang mengandung angka
- tanda baca selain tanda petik dan tanda hubung
- singkatan umum di Aceh: "Mns." menjadi meunasah, "Kp." menjadi kampung, "Tgk." menjadi teungku
- kata yang menempel tanpa spasi, misalnya "SeuneubokTeungoh" menjadi "seuneubok teungoh"

Yang sengaja dipertahankan:
- kata khas daerah seperti gampong, huta, lumban, pekon, tiuh, negeri, marga, lembang, kampung
- kata "desa" yang menjadi bagian nama, misalnya "Desa Baru"
- kata bilangan seperti "Satu" dan "Dua", karena merupakan kata biasa dalam bahasa
- tanda petik (misalnya "Kandua'", ciri bahasa di Sulawesi) dan tanda hubung (misalnya "Sigurung-gurung")
"""

import re

_APOSTROF = str.maketrans({"’": "'", "‘": "'", "`": "'", "´": "'"})
_CAMEL = re.compile(r"(?<=[a-z])(?=[A-Z][a-z])")
_SINGKATAN = [
    (re.compile(r"\bmns\.?(?=\s|$)"), "meunasah"),
    (re.compile(r"\bkp\.?(?=\s|$)"), "kampung"),
    (re.compile(r"\btgk\.?(?=\s|$)"), "teungku"),
]
_ROMAWI = re.compile(r"^(x{0,2})(ix|iv|v?i{0,3})$")
_BUKAN_HURUF = re.compile(r"[^a-z' -]")
_SPASI = re.compile(r"\s+")


def _romawi(token):
    return token != "" and _ROMAWI.match(token) is not None


def clean_nama(nama):
    """Ubah satu nama desa menjadi bentuk bersih. Hasilnya bisa string kosong."""
    if not isinstance(nama, str):
        return ""
    s = nama.translate(_APOSTROF)
    s = _CAMEL.sub(" ", s)
    s = s.lower()
    s = re.sub(r"^desa adat\s+", "", s)
    s = s.replace(".", ". ")
    for pola, ganti in _SINGKATAN:
        s = pola.sub(ganti, s)
    s = re.sub(r"[/(),.]", " ", s)

    tokens = []
    for tok in s.split():
        if any(ch.isdigit() for ch in tok):
            continue
        # tanda petik di akhir kata dipertahankan (misalnya "kandua'"), di awal kata dibuang
        tok = _BUKAN_HURUF.sub("", tok).strip("-").lstrip("'")
        if not tok or _romawi(tok):
            continue
        tokens.append(tok)
    return _SPASI.sub(" ", " ".join(tokens)).strip()


def layak_dipakai(nama_asli, nama_bersih):
    """False untuk nama yang tidak membawa informasi bahasa: kosong, satu huruf, atau singkatan huruf kapital semua (misalnya "OP", "MKCM")."""
    if len(nama_bersih.replace(" ", "")) < 2:
        return False
    huruf = [ch for ch in nama_asli if ch.isalpha()]
    if huruf and all(ch.isupper() for ch in huruf):
        return False
    return True
