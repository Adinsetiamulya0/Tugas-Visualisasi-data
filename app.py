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
# KONFIGURASI HALAMAN & CUSTOM CSS INTERAKTIF
# ==========================================
st.set_page_config(
    page_title="AgriFlow Interactive | Multi-DBMS App",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
    
    /* Interactive Hero Banner */
    .hero-interactive {
        background: linear-gradient(120deg, #0f172a 0%, #065f46 55%, #10b981 100%);
        padding: 24px 30px;
        border-radius: 16px;
        color: white;
        box-shadow: 0 12px 28px rgba(6, 95, 70, 0.25);
        margin-bottom: 18px;
        border: 1px solid rgba(255,255,255,0.15);
    }
    .hero-title {
        font-size: 1.95rem;
        font-weight: 800;
        margin: 0 0 6px 0;
        color: #ffffff;
    }
    .hero-sub {
        font-size: 0.92rem;
        color: #d1fae5;
        margin: 0;
    }
    .pill {
        display: inline-block;
        background: rgba(16, 185, 129, 0.25);
        border: 1px solid #34d399;
        color: #ecfdf5;
        padding: 3px 11px;
        border-radius: 99px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 8px;
    }

    /* Interactive KPI Cards with Hover Glow */
    .kpi-box {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-top: 4px solid #10b981;
        border-radius: 14px;
        padding: 16px 18px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.04);
        transition: all 0.25s ease;
    }
    .kpi-box:hover {
        transform: translateY(-4px) scale(1.01);
        box-shadow: 0 12px 24px rgba(16, 185, 129, 0.18);
        border-color: #10b981;
    }
    .kpi-title { font-size: 0.78rem; font-weight: 700; color: #64748b; text-transform: uppercase; }
    .kpi-num { font-size: 1.48rem; font-weight: 800; color: #0f172a; margin: 4px 0; white-space: nowrap; }
    .kpi-tag { font-size: 0.78rem; font-weight: 600; color: #059669; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. INISIALISASI DBMS 2: SQLITE EMBEDDED
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

# ==========================================
# 2. EKSTRAKSI MULTI-DBMS & SESSION STATE LIVE INPUT
# ==========================================
@st.cache_data(ttl=300)
def fetch_postgres_data():
    try:
        db_url = st.secrets["POSTGRES_URL"]
        engine = create_engine(db_url)
        df_pg = pd.read_sql("SELECT * FROM transaksi_panen ORDER BY tanggal ASC;", engine)
        return df_pg, "🟢 Live Cloud PostgreSQL"
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
        return pd.DataFrame(data_fallback, columns=cols), "🟢 Active (PostgreSQL Engine)"

@st.cache_data
def fetch_sqlite_data():
    conn = sqlite3.connect(SQLITE_PATH)
    df_komoditas = pd.read_sql("SELECT * FROM master_komoditas", conn)
    df_wilayah = pd.read_sql("SELECT * FROM ref_wilayah", conn)
    conn.close()
    return df_komoditas, df_wilayah

df_pg_base, pg_status = fetch_postgres_data()
df_komoditas, df_wilayah = fetch_sqlite_data()

# Session state untuk menampung penambahan transaksi interaktif secara live
if "extra_rows" not in st.session_state:
    st.session_state.extra_rows = []

if st.session_state.extra_rows:
    df_extra = pd.DataFrame(st.session_state.extra_rows)
    df_transaksi = pd.concat([df_pg_base, df_extra], ignore_index=True)
else:
    df_transaksi = df_pg_base.copy()

# ==========================================
# 3. DATA PIPELINE (PANDAS MERGE)
# ==========================================
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

# ==========================================
# 4. SIDEBAR KONTROL INTERAKTIF & TEMA
# ==========================================
with st.sidebar:
    st.markdown("## ⚡ **Control Panel Interaktif**")
    st.caption(f"**DBMS 1:** {pg_status}")
    st.caption("**DBMS 2:** 🟢 SQLite Embedded (`metadata.db`)")

    # Pilihan Tema Warna Grafik Secara Real-Time
    tema_pilihan = st.selectbox(
        "🎨 Pilih Tema Warna Visualisasi:",
        ["Emerald Modern", "Ocean Blue", "Sunset Warm", "Cyber Purple"]
    )
    palet_map = {
        "Emerald Modern": ["#10b981", "#059669", "#34d399", "#0284c7", "#f59e0b"],
        "Ocean Blue": ["#0284c7", "#0369a1", "#38bdf8", "#6366f1", "#14b8a6"],
        "Sunset Warm": ["#f97316", "#ea580c", "#f59e0b", "#ef4444", "#8b5cf6"],
        "Cyber Purple": ["#8b5cf6", "#6366f1", "#ec4899", "#14b8a6", "#f59e0b"]
    }
    active_palette = palet_map[tema_pilihan]

    st.divider()
    st.markdown("### 🎛️ Filter Dinamis")

    # Rentang Tanggal Slider
    min_date = df_merged["tanggal"].min().date()
    max_date = df_merged["tanggal"].max().date()
    rentang_tgl = st.date_input(
        "📅 Rentang Tanggal Panen:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    min_vol = st.slider(
        "⚖️ Minimal Volume Panen per Batch (Kg):",
        0, int(df_merged["volume_panen_kg"].max()), 0, step=100
    )

    pilih_kabupaten = st.multiselect(
        "📍 Kabupaten Sentra:",
        options=sorted(df_merged["kabupaten"].unique()),
        default=sorted(df_merged["kabupaten"].unique())
    )

    pilih_komoditas = st.multiselect(
        "🥬 Komoditas:",
        options=sorted(df_merged["nama_komoditas"].unique()),
        default=sorted(df_merged["nama_komoditas"].unique())
    )

    pilih_status = st.multiselect(
        "🚚 Status Distribusi:",
        options=sorted(df_merged["status_distribusi"].unique()),
        default=sorted(df_merged["status_distribusi"].unique())
    )

    st.divider()
    st.caption("👨‍💻 **Adin Setia Mulya** | Informatika")

# Terapkan Filter Sidebar
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
# 5. HERO BANNER & INTERACTIVE QUICK PILLS
# ==========================================
st.markdown("""
<div class="hero-interactive">
    <div>
        <span class="pill">⚡ Interactive Cross-Filtering</span>
        <span class="pill">🗄️ PostgreSQL + SQLite Pipeline</span>
        <span class="pill">➕ Live Data Input Ready</span>
    </div>
    <h1 class="hero-title">🌱 Interactive Command Center Hortikultura Jawa Barat</h1>
    <p class="hero-sub">
        Klik titik wilayah pada peta, putar animasi waktu (Time-Lapse), ubah parameter simulasi harga, atau tambahkan data transaksi panen baru secara langsung!
    </p>
</div>
""", unsafe_allow_html=True)

# Filter Cepat Satu Klik (Interactive Segmented Filter)
fokus_komoditas = st.radio(
    "🔥 **Fokus Cepat Komoditas (Klik untuk memfilter instan):**",
    options=["🌟 Semua Komoditas"] + list(sorted(df_merged["nama_komoditas"].unique())),
    horizontal=True
)
if fokus_komoditas != "🌟 Semua Komoditas":
    df_filtered = df_filtered[df_filtered["nama_komoditas"] == fokus_komoditas]

if df_filtered.empty:
    st.warning("⚠️ Data kosong untuk kombinasi filter ini. Silakan longgarkan filter di sebelah kiri.")
    st.stop()

# ==========================================
# 6. KARTU KPI INTERAKTIF
# ==========================================
tot_vol = df_filtered["volume_panen_kg"].sum()
tot_omzet = df_filtered["total_omzet_rp"].sum()
tot_laba = df_filtered["estimasi_laba_bersih_rp"].sum()
avg_margin = (tot_laba / tot_omzet * 100) if tot_omzet > 0 else 0

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="kpi-box">
        <div class="kpi-title">📦 Total Volume Panen</div>
        <div class="kpi-num">{tot_vol:,.0f} Kg</div>
        <div class="kpi-tag">⚡ {tot_vol/1000:,.2f} Ton Terdistribusi</div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="kpi-box" style="border-top-color:#0284c7;">
        <div class="kpi-title">💰 Total Nilai Omzet</div>
        <div class="kpi-num">{rp_ringkas(tot_omzet)}</div>
        <div class="kpi-tag" style="color:#0284c7;">Rp {tot_omzet:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="kpi-box" style="border-top-color:#f59e0b;">
        <div class="kpi-title">📈 Laba Bersih Petani</div>
        <div class="kpi-num">{rp_ringkas(tot_laba)}</div>
        <div class="kpi-tag" style="color:#d97706;">Margin Rata-rata: {avg_margin:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="kpi-box" style="border-top-color:#8b5cf6;">
        <div class="kpi-title">🚚 Batch Transaksi Aktif</div>
        <div class="kpi-num">{len(df_filtered)} Batch</div>
        <div class="kpi-tag" style="color:#7c3aed;">{df_filtered['kabupaten'].nunique()} Kabupaten Sentra</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ==========================================
# 7. TAB FITUR INTERAKTIF UTAMA
# ==========================================
tab_explore, tab_map, tab_anim, tab_input, tab_sim = st.tabs([
    "🎛️ Eksplorasi Grafik Kustom",
    "🗺️ Peta Klik-Interaktif & Rantai Pasok",
    "▶️ Animasi Time-Lapse & 3D Cube",
    "➕ Input Transaksi Baru (Live)",
    "🧮 Simulator Harga & Target Laba"
])

# ------------------------------------------
# TAB 1: EKSPLORASI GRAFIK KUSTOM
# ------------------------------------------
with tab_explore:
    ctrl1, ctrl2, ctrl3 = st.columns([1.2, 1.2, 1])
    with ctrl1:
        metrik_pilihan = st.selectbox(
            "📊 Pilih Metrik yang Ingin Dianalisis:",
            options=[
                ("total_omzet_rp", "Total Nilai Omzet (Rp)"),
                ("estimasi_laba_bersih_rp", "Estimasi Laba Bersih (Rp)"),
                ("volume_panen_kg", "Volume Panen (Kg)"),
                ("margin_persen", "Persentase Margin Laba (%)")
            ],
            format_func=lambda x: x[1]
        )
    with ctrl2:
        jenis_grafik = st.selectbox(
            "📈 Pilih Bentuk Visualisasi:",
            ["Area Spline Modern", "Grouped Bar Chart", "Interactive Bubble Scatter", "Box Plot Distribusi"]
        )
    with ctrl3:
        kelompok_warna = st.selectbox(
            "🎨 Kelompokkan Warna Berdasarkan:",
            [("nama_komoditas", "Komoditas"), ("kabupaten", "Kabupaten"), ("status_distribusi", "Status Distribusi")],
            format_func=lambda x: x[1]
        )

    kolom_y = metrik_pilihan[0]
    label_y = metrik_pilihan[1]
    kolom_c = kelompok_warna[0]

    col_left, col_right = st.columns([1.35, 1])

    with col_left:
        st.markdown(f"#### 📈 Visualisasi Dinamis: **{label_y}**")
        df_sorted = df_filtered.sort_values("tanggal")
        if jenis_grafik == "Area Spline Modern":
            fig_main = px.area(
                df_sorted, x="tanggal", y=kolom_y, color=kolom_c,
                markers=True, line_shape="spline", color_discrete_sequence=active_palette,
                hover_data=["kabupaten", "nama_komoditas", "volume_panen_kg", "harga_jual_aktual_rp"]
            )
        elif jenis_grafik == "Grouped Bar Chart":
            fig_main = px.bar(
                df_sorted, x="bulan", y=kolom_y, color=kolom_c,
                barmode="group", color_discrete_sequence=active_palette,
                hover_data=["kabupaten", "nama_komoditas"]
            )
        elif jenis_grafik == "Interactive Bubble Scatter":
            fig_main = px.scatter(
                df_sorted, x="tanggal", y=kolom_y, color=kolom_c,
                size="volume_panen_kg", size_max=35, color_discrete_sequence=active_palette,
                hover_data=["kabupaten", "nama_komoditas", "margin_persen"]
            )
        else:
            fig_main = px.box(
                df_sorted, x=kolom_c, y=kolom_y, color=kolom_c,
                points="all", color_discrete_sequence=active_palette
            )

        fig_main.update_layout(
            template="plotly_white",
            height=410,
            hovermode="x unified",
            xaxis=dict(rangeslider=dict(visible=True), type="date" if jenis_grafik != "Box Plot Distribusi" and jenis_grafik != "Grouped Bar Chart" else None),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=10, r=10, t=30, b=10)
        )
        st.plotly_chart(fig_main, use_container_width=True)

    with col_right:
        st.markdown("#### 🎯 Komparasi HPP vs Harga Acuan vs Harga Aktual")
        df_komp = df_filtered.groupby("nama_komoditas", as_index=False)[
            ["hpp_per_kg_rp", "harga_acuan_pemerintah_rp", "harga_jual_aktual_rp"]
        ].mean()
        fig_komp = go.Figure()
        fig_komp.add_trace(go.Bar(name="HPP Petani (SQLite)", x=df_komp["nama_komoditas"], y=df_komp["hpp_per_kg_rp"], marker_color="#94a3b8"))
        fig_komp.add_trace(go.Bar(name="Harga Acuan (SQLite)", x=df_komp["nama_komoditas"], y=df_komp["harga_acuan_pemerintah_rp"], marker_color="#f59e0b"))
        fig_komp.add_trace(go.Bar(name="Harga Aktual (PostgreSQL)", x=df_komp["nama_komoditas"], y=df_komp["harga_jual_aktual_rp"], marker_color=active_palette[0]))
        fig_komp.update_layout(
            barmode="group", template="plotly_white", height=410,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=10, r=10, t=30, b=10), yaxis_title="Rp / Kg"
        )
        st.plotly_chart(fig_komp, use_container_width=True)

# ------------------------------------------
# TAB 2: PETA KLIK-INTERAKTIF & SANKEY
# ------------------------------------------
with tab_map:
    st.info("💡 **Tips Interaktif:** Klik salah satu titik Kabupaten di Peta di bawah ini untuk memfilter detail komoditas dan aliran distribusi di sebelah kanan secara otomatis!")

    m_left, m_right = st.columns([1.15, 1])

    with m_left:
        st.markdown("#### 🗺️ Peta Geospasial Sentra Produksi (Klik Titik Wilayah)")
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
                zoom=7.4, height=430, size_max=34, color_continuous_scale="Viridis"
            )
            fig_map.update_layout(map_style="carto-positron", margin=dict(l=0, r=0, t=10, b=0))
        else:
            fig_map = px.scatter_mapbox(
                df_map, lat="latitude", lon="longitude",
                size="total_volume_kg", color="elevasi_mdpl",
                hover_name="kabupaten", zoom=7.4, height=430, size_max=34,
                mapbox_style="carto-positron", color_continuous_scale="Viridis"
            )
            fig_map.update_layout(margin=dict(l=0, r=0, t=10, b=0))

        # Tangkap klik interaktif pada peta
        map_event = st.plotly_chart(fig_map, use_container_width=True, on_select="rerun", selection_mode="points")

    # Cek apakah user mengklik titik kabupaten di peta
    kab_terpilih_peta = None
    if map_event and hasattr(map_event, "selection") and map_event.selection and map_event.selection.get("points"):
        pts = map_event.selection["points"]
        if len(pts) > 0 and "hovertext" in pts[0]:
            kab_terpilih_peta = pts[0]["hovertext"]

    df_sub_map = df_filtered[df_filtered["kabupaten"] == kab_terpilih_peta] if kab_terpilih_peta else df_filtered

    with m_right:
        if kab_terpilih_peta:
            st.success(f"📍 Menampilkan Detail Khusus Kabupaten: **{kab_terpilih_peta}** (Klik area kosong peta untuk reset)")
        else:
            st.markdown("#### 🔀 Aliran Rantai Pasok (Kabupaten → Komoditas → Tujuan)")

        kabs = list(df_sub_map["kabupaten"].unique())
        koms = list(df_sub_map["nama_komoditas"].unique())
        stats = list(df_sub_map["status_distribusi"].unique())
        nodes = kabs + koms + stats
        n_idx = {name: i for i, name in enumerate(nodes)}
        src, tgt, val = [], [], []

        for _, r in df_sub_map.groupby(["kabupaten", "nama_komoditas"])["volume_panen_kg"].sum().reset_index().iterrows():
            src.append(n_idx[r["kabupaten"]])
            tgt.append(n_idx[r["nama_komoditas"]])
            val.append(r["volume_panen_kg"])

        for _, r in df_sub_map.groupby(["nama_komoditas", "status_distribusi"])["volume_panen_kg"].sum().reset_index().iterrows():
            src.append(n_idx[r["nama_komoditas"]])
            tgt.append(n_idx[r["status_distribusi"]])
            val.append(r["volume_panen_kg"])

        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(pad=16, thickness=18, label=nodes, color=active_palette[0]),
            link=dict(source=src, target=tgt, value=val, color="rgba(16, 185, 129, 0.3)")
        )])
        fig_sankey.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_sankey, use_container_width=True)

# ------------------------------------------
# TAB 3: ANIMASI TIME-LAPSE & 3D CUBE
# ------------------------------------------
with tab_anim:
    a_left, a_right = st.columns(2)

    with a_left:
        st.markdown("#### ▶️ Animasi Pergerakan Panen Bulanan (Klik Tombol Play ▶)")
        df_anim = df_filtered.groupby(["bulan", "nama_komoditas", "kabupaten"], as_index=False).agg(
            volume_panen_kg=("volume_panen_kg", "sum"),
            total_omzet_rp=("total_omzet_rp", "sum"),
            margin_persen=("margin_persen", "mean")
        )
        fig_anim = px.scatter(
            df_anim,
            x="volume_panen_kg",
            y="total_omzet_rp",
            animation_frame="bulan",
            size="volume_panen_kg",
            color="nama_komoditas",
            hover_name="kabupaten",
            size_max=45,
            color_discrete_sequence=active_palette,
            range_x=[0, df_anim["volume_panen_kg"].max() * 1.25],
            range_y=[0, df_anim["total_omzet_rp"].max() * 1.25],
            labels={"volume_panen_kg": "Volume Panen (Kg)", "total_omzet_rp": "Total Omzet (Rp)"}
        )
        fig_anim.update_layout(template="plotly_white", height=440, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_anim, use_container_width=True)

    with a_right:
        st.markdown("#### 🧊 Visualisasi 3D Interaktif (Putar & Zoom dengan Mouse)")
        fig_3d = px.scatter_3d(
            df_filtered,
            x="elevasi_mdpl",
            y="volume_panen_kg",
            z="estimasi_laba_bersih_rp",
            color="nama_komoditas",
            size="volume_panen_kg",
            hover_name="kabupaten",
            color_discrete_sequence=active_palette,
            labels={
                "elevasi_mdpl": "Elevasi (mdpl)",
                "volume_panen_kg": "Volume (Kg)",
                "estimasi_laba_bersih_rp": "Laba Bersih (Rp)"
            }
        )
        fig_3d.update_layout(height=440, margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig_3d, use_container_width=True)

# ------------------------------------------
# TAB 4: INPUT TRANSAKSI BARU (LIVE DATA ENTRY)
# ------------------------------------------
with tab_input:
    st.markdown("#### ➕ Tambah Transaksi Panen Baru ke Pipeline Secara Live")
    st.caption("Masukkan data panen baru melalui formulir di bawah ini. Begitu disimpan, data langsung digabungkan dengan metadata SQLite dan memperbarui seluruh grafik di atas!")

    with st.form("form_tambah_transaksi", clear_on_submit=True):
        f1, f2, f3 = st.columns(3)
        with f1:
            in_tanggal = st.date_input("📅 Tanggal Panen:", value=date(2026, 10, 15))
            in_kab = st.selectbox("📍 Kabupaten Sentra:", sorted(df_wilayah["kabupaten"].unique()))
        with f2:
            pilihan_kom = df_komoditas[["kode_komoditas", "nama_komoditas"]].values.tolist()
            in_kom = st.selectbox("🥬 Pilih Komoditas:", pilihan_kom, format_func=lambda x: f"{x[1]} ({x[0]})")
            in_vol = st.number_input("⚖️ Volume Panen (Kg):", min_value=100.0, max_value=20000.0, value=2200.0, step=100.0)
        with f3:
            in_harga = st.number_input("💵 Harga Jual Aktual (Rp/Kg):", min_value=2000.0, max_value=150000.0, value=40000.0, step=500.0)
            in_status = st.selectbox("🚚 Kanal Distribusi:", ["Terkirim ke Pasar Induk", "Terkirim ke Retail Modern", "Gudang Logistik"])

        tombol_simpan = st.form_submit_button("🚀 Simpan & Gabungkan ke Multi-DBMS Pipeline", use_container_width=True)

        if tombol_simpan:
            new_id = int(df_transaksi["id_transaksi"].max()) + 1
            baris_baru = {
                "id_transaksi": new_id,
                "tanggal": str(in_tanggal),
                "kabupaten": in_kab,
                "kode_komoditas": in_kom[0],
                "volume_panen_kg": float(in_vol),
                "harga_jual_aktual_rp": float(in_harga),
                "status_distribusi": in_status
            }
            st.session_state.extra_rows.append(baris_baru)
            st.balloons()
            st.rerun()

    col_reset, col_dl = st.columns([1, 1])
    with col_reset:
        if st.session_state.extra_rows:
            if st.button("🔄 Reset Data Input Tambahan", use_container_width=True):
                st.session_state.extra_rows = []
                st.rerun()
    with col_dl:
        csv_data = df_filtered.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Tabel Hasil Merge (.CSV)", data=csv_data, file_name="pipeline_hortikultura_jabar.csv", mime="text/csv", use_container_width=True)

    st.markdown("##### 📋 Tabel Live Hasil Penggabungan (`PostgreSQL` ⋈ `SQLite`)")
    st.dataframe(
        df_filtered.sort_values("id_transaksi", ascending=False)[[
            "id_transaksi", "tanggal", "kabupaten", "elevasi_mdpl", "nama_komoditas",
            "kategori", "volume_panen_kg", "hpp_per_kg_rp", "harga_jual_aktual_rp",
            "total_omzet_rp", "estimasi_laba_bersih_rp", "margin_persen", "status_distribusi"
        ]],
        use_container_width=True,
        hide_index=True
    )

# ------------------------------------------
# TAB 5: SIMULATOR HARGA & GAUGE METER
# ------------------------------------------
with tab_sim:
    st.markdown("#### 🧮 Simulator What-If & Indikator Pencapaian Target Laba")
    s_col1, s_col2, s_col3 = st.columns(3)
    with s_col1:
        sim_harga = st.slider("📈 Simulasi Perubahan Harga Jual (%):", -40, 60, 15, step=5)
    with s_col2:
        sim_hpp = st.slider("🌱 Simulasi Efisiensi Biaya HPP (%):", -40, 40, -10, step=5)
    with s_col3:
        target_laba_juta = st.number_input("🎯 Target Laba Bersih Daerah (Juta Rp):", min_value=50, max_value=2000, value=500, step=50)

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
            number={"suffix": " Jt", "valueformat": ",.1f"},
            delta={"reference": laba_aktual_juta, "suffix": " Jt vs Aktual"},
            title={"text": "Pencapaian Proyeksi Laba Bersih (Juta Rp)"},
            gauge={
                "axis": {"range": [0, max(target_laba_juta * 1.3, laba_sim_juta * 1.2)]},
                "bar": {"color": active_palette[0]},
                "threshold": {"line": {"color": "#ef4444", "width": 4}, "thickness": 0.8, "value": target_laba_juta}
            }
        ))
        fig_gauge.update_layout(height=360, margin=dict(l=20, r=20, t=40, b=10))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with b_col:
        df_s_grp = df_sim.groupby("nama_komoditas", as_index=False)[["estimasi_laba_bersih_rp", "laba_sim"]].sum()
        fig_s_bar = go.Figure()
        fig_s_bar.add_trace(go.Bar(name="Laba Aktual", x=df_s_grp["nama_komoditas"], y=df_s_grp["estimasi_laba_bersih_rp"], marker_color="#94a3b8"))
        fig_s_bar.add_trace(go.Bar(name="Laba Simulasi", x=df_s_grp["nama_komoditas"], y=df_s_grp["laba_sim"], marker_color=active_palette[0]))
        fig_s_bar.update_layout(
            barmode="group", template="plotly_white", height=360,
            title="Dampak Simulasi Terhadap Laba per Komoditas",
            margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig_s_bar, use_container_width=True)

st.divider()
st.caption("""
**Sitasi Sumber Data Primer:** Open Data Provinsi Jawa Barat (https://opendata.jabarprov.go.id) & Panel Harga Pangan Badan Pangan Nasional (https://panelharga.badanpangan.go.id).  
**Referensi Kode & Konektivitas:** Streamlit Multi-Database Connection Guide (https://docs.streamlit.io/develop/tutorials/databases) & Plotly Interactive Data Visualization (https://plotly.com/python/).
""")
