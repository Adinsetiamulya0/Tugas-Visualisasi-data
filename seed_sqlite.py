import sqlite3
import os

def init_sqlite_db(db_path="database/metadata_komoditas.db"):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
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

if __name__ == "__main__":
    init_sqlite_db()
