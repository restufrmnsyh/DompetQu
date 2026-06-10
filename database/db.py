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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    cursor.execute("""
    INSERT OR IGNORE INTO users
    (username, password)
    VALUES (?, ?)
    """, (

        "restu",
        "12345"

    ))

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS kategori (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        nama TEXT UNIQUE NOT NULL

    )
    """)
    
    kategori_default = [
        "Makanan",
        "Minuman",
        "Belanja",
        "BBM"
    ]

    for k in kategori_default:
        cursor.execute("""
        INSERT OR IGNORE INTO kategori
        (nama)
        VALUES (?)
        """, (k,))

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

def restore_transaksi(data):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM transaksi")

    for item in data:

        cursor.execute("""
        INSERT INTO transaksi
        (
            tanggal,
            jenis,
            kategori,
            nominal,
            catatan
        )
        VALUES (?, ?, ?, ?, ?)
        """, (

            item["tanggal"],
            item["jenis"],
            item["kategori"],
            item["nominal"],
            item["catatan"]

        ))

    conn.commit()
    conn.close()

def cek_login(username, password):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM users
    WHERE username = ?
    AND password = ?
    """, (

        username,
        password

    ))

    user = cursor.fetchone()
    conn.close()
    return user

def ganti_password(username, password_lama, password_baru):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM users
    WHERE username = ?
    AND password = ?
    """, (

        username,
        password_lama

    ))

    user = cursor.fetchone()

    if not user:

        conn.close()

        return False

    cursor.execute("""
    UPDATE users
    SET password = ?
    WHERE username = ?
    """, (

        password_baru,
        username

    ))

    conn.commit()
    conn.close()

    return True

def ambil_kategori():

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM kategori
    ORDER BY nama
    """)

    data = cursor.fetchall()

    conn.close()

    return data

def tambah_kategori(nama):

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO kategori
    (nama)
    VALUES (?)
    """, (nama,))

    conn.commit()
    conn.close()

def hapus_kategori(id):

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM kategori
    WHERE id = ?
    """, (id,))

    conn.commit()
    conn.close()
