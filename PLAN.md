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
| Bonus (opsional) | GeoNames (geonames.org, CC-BY 4.0) | Hanya kalau ada sisa waktu di hari 4, lihat bagian 10 |

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

## 7. Tahapan pengerjaan

Pekerjaan dibagi menjadi 10 tahap. Setiap tahap punya penanggung jawab, hasil berupa file, dan syarat selesai. Tahap yang tidak saling bergantung dikerjakan paralel.

### Urutan dan ketergantungan

```
Tahap 0 Persiapan
   |
Tahap 1 Data bersih  ------------------------------------------+
   |                                                           |
   +--> Tahap 2 EDA                                            |
   +--> Tahap 3 Klasifikasi --+--> Tahap 5 Analisis kesalahan  |
   +--> Tahap 4 Klastering    +--> Tahap 6 Generator (uji)     |
   |                          +--> Tahap 7 Dashboard (final)   |
   +--> Tahap 6 Generator (membuat nama, tidak perlu model)    |
                                                               |
Tahap 8 Laporan (berjalan sejak hari 1) <----------------------+
   |
Tahap 9 Presentasi dan gladi
```

Artinya: **Tahap 1 harus selesai paling dulu**, karena semua orang memakai file hasilnya. **Tahap 3 jadi kunci kedua**, karena analisis kesalahan, uji generator, dan dashboard butuh model yang sudah tersimpan.

### Kontrak file antar tahap

Supaya bisa kerja paralel tanpa saling tunggu, semua orang memakai nama file dan kolom berikut. Jangan diubah tanpa memberi tahu tim.

| File | Dibuat di | Isi |
|---|---|---|
| `data/raw/wilayah_2025.csv` | Tahap 1 | data asli, tidak boleh diubah |
| `data/processed/desa_clean.parquet` | Tahap 1 | kolom: `kode_desa`, `nama_asli`, `nama_bersih`, `kabupaten`, `provinsi`, `wilayah` (7 wilayah besar) |
| `models/best_provinsi.joblib` | Tahap 3 | pipeline TF-IDF + model terbaik untuk target provinsi |
| `models/best_wilayah.joblib` | Tahap 3 | pipeline TF-IDF + model terbaik untuk target wilayah besar |
| `data/processed/klaster_kabupaten.csv` | Tahap 4 | kolom: `kabupaten`, `provinsi`, `klaster` |
| `data/processed/kandidat_salah_kode.csv` | Tahap 5 | desa yang namanya sangat tidak cocok dengan provinsinya |
| `data/processed/nama_karangan.csv` | Tahap 6 | kolom: `wilayah`, `nama_karangan`, `tebakan_model` |
| `reports/figures/` | semua tahap | semua grafik untuk laporan dan slide, format PNG |

### Tahap 0. Persiapan (hari 1, pagi, semua anggota)

Langkah:
1. Clone repo dan buat struktur folder sesuai bagian 5.
2. Buat `requirements.txt`, lalu setiap anggota memasang library di laptop masing-masing.
3. Buat `.gitignore` untuk folder cache Python dan checkpoint notebook. File di `data/processed/` dan `models/` tetap di-commit, karena anggota lain membutuhkannya untuk bekerja paralel. Kalau ada file model lebih dari 50 MB, bagikan lewat Google Drive dan tulis tautannya di README.
4. Isi nama anggota di bagian 8.
5. P5 menyampaikan judul baru ke dosen dan mengisi kolom algoritma dan dataset di sheet kelompok.

Selesai jika: semua anggota bisa menjalankan `python -c "import sklearn, pandas, streamlit"` tanpa error.

### Tahap 1. Data bersih (hari 1, P1, dibantu P3)

Langkah:
1. Unduh CSV Kepmendagri 2025 ke `data/raw/wilayah_2025.csv`.
2. Cek nama kolom, jumlah baris, dan encoding. Catat hasilnya di README.
3. P1 menulis `src/clean.py` (aturan di 6.1). P3 menulis `src/regions.py` (pemetaan 38 provinsi ke 7 wilayah besar).
4. Ambil hanya baris tingkat desa atau kelurahan, lalu buat kolom sesuai kontrak file.
5. Simpan ke `data/processed/desa_clean.parquet`, lalu umumkan ke grup.

Selesai jika: file parquet ada, kolomnya sesuai kontrak, jumlah baris sekitar 83 ribu, dan tidak ada `nama_bersih` yang kosong.

### Tahap 2. EDA (hari 1 sampai 2, P1 dan P4)

Notebook: `01_eda.ipynb`.

Langkah:
1. Jumlah desa per provinsi dan per wilayah besar, dalam bentuk grafik batang.
2. Distribusi panjang nama desa.
3. Nama desa paling sering muncul dan nama kembar lintas provinsi, misalnya Sukamaju.
4. Awalan dan akhiran paling umum per wilayah, sebagai gambaran awal.

Selesai jika: minimal 4 grafik tersimpan di `reports/figures/`, ditambah ringkasan temuan 5 sampai 10 kalimat di notebook.

### Tahap 3. Klasifikasi (hari 2 sampai 3, P2)

Notebook: `02_classification.ipynb`.

Langkah:
1. Split data dengan `GroupShuffleSplit` berdasarkan `nama_bersih` (80 persen latih, 20 persen uji). Tambahkan assert bahwa tidak ada nama yang muncul di keduanya.
2. Buat pipeline TF-IDF n-gram karakter + model untuk NB, LR, dan SVM.
3. Latih untuk dua target: `provinsi` dan `wilayah`.
4. Hitung accuracy, macro-F1, dan top-3 accuracy, lalu buat tabel perbandingan.
5. Tuning ringan untuk model terbaik, misalnya nilai `C` pada LR atau SVM dan rentang n-gram.
6. Simpan model terbaik ke `models/best_provinsi.joblib` dan `models/best_wilayah.joblib`, lalu umumkan ke grup.
7. Kalau masih sempat, tambahkan Random Forest sebagai pembanding.

Selesai jika: tabel 3 model x 2 target ada, dua file model tersimpan, dan assert split lolos.

### Tahap 4. Klastering dan peta (hari 2 sampai 3, P3)

Notebook: `03_clustering.ipynb`.

Langkah:
1. Untuk setiap kabupaten, hitung rata-rata vektor TF-IDF nama-nama desanya.
2. Opsional: perkecil dimensi dengan TruncatedSVD.
3. Jalankan K-Means dan Agglomerative (Ward) untuk beberapa nilai k, lalu pilih k terbaik dengan silhouette score.
4. Hitung ARI terhadap provinsi asli.
5. Buat peta berwarna sesuai klaster. Pakai GeoJSON kabupaten, atau GeoJSON provinsi kalau versi kabupaten tidak ada.
6. Simpan `data/processed/klaster_kabupaten.csv`.

Selesai jika: tabel silhouette dan ARI untuk kedua metode ada, peta tersimpan, dan file klaster tersimpan.

### Tahap 5. N-gram khas dan analisis kesalahan (hari 3, P4)

Notebook: `04_error_analysis.ipynb`. Butuh model dari Tahap 3.

Langkah:
1. Ambil n-gram dengan koefisien terbesar per provinsi dari model Logistic Regression.
2. Buat confusion matrix tingkat wilayah besar.
3. Analisis transmigrasi: persentase desa di Lampung, Sumatera Selatan, Jambi, Kalimantan, dan Sulawesi Tengah yang ditebak sebagai provinsi di Jawa, dibandingkan dengan provinsi lain. Sertakan contoh nama.
4. Kandidat salah kode wilayah: desa yang tebakan modelnya sangat yakin tapi berbeda dari label. Simpan ke `data/processed/kandidat_salah_kode.csv`.

Selesai jika: tabel n-gram khas, confusion matrix, grafik transmigrasi, dan file kandidat salah kode sudah ada.

### Tahap 6. Generator nama desa (hari 2 sampai 3, P4)

Kode: `src/generator.py`. Notebook: `05_generator.ipynb`.

Langkah:
1. Tulis generator n-gram karakter (aturan di 6.8). Membuat nama tidak butuh model klasifikasi, jadi bisa dimulai di hari 2.
2. Hasilkan sekitar 50 nama per wilayah besar, lalu buang nama yang sudah ada di data asli.
3. Setelah model dari Tahap 3 tersedia, tebak wilayah nama-nama karangan itu dan hitung persentase yang benar.
4. Simpan `data/processed/nama_karangan.csv`.
5. Siapkan bahan dua kuis: 5 nama desa untuk "Manusia vs Mesin", dan 10 nama campuran (5 asli, 5 karangan) untuk "Asli atau Palsu?".

Selesai jika: file nama karangan ada, persentase tebakan benar sudah dilaporkan, dan bahan kuis siap.

### Tahap 7. Dashboard (hari 2 sampai 4, P5)

Kode: `app/streamlit_app.py`.

Langkah:
1. Hari 2: buat kerangka 4 halaman dengan data contoh, supaya tidak menunggu model.
2. Hari 3: sambungkan halaman "Tebak nama desa" ke `models/best_provinsi.joblib`. Gunakan `src/clean.py` untuk membersihkan input.
3. Hari 4: sambungkan halaman peta, fakta menarik, serta generator dan kuis ke file hasil Tahap 4, 5, dan 6.
4. Uji dengan 10 nama desa asli (sebagian dari luar data latih) dan 3 nama karangan.

Selesai jika: `streamlit run app/streamlit_app.py` berjalan dan keempat halaman berfungsi.

### Tahap 8. Laporan (hari 1 sampai 4, P5, semua anggota menyumbang)

Langkah:
1. Hari 1: buat kerangka laporan mengikuti 7 tahap TBP.
2. Setiap penanggung jawab tahap menulis bagiannya sendiri: metode, hasil, dan grafik dari `reports/figures/`.
3. P5 menyatukan, merapikan bahasa, dan menambahkan bagian keterbatasan dan saran pengembangan (termasuk Apriori dan versi dunia).

Selesai jika: semua bagian terisi, semua grafik punya keterangan, dan daftar pustaka lengkap.

### Tahap 9. Presentasi dan gladi (hari 5, semua anggota)

Langkah:
1. Susun slide. Setiap anggota membuat slide bagiannya sendiri.
2. Siapkan dashboard di satu laptop yang dipakai untuk demo. Siapkan juga cadangan berupa rekaman layar kalau demo gagal.
3. Gladi lengkap: alur presentasi, demo tebak nama, dan kedua kuis.
4. Latihan tanya jawab: saling menguji pertanyaan yang kemungkinan ditanyakan dosen, misalnya "kan bisa dicari di Google?", "kenapa pakai n-gram karakter?", dan "kenapa split per nama unik?".

Selesai jika: gladi berjalan lancar dalam batas waktu, dan setiap anggota bisa menjawab pertanyaan tentang bagiannya.

## 8. Pembagian tugas

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

## 9. Jadwal 5 hari

| Hari | P1 Data | P2 Klasifikasi | P3 Klastering dan Peta | P4 Analisis dan Generator | P5 Dashboard dan Laporan |
|---|---|---|---|---|---|
| 1 | unduh dan cek CSV, `clean.py` | setup repo, baseline NB | cari GeoJSON, `regions.py` | literatur dan EDA | kerangka laporan, konsultasi dosen |
| 2 | finalisasi data, EDA nama kembar | 3 model x 2 target | klaster kabupaten | n-gram khas per daerah, mulai generator | kerangka Streamlit |
| 3 | bantu tim, README | tuning, top-3, simpan model, RF kalau sempat | peta klaster, ARI | analisis kesalahan, transmigrasi, uji generator ke classifier | halaman tebak nama |
| 4 | cek reproduksibilitas | interpretasi hasil | interpretasi hasil | rangkum temuan, siapkan 2 kuis | halaman peta, fakta, generator, tulis laporan |
| 5 | slide, latihan tanya jawab | slide, latihan tanya jawab | slide, latihan tanya jawab | slide, latihan tanya jawab | gladi demo dan kuis, finalisasi laporan |

## 10. Bonus opsional (hanya kalau hari 4 longgar)

GeoNames (geonames.org) berisi nama tempat dari seluruh dunia. Ada dua cara memakainya:

1. **Uji generalisasi.** Ambil nama tempat Indonesia dari GeoNames yang tidak ada di data Kemendagri, lalu cek apakah model tetap bisa menebak provinsinya dengan benar.
2. **Versi dunia.** Tebak negara dari nama kota memakai subset `cities1000`, dengan kolom `asciiname` dan `country code`. Batasi ke 30 sampai 50 negara.

## 11. Risiko dan cara mengatasinya

| Risiko | Cara mengatasi |
|---|---|
| Provinsi hasil pemekaran (6 provinsi Papua, Kalimantan Utara, Sulawesi Barat) hampir mustahil dibedakan dari nama | laporkan juga hasil tingkat wilayah besar dan top-3, lalu jadikan temuan |
| Nama kembar membuat akurasi palsu | split data per nama unik |
| Kelas tidak seimbang | pakai macro-F1 dan class weight |
| GeoJSON kabupaten tidak tersedia | turun ke peta tingkat provinsi |

## 12. Aturan kerja bersama

- **Fungsi bersama** hanya ditulis di `src/`. Notebook dan app mengimpor dari sana, tidak menyalin kode.
- **Data mentah** di `data/raw/` jangan diubah. Hasil olahan disimpan di `data/processed/`.
- **Notebook** harus bisa dijalankan dari awal sampai akhir (Restart and Run All) tanpa error sebelum di-commit.
- **Commit** kecil-kecil, dengan pesan yang jelas tentang apa yang diubah.

## 13. Checklist selesai

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
