# PLAN: Tebak Asal Daerah dari Nama Desa

Rencana kerja Team-Based Project (TBP) Data Mining. Dokumen ini jadi pegangan bersama, jadi baca sampai habis sebelum mulai mengerjakan bagianmu.

## 1. Ringkasan

Kita membangun model yang menebak **provinsi asal sebuah desa hanya dari namanya**. Setelah itu kita melihat apakah pola budaya Indonesia muncul dengan sendirinya dari data. Contohnya awalan "Ci-" untuk Sunda, akhiran "-rejo" atau "-harjo" untuk Jawa, "Lumban" atau "Huta" untuk Batak, dan "Nagari" untuk Minang.

- **Kuadran novelty:** metode lama untuk masalah baru.
- **Metode:**
  - ekstraksi fitur teks: TF-IDF n-gram karakter;
  - klasifikasi: Naive Bayes, Logistic Regression, SVM (Random Forest opsional);
  - klastering: K-Means dan Hierarchical;
  - generator nama desa: model n-gram karakter (rantai Markov).
- **Usulan judul:** Jejak Budaya dalam Nama: Klasifikasi, Klastering, dan Generasi Nama Desa di Indonesia Berbasis N-gram Karakter.
- **Tim dan waktu:** 5 orang, 5 hari.
- **Output wajib TBP:** dataset, kode, model, dashboard, laporan, dan presentasi. Detailnya ada di `docs/datmin-tbp.jpeg`.

## 2. Kenapa topik ini

- **Belum ada yang meneliti.** Kita belum menemukan studi klasifikasi atau klastering nama desa Indonesia. Studi terdekat hanya identifikasi bahasa daerah dari kalimat.
- **Datanya siap pakai.** Datanya berupa satu CSV resmi, sudah berlabel, dan bersih. Tidak perlu scraping.
- **Demonya menarik.** Penonton bisa mengetik nama desa kampung halamannya, lalu model menebak provinsinya.

### Jawaban kalau ditanya "kan bisa dicari di Google?"

Pertanyaan riset kita bukan "di mana desa X". Pertanyaan kita adalah **"informasi budaya apa yang tersimpan di 83 ribu nama desa Indonesia"**. Model dipakai sebagai alat untuk membedah pola itu.

Selain itu, ada kegunaan nyata yang tidak bisa digantikan mesin pencari:

1. **Berlaku untuk nama yang tidak ada di database.** Misalnya nama dusun atau kampung, nama desa lama di arsip atau peta kolonial, dan desa hasil pemekaran baru.
2. **Pemeriksa kualitas data administrasi.** Desa yang namanya sangat tidak cocok dengan provinsinya bisa ditandai sebagai kandidat salah input kode wilayah.
3. **Temuan sejarah sosial.** Contohnya jejak transmigrasi, yaitu desa di Lampung atau Sumatera Selatan yang namanya "berbau Jawa".
4. **Pola budaya yang terukur.** Kita bisa menunjukkan dengan angka potongan huruf apa yang paling khas di tiap daerah.

Penelitian sejenis yang bisa dijadikan pembanding di laporan:

- Ambekar et al., KDD 2009: menebak kelompok etnis dari nama orang.
- Ye et al., 2017, NamePrism: menebak kebangsaan dari nama orang.
- Fize et al., 2021, IJGI: n-gram karakter pada nama tempat. Contohnya, nama tempat di barat daya Prancis cenderung berakhiran "-ac".
- Swiss toponyms char-RNN (blog hunzikp.github.io): menebak lokasi dari nama tempat di Swiss.
- YearPredictionMSD (Bertin-Mahieux et al., 2011) dan PIGEON (Haas et al., CVPR 2024). **Sitasi dua ini belum dicek, cek dulu sebelum dipakai.**

## 3. Pertanyaan penelitian

1. Seberapa akurat nama desa saja bisa menebak asal daerah? Ada dua tingkat yang diuji:
   - **provinsi** (38 kelas);
   - **wilayah besar** (7 kelas): Sumatera, Jawa, Bali dan Nusa Tenggara, Kalimantan, Sulawesi, Maluku, Papua.
2. Potongan huruf (n-gram) apa yang paling khas di tiap daerah?
3. Kalau kabupaten dikelompokkan berdasarkan nama-nama desanya **tanpa label**, apakah kelompok yang terbentuk mirip wilayah budaya?
4. Di mana kesalahan model punya makna? Misalnya jejak transmigrasi.
5. Kalau model mengarang nama desa baru untuk tiap daerah, apakah manusia bisa membedakannya dari nama asli, dan apakah classifier menebak daerah yang sesuai?

## 4. Data

| Data | Sumber | Keterangan |
|---|---|---|
| Kode wilayah 2025 (utama) | github.com/yonatanyl/KODE-WILAYAH-KEPMENDAGRI-2025 | CSV, 75.266 desa + 8.496 kelurahan, berisi kode dan nama provinsi, kabupaten, kecamatan, dan desa |
| Kode wilayah (cadangan) | github.com/cahyadsn/wilayah | SQL, diperbarui Februari 2026 |
| Peta | GeoJSON provinsi atau kabupaten Indonesia dari repo publik | Dicari di hari 1. Kalau versi kabupaten tidak ada, pakai peta provinsi |
| Bonus (opsional) | GeoNames (geonames.org, CC-BY 4.0) | Hanya kalau ada sisa waktu di hari 4, lihat bagian 9 |

**Wajib dicek di hari 1:** nama kolom yang sebenarnya, jumlah baris, dan encoding file.

## 5. Struktur repo

```
data-mining-projects/
  PLAN.md
  README.md
  requirements.txt
  .gitignore
  data/
    raw/wilayah_2025.csv
    processed/desa_clean.parquet
    geo/                       (GeoJSON)
  notebooks/
    01_eda.ipynb               (distribusi, nama kembar, panjang nama)
    02_classification.ipynb    (NB vs LR vs SVM, RF opsional, 2 level label)
    03_clustering.ipynb        (klaster kabupaten, peta, ARI)
    04_error_analysis.ipynb    (confusion matrix, transmigrasi, cek kualitas data)
    05_generator.ipynb         (generator nama desa, uji ke classifier, bahan kuis)
  src/
    clean.py                   (normalisasi nama, dipakai notebook dan app)
    regions.py                 (pemetaan provinsi ke 7 wilayah besar)
    generator.py               (model n-gram karakter untuk mengarang nama)
  models/                      (model terbaik, format joblib)
  app/
    streamlit_app.py
  reports/                     (laporan dan slide)
  docs/                        (bahan dari dosen)
```

**Library:** pandas, scikit-learn, matplotlib, plotly, streamlit, joblib. Opsional: geopandas.

## 6. Langkah kerja (pipeline)

### 6.1 Preprocessing (`src/clean.py`)

- Ubah ke huruf kecil.
- Buang tanda baca dan spasi ganda.
- Buang awalan administratif seperti "desa" dan "kelurahan". Untuk "kampung", cek dulu: kadang kata itu memang bagian dari nama desa.
- Buang angka atau angka romawi penanda pemekaran, misalnya "I", "II", "Satu".
- Simpan juga kolom nama asli.
- **Semua notebook dan dashboard harus memakai fungsi pembersih yang sama dari file ini.** Jangan bikin versi sendiri-sendiri.

### 6.2 Nama kembar

- Banyak nama muncul di lebih dari satu provinsi, misalnya "Sukamaju" dan "Sidomulyo". Catat ini di EDA, karena bisa jadi temuan menarik.
- Data latih dan uji dibagi **berdasarkan nama unik** dengan `GroupShuffleSplit`, memakai nama yang sudah dibersihkan sebagai group.
- Tujuannya supaya nama yang sama tidak muncul di data latih dan data uji sekaligus. Kalau sampai muncul di keduanya, model cuma menghafal dan akurasinya jadi palsu.

### 6.3 Fitur

- `TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4))`, dengan `min_df` kecil.

### 6.4 Klasifikasi

- **Model inti:** MultinomialNB, LogisticRegression, LinearSVC. Alasan memilih tiap model (wajib ditulis di laporan):
  - **Naive Bayes:** baseline klasik untuk teks, cepat, dan sederhana.
  - **Logistic Regression:** bisa ditafsirkan. Koefisiennya menunjukkan n-gram paling khas tiap daerah.
  - **SVM:** biasanya paling kuat untuk fitur teks yang jumlahnya sangat banyak.
- **Opsional:** RandomForest sebagai pembanding dari keluarga model pohon, kalau masih ada waktu. Model ini berat untuk fitur sebanyak ini, jadi batasi jumlah fiturnya, misalnya dengan `SelectKBest`.
- Catatan: TF-IDF bukan model, melainkan cara mengubah nama menjadi angka. Jadi susunannya 1 ekstraksi fitur dan 3 model yang dibandingkan.
- **Target:** provinsi (38 kelas) dan wilayah besar (7 kelas).
- **Metrik:**
  - accuracy;
  - macro-F1;
  - top-3 accuracy (jawaban benar ada di 3 tebakan teratas);
  - confusion matrix.
- **Ketimpangan kelas:** desa di Jawa Tengah dan Jawa Timur jauh lebih banyak dari provinsi lain. Pakai `class_weight="balanced"`.
- Simpan model terbaik ke `models/`.

### 6.5 N-gram paling khas

- Ambil koefisien Logistic Regression per kelas, lalu tampilkan n-gram teratas tiap provinsi.
- Hasilnya dipakai untuk slide dan dashboard.

### 6.6 Klastering

1. Untuk setiap kabupaten, hitung rata-rata vektor TF-IDF dari semua nama desanya.
2. Opsional: perkecil dimensinya dengan TruncatedSVD.
3. Bandingkan K-Means dengan Agglomerative (Ward). Pilih jumlah klaster (k) berdasarkan silhouette score.
4. Bandingkan hasil klaster dengan provinsi asli memakai Adjusted Rand Index (ARI).
5. Warnai hasilnya di peta.

### 6.7 Analisis kesalahan

- **Jejak transmigrasi.** Di provinsi tujuan transmigrasi (Lampung, Sumatera Selatan, Jambi, Kalimantan, Sulawesi Tengah), hitung persentase desa yang ditebak sebagai provinsi di Jawa. Bandingkan dengan provinsi lain sebagai pembanding. Tampilkan contoh nama desanya.
- **Kandidat salah kode wilayah.** Cari desa yang tebakan model sangat yakin, tapi provinsinya berbeda dari label. Tampilkan sebagai daftar.

### 6.8 Generator nama desa (`src/generator.py`, notebook 05)

Cara kerjanya:

1. Untuk setiap wilayah, kumpulkan semua nama desanya.
2. Hitung huruf apa yang paling sering muncul setelah setiap potongan 3 huruf. Contohnya, setelah "rej" biasanya muncul "o".
3. Bangun nama baru huruf demi huruf berdasarkan peluang itu, sampai bertemu tanda akhir nama.
4. Buang nama hasil karangan yang ternyata sudah ada di data asli, supaya yang tersisa benar-benar nama baru.

Yang dihasilkan:

- Contoh nama karangan untuk tiap wilayah besar.
- **Uji ke classifier:** masukkan nama karangan ke model terbaik, lalu hitung berapa persen yang ditebak sesuai wilayah asalnya.
- **Bahan kuis "Asli atau Palsu?":** 10 nama campuran (5 asli, 5 karangan) untuk presentasi.

### 6.9 Dashboard (Streamlit)

Ada empat halaman:

1. **Tebak nama desa.** Pengguna mengetik nama desa, lalu muncul 3 provinsi teratas beserta probabilitasnya dan n-gram yang paling menentukan.
2. **Peta klaster kabupaten.**
3. **Fakta menarik.** Isinya nama desa yang paling sering muncul, n-gram khas tiap daerah, jejak transmigrasi, dan daftar kandidat salah kode wilayah.
4. **Generator dan kuis.** Pilih wilayah, lalu klik untuk mengarang nama desa baru. Ada juga mode kuis "Asli atau Palsu?" dan "Manusia vs Mesin".

### 6.10 Laporan dan presentasi

- Ikuti 7 tahap TBP: rumusan masalah, pengumpulan data, preprocessing, modeling, evaluasi, prototype, dan presentasi.
- Tiga momen interaktif di presentasi:
  1. **Demo tebak nama:** penonton menyebutkan nama desa kampung halamannya.
  2. **Kuis "Manusia vs Mesin":** penonton menebak provinsi dari 5 nama desa, lalu skornya dibandingkan dengan model.
  3. **Kuis "Asli atau Palsu?":** penonton menebak mana nama desa asli dan mana karangan model.
- Aturan asosiasi (Apriori/FP-Growth) pada kata penyusun nama desa tidak dikerjakan. Tulis sebagai saran pengembangan di laporan.

## 7. Pembagian tugas

| Peran | Tanggung jawab utama |
|---|---|
| P1 Data | unduh dan cek data, `clean.py`, EDA, README, reproduksibilitas |
| P2 Klasifikasi | 3 model x 2 target (RF opsional), tuning, simpan model |
| P3 Klastering dan Peta | `regions.py`, GeoJSON, klaster kabupaten, ARI, peta |
| P4 Analisis dan Generator | literatur, n-gram khas, analisis kesalahan, transmigrasi, generator nama desa, bahan kuis |
| P5 Dashboard dan Laporan | Streamlit, kerangka dan penulisan laporan, konsultasi ke dosen |

Isi nama anggota di setiap peran:

- P1:
- P2:
- P3:
- P4:
- P5:

### Siapa menguasai apa untuk presentasi

Tidak semua anggota harus menguasai semuanya.

- **Semua anggota:** paham gambaran besar proyek, alasan memakai n-gram karakter, dan jawaban untuk pertanyaan "kan bisa dicari di Google?" (bagian 2).
- **Masing-masing:** menguasai bagiannya sendiri secara mendalam.
  - P1: data, preprocessing, dan penanganan nama kembar.
  - P2: cara kerja dan alasan memilih NB, LR, dan SVM, serta arti tiap metrik.
  - P3: cara kerja K-Means dan Hierarchical, silhouette, dan ARI.
  - P4: analisis kesalahan, transmigrasi, dan cara kerja generator.
  - P5: alur dashboard dan jalannya demo.

## 8. Jadwal 5 hari

| Hari | P1 Data | P2 Klasifikasi | P3 Klastering dan Peta | P4 Analisis dan Generator | P5 Dashboard dan Laporan |
|---|---|---|---|---|---|
| 1 | unduh dan cek CSV, `clean.py` | setup repo, baseline NB | cari GeoJSON, `regions.py` | literatur dan EDA | kerangka laporan, konsultasi dosen |
| 2 | finalisasi data, EDA nama kembar | 3 model x 2 target | klaster kabupaten | n-gram khas per daerah, mulai generator | kerangka Streamlit |
| 3 | bantu tim, README | tuning, top-3, simpan model, RF kalau sempat | peta klaster, ARI | analisis kesalahan, transmigrasi, uji generator ke classifier | halaman tebak nama |
| 4 | cek reproduksibilitas | interpretasi hasil | interpretasi hasil | rangkum temuan, siapkan 2 kuis | halaman peta, fakta, generator, tulis laporan |
| 5 | slide, latihan tanya jawab | slide, latihan tanya jawab | slide, latihan tanya jawab | slide, latihan tanya jawab | gladi demo dan kuis, finalisasi laporan |

## 9. Bonus opsional (hanya kalau hari 4 longgar)

GeoNames (geonames.org) berisi nama tempat dari seluruh dunia. Ada dua cara memakainya:

1. **Uji generalisasi.** Ambil nama tempat Indonesia dari GeoNames yang tidak ada di data Kemendagri, lalu cek apakah model tetap bisa menebak provinsinya dengan benar.
2. **Versi dunia.** Tebak negara dari nama kota memakai subset `cities1000`, dengan kolom `asciiname` dan `country code`. Batasi ke 30 sampai 50 negara.

## 10. Risiko dan cara mengatasinya

| Risiko | Cara mengatasi |
|---|---|
| Provinsi hasil pemekaran (6 provinsi Papua, Kalimantan Utara, Sulawesi Barat) hampir mustahil dibedakan dari nama | laporkan juga hasil tingkat wilayah besar dan top-3, lalu jadikan temuan |
| Nama kembar membuat akurasi palsu | split data per nama unik |
| Kelas tidak seimbang | pakai macro-F1 dan class weight |
| GeoJSON kabupaten tidak tersedia | turun ke peta tingkat provinsi |

## 11. Aturan kerja bersama

- **Fungsi bersama** hanya ditulis di `src/`. Notebook dan app mengimpor dari sana, tidak menyalin kode.
- **Data mentah** di `data/raw/` jangan diubah. Hasil olahan disimpan di `data/processed/`.
- **Notebook** harus bisa dijalankan dari awal sampai akhir (Restart and Run All) tanpa error sebelum di-commit.
- **Commit** kecil-kecil, dengan pesan yang jelas tentang apa yang diubah.

## 12. Checklist selesai

- [ ] Notebook 01 sampai 05 berjalan berurutan dari clone baru tanpa error.
- [ ] Ada assert di notebook 02 yang memastikan tidak ada nama yang muncul di data latih dan uji sekaligus.
- [ ] Tabel accuracy, macro-F1, dan top-3 untuk 3 model x 2 target sudah ada, dan pilihan model terbaik dijelaskan dengan angka.
- [ ] Alasan memilih tiap model tertulis di laporan.
- [ ] Hasil klastering lengkap dengan silhouette, ARI, dan peta.
- [ ] Analisis transmigrasi dan daftar kandidat salah kode wilayah sudah ada.
- [ ] Generator menghasilkan nama baru (tidak ada di data asli) untuk tiap wilayah besar, dan hasil ujinya ke classifier sudah dilaporkan.
- [ ] Bahan dua kuis (Manusia vs Mesin, Asli atau Palsu) siap dipakai.
- [ ] `streamlit run app/streamlit_app.py` berjalan, dan sudah diuji dengan 10 nama desa asli (sebagian dari luar data latih) dan 3 nama karangan.
- [ ] Laporan mengikuti 7 tahap TBP.
- [ ] Slide selesai dan gladi demo sudah dilakukan.
