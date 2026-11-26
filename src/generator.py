"""Generator nama desa berbasis rantai Markov n-gram karakter.

Cara kerja (PLAN.md bagian 6.8):
1. Kumpulkan nama desa satu kelompok (misalnya satu wilayah).
2. Hitung huruf apa yang muncul setelah setiap potongan `orde` huruf.
   Contoh orde 3: setelah "rej" hampir selalu muncul "o".
3. Bangun nama baru huruf demi huruf berdasarkan peluang itu, sampai bertemu tanda akhir.
4. Buang nama yang ternyata sudah ada di data asli.

Contoh:
    from src.generator import GeneratorNama
    gen = GeneratorNama(orde=3).latih(daftar_nama)
    gen.karang(5, dilarang=set_semua_nama_asli, seed=1)
"""

import random
from collections import Counter, defaultdict

AWAL = "^"
AKHIR = "$"


class GeneratorNama:
    def __init__(self, orde=3, panjang_min=4, panjang_maks=24):
        self.orde = orde
        self.panjang_min = panjang_min
        self.panjang_maks = panjang_maks
        self.transisi = {}

    def latih(self, daftar_nama):
        """daftar_nama: iterable string nama bersih (huruf kecil). Nama kembar dihitung sekali."""
        hitung = defaultdict(Counter)
        for nama in set(daftar_nama):
            teks = AWAL * self.orde + nama + AKHIR
            for i in range(len(teks) - self.orde):
                hitung[teks[i:i + self.orde]][teks[i + self.orde]] += 1
        # simpan sebagai (daftar huruf, daftar bobot) supaya cepat diambil acak
        self.transisi = {konteks: (list(c.keys()), list(c.values())) for konteks, c in hitung.items()}
        return self

    def _satu_nama(self, rng):
        konteks = AWAL * self.orde
        hasil = []
        while True:
            huruf, bobot = self.transisi[konteks]
            h = rng.choices(huruf, weights=bobot)[0]
            if h == AKHIR:
                return "".join(hasil)
            hasil.append(h)
            if len(hasil) > self.panjang_maks:
                return None
            konteks = konteks[1:] + h

    def karang(self, n, dilarang=(), seed=None, percobaan_maks=10000):
        """Hasilkan n nama baru yang unik dan tidak ada di `dilarang` (misalnya semua nama asli)."""
        if not self.transisi:
            raise RuntimeError("panggil latih() dulu")
        rng = random.Random(seed)
        dilarang = set(dilarang)
        hasil = []
        for _ in range(percobaan_maks):
            nama = self._satu_nama(rng)
            if nama is None or not (self.panjang_min <= len(nama.replace(" ", "")) <= self.panjang_maks):
                continue
            nama = " ".join(nama.split())
            if nama in dilarang or nama in hasil:
                continue
            hasil.append(nama)
            if len(hasil) == n:
                break
        return hasil

    def persen_baru(self, dilarang, n=500, seed=0):
        """Dari n nama yang dibangkitkan tanpa filter, berapa persen yang benar-benar baru."""
        rng = random.Random(seed)
        dilarang = set(dilarang)
        nama = [self._satu_nama(rng) for _ in range(n)]
        nama = [x for x in nama if x]
        return sum(x not in dilarang for x in nama) / max(len(nama), 1)


def rapikan(nama):
    """Huruf kapital di awal setiap kata, untuk ditampilkan."""
    return " ".join(k[:1].upper() + k[1:] for k in nama.split())
