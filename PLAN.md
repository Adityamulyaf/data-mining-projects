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
| Kode wilayah 2025 (utama) | github.com/cahyadsn/wilayah, file `db/wilayah.sql` (lisensi MIT) | Kepmendagri No 300.2.2-2138 Tahun 2025. Sudah diunduh ke `data/raw/wilayah.sql` dan diubah ke `data/raw/wilayah_2025.csv` dengan `src/convert_wilayah.py` |
| Peta | github.com/cahyadsn/wilayah, file `db/wilayah_level_1_2.sql` (lisensi MIT) | batas 38 provinsi dan 514 kabupaten/kota, sudah diubah ke `data/geo/provinsi.geojson` dan `data/geo/kabupaten.geojson` dengan `src/convert_geo.py`. Kodenya cocok 100 persen dengan dataset |
| Bonus (opsional) | GeoNames (geonames.org, CC-BY 4.0) | Hanya kalau ada sisa waktu di hari 4, lihat bagian 9 |

Sumber yang sempat direncanakan sebelumnya (github.com/yonatanyl/KODE-WILAYAH-KEPMENDAGRI-2025) tidak dipakai. Filenya ternyata Excel, bukan CSV, dan datanya dibuat dari hasil OCR dokumen PDF, sehingga nama desanya berisiko mengandung salah ketik.

**Hasil pengecekan `data/raw/wilayah_2025.csv`:**

- Encoding UTF-8, satu baris per desa atau kelurahan.
- Kolom: `kode_desa`, `nama_desa`, `jenis`, `kode_kecamatan`, `nama_kecamatan`, `kode_kabupaten`, `nama_kabupaten`, `kode_provinsi`, `nama_provinsi`.
- Jumlah: 38 provinsi, 514 kabupaten/kota, 7.285 kecamatan, dan 83.762 desa/kelurahan (75.252 desa, 8.496 kelurahan, 14 desa adat). Angka ini cocok dengan angka resmi Kepmendagri.
- Kolom `jenis` dibaca dari digit pertama bagian terakhir kode: 1 kelurahan, 2 desa, 3 desa adat. Ke-14 desa adat semuanya ada di Kabupaten Jayapura dan namanya diawali "Desa Adat".
- Nama yang mengandung tanda petik, misalnya "Pasi Kuala Ba'u", sudah ditangani dengan benar.

## 5. Struktur repo

```
data-mining-projects/
  PLAN.md
  README.md
  requirements.txt
  .gitignore
  data/
    raw/wilayah.sql            (data asli dari cahyadsn)
    raw/wilayah_2025.csv       (hasil convert_wilayah.py)
    processed/desa_clean.parquet
    raw/wilayah_level_1_2.sql  (batas wilayah, 24 MB, tidak di-commit, diunduh otomatis oleh convert_geo.py)
    geo/provinsi.geojson       (batas 38 provinsi)
    geo/kabupaten.geojson      (batas 514 kabupaten/kota)
  notebooks/
    01_eda.ipynb               (distribusi, nama kembar, panjang nama)
    02_classification.ipynb    (NB vs LR vs SVM, RF opsional, 2 level label)
    03_clustering.ipynb        (klaster kabupaten, peta, ARI)
    04_error_analysis.ipynb    (confusion matrix, transmigrasi, cek kualitas data)
    05_generator.ipynb         (generator nama desa, uji ke classifier, bahan kuis)
  src/
    clean.py                   (normalisasi nama, dipakai notebook dan app)
    convert_wilayah.py         (ubah wilayah.sql menjadi wilayah_2025.csv)
    convert_geo.py             (ubah wilayah_level_1_2.sql menjadi GeoJSON di data/geo/)
    build_dataset.py           (buat desa_clean.parquet dari wilayah_2025.csv)
    regions.py                 (pemetaan provinsi ke 7 wilayah besar)
    peta.py                    (gambar peta provinsi/kabupaten dengan matplotlib, dipakai notebook 03 dan 04)
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

Sudah dibuat. Prinsipnya: buang yang administratif, pertahankan yang mengandung petunjuk budaya. Aturan berikut diputuskan setelah melihat data:

- Ubah ke huruf kecil, rapikan spasi.
- Buang awalan "Desa Adat" (14 desa di Kabupaten Jayapura). Kata "desa" lainnya **dipertahankan**, karena ternyata bagian dari nama asli, misalnya "Desa Baru".
- **Pertahankan** kata khas daerah di awal nama, karena justru menjadi petunjuk budaya. Contoh dari data: Gampong (82 desa, semuanya Aceh), Huta (99, semuanya Sumatera Utara), Lumban, Pekon dan Tiuh (Lampung), Negeri, Marga, Lembang, Kampung.
- Buang penanda pemekaran: angka romawi berdiri sendiri (I sampai XX, sekitar 1.270 nama) dan potongan yang mengandung angka ("Blok 15", "N-1 Aek Nabara"). Kata bilangan seperti "Dua" dipertahankan karena merupakan kata biasa.
- Perbaiki singkatan di Aceh: "Mns." menjadi meunasah, "Kp." menjadi kampung, "Tgk." menjadi teungku. Pisahkan kata yang menempel ("SeuneubokTeungoh" menjadi "seuneubok teungoh").
- Buang tanda baca, kecuali tanda petik (misalnya "kandua'" dan "ba'u", ciri bahasa di Sulawesi dan Aceh) dan tanda hubung (misalnya "sigurung-gurung").
- Nama yang tidak dipakai untuk model: singkatan huruf kapital semua ("OP", "MKCM", "WKO", "RD. PJKA"), total 4 nama. Nama asli yang pendek seperti "Tu", "Ur", dan "Uf" tetap dipakai, karena memang nama asli (kebanyakan di Papua, Maluku, dan NTT).
- Kolom nama asli tetap disimpan.
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

Pekerjaan dibagi menjadi 10 tahap. Setiap tahap punya hasil berupa file dan syarat selesai. Tahap yang tidak saling bergantung dikerjakan paralel.

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
| `data/raw/wilayah_2025.csv` | sudah ada | data asli dalam format CSV, tidak boleh diubah. Kolomnya lihat bagian 4 |
| `data/processed/desa_clean.parquet` | sudah ada | kolom: `kode_desa`, `nama_asli`, `nama_bersih`, `jenis`, `kode_kabupaten`, `kabupaten`, `kode_provinsi`, `provinsi`, `wilayah` (7 wilayah besar). Dibuat ulang dengan `python src/build_dataset.py` |
| `models/best_provinsi.joblib` | Tahap 3 | pipeline TF-IDF + model terbaik untuk target provinsi |
| `models/best_wilayah.joblib` | Tahap 3 | pipeline TF-IDF + model terbaik untuk target wilayah besar |
| `data/processed/klaster_kabupaten.csv` | sudah ada (Tahap 4) | kolom: `kode_kabupaten`, `kabupaten`, `provinsi`, `wilayah`, `klaster` (hasil utama), `klaster_kmeans`, `klaster_ward`, `nama_klaster`. Bisa langsung digambar dengan `src/peta.py` |
| `data/processed/prediksi_oof.parquet` | sudah ada (Tahap 5) | `kode_desa` + 38 kolom probabilitas provinsi (out-of-fold, setiap desa ditebak model yang belum pernah melihat namanya). Urutan baris sama dengan `desa_clean.parquet` |
| `data/processed/kandidat_salah_kode.csv` | sudah ada (Tahap 5) | kolom: `kode_desa`, `nama_asli`, `kabupaten`, `provinsi`, `tebakan`, `keyakinan`, `provinsi_lain_dengan_nama_sama` |
| `reports/ngram_khas_provinsi.csv`, `reports/ngram_khas_wilayah.csv` | sudah ada (Tahap 5) | 10 n-gram paling khas per kelas, dengan koefisien, jumlah desa, dan persen desa yang ada di kelas itu. Dipakai dashboard |
| `data/processed/nama_karangan.csv` | sudah ada (Tahap 6) | kolom: `wilayah`, `nama_karangan`, `tebakan_model`, `keyakinan`, `dikenali`, `orde`. 50 nama per wilayah |
| `data/processed/kuis_asli_palsu.csv`, `data/processed/kuis_manusia_vs_mesin.csv` | sudah ada (Tahap 6) | bahan dua kuis presentasi, lengkap dengan kunci jawaban |
| `reports/figures/` | semua tahap | semua grafik untuk laporan dan slide, format PNG |

### Tahap 0. Persiapan (hari 1, pagi, semua anggota)

Langkah:
1. Clone repo dan buat struktur folder sesuai bagian 5.
2. Buat `requirements.txt`, lalu setiap anggota memasang library di laptop masing-masing.
3. Buat `.gitignore` untuk folder cache Python dan checkpoint notebook. File di `data/processed/` dan `models/` tetap di-commit, karena anggota lain membutuhkannya untuk bekerja paralel. Kalau ada file model lebih dari 50 MB, bagikan lewat Google Drive dan tulis tautannya di README.
4. Sampaikan judul baru ke dosen dan mengisi kolom algoritma dan dataset di sheet kelompok.

Selesai jika: semua anggota bisa menjalankan `python -c "import sklearn, pandas, streamlit"` tanpa error.

### Tahap 1. Data bersih (hari 1)

Langkah:
1. Sudah selesai: data diunduh ke `data/raw/wilayah.sql` dan diubah menjadi `data/raw/wilayah_2025.csv` dengan `python src/convert_wilayah.py`. Hasil pengecekannya ada di bagian 4.
2. Sudah selesai: `python src/convert_geo.py` mengubah batas wilayah cahyadsn menjadi `data/geo/provinsi.geojson` (1,1 MB) dan `data/geo/kabupaten.geojson` (6,6 MB). Kode di GeoJSON (`id` fitur, misalnya "11" dan "11.01") sama dengan `kode_provinsi` dan `kode_kabupaten` di parquet, jadi bisa langsung dipakai di `plotly.express.choropleth` dengan `featureidkey="id"`.
3. Sudah selesai: `src/clean.py` (aturan di 6.1) dan `src/regions.py` (38 provinsi ke 7 wilayah besar).
4. Sudah selesai: `python src/build_dataset.py` menghasilkan `data/processed/desa_clean.parquet`.

Status: **selesai**. Hasilnya:

- 83.758 baris (4 singkatan dibuang dari 83.762), 62.769 nama bersih unik, 38 provinsi, 7 wilayah.
- Tidak ada nilai kosong.
- Sebaran per wilayah: Sumatera 25.555, Jawa 25.271, Sulawesi 10.575, Papua 7.355, Kalimantan 7.252, Bali dan Nusa Tenggara 5.321, Maluku 2.416.
- Nama kembar: 4.250 nama bersih muncul di lebih dari satu provinsi, mencakup 19.771 baris. Paling sering: sidomulyo (98), sidorejo (71), karanganyar (70), mekar jaya (66), sukamaju (65). Ini bahan bagus untuk EDA, sekaligus alasan kenapa split harus per nama unik.

### Tahap 2. EDA (hari 1 sampai 2)

Notebook: `01_eda.ipynb`.

Langkah:
1. Jumlah desa per provinsi dan per wilayah besar, dalam bentuk grafik batang.
2. Distribusi panjang nama desa.
3. Nama desa paling sering muncul dan nama kembar lintas provinsi, misalnya Sukamaju.
4. Awalan dan akhiran paling umum per wilayah, sebagai gambaran awal.

Selesai jika: minimal 4 grafik tersimpan di `reports/figures/`, ditambah ringkasan temuan 5 sampai 10 kalimat di notebook.

Status: **selesai** (`notebooks/01_eda.ipynb`). Grafik: `01_jumlah_desa.png`, `01_panjang_nama.png`, `01_nama_kembar.png`, `01_kata_pertama.png`. Ringkasan 7 poin ada di akhir notebook, antara lain: jumlah desa timpang sampai 32 kali lipat, 64 persen nama hanya satu kata, 4.250 nama dipakai di lebih dari satu provinsi, dan kata pertama khas wilayah (sungai, tumbang, nanga di Kalimantan; bonto di Sulawesi; golo di Nusa Tenggara).

### Tahap 3. Klasifikasi (hari 2 sampai 3)

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

Status: **baseline selesai** (`notebooks/02_classification.ipynb`). Langkah 5 (tuning) dan 7 (Random Forest) belum.

| Target | Model | Accuracy | Macro-F1 | Top-3 |
|---|---|---|---|---|
| Provinsi (38 kelas) | Pembanding: tebak kelas terbanyak | 0,100 | 0,005 | - |
| | Naive Bayes | 0,419 | 0,304 | 0,648 |
| | Logistic Regression | 0,401 | 0,330 | 0,642 |
| | SVM | 0,402 | 0,328 | 0,620 |
| Wilayah (7 kelas) | Pembanding: tebak kelas terbanyak | 0,307 | 0,067 | - |
| | Naive Bayes | 0,654 | 0,541 | 0,899 |
| | Logistic Regression | 0,651 | 0,557 | 0,892 |
| | SVM | 0,678 | 0,571 | 0,895 |

- Split per nama unik: 50.215 nama latih, 12.554 nama uji, tidak ada yang bocor.
- Tebakan acak hanya 2,6 persen untuk provinsi, jadi akurasi 40 persen berarti sekitar 15 kali lebih baik dari acak.
- Model yang disimpan untuk kedua target adalah **Logistic Regression**, dilatih ulang dengan seluruh data. Alasannya, selisih macro-F1 dengan model terbaik kecil (0 untuk provinsi, 0,014 untuk wilayah), dan hanya LR yang memberi probabilitas untuk dashboard serta koefisien untuk analisis n-gram khas.
- File: `models/best_provinsi.joblib` (8,3 MB), `models/best_wilayah.joblib` (1,7 MB), `reports/metrics_baseline.csv`, `reports/figures/02_perbandingan_model.png`.

### Tahap 4. Klastering dan peta (hari 2 sampai 3)

Notebook: `03_clustering.ipynb`.

Langkah:
1. Untuk setiap kabupaten, hitung rata-rata vektor TF-IDF nama-nama desanya.
2. Opsional: perkecil dimensi dengan TruncatedSVD.
3. Jalankan K-Means dan Agglomerative (Ward) untuk beberapa nilai k, lalu pilih k terbaik dengan silhouette score.
4. Hitung ARI terhadap provinsi asli.
5. Buat peta berwarna sesuai klaster. Pakai `data/geo/kabupaten.geojson` (sudah dicek: 514 kabupaten, semua kode cocok).
6. Simpan `data/processed/klaster_kabupaten.csv`.

Selesai jika: tabel silhouette dan ARI untuk kedua metode ada, peta tersimpan, dan file klaster tersimpan.

Status: **selesai** (`notebooks/03_clustering.ipynb`). Pengaturan: vektor kabupaten = rata-rata TF-IDF nama desanya, TruncatedSVD 20 dimensi, k = 7, K-Means sebagai hasil utama (silhouette 0,247 vs Ward 0,222). Silhouette tertinggi sebenarnya di k = 13 (0,267), tetapi selisihnya kecil; k = 7 dipilih karena puncak lokal pertama, masih bisa dijelaskan, dan bisa dibandingkan langsung dengan 7 wilayah. Alasan ini harus ditulis terus terang di laporan.

Temuan utama (bahan "wow" untuk presentasi):

- Tanpa label apa pun, Pulau Jawa terbelah menjadi klaster Sunda (Jawa Barat, Banten) dan Jawa (Jawa Tengah, DIY, Jawa Timur).
- Klaster memotong batas provinsi mengikuti batas suku: Aceh pesisir terpisah dari Gayo dan Alas; Sumatera Utara terbelah menjadi tanah Batak, pesisir Melayu, dan Nias; Kota Metro dan Pringsewu (Lampung) masuk klaster Jawa; kabupaten Dayak pedalaman di Kalimantan Tengah terpisah dari pesisir.
- Sebagian besar Sumatera dan Kalimantan menjadi satu klaster Melayu.
- Keterbatasan: Bali tidak membentuk klaster sendiri.
- ARI terhadap 7 wilayah resmi: 0,42 (K-Means) dan 0,46 (Ward). ARI terhadap provinsi: 0,17 dan 0,18.

Grafik: `03_pemilihan_k.png`, `03_peta_klaster.png`, `03_peta_klaster_pembanding.png`. Tabel: `reports/metrics_klastering.csv`, `reports/ringkasan_klaster.csv`.

### Tahap 5. N-gram khas dan analisis kesalahan (hari 3)

Notebook: `04_error_analysis.ipynb`. Butuh model dari Tahap 3.

Langkah:
1. Ambil n-gram dengan koefisien terbesar per provinsi dari model Logistic Regression.
2. Buat confusion matrix tingkat wilayah besar.
3. Analisis transmigrasi: persentase desa di Lampung, Sumatera Selatan, Jambi, Kalimantan, dan Sulawesi Tengah yang ditebak sebagai provinsi di Jawa, dibandingkan dengan provinsi lain. Sertakan contoh nama.
4. Kandidat salah kode wilayah: desa yang tebakan modelnya sangat yakin tapi berbeda dari label. Simpan ke `data/processed/kandidat_salah_kode.csv`.

Selesai jika: tabel n-gram khas, confusion matrix, grafik transmigrasi, dan file kandidat salah kode sudah ada.

Status: **selesai** (`notebooks/04_error_analysis.ipynb`). Catatan metode: analisis kesalahan memakai tebakan out-of-fold (GroupKFold 5 lipatan per nama unik), bukan model di `models/`, karena model itu sudah melihat semua desa. Hasilnya disimpan di `prediksi_oof.parquet`; hitung ulang sekitar 8 sampai 10 menit kalau file itu dihapus.

Temuan utama:

- N-gram khas cocok dengan pengetahuan bahasa daerah: `_ci` dan `eu` (Sunda), `eu`/`ie`/`blang` (Aceh), `pp`/`ll`/`kk`/`bont` (Bugis-Makassar), `oe` (Timor), `way` (Lampung), `koto` (Minang), `aek`/`lau` (Batak).
- Kesalahan terbanyak antara provinsi bertetangga atau pemekaran: DIY ke Jawa Tengah 29 persen, Banten ke Jawa Barat 28 persen. Di tingkat wilayah, 26 persen desa Kalimantan ditebak Sumatera (kosakata Melayu yang sama).
- Jejak transmigrasi: desa luar Jawa yang ditebak "Jawa" 8,4 persen di provinsi tujuan transmigrasi vs 4,3 persen di provinsi lain. Paling kuat di Lampung (16,3 persen), terutama Kota Metro (45 persen) dan Pringsewu (34 persen). Di Kalimantan dan Sulawesi Tengah tidak jauh di atas rata-rata.
- Bukti tanpa model: 96 desa di luar Jawa memakai nama kabupaten/kota di Jawa (Purworejo, Sukoharjo, Banyumas, Klaten, Bantul, dan lain-lain), 41 di antaranya di Lampung.
- Bali 17,9 persen ditebak Jawa, bukan karena transmigrasi tapi karena kedekatan budaya Jawa-Bali.
- Kandidat salah kode wilayah hanya 62 desa (0,07 persen), sebagian besar nama pendek yang kebetulan mirip pola daerah lain. Tidak ditemukan tanda jelas kesalahan kode di data Kepmendagri 2025.

Grafik: `04_ngram_khas.png`, `04_confusion_wilayah.png`, `04_transmigrasi_provinsi.png`, `04_peta_jejak_jawa.png`.

### Tahap 6. Generator nama desa (hari 2 sampai 3)

Kode: `src/generator.py`. Notebook: `05_generator.ipynb`.

Langkah:
1. Tulis generator n-gram karakter (aturan di 6.8). Membuat nama tidak butuh model klasifikasi, jadi bisa dimulai di hari 2.
2. Hasilkan sekitar 50 nama per wilayah besar, lalu buang nama yang sudah ada di data asli.
3. Setelah model dari Tahap 3 tersedia, tebak wilayah nama-nama karangan itu dan hitung persentase yang benar.
4. Simpan `data/processed/nama_karangan.csv`.
5. Siapkan bahan dua kuis: 5 nama desa untuk "Manusia vs Mesin", dan 10 nama campuran (5 asli, 5 karangan) untuk "Asli atau Palsu?".

Selesai jika: file nama karangan ada, persentase tebakan benar sudah dilaporkan, dan bahan kuis siap.

Status: **selesai** (`src/generator.py`, `notebooks/05_generator.ipynb`).

- Orde dipilih dari perbandingan: orde 2 (90 persen baru, 55 persen dikenali), orde 3 (86 persen baru, 72 persen dikenali), orde 4 (69 persen baru, 74 persen dikenali). Orde 3 dipakai.
- 350 nama karangan (50 per wilayah), 71 persen ditebak classifier sesuai wilayah asalnya (tebakan acak 14 persen). Paling mudah dikenali: Sulawesi (80 persen) dan Papua (78 persen); paling sulit: Sumatera (60 persen).
- Contoh nama karangan: Cikayung, Lebangwetan (Jawa); Lubuk Simodo, Teluk Lam Ilit (Sumatera); Lintai Hilir (Kalimantan); Wugunggunome, Abagalo (Papua).
- Kuis "Asli atau Palsu?": 10 nama siap di `kuis_asli_palsu.csv`. Kuis "Manusia vs Mesin": 5 nama di `kuis_manusia_vs_mesin.csv`, tebakan mesin diambil dari prediksi out-of-fold (mesin benar 2 dari 5, wajar karena akurasi provinsi sekitar 40 persen). Ganti `SEED` di notebook untuk set lain.
- Catatan jujur untuk laporan: nama karangan cenderung memakai pola paling umum di wilayahnya, jadi wajar lebih mudah dikenali daripada nama asli (akurasi nama asli sekitar 65 persen).

### Tahap 7. Dashboard (hari 2 sampai 4)

Kode: `app/streamlit_app.py`.

Langkah:
1. Hari 2: buat kerangka 4 halaman dengan data contoh, supaya tidak menunggu model.
2. Hari 3: sambungkan halaman "Tebak nama desa" ke `models/best_provinsi.joblib`. Gunakan `src/clean.py` untuk membersihkan input.
3. Hari 4: sambungkan halaman peta, fakta menarik, serta generator dan kuis ke file hasil Tahap 4, 5, dan 6.
4. Uji dengan 10 nama desa asli (sebagian dari luar data latih) dan 3 nama karangan.

Selesai jika: `streamlit run app/streamlit_app.py` berjalan dan keempat halaman berfungsi.

Status: **selesai, versi pertama**. Keempat halaman berjalan dan sudah diuji (AppTest dan screenshot):

1. **Tebak nama desa**: ketik nama, muncul 3 provinsi teratas, peta peluang per provinsi, dan huruf yang paling mendorong tebakan diwarnai langsung di nama desanya (dari koefisien LR).
2. **Peta klaster**: peta kabupaten, bisa berganti antara K-Means, Ward, dan 7 wilayah resmi, plus tabel isi klaster.
3. **Fakta menarik**: n-gram khas per provinsi (bisa dipilih), peta jejak transmigrasi per kabupaten, 20 nama desa paling umum, dan daftar nama yang "nyasar".
4. **Generator dan kuis**: karang 6 nama per wilayah beserta tebakan classifier, kuis "Asli atau Palsu?" dengan skor, dan kuis "Manusia vs Mesin".

Tampilan: tema warna kertas peta di `.streamlit/config.toml`, huruf Young Serif (judul dan nama desa) dan Public Sans (teks), dimuat dari Google Fonts, jadi butuh internet saat presentasi (kalau tidak ada, otomatis memakai huruf bawaan).

Yang masih bisa dikerjakan: uji dengan 10 nama desa asli dan 3 nama karangan (langkah 4), rapikan teks, dan latihan demo. Peta kabupaten (6,6 MB) butuh beberapa detik saat pertama dibuka.

### Tahap 8. Laporan (hari 1 sampai 4, semua anggota)

Langkah:
1. Hari 1: buat kerangka laporan mengikuti 7 tahap TBP.
2. Tulis metode, hasil, dan grafik dari `reports/figures/` untuk tiap tahap.
3. Satukan, rapikan bahasa, dan tambahkan bagian keterbatasan dan saran pengembangan (termasuk Apriori dan versi dunia).

Selesai jika: semua bagian terisi, semua grafik punya keterangan, dan daftar pustaka lengkap.

### Tahap 9. Presentasi dan gladi (hari 5, semua anggota)

Langkah:
1. Susun slide.
2. Siapkan dashboard di satu laptop yang dipakai untuk demo. Siapkan juga cadangan berupa rekaman layar kalau demo gagal.
3. Gladi lengkap: alur presentasi, demo tebak nama, dan kedua kuis.
4. Latihan tanya jawab: saling menguji pertanyaan yang kemungkinan ditanyakan dosen, misalnya "kan bisa dicari di Google?", "kenapa pakai n-gram karakter?", dan "kenapa split per nama unik?".

Selesai jika: gladi berjalan lancar dalam batas waktu, dan setiap anggota bisa menjawab pertanyaan tentang seluruh bagian proyek.

## 8. Jadwal 5 hari

Semua anggota mengerjakan dan memahami semua bagian; tidak ada pembagian peran.

| Hari | Kegiatan |
|---|---|
| 1 | `clean.py` dan parquet bersih, setup repo, baseline NB, cek data batas wilayah dan `regions.py`, literatur dan EDA, kerangka laporan, konsultasi dosen |
| 2 | finalisasi data dan EDA nama kembar, 3 model x 2 target, klaster kabupaten, n-gram khas per daerah, mulai generator, kerangka Streamlit |
| 3 | tuning, top-3, simpan model, peta klaster dan ARI, analisis kesalahan dan transmigrasi, uji generator ke classifier, halaman tebak nama, README |
| 4 | cek reproduksibilitas, interpretasi hasil, rangkum temuan, siapkan 2 kuis, halaman peta, fakta, dan generator, tulis laporan |
| 5 | slide, latihan tanya jawab, gladi demo dan kuis, finalisasi laporan |

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
| Batas wilayah kabupaten tidak bisa dipakai | cari GeoJSON lain, atau turun ke peta tingkat provinsi |

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
