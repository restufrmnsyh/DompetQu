import sqlite3
import hashlib

DB_PATH = "database.db"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect(DB_PATH)
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

    # Migrate plain passwords to hashed if needed
    cursor.execute("SELECT id, username, password FROM users")
    users = cursor.fetchall()
    for uid, uname, pwd in users:
        if len(pwd) != 64:
            cursor.execute("UPDATE users SET password=? WHERE id=?",
                           (hash_password(pwd), uid))

    cursor.execute("""
    INSERT OR IGNORE INTO users (username, password)
    VALUES (?, ?)
    """, ("restu", hash_password("12345")))

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS kategori (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT UNIQUE NOT NULL
    )
    """)

    kategori_default = ["Makanan", "Minuman", "Belanja", "BBM", "Transportasi", "Kesehatan", "Hiburan", "Gaji"]
    for k in kategori_default:
        cursor.execute("INSERT OR IGNORE INTO kategori (nama) VALUES (?)", (k,))

    conn.commit()
    conn.close()


def tambah_transaksi(tanggal, jenis, kategori, nominal, catatan):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO transaksi (tanggal, jenis, kategori, nominal, catatan)
    VALUES (?, ?, ?, ?, ?)
    """, (tanggal, jenis, kategori, nominal, catatan))
    conn.commit()
    conn.close()


def edit_transaksi(id, tanggal, jenis, kategori, nominal, catatan):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE transaksi SET tanggal=?, jenis=?, kategori=?, nominal=?, catatan=?
    WHERE id=?
    """, (tanggal, jenis, kategori, nominal, catatan, id))
    conn.commit()
    conn.close()


def ambil_transaksi_by_id(id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transaksi WHERE id=?", (id,))
    data = cursor.fetchone()
    conn.close()
    return data


def ambil_semua_transaksi(bulan=None, jenis=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = "SELECT * FROM transaksi WHERE 1=1"
    params = []
    if bulan:
        query += " AND strftime('%Y-%m', tanggal) = ?"
        params.append(bulan)
    if jenis:
        query += " AND jenis = ?"
        params.append(jenis)
    query += " ORDER BY tanggal DESC, id DESC"
    cursor.execute(query, params)
    data = cursor.fetchall()
    conn.close()
    return data


def hitung_saldo():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT jenis, nominal FROM transaksi")
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
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transaksi WHERE id=?", (id,))
    conn.commit()
    conn.close()


def hitung_ringkasan(bulan=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = "SELECT jenis, nominal FROM transaksi WHERE 1=1"
    params = []
    if bulan:
        query += " AND strftime('%Y-%m', tanggal) = ?"
        params.append(bulan)
    cursor.execute(query, params)
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
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM target_tabungan LIMIT 1")
    data = cursor.fetchone()
    conn.close()
    return data


def simpan_target(nama_target, target_nominal, nominal_terkumpul):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM target_tabungan")
    cursor.execute("""
    INSERT INTO target_tabungan (nama_target, target_nominal, nominal_terkumpul)
    VALUES (?, ?, ?)
    """, (nama_target, target_nominal, nominal_terkumpul))
    conn.commit()
    conn.close()


def simpan_budget(bulan, jumlah_budget):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM budget WHERE bulan=?", (bulan,))
    existing = cursor.fetchone()
    if existing:
        cursor.execute("UPDATE budget SET jumlah_budget=? WHERE bulan=?",
                       (jumlah_budget, bulan))
    else:
        cursor.execute("INSERT INTO budget (bulan, jumlah_budget) VALUES (?, ?)",
                       (bulan, jumlah_budget))
    conn.commit()
    conn.close()


def ambil_budget(bulan=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if bulan:
        cursor.execute("SELECT * FROM budget WHERE bulan=?", (bulan,))
    else:
        cursor.execute("SELECT * FROM budget ORDER BY id DESC LIMIT 1")
    data = cursor.fetchone()
    conn.close()
    return data


def ambil_pengeluaran_per_kategori(bulan=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = """
    SELECT kategori, SUM(nominal)
    FROM transaksi
    WHERE jenis = 'Pengeluaran'
    """
    params = []
    if bulan:
        query += " AND strftime('%Y-%m', tanggal) = ?"
        params.append(bulan)
    query += " GROUP BY kategori"
    cursor.execute(query, params)
    data = cursor.fetchall()
    conn.close()
    return data


def ambil_ringkasan_bulanan():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT strftime('%Y-%m', tanggal) as bulan,
           SUM(CASE WHEN jenis='Pemasukan' THEN nominal ELSE 0 END) as pemasukan,
           SUM(CASE WHEN jenis='Pengeluaran' THEN nominal ELSE 0 END) as pengeluaran
    FROM transaksi
    GROUP BY bulan
    ORDER BY bulan DESC
    LIMIT 6
    """)
    data = cursor.fetchall()
    conn.close()
    return data


def restore_transaksi(data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transaksi")
    for item in data:
        cursor.execute("""
        INSERT INTO transaksi (tanggal, jenis, kategori, nominal, catatan)
        VALUES (?, ?, ?, ?, ?)
        """, (item["tanggal"], item["jenis"], item["kategori"],
              item["nominal"], item["catatan"]))
    conn.commit()
    conn.close()


def cek_login(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM users WHERE username=? AND password=?
    """, (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    return user


def ganti_password(username, password_lama, password_baru):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?",
                   (username, hash_password(password_lama)))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return False
    cursor.execute("UPDATE users SET password=? WHERE username=?",
                   (hash_password(password_baru), username))
    conn.commit()
    conn.close()
    return True


def ambil_kategori():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM kategori ORDER BY nama")
    data = cursor.fetchall()
    conn.close()
    return data


def tambah_kategori(nama):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO kategori (nama) VALUES (?)", (nama,))
    conn.commit()
    conn.close()


def hapus_kategori(id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM kategori WHERE id=?", (id,))
    conn.commit()
    conn.close()

def hitung_saldo(bulan=None):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = "SELECT jenis, nominal FROM transaksi WHERE 1=1"
    params = []

    if bulan:
        query += " AND strftime('%Y-%m', tanggal)=?"
        params.append(bulan)

    cursor.execute(query, params)

    data = cursor.fetchall()

    conn.close()

    saldo = 0

    for jenis, nominal in data:

        if jenis == "Pemasukan":
            saldo += nominal
        else:
            saldo -= nominal

    return saldo

def kategori_dipakai(nama_kategori):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*)
    FROM transaksi
    WHERE kategori = ?
    """, (nama_kategori,))

    jumlah = cursor.fetchone()[0]

    conn.close()

    return jumlah > 0

def ambil_kategori_by_id(id):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM kategori
    WHERE id = ?
    """, (id,))

    data = cursor.fetchone()

    conn.close()

    return data

def ambil_statistik_dashboard():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Total transaksi
    cursor.execute("""
    SELECT COUNT(*)
    FROM transaksi
    """)
    total_transaksi = cursor.fetchone()[0]

    # Kategori terbesar
    cursor.execute("""
    SELECT kategori,
           SUM(nominal) as total
    FROM transaksi
    WHERE jenis='Pengeluaran'
    GROUP BY kategori
    ORDER BY total DESC
    LIMIT 1
    """)

    kategori = cursor.fetchone()

    kategori_terbesar = kategori[0] if kategori else "-"

    # Rata-rata pengeluaran
    cursor.execute("""
    SELECT AVG(nominal)
    FROM transaksi
    WHERE jenis='Pengeluaran'
    """)

    rata_pengeluaran = cursor.fetchone()[0] or 0

    # Bulan aktif
    cursor.execute("""
    SELECT COUNT(DISTINCT strftime('%Y-%m', tanggal))
    FROM transaksi
    """)

    bulan_aktif = cursor.fetchone()[0]

    conn.close()

    return (
        total_transaksi,
        kategori_terbesar,
        rata_pengeluaran,
        bulan_aktif
    )

def ambil_insight():

    kategori_data = ambil_pengeluaran_per_kategori()

    if kategori_data:

        kategori_terbesar = max(
            kategori_data,
            key=lambda x: x[1]
        )

    else:

        kategori_terbesar = (
            "Belum ada data",
            0
        )

    pemasukan, pengeluaran = hitung_ringkasan()

    persentase = 0

    if pemasukan > 0:

        persentase = (
            pengeluaran /
            pemasukan
        ) * 100

    return (
        kategori_terbesar,
        persentase
    )

def reset_transaksi():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM transaksi
    """)

    conn.commit()
    conn.close()