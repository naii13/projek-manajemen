import mysql.connector

connection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="",
    database="project"
)

cursor = connection.cursor()

query_pasien = """
    CREATE TABLE IF NOT EXISTS pasien (
        id INT AUTO_INCREMENT PRIMARY KEY,
        kode VARCHAR(255) NOT NULL,
        nama VARCHAR(255) NOT NULL,
        ruangan VARCHAR(255) NOT NULL,
        alamat VARCHAR(255) NOT NULL,
        umur INT NOT NULL,
        status VARCHAR(255) NOT NULL
    );
"""
cursor.execute(query_pasien)
print("tabel pasien berhasil dibuat")


query_history_table = """
    CREATE TABLE IF NOT EXISTS history (
        id INT AUTO_INCREMENT PRIMARY KEY,
        kode_pasien VARCHAR(10),
        nama_pasien VARCHAR(100),
        tindakan VARCHAR(20),
        waktu_keluar DATETIME DEFAULT CURRENT_TIMESTAMP
    );
"""
cursor.execute(query_history_table)
print("tabel history berhasil dibuat")

query = """
    CREATE TABLE IF NOT EXISTS kamar (
        id_kamar INT AUTO_INCREMENT PRIMARY KEY,
        nomor_kamar VARCHAR(255) NOT NULL,
        jenis_kamar VARCHAR(50) NOT NULL,
        status VARCHAR(20) NOT NULL DEFAULT 'Tersedia'
    )
    """
cursor.execute(query)
print("Tabel 'kamar' berhasil dibuat.")

connection.commit()
cursor.close()
connection.close()



