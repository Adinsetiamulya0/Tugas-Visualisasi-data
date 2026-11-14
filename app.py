import os
import sqlite3
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine

# ==========================================
# KONFIGURASI HALAMAN & CUSTOM CSS MODERN
# ==========================================
st.set_page_config(
    page_title="AgriFlow Jabar | Multi-DBMS Analytics",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Background & Tipografi */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    
    /* Hero Banner */
    .hero-box {
        background: linear-gradient(135deg, #064e3b 0%, #047857 55%, #10b981 100%);
        padding: 28px 32px;
        border-radius: 18px;
        color: white;
        box-shadow: 0 10px 25px rgba(4, 120, 87, 0.22);
        margin-bottom: 24px;
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        margin: 0 0 8px 0;
        letter-spacing: -0.5px;
        color: #ffffff;
    }
    .hero-subtitle {
        font-size: 0.98rem;
        opacity: 0.92;
        margin: 0;
        line-height: 1.5;
        color: #ecfdf5;
    }
    .badge-arch {
        display: inline-block;
        background: rgba(255, 255, 255, 0.18);
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 8px;
        margin-bottom: 10px;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }

    /* Kartu KPI Kustom (Tidak Terpotong) */
    .kpi-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 5px solid #10b981;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        transition: transform 0.2s ease;
        height: 100%;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 18px rgba(16, 185, 129, 0.12);
    }
    .kpi-label {
        font-size: 0.82rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.55rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 6px;
        white-space: nowrap;
    }
    .kpi-sub {
        font-size: 0.8rem;
        color: #059669;
        font-weight: 600;
    }

    /* Status Badge Sidebar */
    .db-badge {
        background: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        padding: 10px 12px;
        margin-bottom: 10px;
        font-size: 0.82rem;
    }
    .dot-green {
        height: 9px;
        width: 9px;
        background-color: #10b981;
        border-radius: 50%;
        display: inline-block;
        margin-right: 6px;
    }
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

    data_komoditas = [
        ('KMD-01', 'Cabai Merah Keriting', 'Sayuran Buah', 22000, 35000, 7),
        ('KMD-02', 'Kubis / Engkol', 'Sayuran Daun', 4500, 8000, 14),
        ('KMD-03', 'Tomat Sayur', 'Sayuran Buah', 7500, 13000, 5),
        ('KMD-04', 'Kentang Granola', 'Umbi-umbian', 10000, 16000, 30),
        ('KMD-05', 'Bawang Merah', 'Umbi-umbian', 19000, 30000, 25)
    ]
    cursor.executemany("INSERT OR REPLACE INTO master_komoditas VALUES (?, ?, ?, ?, ?, ?)", data_komoditas)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ref_wilayah (
        kabupaten TEXT PRIMARY KEY,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        elevasi_mdpl INTEGER NOT NULL
    )
    """)

    data_wilayah = [
        ('Sumedang', -6.8586, 107.9204, 750),
        ('Garut', -7.2279, 107.9087, 717),
        ('Bandung', -7.0251, 107.5198, 1100),
        ('Majalengka', -6.8364, 108.2274, 600),
        ('Cianjur', -6.8168, 107.1425, 1050)
    ]
    cursor.executemany("INSERT OR REPLACE INTO ref_wilayah VALUES (?, ?, ?, ?)", data_wilayah)

    conn.commit()
    conn.close()

init_sqlite_db(SQLITE_PATH)

# ==========================================
# 2. EKSTRAKSI DATA DARI 2 DBMS BERBEDA
# ==========================================
@st.cache_data(ttl=300)
def fetch_postgres_data():
    try:
        db_url = st.secrets["POSTGRES_URL"]
        engine = create_engine(db_url)
        query = "SELECT * FROM transaksi_panen ORDER BY tanggal ASC;"
        df_pg = pd.read_sql(query, engine)
        return df_pg, "Live Cloud (Supabase PostgreSQL)"
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
        return pd.DataFrame(data_fallback, columns=cols), "Active (PostgreSQL Seed Engine)"

@st.cache_data
def fetch_sqlite_data():
    conn = sqlite3.connect(SQLITE_PATH)
    df_komoditas = pd.read_sql("SELECT * FROM master_komoditas", conn)
    df_wilayah = pd.read_sql("SELECT * FROM ref_wilayah", conn)
    conn.close()
    return df_komoditas, df_wilayah

# ==========================================
# 3. DATA PIPELINE & FEDERATION (PANDAS MERGE)
# ==========================================
df_transaksi, pg_status = fetch_postgres_data()
df_komoditas, df_wilayah = fetch_sqlite_data()

df_merged = pd.merge(df_transaksi, df_komoditas, on="kode_komoditas", how="left")
df_merged = pd.merge(df_merged, df_wilayah, on="kabupaten", how="left")

df_merged["tanggal"] = pd.to_datetime(df_merged["tanggal"])
df_merged["bulan"] = df_merged["tanggal"].dt.strftime("%Y-%m")
df_merged["total_omzet_rp"] = df_merged["volume_panen_kg"] * df_merged["harga_jual_aktual_rp"]
df_merged["total_biaya_hpp_rp"] = df_merged["volume_panen_kg"] * df_merged["hpp_per_kg_rp"]
df_merged["estimasi_laba_bersih_rp"] = df_merged["total_omzet_rp"] - df_merged["total_biaya_hpp_rp"]
df_merged["margin_persen"] = (df_merged["estimasi_laba_bersih_rp"] / df_merged["total_omzet_rp"]) * 100

def format_rupiah_ringkas(nilai):
    if abs(nilai) >= 1_000_000_000:
        return f"Rp {nilai / 1_000_000_000:,.2f} Miliar"
    elif abs(nilai) >= 1_000_000:
        return f"Rp {nilai / 1_000_000:,.2f} Juta"
    else:
        return f"Rp {nilai:,.0f}"

# ==========================================
# 4. SIDEBAR FILTER & KONTROL PIPELINE
# ==========================================
with st.sidebar:
    st.markdown("## 🌿 **AgriFlow Jabar**")
    st.caption("Multi-DBMS Data Pipeline & Analytics")
    
    st.markdown(f"""
    <div class="db-badge">
        <div><span class="dot-green"></span><b>DBMS 1 (PostgreSQL)</b></div>
        <div style="color:#475569; padding-left:15px;">{pg_status}</div>
        <div style="margin-top:6px;"><span class="dot-green"></span><b>DBMS 2 (SQLite3)</b></div>
        <div style="color:#475569; padding-left:15px;">Embedded (metadata_komoditas.db)</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("### 🔍 Filter Interaktif")

    pilih_kabupaten = st.multiselect(
        "📍 Sentra Kabupaten:",
        options=sorted(df_merged["kabupaten"].unique()),
        default=sorted(df_merged["kabupaten"].unique())
    )

    pilih_komoditas = st.multiselect(
        "🥬 Komoditas Hortikultura:",
        options=sorted(df_merged["nama_komoditas"].unique()),
        default=sorted(df_merged["nama_komoditas"].unique())
    )

    pilih_status = st.multiselect(
        "🚚 Kanal Distribusi:",
        options=sorted(df_merged["status_distribusi"].unique()),
        default=sorted(df_merged["status_distribusi"].unique())
    )

    st.divider()
    st.caption("👨‍💻 **Adin Setia Mulya**  \nProdi Informatika - Universitas Sebelas April")

df_filtered = df_merged[
    (df_merged["kabupaten"].isin(pilih_kabupaten)) &
    (df_merged["nama_komoditas"].isin(pilih_komoditas)) &
    (df_merged["status_distribusi"].isin(pilih_status))
].copy()

# ==========================================
# 5. HERO BANNER & KARTU KPI EKSEKUTIF
# ==========================================
st.markdown("""
<div class="hero-box">
    <div>
        <span class="badge-arch">🗄️ DBMS 1: PostgreSQL (Transaksi Panen)</span>
        <span class="badge-arch">📦 DBMS 2: SQLite (Master HPP & Geospasial)</span>
        <span class="badge-arch">🔗 Pipeline: Python Pandas Merge</span>
    </div>
    <h1 class="hero-title">🌱 Command Center Rantai Pasok Hortikultura Jawa Barat</h1>
    <p class="hero-subtitle">
        Integrasi arsitektur Multi-DBMS secara <i>real-time</i> untuk memantau produktivitas panen, struktur biaya pokok produksi (HPP), disparitas harga acuan pemerintah, dan pemetaan geospasial sentra komoditas.
    </p>
</div>
""", unsafe_allow_html=True)

if df_filtered.empty:
    st.warning("⚠️ Tidak ada data yang cocok dengan kombinasi filter di sebelah kiri. Silakan pilih minimal satu wilayah dan komoditas.")
    st.stop()

tot_vol = df_filtered["volume_panen_kg"].sum()
tot_omzet = df_filtered["total_omzet_rp"].sum()
tot_laba = df_filtered["estimasi_laba_bersih_rp"].sum()
avg_margin = (tot_laba / tot_omzet * 100) if tot_omzet > 0 else 0
tot_batch = len(df_filtered)

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">📦 Total Volume Panen</div>
        <div class="kpi-value">{tot_vol:,.0f} Kg</div>
        <div class="kpi-sub">Setara {tot_vol/1000:,.2f} Ton Komoditas Segar</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: #0284c7;">
        <div class="kpi-label">💰 Nilai Transaksi (Omzet)</div>
        <div class="kpi-value">{format_rupiah_ringkas(tot_omzet)}</div>
        <div class="kpi-sub">Rp {tot_omzet:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: #f59e0b;">
        <div class="kpi-label">📈 Estimasi Laba Bersih Petani</div>
        <div class="kpi-value">{format_rupiah_ringkas(tot_laba)}</div>
        <div class="kpi-sub">Rata-rata Margin Bersih: {avg_margin:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: #8b5cf6;">
        <div class="kpi-label">🚚 Frekuensi Pengiriman</div>
        <div class="kpi-value">{tot_batch} Batch</div>
        <div class="kpi-sub">Dari {df_filtered['kabupaten'].nunique()} Kabupaten Sentra</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ==========================================
# 6. TABS VISUALISASI KREATIF & INTERAKTIF
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Ringkasan Eksekutif & Profitabilitas",
    "🗺️ Peta Geospasial & Aliran Rantai Pasok",
    "🧮 Simulator Harga & Laba Petani",
    "🗄️ Inspeksi Arsitektur Multi-DBMS"
])

color_palette = ["#10b981", "#0284c7", "#f59e0b", "#8b5cf6", "#ef4444"]

# ------------------------------------------
# TAB 1: RINGKASAN EKSEKUTIF
# ------------------------------------------
with tab1:
    col_a, col_b = st.columns([1.2, 1])

    with col_a:
        st.markdown("#### 📈 Tren Dinamika Omzet Panen per Komoditas")
        fig_area = px.area(
            df_filtered.sort_values("tanggal"),
            x="tanggal",
            y="total_omzet_rp",
            color="nama_komoditas",
            markers=True,
            color_discrete_sequence=color_palette,
            hover_data=["kabupaten", "volume_panen_kg", "harga_jual_aktual_rp"],
            labels={
                "total_omzet_rp": "Nilai Omzet (Rp)",
                "tanggal": "Tanggal Transaksi",
                "nama_komoditas": "Komoditas"
            }
        )
        fig_area.update_layout(
            template="plotly_white",
            height=390,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=10, r=10, t=30, b=10)
        )
        st.plotly_chart(fig_area, use_container_width=True)

    with col_b:
        st.markdown("#### 🏛️ Omzet vs Biaya HPP vs Laba Bersih per Kabupaten")
        df_kab = df_filtered.groupby("kabupaten", as_index=False)[
            ["total_omzet_rp", "total_biaya_hpp_rp", "estimasi_laba_bersih_rp"]
        ].sum()
        df_kab_melt = df_kab.melt(
            id_vars="kabupaten",
            value_vars=["total_omzet_rp", "total_biaya_hpp_rp", "estimasi_laba_bersih_rp"],
            var_name="Metrik",
            value_name="Rupiah"
        )
        df_kab_melt["Metrik"] = df_kab_melt["Metrik"].replace({
            "total_omzet_rp": "Total Omzet",
            "total_biaya_hpp_rp": "Total Biaya HPP",
            "estimasi_laba_bersih_rp": "Laba Bersih"
        })
        fig_bar = px.bar(
            df_kab_melt,
            x="kabupaten",
            y="Rupiah",
            color="Metrik",
            barmode="group",
            color_discrete_map={
                "Total Omzet": "#0284c7",
                "Total Biaya HPP": "#94a3b8",
                "Laba Bersih": "#10b981"
            }
        )
        fig_bar.update_layout(
            template="plotly_white",
            height=390,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=10, r=10, t=30, b=10)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    col_c, col_d = st.columns([1, 1])

    with col_c:
        st.markdown("#### 🎯 Perbandingan Harga Jual Aktual vs Harga Acuan Pemerintah (Rp/Kg)")
        df_harga = df_filtered.groupby("nama_komoditas", as_index=False)[
            ["hpp_per_kg_rp", "harga_acuan_pemerintah_rp", "harga_jual_aktual_rp"]
        ].mean()
        fig_price = go.Figure()
        fig_price.add_trace(go.Bar(
            name="HPP Petani (SQLite)",
            x=df_harga["nama_komoditas"],
            y=df_harga["hpp_per_kg_rp"],
            marker_color="#cbd5e1"
        ))
        fig_price.add_trace(go.Bar(
            name="Harga Acuan Pemerintah (SQLite)",
            x=df_harga["nama_komoditas"],
            y=df_harga["harga_acuan_pemerintah_rp"],
            marker_color="#f59e0b"
        ))
        fig_price.add_trace(go.Bar(
            name="Rata-rata Harga Aktual (PostgreSQL)",
            x=df_harga["nama_komoditas"],
            y=df_harga["harga_jual_aktual_rp"],
            marker_color="#10b981"
        ))
        fig_price.update_layout(
            barmode="group",
            template="plotly_white",
            height=360,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=10, r=10, t=30, b=10),
            yaxis_title="Rupiah / Kg"
        )
        st.plotly_chart(fig_price, use_container_width=True)

    with col_d:
        st.markdown("#### 🥬 Hierarki Distribusi Volume Komoditas (Sunburst Chart)")
        fig_sun = px.sunburst(
            df_filtered,
            path=["kategori", "nama_komoditas", "status_distribusi"],
            values="volume_panen_kg",
            color="kategori",
            color_discrete_sequence=["#10b981", "#0284c7", "#f59e0b"]
        )
        fig_sun.update_layout(
            height=360,
            margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig_sun, use_container_width=True)

# ------------------------------------------
# TAB 2: PETA GEOSPASIAL & SANKEY DIAGRAM
# ------------------------------------------
with tab2:
    col_map, col_sankey = st.columns([1.15, 1])

    with col_map:
        st.markdown("#### 🗺️ Peta Geospasial Sentra Produksi Jawa Barat (Integrasi Koordinat SQLite)")
        df_map = df_filtered.groupby(
            ["kabupaten", "latitude", "longitude", "elevasi_mdpl"], as_index=False
        ).agg(
            total_volume_kg=("volume_panen_kg", "sum"),
            total_omzet=("total_omzet_rp", "sum")
        )

        # Kompatibilitas penuh untuk Plotly v5 maupun Plotly v6+
        if hasattr(px, "scatter_map"):
            fig_map = px.scatter_map(
                df_map,
                lat="latitude",
                lon="longitude",
                size="total_volume_kg",
                color="elevasi_mdpl",
                hover_name="kabupaten",
                hover_data={"total_volume_kg": ":,.0f", "total_omzet": ":,.0f", "elevasi_mdpl": True},
                zoom=7.4,
                height=440,
                size_max=32,
                color_continuous_scale="Tealgrn",
                labels={"total_volume_kg": "Volume (Kg)", "elevasi_mdpl": "Elevasi (mdpl)"}
            )
            fig_map.update_layout(map_style="carto-positron", margin=dict(l=0, r=0, t=10, b=0))
        else:
            fig_map = px.scatter_mapbox(
                df_map,
                lat="latitude",
                lon="longitude",
                size="total_volume_kg",
                color="elevasi_mdpl",
                hover_name="kabupaten",
                zoom=7.4,
                height=440,
                size_max=32,
                mapbox_style="carto-positron",
                color_continuous_scale="Tealgrn"
            )
            fig_map.update_layout(margin=dict(l=0, r=0, t=10, b=0))

        st.plotly_chart(fig_map, use_container_width=True)

    with col_sankey:
        st.markdown("#### 🔀 Diagram Alir Rantai Pasok (Kabupaten → Komoditas → Kanal Distribusi)")
        # Membangun Sankey Diagram dari df_filtered
        kabs = list(df_filtered["kabupaten"].unique())
        koms = list(df_filtered["nama_komoditas"].unique())
        stats = list(df_filtered["status_distribusi"].unique())
        all_nodes = kabs + koms + stats
        node_idx = {name: i for i, name in enumerate(all_nodes)}

        sources, targets, values = [], [], []

        # Link 1: Kabupaten -> Komoditas
        g1 = df_filtered.groupby(["kabupaten", "nama_komoditas"])["volume_panen_kg"].sum().reset_index()
        for _, row in g1.iterrows():
            sources.append(node_idx[row["kabupaten"]])
            targets.append(node_idx[row["nama_komoditas"]])
            values.append(row["volume_panen_kg"])

        # Link 2: Komoditas -> Status Distribusi
        g2 = df_filtered.groupby(["nama_komoditas", "status_distribusi"])["volume_panen_kg"].sum().reset_index()
        for _, row in g2.iterrows():
            sources.append(node_idx[row["nama_komoditas"]])
            targets.append(node_idx[row["status_distribusi"]])
            values.append(row["volume_panen_kg"])

        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(
                pad=18,
                thickness=18,
                line=dict(color="#cbd5e1", width=0.5),
                label=all_nodes,
                color="#10b981"
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                color="rgba(16, 185, 129, 0.28)"
            )
        )])
        fig_sankey.update_layout(height=440, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_sankey, use_container_width=True)

# ------------------------------------------
# TAB 3: SIMULATOR WHAT-IF LABA PETANI
# ------------------------------------------
with tab3:
    st.markdown("#### 🧮 Simulator Sensitivitas Harga Pasar & Efisiensi Biaya Produksi (HPP)")
    st.caption("Geser parameter di bawah untuk mensimulasikan dampak perubahan harga pasar dan efisiensi pupuk/bibit terhadap laba bersih petani.")

    s1, s2 = st.columns(2)
    with s1:
        sim_harga_pct = st.slider("📈 Simulasi Perubahan Harga Jual Pasar (%):", -30, 50, 10, step=5)
    with s2:
        sim_hpp_pct = st.slider("🌱 Simulasi Efisiensi / Perubahan Biaya HPP (%):", -30, 30, -5, step=5)

    df_sim = df_filtered.copy()
    df_sim["omzet_simulasi"] = df_sim["total_omzet_rp"] * (1 + sim_harga_pct / 100.0)
    df_sim["hpp_simulasi"] = df_sim["total_biaya_hpp_rp"] * (1 + sim_hpp_pct / 100.0)
    df_sim["laba_simulasi"] = df_sim["omzet_simulasi"] - df_sim["hpp_simulasi"]

    laba_awal = df_sim["estimasi_laba_bersih_rp"].sum()
    laba_baru = df_sim["laba_simulasi"].sum()
    selisih_laba = laba_baru - laba_awal

    m1, m2, m3 = st.columns(3)
    m1.metric("Laba Bersih Aktual Saat Ini", format_rupiah_ringkas(laba_awal))
    m2.metric("Proyeksi Laba Hasil Simulasi", format_rupiah_ringkas(laba_baru), f"{selisih_laba:+,.0f} Rp")
    m3.metric("Margin Bersih Simulasi", f"{(laba_baru / df_sim['omzet_simulasi'].sum() * 100):.1f}%")

    df_sim_grp = df_sim.groupby("nama_komoditas", as_index=False)[["estimasi_laba_bersih_rp", "laba_simulasi"]].sum()
    fig_sim = go.Figure()
    fig_sim.add_trace(go.Bar(
        name="Laba Aktual",
        x=df_sim_grp["nama_komoditas"],
        y=df_sim_grp["estimasi_laba_bersih_rp"],
        marker_color="#94a3b8"
    ))
    fig_sim.add_trace(go.Bar(
        name="Laba Hasil Simulasi",
        x=df_sim_grp["nama_komoditas"],
        y=df_sim_grp["laba_simulasi"],
        marker_color="#10b981"
    ))
    fig_sim.update_layout(
        barmode="group",
        template="plotly_white",
        height=350,
        title="Perbandingan Laba Aktual vs Simulasi per Komoditas"
    )
    st.plotly_chart(fig_sim, use_container_width=True)

# ------------------------------------------
# TAB 4: INSPEKSI ARSITEKTUR & DATA MERGE
# ------------------------------------------
with tab4:
    st.markdown("#### 🔗 Tabel Federasi Data (`PostgreSQL` ⋈ `SQLite` via `pandas.merge()`)")

    col_dl1, col_dl2 = st.columns([3, 1])
    with col_dl1:
        st.info("💡 Kolom **Tanggal, Kabupaten, Volume, & Harga Aktual** berasal dari **DBMS 1 (PostgreSQL)**, sedangkan **Kategori, HPP, Harga Acuan, Koordinat & Elevasi** berasal dari **DBMS 2 (SQLite)**.")
    with col_dl2:
        csv_bytes = df_filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Data Terintegrasi (.CSV)",
            data=csv_bytes,
            file_name="data_federasi_hortikultura_jabar.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.dataframe(
        df_filtered[[
            "id_transaksi", "tanggal", "kabupaten", "elevasi_mdpl", "nama_komoditas",
            "kategori", "volume_panen_kg", "hpp_per_kg_rp", "harga_acuan_pemerintah_rp",
            "harga_jual_aktual_rp", "total_omzet_rp", "estimasi_laba_bersih_rp",
            "margin_persen", "status_distribusi"
        ]],
        use_container_width=True,
        hide_index=True
    )

st.divider()
st.caption("""
**Sitasi Sumber Data Primer:** Open Data Provinsi Jawa Barat - Produksi Tanaman Sayuran dan Buah-Buahan Semusim (https://opendata.jabarprov.go.id) & Panel Harga Pangan Badan Pangan Nasional (https://panelharga.badanpangan.go.id).  
**Referensi Kode & Konektivitas:** Streamlit Multi-Database Connection Guide (https://docs.streamlit.io/develop/tutorials/databases) & Plotly Interactive Data Visualization (https://plotly.com/python/).
""")
