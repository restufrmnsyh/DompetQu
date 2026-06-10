import sqlite3

def init_db():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transaksi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tanggal TEXT NOT NULL,
        jenis TEXT NOT NULL,
        kategori TEXT NOT NULL,
        nominal INTEGER NOT NULL,
        catatan TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS target_tabungan (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama_target TEXT NOT NULL,
        target_nominal INTEGER NOT NULL,
        nominal_terkumpul INTEGER DEFAULT 0
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS budget (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bulan TEXT NOT NULL,
        jumlah_budget INTEGER NOT NULL
    )
    """)

    conn.commit()
    conn.close()


def tambah_transaksi(tanggal, jenis, kategori, nominal, catatan):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO transaksi
    (tanggal, jenis, kategori, nominal, catatan)
    VALUES (?, ?, ?, ?, ?)
    """, (tanggal, jenis, kategori, nominal, catatan))

    conn.commit()
    conn.close()


def ambil_semua_transaksi():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM transaksi
    ORDER BY id DESC
    """)

    data = cursor.fetchall()

    conn.close()

    return data


def hitung_saldo():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT jenis, nominal
    FROM transaksi
    """)

    data = cursor.fetchall()

    conn.close()

    saldo = 0

    for jenis, nominal in data:

        if jenis == "Pemasukan":
            saldo += nominal
        else:
            saldo -= nominal

    return saldo


def hapus_transaksi(id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM transaksi
    WHERE id = ?
    """, (id,))

    conn.commit()
    conn.close()


def hitung_ringkasan():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT jenis, nominal
    FROM transaksi
    """)

    data = cursor.fetchall()

    conn.close()

    pemasukan = 0
    pengeluaran = 0

    for jenis, nominal in data:

        if jenis == "Pemasukan":
            pemasukan += nominal

        elif jenis == "Pengeluaran":
            pengeluaran += nominal

    return pemasukan, pengeluaran


def ambil_target():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM target_tabungan
    LIMIT 1
    """)

    data = cursor.fetchone()

    conn.close()

    return data


def simpan_target(
    nama_target,
    target_nominal,
    nominal_terkumpul
):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM target_tabungan
    """)

    cursor.execute("""
    INSERT INTO target_tabungan
    (
        nama_target,
        target_nominal,
        nominal_terkumpul
    )
    VALUES (?, ?, ?)
    """,
    (
        nama_target,
        target_nominal,
        nominal_terkumpul
    ))

    conn.commit()
    conn.close()

def simpan_budget(bulan, jumlah_budget):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM budget")

    cursor.execute("""
    INSERT INTO budget
    (bulan, jumlah_budget)
    VALUES (?, ?)
    """, (bulan, jumlah_budget))

    conn.commit()
    conn.close()

def ambil_budget():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM budget
    LIMIT 1
    """)

    data = cursor.fetchone()

    conn.close()

    return data

def ambil_pengeluaran_per_kategori():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT kategori,
           SUM(nominal)
    FROM transaksi
    WHERE jenis = 'Pengeluaran'
    GROUP BY kategori
    """)

    data = cursor.fetchall()

    conn.close()

    return data