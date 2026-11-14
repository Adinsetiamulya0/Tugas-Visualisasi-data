-- Skema Tabel Transaksi Panen & Distribusi (DBMS 1: PostgreSQL)
DROP TABLE IF EXISTS transaksi_panen;

CREATE TABLE transaksi_panen (
    id_transaksi SERIAL PRIMARY KEY,
    tanggal DATE NOT NULL,
    kabupaten VARCHAR(50) NOT NULL,
    kode_komoditas VARCHAR(10) NOT NULL,
    volume_panen_kg NUMERIC(10, 2) NOT NULL,
    harga_jual_aktual_rp NUMERIC(10, 2) NOT NULL,
    status_distribusi VARCHAR(30) NOT NULL
);

-- Seed Data Transaksi Panen di Jawa Barat
INSERT INTO transaksi_panen (tanggal, kabupaten, kode_komoditas, volume_panen_kg, harga_jual_aktual_rp, status_distribusi) VALUES
('2026-05-05', 'Sumedang', 'KMD-01', 1250.50, 38000, 'Terkirim ke Pasar Induk'),
('2026-05-12', 'Sumedang', 'KMD-02', 2400.00, 8500, 'Terkirim ke Pasar Induk'),
('2026-05-18', 'Garut', 'KMD-01', 1800.00, 36500, 'Terkirim ke Retail Modern'),
('2026-05-25', 'Bandung', 'KMD-03', 3100.00, 14000, 'Terkirim ke Pasar Induk'),
('2026-06-02', 'Sumedang', 'KMD-01', 1420.00, 42000, 'Terkirim ke Retail Modern'),
('2026-06-10', 'Majalengka', 'KMD-05', 1950.00, 31000, 'Terkirim ke Pasar Induk'),
('2026-06-15', 'Garut', 'KMD-02', 2850.00, 7800, 'Gudang Logistik'),
('2026-06-22', 'Bandung', 'KMD-04', 4200.00, 16500, 'Terkirim ke Retail Modern'),
('2026-07-04', 'Sumedang', 'KMD-02', 2600.00, 9200, 'Terkirim ke Pasar Induk'),
('2026-07-11', 'Cianjur', 'KMD-03', 1750.00, 15200, 'Terkirim ke Pasar Induk'),
('2026-07-19', 'Sumedang', 'KMD-01', 1680.00, 45000, 'Terkirim ke Retail Modern'),
('2026-07-27', 'Garut', 'KMD-04', 3500.00, 17000, 'Terkirim ke Pasar Induk'),
('2026-08-03', 'Bandung', 'KMD-02', 3900.00, 8900, 'Terkirim ke Pasar Induk'),
('2026-08-14', 'Majalengka', 'KMD-01', 1100.00, 41000, 'Gudang Logistik'),
('2026-08-21', 'Sumedang', 'KMD-03', 2100.00, 13800, 'Terkirim ke Pasar Induk'),
('2026-09-02', 'Cianjur', 'KMD-05', 1550.00, 33000, 'Terkirim ke Retail Modern'),
('2026-09-10', 'Sumedang', 'KMD-01', 1900.00, 39500, 'Terkirim ke Pasar Induk'),
('2026-09-18', 'Garut', 'KMD-02', 3100.00, 8400, 'Terkirim ke Retail Modern'),
('2026-09-25', 'Bandung', 'KMD-04', 4600.00, 17500, 'Terkirim ke Pasar Induk'),
('2026-10-05', 'Sumedang', 'KMD-02', 2950.00, 9500, 'Terkirim ke Retail Modern');
