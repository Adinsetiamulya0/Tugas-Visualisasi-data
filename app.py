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
# KONFIGURASI HALAMAN & DESAIN VISUAL KREATIF
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

    /* Hero Banner dengan Foto Perkebunan Asli */
    .hero-photo {
        background-image: linear-gradient(90deg, rgba(6, 78, 59, 0.92) 0%, rgba(4, 120, 87, 0.78) 55%, rgba(16, 185, 129, 0.45) 100%), 
                          url('https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1600&q=80');
        background-size: cover;
        background-position: center;
        padding: 42px 38px;
        border-radius: 24px;
        color: white;
        box-shadow: 0 18px 35px rgba(6, 78, 59, 0.22);
        margin-bottom: 26px;
    }
    .hero-photo h1 {
        font-size: 2.35rem;
        font-weight: 800;
        color: #ffffff;
        margin: 0 0 10px 0;
        text-shadow: 0 2px 10px rgba(0,0,0,0.25);
    }
    .hero-photo p {
        font-size: 1.02rem;
        color: #ecfdf5;
        max-width: 780px;
        margin: 0;
        line-height: 1.6;
    }

    /* Kartu KPI Berwarna Gradasi Modern */
    .metric-card-1 {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white; padding: 22px; border-radius: 20px;
        box-shadow: 0 10px 20px rgba(16, 185, 129, 0.25);
    }
    .metric-card-2 {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white; padding: 22px; border-radius: 20px;
        box-shadow: 0 10px 20px rgba(59, 130, 246, 0.25);
    }
    .metric-card-3 {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white; padding: 22px; border-radius: 20px;
        box-shadow: 0 10px 20px rgba(245, 158, 11, 0.25);
    }
    .metric-card-4 {
        background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
        color: white; padding: 22px; border-radius: 20px;
        box-shadow: 0 10px 20px rgba(139, 92, 246, 0.25);
    }
    .m-label { font-size: 0.85rem; font-weight: 600; opacity: 0.9; text-transform: uppercase; letter-spacing: 0.5px; }
    .m-val { font-size: 1.65rem; font-weight: 800; margin: 6px 0; white-space: nowrap; }
    .m-sub { font-size: 0.82rem; opacity: 0.92; font-weight: 500; }

    /* Kartu Galeri Foto Komoditas */
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
        box-shadow: 0 14px 28px rgba(16, 185, 129, 0.18);
    }
    .crop-img {
        width: 100%;
        height: 135px;
        object-fit: cover;
    }
    .crop-body {
        padding: 14px 16px;
    }
    .crop-title {
        font-weight: 800;
        font-size: 0.98rem;
        color: #0f172a;
        margin-bottom: 4px;
    }
    .crop-price {
        font-size: 0.85rem;
        font-weight: 700;
        color: #059669;
    }
    .crop-vol {
        font-size: 0.78rem;
        color: #64748b;
        margin-top: 4px;
    }

    /* Sidebar Foto Header */
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

# Foto Ilustrasi Komoditas Resolusi Tinggi
FOTO_KOMODITAS = {
    "Cabai Merah Keriting": "https://images.unsplash.com/photo-1588252303782-cb80119abd6d?auto=format&fit=crop&w=600&q=80",
    "Kubis / Engkol": "https://images.unsplash.com/photo-1594282486552-05b4d80fbb9f?auto=format&fit=crop&w=600&q=80",
    "Tomat Sayur": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&w=600&q=80",
    "Kentang Granola": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=600&q=80",
    "Bawang Merah": "https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?auto=format&fit=crop&w=600&q=80"
}

# ==========================================
# 2. PENGAMBILAN & PENGGABUNGAN DATA
# ==========================================
@st.cache_data(ttl=300)
def fetch_postgres_data():
    try:
        db_url = st.secrets["POSTGRES_URL"]
        engine = create_engine(db_url)
        return pd.read_sql("SELECT * FROM transaksi_panen ORDER BY tanggal ASC;", engine)
    except Exception:
        data_fallback = [
            (1, '2026-05-05', 'Sumedang', 'KMD-01', 1250.50, 38000, 'Terkirim ke Pasar Induk'),
            (2, '2026-05-12', 'Sumedang', 'KMD-02', 2400.00, 8500, 'Terkirim ke Pasar Induk'),
            (3, '2026-05-18', 'Garut', 'KMD-01', 1800.00, 36500, 'Terkirim ke Retail Modern'),
            (4, '2026-05-25', 'Bandung', 'KMD-03', 3100.00, 14000, 'Terkirim ke Pasar Induk'),
            (5, '2026-06-02', 'Sumedang', 'KMD-01', 1420.00, 42000, 'Terkirim ke Retail Modern'),
            (6, '2026-06-10', 'Majalengka', 'KMD-05', 1950.00, 31000, 'Terkirim ke Pasar Induk'),
            (7, '2026-06-15', 'Garut', 'KMD-02', 2850.00, 7800, 'Gudang Logistik'),
            (8, '2026-06-22', 'Bandung', 'KMD-04', 4200.00, 16500, 'Terkirim ke Retail Modern'),
            (9, '2026-07-04', 'Sumedang', 'KMD-02', 2600.00, 9200, 'Terkirim ke Pasar Induk'),
            (10, '2026-07-11', 'Cianjur', 'KMD-03', 1750.00, 15200, 'Terkirim ke Pasar Induk'),
            (11, '2026-07-19', 'Sumedang', 'KMD-01', 1680.00, 45000, 'Terkirim ke Retail Modern'),
            (12, '2026-07-27', 'Garut', 'KMD-04', 3500.00, 17000, 'Terkirim ke Pasar Induk'),
            (13, '2026-08-03', 'Bandung', 'KMD-02', 3900.00, 8900, 'Terkirim ke Pasar Induk'),
            (14, '2026-08-14', 'Majalengka', 'KMD-01', 1100.00, 41000, 'Gudang Logistik'),
            (15, '2026-08-21', 'Sumedang', 'KMD-03', 2100.00, 13800, 'Terkirim ke Pasar Induk'),
            (16, '2026-09-02', 'Cianjur', 'KMD-05', 1550.00, 33000, 'Terkirim ke Retail Modern'),
            (17, '2026-09-10', 'Sumedang', 'KMD-01', 1900.00, 39500, 'Terkirim ke Pasar Induk'),
            (18, '2026-09-18', 'Garut', 'KMD-02', 3100.00, 8400, 'Terkirim ke Retail Modern'),
            (19, '2026-09-25', 'Bandung', 'KMD-04', 4600.00, 17500, 'Terkirim ke Pasar Induk'),
            (20, '2026-10-05', 'Sumedang', 'KMD-02', 2950.00, 9500, 'Terkirim ke Retail Modern')
        ]
        cols = ['id_transaksi', 'tanggal', 'kabupaten', 'kode_komoditas', 'volume_panen_kg', 'harga_jual_aktual_rp', 'status_distribusi']
        return pd.DataFrame(data_fallback, columns=cols)

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
# 3. SIDEBAR BERSIH DENGAN GAMBAR ILUSTRASI
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

    pilih_komoditas = st.multiselect(
        "🥬 Jenis Komoditas:",
        options=sorted(df_merged["nama_komoditas"].unique()),
        default=sorted(df_merged["nama_komoditas"].unique())
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
    (df_merged["nama_komoditas"].isin(pilih_komoditas)) &
    (df_merged["status_distribusi"].isin(pilih_status))
].copy()

# ==========================================
# 4. HERO BANNER FOTOGRAFI PERKEBUNAN
# ==========================================
st.markdown("""
<div class="hero-photo">
    <h1>🌾 Dashboard Sentra Hortikultura Jawa Barat</h1>
    <p>
        Pemantauan interaktif hasil panen petani, pergerakan harga pasar, estimasi keuntungan bersih, serta pemetaan geospasial distribusi sayuran unggulan di Jawa Barat.
    </p>
</div>
""", unsafe_allow_html=True)

# Filter Instan Satu Klik
fokus_komoditas = st.radio(
    "✨ **Pilih Komoditas Unggulan untuk Eksplorasi Cepat:**",
    options=["🌟 Semua Komoditas"] + list(sorted(df_merged["nama_komoditas"].unique())),
    horizontal=True
)
if fokus_komoditas != "🌟 Semua Komoditas":
    df_filtered = df_filtered[df_filtered["nama_komoditas"] == fokus_komoditas]

if df_filtered.empty:
    st.warning("⚠️ Tidak ada data untuk filter yang dipilih. Silakan sesuaikan pilihan di sebelah kiri.")
    st.stop()

# ==========================================
# 5. GALERI KARTU FOTO KOMODITAS (VISUAL CARDS)
# ==========================================
st.markdown("#### 📸 Galeri Komoditas & Ringkasan Harga Pasar")
cols_galeri = st.columns(5)
semua_kom = sorted(df_merged["nama_komoditas"].unique())

for idx, nama_k in enumerate(semua_kom):
    df_k = df_filtered[df_filtered["nama_komoditas"] == nama_k]
    vol_k = df_k["volume_panen_kg"].sum()
    rata_harga = df_k["harga_jual_aktual_rp"].mean() if not df_k.empty else 0
    img_url = FOTO_KOMODITAS.get(nama_k, "")
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

st.write("")

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
    "🗺️ Peta Wilayah & Alur Distribusi",
    "▶️ Animasi Pertumbuhan & Grafik 3D",
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
# TAB 2: PETA WILAYAH & ALUR DISTRIBUSI
# ------------------------------------------
with tab_map:
    st.info("💡 **Klik salah satu bulatan wilayah di Peta Jawa Barat** untuk memfilter rincian alur pengiriman komoditas di sebelah kanan!")

    p_kiri, p_kanan = st.columns([1.15, 1])

    with p_kiri:
        st.markdown("#### 🗺️ Peta Lokasi Sentra Panen Jawa Barat")
        df_map = df_filtered.groupby(
            ["kabupaten", "latitude", "longitude", "elevasi_mdpl"], as_index=False
        ).agg(
            total_volume_kg=("volume_panen_kg", "sum"),
            total_omzet=("total_omzet_rp", "sum"),
            rata_margin=("margin_persen", "mean")
        )

        if hasattr(px, "scatter_map"):
            fig_map = px.scatter_map(
                df_map, lat="latitude", lon="longitude",
                size="total_volume_kg", color="elevasi_mdpl",
                hover_name="kabupaten",
                hover_data={"total_volume_kg": ":,.0f", "total_omzet": ":,.0f", "rata_margin": ":.1f"},
                zoom=7.4, height=430, size_max=36, color_continuous_scale="Tealgrn"
            )
            fig_map.update_layout(map_style="carto-positron", margin=dict(l=0, r=0, t=10, b=0))
        else:
            fig_map = px.scatter_mapbox(
                df_map, lat="latitude", lon="longitude",
                size="total_volume_kg", color="elevasi_mdpl",
                hover_name="kabupaten", zoom=7.4, height=430, size_max=36,
                mapbox_style="carto-positron", color_continuous_scale="Tealgrn"
            )
            fig_map.update_layout(margin=dict(l=0, r=0, t=10, b=0))

        map_event = st.plotly_chart(fig_map, use_container_width=True, on_select="rerun", selection_mode="points")

    kab_terpilih = None
    if map_event and hasattr(map_event, "selection") and map_event.selection and map_event.selection.get("points"):
        pts = map_event.selection["points"]
        if len(pts) > 0 and "hovertext" in pts[0]:
            kab_terpilih = pts[0]["hovertext"]

    df_sub = df_filtered[df_filtered["kabupaten"] == kab_terpilih] if kab_terpilih else df_filtered

    with p_kanan:
        if kab_terpilih:
            st.success(f"📍 Menampilkan Alur Pengiriman Khusus Wilayah: **{kab_terpilih}**")
        else:
            st.markdown("#### 🔀 Alur Distribusi Hasil Panen (Kabupaten → Komoditas → Pasar)")

        kabs = list(df_sub["kabupaten"].unique())
        koms = list(df_sub["nama_komoditas"].unique())
        stats = list(df_sub["status_distribusi"].unique())
        nodes = kabs + koms + stats
        n_idx = {name: i for i, name in enumerate(nodes)}
        src, tgt, val = [], [], []

        for _, r in df_sub.groupby(["kabupaten", "nama_komoditas"])["volume_panen_kg"].sum().reset_index().iterrows():
            src.append(n_idx[r["kabupaten"]])
            tgt.append(n_idx[r["nama_komoditas"]])
            val.append(r["volume_panen_kg"])

        for _, r in df_sub.groupby(["nama_komoditas", "status_distribusi"])["volume_panen_kg"].sum().reset_index().iterrows():
            src.append(n_idx[r["nama_komoditas"]])
            tgt.append(n_idx[r["status_distribusi"]])
            val.append(r["volume_panen_kg"])

        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(pad=16, thickness=18, label=nodes, color="#10b981"),
            link=dict(source=src, target=tgt, value=val, color="rgba(16, 185, 129, 0.28)")
        )])
        fig_sankey.update_layout(height=410, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_sankey, use_container_width=True)

# ------------------------------------------
# TAB 3: ANIMASI & GRAFIK 3D
# ------------------------------------------
with tab_anim:
    a_kiri, a_kanan = st.columns(2)

    with a_kiri:
        st.markdown("#### ▶️ Animasi Pergerakan Panen per Bulan (Klik Tombol Play ▶)")
        df_anim = df_filtered.groupby(["bulan", "nama_komoditas", "kabupaten"], as_index=False).agg(
            volume_panen_kg=("volume_panen_kg", "sum"),
            total_omzet_rp=("total_omzet_rp", "sum")
        )
        fig_anim = px.scatter(
            df_anim, x="volume_panen_kg", y="total_omzet_rp",
            animation_frame="bulan", size="volume_panen_kg",
            color="nama_komoditas", hover_name="kabupaten",
            size_max=45, color_discrete_sequence=palet_utama,
            range_x=[0, df_anim["volume_panen_kg"].max() * 1.25],
            range_y=[0, df_anim["total_omzet_rp"].max() * 1.25],
            labels={"volume_panen_kg": "Volume Panen (Kg)", "total_omzet_rp": "Nilai Penjualan (Rp)"}
        )
        fig_anim.update_layout(template="plotly_white", height=430, margin=dict(l=10, r=10, t=20, b=10))
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
        fig_3d.update_layout(height=430, margin=dict(l=0, r=0, t=20, b=0))
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
            in_tanggal = st.date_input("📅 Tanggal Panen:", value=date(2026, 10, 15))
            in_kab = st.selectbox("📍 Kabupaten:", sorted(df_wilayah["kabupaten"].unique()))
        with f2:
            pilihan_kom = df_komoditas[["kode_komoditas", "nama_komoditas"]].values.tolist()
            in_kom = st.selectbox("🥬 Komoditas:", pilihan_kom, format_func=lambda x: x[1])
            in_vol = st.number_input("⚖️ Volume Panen (Kg):", min_value=100.0, max_value=20000.0, value=2200.0, step=100.0)
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
