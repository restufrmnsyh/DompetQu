import sqlite3
import hashlib
import calendar

from datetime import timedelta
from utils.waktu import sekarang_wib
import os

DB_PATH = os.path.expanduser(
    "~/database.db"
)

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

    try:
        cursor.execute("""
        ALTER TABLE transaksi
        ADD COLUMN user_id INTEGER
        """)
    except:
        pass

    cursor.execute("""
        UPDATE transaksi
        SET user_id = 1
        WHERE user_id IS NULL
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS target_tabungan (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama_target TEXT NOT NULL,
        target_nominal INTEGER NOT NULL,
        nominal_terkumpul INTEGER DEFAULT 0
    )
    """)
    try:
        cursor.execute("""
        ALTER TABLE target_tabungan
        ADD COLUMN user_id INTEGER
        """)
    except:
        pass

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS budget (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bulan TEXT NOT NULL,
        jumlah_budget INTEGER NOT NULL
    )
    """)
    try:
        cursor.execute("""
        ALTER TABLE budget
        ADD COLUMN user_id INTEGER
        """)
    except:
        pass

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    try:
        cursor.execute("""
        ALTER TABLE users
        ADD COLUMN foto_profil TEXT
        """)
    except:
        pass


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
    try:
        cursor.execute("""
        ALTER TABLE kategori
        ADD COLUMN user_id INTEGER
        """)
    except:
        pass

    cursor.execute("""
    UPDATE kategori
    SET user_id = 1
    WHERE user_id IS NULL
    """)

    kategori_default = ["Makanan", "Minuman", "Belanja", "BBM", "Transportasi", "Kesehatan", "Hiburan", "Gaji"]
    for k in kategori_default:
        cursor.execute("INSERT OR IGNORE INTO kategori (nama, user_id) VALUES (?, ?)", (k, 1))

    cursor.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS idx_kategori_user
    ON kategori(nama, user_id)
    """)
    conn.commit()
    conn.close()


def tambah_transaksi(user_id, tanggal, jenis, kategori, nominal, catatan):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO transaksi (
        user_id,
        tanggal,
        jenis,
        kategori,
        nominal,
        catatan
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        tanggal,
        jenis,
        kategori,
        nominal,
        catatan
    ))

    conn.commit()
    conn.close()


def edit_transaksi(
    user_id,
    id,
    tanggal,
    jenis,
    kategori,
    nominal,
    catatan
):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE transaksi
    SET tanggal=?,
        jenis=?,
        kategori=?,
        nominal=?,
        catatan=?
    WHERE id=?
    AND user_id=?
    """, (
        tanggal,
        jenis,
        kategori,
        nominal,
        catatan,
        id,
        user_id
    ))

    conn.commit()
    conn.close()

def ambil_transaksi_by_id(
    user_id,
    id
):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM transaksi
    WHERE id=?
    AND user_id=?
    """, (
        id,
        user_id
    ))

    data = cursor.fetchone()

    conn.close()

    return data


def ambil_semua_transaksi(user_id, bulan=None, jenis=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = """
    SELECT *
    FROM transaksi
    WHERE user_id = ?
    """

    params = [user_id]

    if bulan:
        query += """
        AND strftime('%Y-%m', tanggal) = ?
        """
        params.append(bulan)
        
    if jenis:
        query += """
        AND jenis = ?
        """
        params.append(jenis)
    query += """
    ORDER BY tanggal DESC, id DESC
    """
    cursor.execute(query, params)
    data = cursor.fetchall()
    conn.close()
    return data

def hapus_transaksi(user_id, id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transaksi WHERE id=? AND user_id = ?", ( id,user_id))
    conn.commit()
    conn.close()


def hitung_ringkasan(user_id, bulan=None):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = """
    SELECT jenis, nominal
    FROM transaksi
    WHERE user_id = ?
    """

    params = [user_id]

    if bulan:
        query += """
        AND strftime('%Y-%m', tanggal) = ?
        """
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

def ambil_target(user_id):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM target_tabungan
    WHERE user_id = ?
    ORDER BY id DESC
    LIMIT 1
    """, (user_id,))

    data = cursor.fetchone()

    conn.close()
    return data


def simpan_target(
    user_id,
    nama_target,
    target_nominal,
    nominal_terkumpul
):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM target_tabungan
    WHERE user_id = ?
    """, (user_id,))

    cursor.execute("""
    INSERT INTO target_tabungan (
        user_id,
        nama_target,
        target_nominal,
        nominal_terkumpul
    )
    VALUES (?, ?, ?, ?)
    """, (
        user_id,
        nama_target,
        target_nominal,
        nominal_terkumpul
    ))

    conn.commit()
    conn.close()


def simpan_budget(
    user_id,
    bulan,
    jumlah_budget
):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id
    FROM budget
    WHERE user_id = ?
    AND bulan = ?
    """, (
        user_id,
        bulan
    ))

    existing = cursor.fetchone()

    if existing:

        cursor.execute("""
        UPDATE budget
        SET jumlah_budget = ?
        WHERE user_id = ?
        AND bulan = ?
        """, (
            jumlah_budget,
            user_id,
            bulan
        ))

    else:

        cursor.execute("""
        INSERT INTO budget (
            user_id,
            bulan,
            jumlah_budget
        )
        VALUES (?, ?, ?)
        """, (
            user_id,
            bulan,
            jumlah_budget
        ))

    conn.commit()
    conn.close()

def ambil_budget(
    user_id,
    bulan=None
):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if bulan:

        cursor.execute("""
        SELECT *
        FROM budget
        WHERE user_id = ?
        AND bulan = ?
        """, (
            user_id,
            bulan
        ))

    else:

        cursor.execute("""
        SELECT *
        FROM budget
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
        """, (user_id,))

    data = cursor.fetchone()

    conn.close()

    return data


def ambil_pengeluaran_per_kategori(user_id, bulan=None):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = """
    SELECT kategori, SUM(nominal)
    FROM transaksi
    WHERE jenis = 'Pengeluaran'
    AND user_id = ?
    """

    params = [user_id]

    if bulan:
        query += """
        AND strftime('%Y-%m', tanggal) = ?
        """
        params.append(bulan)

    query += """
    GROUP BY kategori
    """

    cursor.execute(query, params)
    data = cursor.fetchall()
    conn.close()

    return data


def ambil_ringkasan_bulanan(user_id):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT strftime('%Y-%m', tanggal) as bulan,
           SUM(
               CASE
               WHEN jenis='Pemasukan'
               THEN nominal
               ELSE 0
               END
           ) as pemasukan,
           SUM(
               CASE
               WHEN jenis='Pengeluaran'
               THEN nominal
               ELSE 0
               END
           ) as pengeluaran
    FROM transaksi
    WHERE user_id = ?
    GROUP BY bulan
    ORDER BY bulan DESC
    LIMIT 6
    """, (user_id,))
    data = cursor.fetchall()

    conn.close()
    return data


def restore_transaksi(user_id, data):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM transaksi
    WHERE user_id = ?
    """, (user_id,))

    for item in data:

        cursor.execute("""
        INSERT INTO transaksi (
            user_id,
            tanggal,
            jenis,
            kategori,
            nominal,
            catatan
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            item["tanggal"],
            item["jenis"],
            item["kategori"],
            item["nominal"],
            item["catatan"]
        ))

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


def ambil_kategori(user_id):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM kategori
    WHERE user_id = ?
    ORDER BY nama
    """, (user_id,))

    data = cursor.fetchall()

    conn.close()

    return data

def tambah_kategori(
    user_id,
    nama
):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO kategori (
        user_id,
        nama
    )
    VALUES (?, ?)
    """, (
        user_id,
        nama
    ))

    conn.commit()
    conn.close()


def hapus_kategori(user_id, id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(""" DELETE FROM kategori WHERE id = ? AND user_id = ? """, (id,user_id))

    conn.commit()
    conn.close()

def hitung_saldo(user_id):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT jenis, nominal
    FROM transaksi
    WHERE user_id = ?
    """, (user_id,))

    data = cursor.fetchall()

    conn.close()

    saldo = 0

    for jenis, nominal in data:

        if jenis == "Pemasukan":
            saldo += nominal
        else:
            saldo -= nominal

    return saldo

def kategori_dipakai(
    user_id,
    nama_kategori
):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*)
    FROM transaksi
    WHERE user_id = ?
    AND kategori = ?
    """, (
        user_id,
        nama_kategori
    ))

    jumlah = cursor.fetchone()[0]

    conn.close()
    return jumlah > 0

def ambil_kategori_by_id(
    user_id,
    id
):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM kategori
    WHERE id = ?
    AND user_id = ?
    """, (
        id,
        user_id
    ))

    data = cursor.fetchone()

    conn.close()

    return data

def ambil_statistik_dashboard(user_id):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Total transaksi
    cursor.execute("""
    SELECT COUNT(*)
    FROM transaksi
    WHERE user_id = ?
    """, (user_id,))

    total_transaksi = cursor.fetchone()[0]

    # Kategori terbesar
    cursor.execute("""
    SELECT kategori,
           SUM(nominal) as total
    FROM transaksi
    WHERE jenis='Pengeluaran'
    AND user_id = ?
    GROUP BY kategori
    ORDER BY total DESC
    LIMIT 1
    """, (user_id,))

    kategori = cursor.fetchone()

    kategori_terbesar = kategori[0] if kategori else "-"

    # Rata-rata pengeluaran
    cursor.execute("""
    SELECT AVG(nominal)
    FROM transaksi
    WHERE jenis='Pengeluaran'
    AND user_id = ?
    """, (user_id,))

    rata_pengeluaran = cursor.fetchone()[0] or 0

    # Bulan aktif
    cursor.execute("""
    SELECT COUNT(DISTINCT strftime('%Y-%m', tanggal))
    FROM transaksi
    WHERE user_id = ?
    """, (user_id,))

    bulan_aktif = cursor.fetchone()[0]

    conn.close()

    return (
        total_transaksi,
        kategori_terbesar,
        rata_pengeluaran,
        bulan_aktif
    )

def ambil_insight(user_id):

    kategori_data = ambil_pengeluaran_per_kategori(user_id)

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

    pemasukan, pengeluaran = hitung_ringkasan(user_id)

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

def reset_transaksi(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM transaksi
    WHERE user_id = ?
    """, (user_id,))

    conn.commit()
    conn.close()

def tambah_user(username, password):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:

        cursor.execute("""
        INSERT INTO users (
            username,
            password
        )
        VALUES (?, ?)
        """, (
            username,
            hash_password(password)
        ))

        user_id = cursor.lastrowid

        kategori_default = [
            "Makanan",
            "Minuman",
            "Belanja",
            "BBM",
            "Transportasi",
            "Kesehatan",
            "Hiburan",
            "Gaji"
        ]

        for k in kategori_default:
            cursor.execute("""
            INSERT INTO kategori (
                nama,
                user_id
            )
            VALUES (?, ?)
            """, (
                k,
                user_id
            ))
        conn.commit()

        berhasil = True

    except Exception as e:

        print("ERROR REGISTER:", e)

        berhasil = False

    conn.close()

    return berhasil

def ambil_pengeluaran_harian_minggu(user_id):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    hari_ini = sekarang_wib()

    awal_minggu = (
        hari_ini -
        timedelta(days=hari_ini.weekday())
    )

    urutan = [
        "Senin",
        "Selasa",
        "Rabu",
        "Kamis",
        "Jumat",
        "Sabtu",
        "Minggu"
    ]

    data = []
    total = 0

    for i in range(7):

        tanggal = (
            awal_minggu +
            timedelta(days=i)
        ).strftime("%Y-%m-%d")

        cursor.execute("""
        SELECT COALESCE(
            SUM(nominal),
            0
        )
        FROM transaksi
        WHERE user_id = ?
        AND jenis = 'Pengeluaran'
        AND tanggal = ?
        """, (
            user_id,
            tanggal
        ))

        nominal = cursor.fetchone()[0]

        total += nominal

        data.append(
            (
                urutan[i],
                nominal
            )
        )

    conn.close()

    return data, total


def ambil_tren_harian(user_id, hari=7):
    """Pemasukan vs pengeluaran N hari terakhir"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"""
    SELECT tanggal,
           SUM(CASE WHEN jenis='Pemasukan' THEN nominal ELSE 0 END),
           SUM(CASE WHEN jenis='Pengeluaran' THEN nominal ELSE 0 END)
    FROM transaksi
    WHERE user_id = ? AND tanggal >= date('now', '-{hari-1} days')
    GROUP BY tanggal
    ORDER BY tanggal
    """, (user_id,))
    data = cursor.fetchall()
    conn.close()
    return data


def ambil_statistik_hari(user_id):
    """
    Rata-rata pengeluaran per hari dalam seminggu
    berdasarkan user yang sedang login
    """

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        CASE strftime('%w', tanggal)
            WHEN '1' THEN 'Senin'
            WHEN '2' THEN 'Selasa'
            WHEN '3' THEN 'Rabu'
            WHEN '4' THEN 'Kamis'
            WHEN '5' THEN 'Jumat'
            WHEN '6' THEN 'Sabtu'
            WHEN '0' THEN 'Minggu'
        END AS hari,
        strftime('%w', tanggal) AS num,
        AVG(nominal) AS rata
    FROM transaksi
    WHERE user_id = ?
      AND jenis = 'Pengeluaran'
    GROUP BY num
    ORDER BY
        CASE strftime('%w', tanggal)
            WHEN '1' THEN 1
            WHEN '2' THEN 2
            WHEN '3' THEN 3
            WHEN '4' THEN 4
            WHEN '5' THEN 5
            WHEN '6' THEN 6
            WHEN '0' THEN 7
        END
    """, (user_id,))

    data = cursor.fetchall()

    conn.close()

    urutan = [
        'Senin',
        'Selasa',
        'Rabu',
        'Kamis',
        'Jumat',
        'Sabtu',
        'Minggu'
    ]

    data_dict = {
        r[0]: round(r[2], 0)
        for r in data
    }

    return [
        (hari, data_dict.get(hari, 0))
        for hari in urutan
    ]

def ambil_pengeluaran_per_tanggal_bulan(user_id, bulan):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT strftime('%d', tanggal) as tgl,
           SUM(nominal)
    FROM transaksi
    WHERE user_id = ?
      AND jenis = 'Pengeluaran'
      AND strftime('%Y-%m', tanggal) = ?
    GROUP BY tgl
    ORDER BY tgl
    """, (user_id, bulan))
    data = cursor.fetchall()
    conn.close()
    return {
        int(r[0]): r[1]
        for r in data
    }


def ambil_top_transaksi(user_id, limit=5, bulan=None):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if bulan:

        cursor.execute("""
        SELECT
            tanggal,
            kategori,
            nominal,
            catatan
        FROM transaksi
        WHERE user_id = ?
          AND jenis = 'Pengeluaran'
          AND strftime('%Y-%m', tanggal) = ?
        ORDER BY nominal DESC
        LIMIT ?
        """, (
            user_id,
            bulan,
            limit
        ))

    else:

        cursor.execute("""
        SELECT
            tanggal,
            kategori,
            nominal,
            catatan
        FROM transaksi
        WHERE user_id = ?
          AND jenis = 'Pengeluaran'
        ORDER BY nominal DESC
        LIMIT ?
        """, (
            user_id,
            limit
        ))

    data = cursor.fetchall()

    conn.close()

    return data

def ambil_pengeluaran_per_minggu(user_id, bulan, minggu):
    """
    Minggu: 1 sampai jumlah minggu pada bulan
    Bulan: format YYYY-MM
    """
    import calendar
    from datetime import date

    tahun, bln = map(int, bulan.split('-'))
    jumlah_hari = calendar.monthrange(tahun, bln)[1]

    # Tentukan rentang tanggal per minggu
    minggu_ranges = []
    start = 1
    while start <= jumlah_hari:
        end = min(
            start + 6,
            jumlah_hari
        )
        minggu_ranges.append(
            (start, end)
        )
        start = end + 1

    if minggu < 1 or minggu > len(minggu_ranges):
        return [], 0, "", ""

    tgl_start, tgl_end = minggu_ranges[minggu - 1]
    date_start = f"{bulan}-{tgl_start:02d}"
    date_end   = f"{bulan}-{tgl_end:02d}"

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT tanggal,
           SUM(CASE WHEN jenis='Pengeluaran' THEN nominal ELSE 0 END) as keluar,
           SUM(CASE WHEN jenis='Pemasukan'   THEN nominal ELSE 0 END) as masuk
    FROM transaksi
    WHERE user_id = ? AND tanggal BETWEEN ? AND ?
    GROUP BY tanggal
    ORDER BY tanggal
    """, (user_id, date_start, date_end))
    rows = cursor.fetchall()
    conn.close()

    # Isi semua hari dalam rentang (termasuk yang 0)
    from datetime import date, timedelta
    d = date(tahun, bln, tgl_start)
    end_d = date(tahun, bln, tgl_end)
    data_dict = {r[0]: (r[1], r[2]) for r in rows}

    result = []
    while d <= end_d:
        tgl_str = d.strftime("%Y-%m-%d")
        keluar, masuk = data_dict.get(tgl_str, (0, 0))
        result.append({
            "tanggal": tgl_str,
            "hari": ["Sen","Sel","Rab","Kam","Jum","Sab","Min"][d.weekday()],
            "keluar": keluar,
            "masuk": masuk,
        })
        d += timedelta(days=1)

    total = sum(r["keluar"] for r in result)
    return result, total, date_start, date_end


def ambil_pengeluaran_kategori_bulan(
    user_id,
    bulan
):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT kategori, SUM(nominal)
    FROM transaksi
    WHERE user_id = ?
      AND jenis = 'Pengeluaran'
      AND strftime('%Y-%m', tanggal) = ?
    GROUP BY kategori
    ORDER BY SUM(nominal) DESC
    """, (
        user_id,
        bulan
    ))

    data = cursor.fetchall()

    conn.close()

    return {r[0]: r[1] for r in data}

def ambil_transaksi_per_tanggal(
    user_id,
    tanggal
):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM transaksi
    WHERE user_id = ?
      AND tanggal = ?
    ORDER BY id DESC
    """, (
        user_id,
        tanggal
    ))

    data = cursor.fetchall()

    conn.close()

    return data

def ambil_pengeluaran_per_minggu_ringkas(
    user_id,
    bulan
):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    tahun, bln = map(
        int,
        bulan.split("-")
    )

    jumlah_hari = calendar.monthrange(
        tahun,
        bln
    )[1]

    hasil = []
    total = 0

    start = 1
    minggu_ke = 1

    while start <= jumlah_hari:

        end = min(
            start + 6,
            jumlah_hari
        )

        tgl_awal = f"{bulan}-{start:02d}"
        tgl_akhir = f"{bulan}-{end:02d}"

        cursor.execute("""
        SELECT COALESCE(
            SUM(nominal),
            0
        )
        FROM transaksi
        WHERE user_id = ?
        AND jenis = 'Pengeluaran'
        AND tanggal BETWEEN ? AND ?
        """, (
            user_id,
            tgl_awal,
            tgl_akhir
        ))

        nominal = cursor.fetchone()[0]

        hasil.append(
            (
                f"Minggu {minggu_ke}",
                nominal
            )
        )

        total += nominal

        minggu_ke += 1
        start = end + 1

    conn.close()

    return hasil, total

def ambil_tren_bulan(user_id, bulan):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        tanggal,

        SUM(
            CASE
                WHEN jenis='Pemasukan'
                THEN nominal
                ELSE 0
            END
        ) as masuk,

        SUM(
            CASE
                WHEN jenis='Pengeluaran'
                THEN nominal
                ELSE 0
            END
        ) as keluar

    FROM transaksi

    WHERE user_id = ?
      AND strftime('%Y-%m', tanggal) = ?

    GROUP BY tanggal
    ORDER BY tanggal
    """, (
        user_id,
        bulan
    ))

    data = cursor.fetchall()

    conn.close()

    return data

def ambil_foto_profil(user_id):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT foto_profil
    FROM users
    WHERE id = ?
    """, (user_id,))

    data = cursor.fetchone()

    conn.close()

    return data[0] if data else None

def update_foto_profil(user_id, foto):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users
    SET foto_profil = ?
    WHERE id = ?
    """, (
        foto,
        user_id
    ))

    conn.commit()
    conn.close()

def verifikasi_password(
    user_id,
    password
):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id
    FROM users
    WHERE id = ?
    AND password = ?
    """, (
        user_id,
        hash_password(password)
    ))

    hasil = cursor.fetchone()

    conn.close()

    return hasil is not None    


def hapus_akun(user_id):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM transaksi WHERE user_id=?",
        (user_id,)
    )

    cursor.execute(
        "DELETE FROM kategori WHERE user_id=?",
        (user_id,)
    )

    cursor.execute(
        "DELETE FROM budget WHERE user_id=?",
        (user_id,)
    )

    cursor.execute(
        "DELETE FROM target_tabungan WHERE user_id=?",
        (user_id,)
    )

    cursor.execute(
        "DELETE FROM users WHERE id=?",
        (user_id,)
    )

    conn.commit()
    conn.close()


def update_username(user_id, username_baru):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:

        cursor.execute("""
        UPDATE users
        SET username = ?
        WHERE id = ?
        """, (
            username_baru,
            user_id
        ))

        conn.commit()

        berhasil = True

    except Exception as e:
        print("ERROR UPDATE USERNAME:", e)
        berhasil = False
    conn.close()
    return berhasil

def username_sudah_ada(username):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id
    FROM users
    WHERE username = ?
    """, (username,))

    hasil = cursor.fetchone()

    conn.close()

    return hasil is not None