# Multi-DBMS Data Pipeline & Web Visualization: Analitik Rantai Pasok Hortikultura Jawa Barat

Proyek ini disusun untuk memenuhi **Tugas Mandiri Terstruktur Mata Kuliah Visualisasi Data dan Informasi** (Program Studi Informatika, Dosen Pengampu: Irfan Fadil).

## 1. Identitas Mahasiswa
* **Nama Lengkap:** Adin Setia Mulya
* **Program Studi:** Informatika - Universitas Sebelas April

## 2. Daftar Tautan Utama
* **URL Live Web Application:** *(https://tugas-visualisasi-data-erqflv2qfuasrhwbf9bb8r.streamlit.app/ )*
* **URL Repositori GitHub:** *(https://github.com/Adinsetiamulya0/Tugas-Visualisasi-data.git)*
* **URL Sumber Data Asli (Primer):**
  1. [Open Data Jabar - Data Produksi Hortikultura Kabupaten/Kota Jawa Barat](https://opendata.jabarprov.go.id/id/dataset/produksi-tanaman-sayuran-dan-buah-buahan-semusim-berdasarkan-kabupatenkota-di-jawa-barat)
  2. [Panel Harga Pangan Badan Pangan Nasional (Bapanas)](https://panelharga.badanpangan.go.id/)
* **URL Referensi Kode/Proyek:**
  1. [Streamlit Database Connections & SQLAlchemy Official Guide](https://docs.streamlit.io/develop/tutorials/databases/postgresql)
  2. [Plotly Express Interactive Mapbox & Sunburst Charts](https://plotly.com/python/plotly-express/)

## 3. Ringkasan Arsitektur Multi-DBMS
Sistem ini menerapkan arsitektur federasi data (*multi-DBMS data federation*) yang memisahkan beban transaksi operasional dengan penyimpanan referensi metadata statis:

```text
+-----------------------------------+       +-----------------------------------+
|      DBMS 1: PostgreSQL Cloud     |       |   DBMS 2: SQLite Local Embedded   |
|         (Supabase / Neon)         |       |      (metadata_komoditas.db)      |
|-----------------------------------|       |-----------------------------------|
| - Tabel: transaksi_panen          |       | - Tabel 1: master_komoditas       |
| - Fungsi: Menyimpan catatan log   |       |   (HPP, Harga Acuan, Masa Simpan) |
|   transaksi panen harian, volume, |       | - Tabel 2: ref_wilayah            |
|   dan harga jual aktual petani.   |       |   (Koordinat Lat/Lon & Elevasi)   |
+-----------------+-----------------+       +-----------------+-----------------+
                  |                                           |
                  |  Konektor: SQLAlchemy + psycopg2          |  Konektor: sqlite3
                  +---------------------+---------------------+
                                        |
                                        v
                  +-------------------------------------------+
                  |      DATA PIPELINE (Python & Pandas)      |
                  |-------------------------------------------|
                  | - Penggabungan via pd.merge() pada kunci  |
                  |   `kode_komoditas` dan `kabupaten`        |
                  | - Kalkulasi Omzet, HPP, dan Laba Bersih   |
                  +---------------------+---------------------+
                                        |
                                        v
                  +-------------------------------------------+
                  |   WEB APPLICATION (Streamlit & Plotly)    |
                  |-------------------------------------------|
                  | - Filter Multiselect Wilayah & Komoditas  |
                  | - Grafik Tren, Bar Chart, Peta & Sunburst |
                  +-------------------------------------------+
```

## 4. Alur Integrasi Data (Data Pipeline)
1. **Ekstraksi DBMS 1 (PostgreSQL):** Aplikasi mengambil data transaksi harian (`transaksi_panen`) dari *cloud database* menggunakan `SQLAlchemy` dan `psycopg2` melalui kredensial yang diamankan di `st.secrets["POSTGRES_URL"]`.
2. **Ekstraksi DBMS 2 (SQLite):** Aplikasi membaca tabel `master_komoditas` dan `ref_wilayah` dari file database lokal `database/metadata_komoditas.db` menggunakan pustaka `sqlite3`.
3. **Federasi & Transformasi (Pandas):** Kedua sumber data digabungkan di memori aplikasi menggunakan `pd.merge()` berdasarkan kolom `kode_komoditas` dan `kabupaten`, dilanjutkan dengan perhitungan variabel turunan seperti `total_omzet_rp` dan `estimasi_laba_bersih_rp`.

## 5. Fitur Interaktivitas Antarmuka Visualisasi
* **Filter Multi-Dimensi:** Pengguna dapat memfilter data secara *real-time* berdasarkan Kabupaten/Kota, jenis Komoditas (Cabai Merah, Kubis/Engkol, Tomat, Kentang, Bawang Merah), dan Status Distribusi.
* **Indikator KPI Dinamis:** Menampilkan agregasi total volume panen (Kg), total nilai transaksi (Rp), estimasi laba bersih petani, dan total pengiriman.
* **Visualisasi Interaktif Plotly:** Mencakup grafik tren waktu (*Line Chart*), perbandingan profitabilitas wilayah (*Grouped Bar Chart*), peta geospasial sentra produksi (*Scatter Mapbox*), dan hierarki distribusi komoditas (*Sunburst Chart*).
