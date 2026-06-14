from flask import Blueprint, render_template, session, redirect
from database.db import (
    ambil_pengeluaran_harian_minggu,
    ambil_tren_harian,
    hitung_ringkasan,
    ambil_pengeluaran_per_tanggal_bulan,
    ambil_top_transaksi,
    ambil_pengeluaran_per_kategori,
    ambil_ringkasan_bulanan,
)
from datetime import datetime
import calendar

analisis = Blueprint("analisis", __name__)


@analisis.route("/analisis")
def halaman_analisis():
    if "login" not in session:
        return redirect("/login")

    bulan_ini = datetime.now().strftime("%Y-%m")
    tahun = datetime.now().year
    bulan = datetime.now().month

    if bulan == 1:
        bulan_lalu = f"{tahun - 1}-12"
    else:
        bulan_lalu = f"{tahun}-{bulan - 1:02d}"

    # Perbandingan bulan ini vs lalu
    p_ini, e_ini = hitung_ringkasan(session["user_id"],bulan=bulan_ini)
    p_lalu, e_lalu = hitung_ringkasan(session["user_id"],bulan=bulan_lalu)
    selisih_pengeluaran = e_ini - e_lalu
    selisih_persen = ((e_ini - e_lalu) / e_lalu * 100) if e_lalu > 0 else 0

    # Rincian per hari minggu ini
    data_mingguan, total_mingguan = ambil_pengeluaran_harian_minggu(session["user_id"])
    hari_terboros = max(data_mingguan, key=lambda x: x[1]) if any(x[1] > 0 for x in data_mingguan) else ("–", 0)

    # Tren 7 hari
    tren = ambil_tren_harian(session["user_id"],7)
    tren_labels = [x[0] for x in tren]
    tren_pemasukan = [x[1] for x in tren]
    tren_pengeluaran = [x[2] for x in tren]

    # Kalender pengeluaran bulan ini
    jumlah_hari = calendar.monthrange(tahun, bulan)[1]
    data_kalender = ambil_pengeluaran_per_tanggal_bulan(session["user_id"],bulan_ini)
    max_kal = max(data_kalender.values()) if data_kalender else 1
    hari_pertama = calendar.monthrange(tahun, bulan)[0]

    # Top 5 transaksi terbesar
    top_transaksi = ambil_top_transaksi(session["user_id"],5)

    # Kategori pengeluaran bulan ini
    kategori_bulan = ambil_pengeluaran_per_kategori(session["user_id"],bulan=bulan_ini)
    total_kategori = sum(k[1] for k in kategori_bulan) or 1

    # Riwayat 6 bulan
    ringkasan_bulanan = ambil_ringkasan_bulanan(session["user_id"])

    return render_template(
        "analisis.html",
        bulan_ini=bulan_ini, bulan_lalu=bulan_lalu,
        p_ini=p_ini, e_ini=e_ini,
        p_lalu=p_lalu, e_lalu=e_lalu,
        selisih_pengeluaran=selisih_pengeluaran,
        selisih_persen=selisih_persen,
        data_mingguan=data_mingguan,
        total_mingguan=total_mingguan,
        hari_terboros=hari_terboros,
        tren_labels=tren_labels,
        tren_pemasukan=tren_pemasukan,
        tren_pengeluaran=tren_pengeluaran,
        jumlah_hari=jumlah_hari,
        hari_pertama=hari_pertama,
        data_kalender=data_kalender,
        max_kal=max_kal,
        bulan_nama=datetime.now().strftime("%B %Y"),
        top_transaksi=top_transaksi,
        kategori_bulan=kategori_bulan,
        total_kategori=total_kategori,
        ringkasan_bulanan=ringkasan_bulanan,
    )