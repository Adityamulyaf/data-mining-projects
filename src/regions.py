"""Pemetaan 38 provinsi ke 7 wilayah besar.

Nama provinsi mengikuti kolom `nama_provinsi` di data/raw/wilayah_2025.csv.
"""

WILAYAH = {
    "Sumatera": [
        "Aceh",
        "Sumatera Utara",
        "Sumatera Barat",
        "Riau",
        "Kepulauan Riau",
        "Jambi",
        "Sumatera Selatan",
        "Kepulauan Bangka Belitung",
        "Bengkulu",
        "Lampung",
    ],
    "Jawa": [
        "Daerah Khusus Ibukota Jakarta",
        "Jawa Barat",
        "Banten",
        "Jawa Tengah",
        "Daerah Istimewa Yogyakarta",
        "Jawa Timur",
    ],
    "Bali dan Nusa Tenggara": [
        "Bali",
        "Nusa Tenggara Barat",
        "Nusa Tenggara Timur",
    ],
    "Kalimantan": [
        "Kalimantan Barat",
        "Kalimantan Tengah",
        "Kalimantan Selatan",
        "Kalimantan Timur",
        "Kalimantan Utara",
    ],
    "Sulawesi": [
        "Sulawesi Utara",
        "Gorontalo",
        "Sulawesi Tengah",
        "Sulawesi Barat",
        "Sulawesi Selatan",
        "Sulawesi Tenggara",
    ],
    "Maluku": [
        "Maluku",
        "Maluku Utara",
    ],
    "Papua": [
        "Papua",
        "Papua Barat",
        "Papua Barat Daya",
        "Papua Tengah",
        "Papua Pegunungan",
        "Papua Selatan",
    ],
}

PROVINSI_KE_WILAYAH = {prov: wil for wil, daftar in WILAYAH.items() for prov in daftar}


def wilayah_dari_provinsi(nama_provinsi):
    """Kembalikan nama wilayah besar untuk sebuah provinsi. Error kalau provinsi tidak dikenal."""
    return PROVINSI_KE_WILAYAH[nama_provinsi]
