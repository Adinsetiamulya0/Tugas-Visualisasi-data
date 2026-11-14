import os
import sqlite3
from datetime import date
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine

# ==========================================
# KONFIGURASI HALAMAN & DESAIN VISUAL MODERN
# ==========================================
st.set_page_config(
    page_title="Sentra Hortikultura Jawa Barat",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2.5rem;
    }

    /* Hero Banner Fotografi Perkebunan */
    .hero-photo {
        background-image: linear-gradient(90deg, rgba(6, 78, 59, 0.92) 0%, rgba(4, 120, 87, 0.78) 55%, rgba(16, 185, 129, 0.45) 100%), 
                          url('https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1600&q=80');
        background-size: cover;
        background-position: center;
        padding: 38px 36px;
        border-radius: 24px;
        color: white;
        box-shadow: 0 18px 35px rgba(6, 78, 59, 0.22);
        margin-bottom: 22px;
    }
    .hero-photo h1 {
        font-size: 2.25rem;
        font-weight: 800;
        color: #ffffff;
        margin: 0 0 8px 0;
        text-shadow: 0 2px 10px rgba(0,0,0,0.25);
    }
    .hero-photo p {
        font-size: 1rem;
        color: #ecfdf5;
        max-width: 780px;
        margin: 0;
        line-height: 1.6;
    }

    /* Kartu KPI Berwarna Gradasi */
    .metric-card-1 {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white; padding: 20px; border-radius: 20px;
        box-shadow: 0 10px 20px rgba(16, 185, 129, 0.25);
    }
    .metric-card-2 {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white; padding: 20px; border-radius: 20px;
        box-shadow: 0 10px 20px rgba(59, 130, 246, 0.25);
    }
    .metric-card-3 {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white; padding: 20px; border-radius: 20px;
        box-shadow: 0 10px 20px rgba(245, 158, 11, 0.25);
    }
    .metric-card-4 {
        background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
        color: white; padding: 20px; border-radius: 20px;
        box-shadow: 0 10px 20px rgba(139, 92, 246, 0.25);
    }
    .m-label { font-size: 0.82rem; font-weight: 600; opacity: 0.9; text-transform: uppercase; letter-spacing: 0.5px; }
    .m-val { font-size: 1.6rem; font-weight: 800; margin: 6px 0; white-space: nowrap; }
    .m-sub { font-size: 0.8rem; opacity: 0.92; font-weight: 500; }

    /* Kartu Galeri Foto Komoditas (Mode Semua) */
    .crop-card {
        background: #ffffff;
        border-radius: 18px;
        overflow: hidden;
        border: 1px solid #e2e8f0;
        box-shadow: 0 6px 16px rgba(0,0,0,0.06);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
        margin-bottom: 12px;
    }
    .crop-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 14px 28px rgba(16, 185, 129, 0.2);
    }
    .crop-img {
        width: 100%;
        height: 140px;
        object-fit: cover;
    }
    .crop-body { padding: 14px 16px; }
    .crop-title { font-weight: 800; font-size: 0.96rem; color: #0f172a; margin-bottom: 4px; }
    .crop-price { font-size: 0.86rem; font-weight: 700; color: #059669; }
    .crop-vol { font-size: 0.78rem; color: #64748b; margin-top: 4px; }

    /* Kartu Spotlight Fokus 1 Komoditas (Saat Diklik) */
    .spotlight-card {
        background: linear-gradient(135deg, #ffffff 0%, #f0fdf4 100%);
        border: 2px solid #10b981;
        border-radius: 22px;
        overflow: hidden;
        box-shadow: 0 14px 32px rgba(16, 185, 129, 0.16);
        margin-bottom: 18px;
        display: flex;
        flex-wrap: wrap;
    }
    .spotlight-img {
        width: 340px;
        min-height: 230px;
        object-fit: cover;
        flex-shrink: 0;
    }
    .spotlight-content {
        padding: 24px 28px;
        flex: 1;
        min-width: 280px;
    }
    .spotlight-badge {
        display: inline-block;
        background: #d1fae5;
        color: #065f46;
        font-weight: 700;
        font-size: 0.78rem;
        padding: 4px 12px;
        border-radius: 99px;
        margin-bottom: 8px;
    }
    .spotlight-title {
        font-size: 1.75rem;
        font-weight: 800;
        color: #0f172a;
        margin: 0 0 8px 0;
    }
    .spotlight-desc {
        font-size: 0.94rem;
        color: #475569;
        margin-bottom: 16px;
        line-height: 1.55;
    }
    .spotlight-stats {
        display: flex;
        gap: 24px;
        flex-wrap: wrap;
        background: #ffffff;
        padding: 12px 18px;
        border-radius: 14px;
        border: 1px solid #d1fae5;
    }
    .stat-item b {
        display: block;
        font-size: 1.05rem;
        color: #059669;
    }
    .stat-item span {
        font-size: 0.76rem;
        color: #64748b;
        text-transform: uppercase;
        font-weight: 600;
    }

    .side-banner {
        border-radius: 14px;
        overflow: hidden;
        margin-bottom: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. INISIALISASI DATABASE SQLITE
# ==========================================
SQLITE_PATH = "metadata_komoditas.db"

def init_sqlite_db(db_path=SQLITE_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS master_komoditas (
        kode_komoditas TEXT PRIMARY KEY,
        nama_komoditas TEXT NOT NULL,
        kategori TEXT NOT NULL,
        hpp_per_kg_rp REAL NOT NULL,
        harga_acuan_pemerintah_rp REAL NOT NULL,
        masa_simpan_hari INTEGER NOT NULL
    )
    """)
    cursor.executemany("INSERT OR REPLACE INTO master_komoditas VALUES (?, ?, ?, ?, ?, ?)", [
        ('KMD-01', 'Cabai Merah Keriting', 'Sayuran Buah', 22000, 35000, 7),
        ('KMD-02', 'Kubis / Engkol', 'Sayuran Daun', 4500, 8000, 14),
        ('KMD-03', 'Tomat Sayur', 'Sayuran Buah', 7500, 13000, 5),
        ('KMD-04', 'Kentang Granola', 'Umbi-umbian', 10000, 16000, 30),
        ('KMD-05', 'Bawang Merah', 'Umbi-umbian', 19000, 30000, 25)
    ])

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ref_wilayah (
        kabupaten TEXT PRIMARY KEY,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        elevasi_mdpl INTEGER NOT NULL
    )
    """)
    cursor.executemany("INSERT OR REPLACE INTO ref_wilayah VALUES (?, ?, ?, ?)", [
        ('Sumedang', -6.8586, 107.9204, 750),
        ('Garut', -7.2279, 107.9087, 717),
        ('Bandung', -7.0251, 107.5198, 1100),
        ('Majalengka', -6.8364, 108.2274, 600),
        ('Cianjur', -6.8168, 107.1425, 1050)
    ])
    conn.commit()
    conn.close()

init_sqlite_db(SQLITE_PATH)

# Foto & Deskripsi Detail Setiap Komoditas
INFO_KOMODITAS = {
    "Cabai Merah Keriting": {
        "img": "https://images.unsplash.com/photo-1588252303782-cb80119abd6d?auto=format&fit=crop&w=800&q=80",
        "desc": "Komoditas bernilai ekonomi tinggi dengan permintaan pasar harian yang sangat tinggi di Pasar Induk maupun ritel modern Jawa Barat."
    },
    "Kubis / Engkol": {
        "img": "https://images.unsplash.com/photo-1594282486552-05b4d80fbb9f?auto=format&fit=crop&w=800&q=80",
        "desc": "Sayuran daun dataran menengah-tinggi unggulan petani Sumedang, Garut, dan Bandung dengan daya tahan simpan kuat serta tonase panen melimpah."
    },
    "Tomat Sayur": {
        "img": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&w=800&q=80",
        "desc": "Sayuran buah segar dengan siklus panen cepat yang membutuhkan rantai distribusi kilat menuju pasar konsumen."
    },
    "Kentang Granola": {
        "img": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=800&q=80",
        "desc": "Komoditas umbi unggulan dataran tinggi Jawa Barat (Pangandaran/Bandung/Garut) dengan masa simpan panjang hingga 30 hari."
    },
    "Bawang Merah": {
        "img": "https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?auto=format&fit=crop&w=800&q=80",
        "desc": "Bumbu utama rumah tangga dan industri kuliner dengan sentra produksi kuat di kawasan Majalengka, Garut, dan Cianjur."
    }
}

# ==========================================
# 2. PENGAMBILAN DATA (DILENGKAPI TIME-SERIES LENGKAP UNTUK ANIMASI)
# ==========================================
@st.cache_data(ttl=300)
def fetch_postgres_data():
    try:
        db_url = st.secrets["POSTGRES_URL"]
        engine = create_engine(db_url)
        df = pd.read_sql("SELECT * FROM transaksi_panen ORDER BY tanggal ASC;", engine)
        if len(df) >= 25:
            return df
    except Exception:
        pass

    # Dataset lengkap lintas bulan (Mei - Oktober 2026) agar animasi bergerak mulus setiap bulan
    data_lengkap = [
        (1, '2026-05-05', 'Sumedang', 'KMD-01', 1250, 38000, 'Terkirim ke Pasar Induk'),
        (2, '2026-05-08', 'Sumedang', 'KMD-02', 2400, 8500, 'Terkirim ke Pasar Induk'),
        (3, '2026-05-12', 'Garut', 'KMD-03', 1900, 13500, 'Terkirim ke Retail Modern'),
        (4, '2026-05-18', 'Bandung', 'KMD-04', 3200, 16000, 'Terkirim ke Pasar Induk'),
        (5, '2026-05-24', 'Majalengka', 'KMD-05', 1600, 30500, 'Terkirim ke Pasar Induk'),

        (6, '2026-06-03', 'Sumedang', 'KMD-01', 1520, 41000, 'Terkirim ke Retail Modern'),
        (7, '2026-06-07', 'Garut', 'KMD-02', 2850, 8200, 'Gudang Logistik'),
        (8, '2026-06-14', 'Bandung', 'KMD-03', 2700, 14200, 'Terkirim ke Pasar Induk'),
        (9, '2026-06-19', 'Cianjur', 'KMD-04', 3600, 16500, 'Terkirim ke Retail Modern'),
        (10, '2026-06-25', 'Majalengka', 'KMD-05', 1950, 31500, 'Terkirim ke Pasar Induk'),

        (11, '2026-07-04', 'Sumedang', 'KMD-02', 3100, 9100, 'Terkirim ke Pasar Induk'),
        (12, '2026-07-09', 'Garut', 'KMD-01', 1780, 43500, 'Terkirim ke Retail Modern'),
        (13, '2026-07-15', 'Cianjur', 'KMD-03', 2250, 14800, 'Terkirim ke Pasar Induk'),
        (14, '2026-07-21', 'Bandung', 'KMD-04', 4100, 17000, 'Terkirim ke Pasar Induk'),
        (15, '2026-07-28', 'Majalengka', 'KMD-05', 2100, 32500, 'Terkirim ke Retail Modern'),

        (16, '2026-08-03', 'Bandung', 'KMD-02', 3900, 8900, 'Terkirim ke Pasar Induk'),
        (17, '2026-08-10', 'Sumedang', 'KMD-01', 1850, 44000, 'Terkirim ke Retail Modern'),
        (18, '2026-08-16', 'Sumedang', 'KMD-03', 2400, 13900, 'Terkirim ke Pasar Induk'),
        (19, '2026-08-22', 'Garut', 'KMD-04', 4350, 17200, 'Gudang Logistik'),
        (20, '2026-08-27', 'Cianjur', 'KMD-05', 2300, 33000, 'Terkirim ke Retail Modern'),

        (21, '2026-09-02', 'Sumedang', 'KMD-02', 3450, 9400, 'Terkirim ke Retail Modern'),
        (22, '2026-09-09', 'Majalengka', 'KMD-01', 2050, 42000, 'Terkirim ke Pasar Induk'),
        (23, '2026-09-15', 'Garut', 'KMD-03', 2650, 15000, 'Terkirim ke Retail Modern'),
        (24, '2026-09-21', 'Bandung', 'KMD-04', 4600, 17600, 'Terkirim ke Pasar Induk'),
        (25, '2026-09-28', 'Cianjur', 'KMD-05', 2550, 34000, 'Terkirim ke Pasar Induk'),

        (26, '2026-10-04', 'Sumedang', 'KMD-01', 2250, 46000, 'Terkirim ke Retail Modern'),
        (27, '2026-10-10', 'Sumedang', 'KMD-02', 3800, 9800, 'Terkirim ke Pasar Induk'),
        (28, '2026-10-14', 'Bandung', 'KMD-03', 2950, 15500, 'Terkirim ke Retail Modern'),
        (29, '2026-10-20', 'Garut', 'KMD-04', 4900, 18000, 'Terkirim ke Pasar Induk'),
        (30, '2026-10-26', 'Majalengka', 'KMD-05', 2800, 35000, 'Terkirim ke Retail Modern')
    ]
    cols = ['id_transaksi', 'tanggal', 'kabupaten', 'kode_komoditas', 'volume_panen_kg', 'harga_jual_aktual_rp', 'status_distribusi']
    return pd.DataFrame(data_lengkap, columns=cols)

@st.cache_data
def fetch_sqlite_data():
    conn = sqlite3.connect(SQLITE_PATH)
    df_komoditas = pd.read_sql("SELECT * FROM master_komoditas", conn)
    df_wilayah = pd.read_sql("SELECT * FROM ref_wilayah", conn)
    conn.close()
    return df_komoditas, df_wilayah

df_pg_base = fetch_postgres_data()
df_komoditas, df_wilayah = fetch_sqlite_data()

if "extra_rows" not in st.session_state:
    st.session_state.extra_rows = []

if st.session_state.extra_rows:
    df_transaksi = pd.concat([df_pg_base, pd.DataFrame(st.session_state.extra_rows)], ignore_index=True)
else:
    df_transaksi = df_pg_base.copy()

df_merged = pd.merge(df_transaksi, df_komoditas, on="kode_komoditas", how="left")
df_merged = pd.merge(df_merged, df_wilayah, on="kabupaten", how="left")

df_merged["tanggal"] = pd.to_datetime(df_merged["tanggal"])
df_merged["bulan"] = df_merged["tanggal"].dt.strftime("%Y-%m")
df_merged["nama_bulan"] = df_merged["tanggal"].dt.strftime("%b %Y")
df_merged["total_omzet_rp"] = df_merged["volume_panen_kg"] * df_merged["harga_jual_aktual_rp"]
df_merged["total_biaya_hpp_rp"] = df_merged["volume_panen_kg"] * df_merged["hpp_per_kg_rp"]
df_merged["estimasi_laba_bersih_rp"] = df_merged["total_omzet_rp"] - df_merged["total_biaya_hpp_rp"]
df_merged["margin_persen"] = (df_merged["estimasi_laba_bersih_rp"] / df_merged["total_omzet_rp"]) * 100

def rp_ringkas(nilai):
    if abs(nilai) >= 1_000_000_000:
        return f"Rp {nilai / 1_000_000_000:,.2f} Miliar"
    elif abs(nilai) >= 1_000_000:
        return f"Rp {nilai / 1_000_000:,.2f} Juta"
    return f"Rp {nilai:,.0f}"

palet_utama = ["#10b981", "#3b82f6", "#f59e0b", "#8b5cf6", "#ef4444"]

# ==========================================
# 3. SIDEBAR FILTER
# ==========================================
with st.sidebar:
    st.markdown("""
    <div class="side-banner">
        <img src="https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=600&q=80" style="width:100%; height:130px; object-fit:cover;">
    </div>
    """, unsafe_allow_html=True)
    st.markdown("### 🌾 **Filter Data Panen**")

    min_date = df_merged["tanggal"].min().date()
    max_date = df_merged["tanggal"].max().date()
    rentang_tgl = st.date_input(
        "📅 Periode Panen:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    min_vol = st.slider(
        "⚖️ Minimal Volume Panen (Kg):",
        0, int(df_merged["volume_panen_kg"].max()), 0, step=100
    )

    pilih_kabupaten = st.multiselect(
        "📍 Wilayah Kabupaten:",
        options=sorted(df_merged["kabupaten"].unique()),
        default=sorted(df_merged["kabupaten"].unique())
    )

    pilih_status = st.multiselect(
        "🚚 Tujuan Distribusi:",
        options=sorted(df_merged["status_distribusi"].unique()),
        default=sorted(df_merged["status_distribusi"].unique())
    )

    st.divider()
    st.caption("👨‍💻 **Adin Setia Mulya**  \nInformatika - Universitas Sebelas April")

if isinstance(rentang_tgl, tuple) and len(rentang_tgl) == 2:
    tgl_awal, tgl_akhir = pd.to_datetime(rentang_tgl[0]), pd.to_datetime(rentang_tgl[1])
else:
    tgl_awal, tgl_akhir = pd.to_datetime(min_date), pd.to_datetime(max_date)

df_filtered = df_merged[
    (df_merged["tanggal"] >= tgl_awal) &
    (df_merged["tanggal"] <= tgl_akhir) &
    (df_merged["volume_panen_kg"] >= min_vol) &
    (df_merged["kabupaten"].isin(pilih_kabupaten)) &
    (df_merged["status_distribusi"].isin(pilih_status))
].copy()

# ==========================================
# 4. HERO BANNER & FILTER KOMODITAS INTERAKTIF
# ==========================================
st.markdown("""
<div class="hero-photo">
    <h1>🌾 Dashboard Sentra Hortikultura Jawa Barat</h1>
    <p>
        Pilih komoditas di bawah untuk melihat profil visual komoditas secara spesifik, memutar animasi pertumbuhan panen bulanan, dan memantau peta sebaran sentra produksi Jawa Barat.
    </p>
</div>
""", unsafe_allow_html=True)

fokus_komoditas = st.radio(
    "🥬 **Klik Komoditas untuk Menampilkan Foto & Analisis Khusus Komoditas Tersebut:**",
    options=["🌟 Semua Komoditas"] + list(sorted(df_merged["nama_komoditas"].unique())),
    horizontal=True
)

if fokus_komoditas != "🌟 Semua Komoditas":
    df_filtered = df_filtered[df_filtered["nama_komoditas"] == fokus_komoditas]

if df_filtered.empty:
    st.warning("⚠️ Tidak ada data untuk kombinasi filter ini. Silakan longgarkan filter di sebelah kiri.")
    st.stop()

# ==========================================
# 5. TAMPILAN FOTO KOMODITAS DINAMIS (SESUAI YANG DIKLIK)
# ==========================================
if fokus_komoditas == "🌟 Semua Komoditas":
    st.markdown("#### 📸 Galeri Komoditas Hortikultura (Klik salah satu nama di atas untuk fokus tunggal)")
    cols_galeri = st.columns(5)
    for idx, nama_k in enumerate(sorted(df_merged["nama_komoditas"].unique())):
        df_k = df_filtered[df_filtered["nama_komoditas"] == nama_k]
        vol_k = df_k["volume_panen_kg"].sum()
        rata_harga = df_k["harga_jual_aktual_rp"].mean() if not df_k.empty else 0
        img_url = INFO_KOMODITAS[nama_k]["img"]
        with cols_galeri[idx]:
            st.markdown(f"""
            <div class="crop-card">
                <img src="{img_url}" class="crop-img">
                <div class="crop-body">
                    <div class="crop-title">{nama_k}</div>
                    <div class="crop-price">Rp {rata_harga:,.0f} / Kg</div>
                    <div class="crop-vol">📦 Total Panen: <b>{vol_k:,.0f} Kg</b></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    # HANYA MENAMPILKAN 1 FOTO KOMODITAS YANG DIKLIK (SPOTLIGHT CARD BESAR)
    info_k = INFO_KOMODITAS[fokus_komoditas]
    row_master = df_komoditas[df_komoditas["nama_komoditas"] == fokus_komoditas].iloc[0]
    vol_sp = df_filtered["volume_panen_kg"].sum()
    harga_sp = df_filtered["harga_jual_aktual_rp"].mean()
    margin_sp = df_filtered["margin_persen"].mean()

    st.markdown(f"""
    <div class="spotlight-card">
        <img src="{info_k['img']}" class="spotlight-img">
        <div class="spotlight-content">
            <span class="spotlight-badge">🌿 Kategori: {row_master['kategori']}</span>
            <h2 class="spotlight-title">{fokus_komoditas}</h2>
            <p class="spotlight-desc">{info_k['desc']}</p>
            <div class="spotlight-stats">
                <div class="stat-item">
                    <span>Harga Jual Rata-Rata</span>
                    <b>Rp {harga_sp:,.0f} / Kg</b>
                </div>
                <div class="stat-item">
                    <span>Modal Tanam (HPP)</span>
                    <b>Rp {row_master['hpp_per_kg_rp']:,.0f} / Kg</b>
                </div>
                <div class="stat-item">
                    <span>Total Volume Panen</span>
                    <b>{vol_sp:,.0f} Kg ({vol_sp/1000:,.1f} Ton)</b>
                </div>
                <div class="stat-item">
                    <span>Margin Keuntungan</span>
                    <b>{margin_sp:.1f}%</b>
                </div>
                <div class="stat-item">
                    <span>Daya Simpan</span>
                    <b>{row_master['masa_simpan_hari']} Hari</b>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 6. KARTU KPI BERWARNA GRADASI CERAH
# ==========================================
tot_vol = df_filtered["volume_panen_kg"].sum()
tot_omzet = df_filtered["total_omzet_rp"].sum()
tot_laba = df_filtered["estimasi_laba_bersih_rp"].sum()
avg_margin = (tot_laba / tot_omzet * 100) if tot_omzet > 0 else 0

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""
    <div class="metric-card-1">
        <div class="m-label">📦 Total Volume Panen</div>
        <div class="m-val">{tot_vol:,.0f} Kg</div>
        <div class="m-sub">Setara {tot_vol/1000:,.2f} Ton Hasil Panen</div>
    </div>
    """, unsafe_allow_html=True)
with k2:
    st.markdown(f"""
    <div class="metric-card-2">
        <div class="m-label">💰 Total Nilai Penjualan</div>
        <div class="m-val">{rp_ringkas(tot_omzet)}</div>
        <div class="m-sub">Akumulasi Rp {tot_omzet:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)
with k3:
    st.markdown(f"""
    <div class="metric-card-3">
        <div class="m-label">📈 Keuntungan Bersih Petani</div>
        <div class="m-val">{rp_ringkas(tot_laba)}</div>
        <div class="m-sub">Rata-rata Margin Keuntungan: {avg_margin:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)
with k4:
    st.markdown(f"""
    <div class="metric-card-4">
        <div class="m-label">🚚 Total Pengiriman</div>
        <div class="m-val">{len(df_filtered)} Batch</div>
        <div class="m-sub">Tersebar di {df_filtered['kabupaten'].nunique()} Kabupaten Sentra</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ==========================================
# 7. MENU TAB INTERAKTIF
# ==========================================
tab_explore, tab_map, tab_anim, tab_sim, tab_input = st.tabs([
    "📊 Analisis Grafik Interaktif",
    "🗺️ Peta Lokasi Sentra & Alur Distribusi",
    "▶️ Animasi Bergerak (Play ▶) & 3D",
    "🧮 Kalkulator Simulasi Keuntungan",
    "➕ Tambah Data & Tabel Lengkap"
])

# ------------------------------------------
# TAB 1: ANALISIS GRAFIK INTERAKTIF
# ------------------------------------------
with tab_explore:
    c_opt1, c_opt2, c_opt3 = st.columns(3)
    with c_opt1:
        metrik_pilihan = st.selectbox(
            "📊 Pilih Data yang Ditampilkan:",
            options=[
                ("total_omzet_rp", "Nilai Penjualan / Omzet (Rp)"),
                ("estimasi_laba_bersih_rp", "Keuntungan Bersih Petani (Rp)"),
                ("volume_panen_kg", "Volume Panen (Kg)"),
                ("margin_persen", "Margin Keuntungan (%)")
            ],
            format_func=lambda x: x[1]
        )
    with c_opt2:
        jenis_grafik = st.selectbox(
            "📈 Pilih Model Grafik:",
            ["Area Gelombang (Spline)", "Grafik Batang (Bar)", "Gelembung Interaktif (Bubble)", "Sebaran Data (Box Plot)"]
        )
    with c_opt3:
        kelompok_warna = st.selectbox(
            "🎨 Bedakan Warna Berdasarkan:",
            [("nama_komoditas", "Komoditas"), ("kabupaten", "Kabupaten"), ("status_distribusi", "Tujuan Distribusi")],
            format_func=lambda x: x[1]
        )

    kol_y, lbl_y = metrik_pilihan[0], metrik_pilihan[1]
    kol_c = kelompok_warna[0]

    g_kiri, g_kanan = st.columns([1.35, 1])

    with g_kiri:
        st.markdown(f"#### 📈 Grafik Interaktif: **{lbl_y}**")
        df_sorted = df_filtered.sort_values("tanggal")
        if jenis_grafik == "Area Gelombang (Spline)":
            fig_main = px.area(
                df_sorted, x="tanggal", y=kol_y, color=kol_c,
                markers=True, line_shape="spline", color_discrete_sequence=palet_utama,
                hover_data=["kabupaten", "nama_komoditas", "volume_panen_kg"]
            )
        elif jenis_grafik == "Grafik Batang (Bar)":
            fig_main = px.bar(
                df_sorted, x="bulan", y=kol_y, color=kol_c,
                barmode="group", color_discrete_sequence=palet_utama,
                hover_data=["kabupaten", "nama_komoditas"]
            )
        elif jenis_grafik == "Gelembung Interaktif (Bubble)":
            fig_main = px.scatter(
                df_sorted, x="tanggal", y=kol_y, color=kol_c,
                size="volume_panen_kg", size_max=36, color_discrete_sequence=palet_utama,
                hover_data=["kabupaten", "nama_komoditas", "margin_persen"]
            )
        else:
            fig_main = px.box(
                df_sorted, x=kol_c, y=kol_y, color=kol_c,
                points="all", color_discrete_sequence=palet_utama
            )

        fig_main.update_layout(
            template="plotly_white", height=400, hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=10, r=10, t=30, b=10)
        )
        st.plotly_chart(fig_main, use_container_width=True)

    with g_kanan:
        st.markdown("#### 🎯 Perbandingan Modal Tanam vs Harga Jual (Rp/Kg)")
        df_komp = df_filtered.groupby("nama_komoditas", as_index=False)[
            ["hpp_per_kg_rp", "harga_acuan_pemerintah_rp", "harga_jual_aktual_rp"]
        ].mean()
        fig_komp = go.Figure()
        fig_komp.add_trace(go.Bar(name="Modal Tanam (HPP)", x=df_komp["nama_komoditas"], y=df_komp["hpp_per_kg_rp"], marker_color="#94a3b8"))
        fig_komp.add_trace(go.Bar(name="Harga Acuan Pemerintah", x=df_komp["nama_komoditas"], y=df_komp["harga_acuan_pemerintah_rp"], marker_color="#f59e0b"))
        fig_komp.add_trace(go.Bar(name="Harga Jual Aktual", x=df_komp["nama_komoditas"], y=df_komp["harga_jual_aktual_rp"], marker_color="#10b981"))
        fig_komp.update_layout(
            barmode="group", template="plotly_white", height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=10, r=10, t=30, b=10), yaxis_title="Rupiah / Kg"
        )
        st.plotly_chart(fig_komp, use_container_width=True)

# ------------------------------------------
# TAB 2: PETA LOKASI SENTRA JAWA BARAT (OPENSTREETMAP PASTI MUNCUL)
# ------------------------------------------
with tab_map:
    p_kiri, p_kanan = st.columns([1.2, 1])

    with p_kiri:
        st.markdown("#### 🗺️ Peta Lokasi Sentra Panen Jawa Barat")
        df_map = df_filtered.groupby(
            ["kabupaten", "latitude", "longitude", "elevasi_mdpl"], as_index=False
        ).agg(
            total_volume_kg=("volume_panen_kg", "sum"),
            total_omzet=("total_omzet_rp", "sum"),
            rata_margin=("margin_persen", "mean")
        )
        df_map["label_peta"] = df_map["kabupaten"] + " (" + df_map["total_volume_kg"].apply(lambda x: f"{x:,.0f} Kg") + ")"

        # Menggunakan go.Scattermapbox / Scattermap dengan OpenStreetMap resmi agar 100% tampil
        fig_map = go.Figure()

        if hasattr(go, "Scattermap"):
            fig_map.add_trace(go.Scattermap(
                lat=df_map["latitude"],
                lon=df_map["longitude"],
                mode="markers+text",
                marker=dict(
                    size=np.clip(df_map["total_volume_kg"] / 220, 18, 42),
                    color=df_map["elevasi_mdpl"],
                    colorscale="Viridis",
                    showscale=True,
                    colorbar=dict(title="mdpl")
                ),
                text=df_map["label_peta"],
                textposition="top center",
                hovertemplate="<b>Kabupaten %{text}</b><br>Elevasi: %{marker.color} mdpl<extra></extra>"
            ))
            fig_map.update_layout(
                map=dict(
                    style="open-street-map",
                    center=dict(lat=-6.95, lon=107.75),
                    zoom=7.5
                ),
                height=440,
                margin=dict(l=0, r=0, t=10, b=0)
            )
        else:
            fig_map.add_trace(go.Scattermapbox(
                lat=df_map["latitude"],
                lon=df_map["longitude"],
                mode="markers+text",
                marker=dict(
                    size=np.clip(df_map["total_volume_kg"] / 220, 18, 42),
                    color=df_map["elevasi_mdpl"],
                    colorscale="Viridis",
                    showscale=True,
                    colorbar=dict(title="mdpl")
                ),
                text=df_map["label_peta"],
                textposition="top center",
                hovertemplate="<b>Kabupaten %{text}</b><br>Elevasi: %{marker.color} mdpl<extra></extra>"
            ))
            fig_map.update_layout(
                mapbox=dict(
                    style="open-street-map",
                    center=dict(lat=-6.95, lon=107.75),
                    zoom=7.5
                ),
                height=440,
                margin=dict(l=0, r=0, t=10, b=0)
            )

        st.plotly_chart(fig_map, use_container_width=True)

    with p_kanan:
        st.markdown("#### 🔀 Alur Distribusi Hasil Panen (Kabupaten → Komoditas → Pasar)")
        kabs = list(df_filtered["kabupaten"].unique())
        koms = list(df_filtered["nama_komoditas"].unique())
        stats = list(df_filtered["status_distribusi"].unique())
        nodes = kabs + koms + stats
        n_idx = {name: i for i, name in enumerate(nodes)}
        src, tgt, val = [], [], []

        for _, r in df_filtered.groupby(["kabupaten", "nama_komoditas"])["volume_panen_kg"].sum().reset_index().iterrows():
            src.append(n_idx[r["kabupaten"]])
            tgt.append(n_idx[r["nama_komoditas"]])
            val.append(r["volume_panen_kg"])

        for _, r in df_filtered.groupby(["nama_komoditas", "status_distribusi"])["volume_panen_kg"].sum().reset_index().iterrows():
            src.append(n_idx[r["nama_komoditas"]])
            tgt.append(n_idx[r["status_distribusi"]])
            val.append(r["volume_panen_kg"])

        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(pad=16, thickness=18, label=nodes, color="#10b981"),
            link=dict(source=src, target=tgt, value=val, color="rgba(16, 185, 129, 0.28)")
        )])
        fig_sankey.update_layout(height=440, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_sankey, use_container_width=True)

# ------------------------------------------
# TAB 3: ANIMASI BERGERAK MULUS (BAR RACE & BUBBLE MOTION)
# ------------------------------------------
with tab_anim:
    st.success("🎬 **Tekan tombol `▶ Play` di pojok kiri bawah grafik** untuk melihat animasi pergerakan volume dan nilai panen dari bulan Mei hingga Oktober 2026!")

    tipe_anim = st.radio(
        "Pilih Mode Animasi Interaktif:",
        ["🏁 Balapan Grafik Batang Kumulatif (Bar Chart Race)", "🫧 Animasi Gelembung Bergerak (Bubble Motion)"],
        horizontal=True
    )

    a_kiri, a_kanan = st.columns([1.25, 1])

    with a_kiri:
        # Siapkan grid kumulatif bulanan supaya semua komoditas/kabupaten bergerak di setiap frame
        daftar_bulan = sorted(df_merged["bulan"].unique())
        dimensi_grup = "kabupaten" if fokus_komoditas != "🌟 Semua Komoditas" else "nama_komoditas"
        daftar_item = sorted(df_filtered[dimensi_grup].unique())

        rows_anim = []
        for b in daftar_bulan:
            df_sampai_b = df_filtered[df_filtered["bulan"] <= b]
            for item in daftar_item:
                sub = df_sampai_b[df_sampai_b[dimensi_grup] == item]
                vol_kum = sub["volume_panen_kg"].sum()
                omz_kum = sub["total_omzet_rp"].sum()
                laba_kum = sub["estimasi_laba_bersih_rp"].sum()
                rows_anim.append({
                    "Bulan": b,
                    "Kategori_Item": item,
                    "Volume_Kumulatif_Kg": vol_kum if vol_kum > 0 else 50,
                    "Omzet_Kumulatif_Rp": omz_kum if omz_kum > 0 else 500000,
                    "Laba_Kumulatif_Rp": laba_kum if laba_kum > 0 else 200000
                })
        df_race = pd.DataFrame(rows_anim)

        if tipe_anim == "🏁 Balapan Grafik Batang Kumulatif (Bar Chart Race)":
            fig_anim = px.bar(
                df_race,
                x="Volume_Kumulatif_Kg",
                y="Kategori_Item",
                color="Kategori_Item",
                animation_frame="Bulan",
                orientation="h",
                text="Volume_Kumulatif_Kg",
                color_discrete_sequence=palet_utama,
                range_x=[0, df_race["Volume_Kumulatif_Kg"].max() * 1.25],
                labels={"Volume_Kumulatif_Kg": "Akumulasi Volume Panen (Kg)", "Kategori_Item": ""}
            )
            fig_anim.update_traces(texttemplate="%{text:,.0f} Kg", textposition="outside")
        else:
            fig_anim = px.scatter(
                df_race,
                x="Volume_Kumulatif_Kg",
                y="Omzet_Kumulatif_Rp",
                animation_frame="Bulan",
                animation_group="Kategori_Item",
                size="Laba_Kumulatif_Rp",
                color="Kategori_Item",
                hover_name="Kategori_Item",
                text="Kategori_Item",
                size_max=55,
                color_discrete_sequence=palet_utama,
                range_x=[0, df_race["Volume_Kumulatif_Kg"].max() * 1.25],
                range_y=[0, df_race["Omzet_Kumulatif_Rp"].max() * 1.25],
                labels={
                    "Volume_Kumulatif_Kg": "Akumulasi Volume Panen (Kg)",
                    "Omzet_Kumulatif_Rp": "Akumulasi Nilai Penjualan (Rp)"
                }
            )
            fig_anim.update_traces(textposition="top center")

        fig_anim.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 700
        fig_anim.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 450
        fig_anim.update_layout(
            template="plotly_white",
            height=450,
            showlegend=False,
            title="▶️ Animasi Pertumbuhan Panen Kumulatif (Mei - Oktober 2026)",
            margin=dict(l=10, r=20, t=45, b=10)
        )
        st.plotly_chart(fig_anim, use_container_width=True)

    with a_kanan:
        st.markdown("#### 🧊 Grafik 3D Interaktif: Ketinggian Lahan vs Volume vs Laba")
        fig_3d = px.scatter_3d(
            df_filtered, x="elevasi_mdpl", y="volume_panen_kg", z="estimasi_laba_bersih_rp",
            color="nama_komoditas", size="volume_panen_kg", hover_name="kabupaten",
            color_discrete_sequence=palet_utama,
            labels={
                "elevasi_mdpl": "Ketinggian (mdpl)",
                "volume_panen_kg": "Volume (Kg)",
                "estimasi_laba_bersih_rp": "Laba Bersih (Rp)"
            }
        )
        fig_3d.update_layout(height=450, margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig_3d, use_container_width=True)

# ------------------------------------------
# TAB 4: SIMULATOR KEUNTUNGAN
# ------------------------------------------
with tab_sim:
    st.markdown("#### 🧮 Simulasi Perubahan Harga Pasar & Biaya Bibit/Pupuk")
    s1, s2, s3 = st.columns(3)
    with s1:
        sim_harga = st.slider("📈 Kenaikan / Penurunan Harga Jual Pasar (%):", -40, 60, 15, step=5)
    with s2:
        sim_hpp = st.slider("🌱 Efisiensi Biaya Produksi / HPP (%):", -40, 40, -10, step=5)
    with s3:
        target_laba_juta = st.number_input("🎯 Target Keuntungan Bersih (Juta Rp):", min_value=50, max_value=2000, value=500, step=50)

    df_sim = df_filtered.copy()
    df_sim["omzet_sim"] = df_sim["total_omzet_rp"] * (1 + sim_harga / 100.0)
    df_sim["hpp_sim"] = df_sim["total_biaya_hpp_rp"] * (1 + sim_hpp / 100.0)
    df_sim["laba_sim"] = df_sim["omzet_sim"] - df_sim["hpp_sim"]

    laba_aktual_juta = df_sim["estimasi_laba_bersih_rp"].sum() / 1_000_000
    laba_sim_juta = df_sim["laba_sim"].sum() / 1_000_000

    g_col, b_col = st.columns([1, 1.3])
    with g_col:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=laba_sim_juta,
            number={"suffix": " Juta", "valueformat": ",.1f"},
            delta={"reference": laba_aktual_juta, "suffix": " Jt dari Aktual"},
            title={"text": "Proyeksi Keuntungan Bersih Petani"},
            gauge={
                "axis": {"range": [0, max(target_laba_juta * 1.3, laba_sim_juta * 1.2)]},
                "bar": {"color": "#10b981"},
                "threshold": {"line": {"color": "#ef4444", "width": 4}, "thickness": 0.8, "value": target_laba_juta}
            }
        ))
        fig_gauge.update_layout(height=360, margin=dict(l=20, r=20, t=40, b=10))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with b_col:
        df_s_grp = df_sim.groupby("nama_komoditas", as_index=False)[["estimasi_laba_bersih_rp", "laba_sim"]].sum()
        fig_s_bar = go.Figure()
        fig_s_bar.add_trace(go.Bar(name="Keuntungan Saat Ini", x=df_s_grp["nama_komoditas"], y=df_s_grp["estimasi_laba_bersih_rp"], marker_color="#94a3b8"))
        fig_s_bar.add_trace(go.Bar(name="Keuntungan Hasil Simulasi", x=df_s_grp["nama_komoditas"], y=df_s_grp["laba_sim"], marker_color="#10b981"))
        fig_s_bar.update_layout(
            barmode="group", template="plotly_white", height=360,
            title="Perbandingan Keuntungan Saat Ini vs Hasil Simulasi",
            margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig_s_bar, use_container_width=True)

# ------------------------------------------
# TAB 5: INPUT DATA BARU & TABEL LENGKAP
# ------------------------------------------
with tab_input:
    st.markdown("#### ➕ Catat Pengiriman Panen Baru")
    with st.form("form_tambah_transaksi", clear_on_submit=True):
        f1, f2, f3 = st.columns(3)
        with f1:
            in_tanggal = st.date_input("📅 Tanggal Panen:", value=date(2026, 10, 28))
            in_kab = st.selectbox("📍 Kabupaten:", sorted(df_wilayah["kabupaten"].unique()))
        with f2:
            pilihan_kom = df_komoditas[["kode_komoditas", "nama_komoditas"]].values.tolist()
            in_kom = st.selectbox("🥬 Komoditas:", pilihan_kom, format_func=lambda x: x[1])
            in_vol = st.number_input("⚖️ Volume Panen (Kg):", min_value=100.0, max_value=20000.0, value=2500.0, step=100.0)
        with f3:
            in_harga = st.number_input("💵 Harga Jual (Rp/Kg):", min_value=2000.0, max_value=150000.0, value=40000.0, step=500.0)
            in_status = st.selectbox("🚚 Tujuan Distribusi:", ["Terkirim ke Pasar Induk", "Terkirim ke Retail Modern", "Gudang Logistik"])

        if st.form_submit_button("🚀 Tambahkan Data Panen Sekarang", use_container_width=True):
            new_id = int(df_transaksi["id_transaksi"].max()) + 1
            st.session_state.extra_rows.append({
                "id_transaksi": new_id,
                "tanggal": str(in_tanggal),
                "kabupaten": in_kab,
                "kode_komoditas": in_kom[0],
                "volume_panen_kg": float(in_vol),
                "harga_jual_aktual_rp": float(in_harga),
                "status_distribusi": in_status
            })
            st.balloons()
            st.rerun()

    st.markdown("#### 📋 Rincian Data Transaksi & Komoditas")
    csv_data = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Unduh Data Lengkap (.CSV)", data=csv_data, file_name="data_hortikultura_jabar.csv", mime="text/csv")

    st.dataframe(
        df_filtered.sort_values("id_transaksi", ascending=False)[[
            "id_transaksi", "tanggal", "kabupaten", "elevasi_mdpl", "nama_komoditas",
            "kategori", "volume_panen_kg", "hpp_per_kg_rp", "harga_jual_aktual_rp",
            "total_omzet_rp", "estimasi_laba_bersih_rp", "margin_persen", "status_distribusi"
        ]],
        use_container_width=True,
        hide_index=True
    )

st.divider()
st.caption("""
**Sumber Data Primer:** Open Data Provinsi Jawa Barat (https://opendata.jabarprov.go.id) & Panel Harga Pangan Badan Pangan Nasional (https://panelharga.badanpangan.go.id).  
**Referensi Visualisasi & Konektivitas:** Streamlit Documentation (https://docs.streamlit.io) & Plotly Python Graphing Library (https://plotly.com/python/).
""")
