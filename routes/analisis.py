from flask import Blueprint, render_template, session, redirect, request
from database.db import (
    ambil_pengeluaran_harian_minggu,
    ambil_tren_harian,
    hitung_ringkasan,
    ambil_pengeluaran_per_tanggal_bulan,
    ambil_top_transaksi,
    ambil_pengeluaran_per_kategori,
    ambil_ringkasan_bulanan,
    ambil_pengeluaran_per_minggu
)

from utils.waktu import sekarang_wib
from datetime import datetime
import calendar

analisis = Blueprint("analisis", __name__)


@analisis.route("/analisis")
def halaman_analisis():

    if "login" not in session:
        return redirect("/login")

    now = sekarang_wib()

    bulan_ini = now.strftime("%Y-%m")
    tahun = now.year
    bulan = now.month

    if bulan == 1:
        bulan_lalu = f"{tahun - 1}-12"
    else:
        bulan_lalu = f"{tahun}-{bulan - 1:02d}"

    # Perbandingan bulan ini vs bulan lalu
    p_ini, e_ini = hitung_ringkasan(
        session["user_id"],
        bulan=bulan_ini
    )

    p_lalu, e_lalu = hitung_ringkasan(
        session["user_id"],
        bulan=bulan_lalu
    )

    selisih_pengeluaran = e_ini - e_lalu

    selisih_persen = (
        ((e_ini - e_lalu) / e_lalu * 100)
        if e_lalu > 0
        else 0
    )

    # Minggu berjalan
    data_mingguan, total_mingguan = (
        ambil_pengeluaran_harian_minggu(
            session["user_id"]
        )
    )

    hari_terboros = (
        max(data_mingguan, key=lambda x: x[1])
        if any(x[1] > 0 for x in data_mingguan)
        else ("-", 0)
    )

    # Tren 7 hari
    tren = ambil_tren_harian(
        session["user_id"],
        7
    )

    tren_labels = [x[0] for x in tren]
    tren_pemasukan = [x[1] for x in tren]
    tren_pengeluaran = [x[2] for x in tren]

    # Kalender
    jumlah_hari = calendar.monthrange(
        tahun,
        bulan
    )[1]

    data_kalender = (
        ambil_pengeluaran_per_tanggal_bulan(
            session["user_id"],
            bulan_ini
        )
    )

    max_kal = (
        max(data_kalender.values())
        if data_kalender
        else 1
    )

    hari_pertama = calendar.monthrange(
        tahun,
        bulan
    )[0]

    # Top transaksi
    top_transaksi = ambil_top_transaksi(
        session["user_id"],
        5
    )

    # Kategori
    kategori_bulan = (
        ambil_pengeluaran_per_kategori(
            session["user_id"],
            bulan=bulan_ini
        )
    )

    total_kategori = (
        sum(k[1] for k in kategori_bulan)
        or 1
    )

    # Riwayat
    ringkasan_bulanan = (
        ambil_ringkasan_bulanan(
            session["user_id"]
        )
    )

    return render_template(
        "analisis.html",
        bulan_ini=bulan_ini,
        bulan_lalu=bulan_lalu,
        p_ini=p_ini,
        e_ini=e_ini,
        p_lalu=p_lalu,
        e_lalu=e_lalu,
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
        bulan_nama=now.strftime("%B %Y"),
        top_transaksi=top_transaksi,
        kategori_bulan=kategori_bulan,
        total_kategori=total_kategori,
        ringkasan_bulanan=ringkasan_bulanan
    )

@analisis.route("/analisis/minggu")
def analisis_minggu():

    if "login" not in session:
        return redirect("/login")

    now = sekarang_wib()

    bulan = request.args.get(
        "bulan",
        now.strftime("%Y-%m")
    )

    minggu = int(
        request.args.get(
            "minggu",
            1
        )
    )

    tahun, bln = map(
        int,
        bulan.split("-")
    )

    jumlah_hari = calendar.monthrange(
        tahun,
        bln
    )[1]

    bulan_nama = datetime(
        tahun,
        bln,
        1
    ).strftime("%B %Y")

    jumlah_minggu = min(
        4,
        (jumlah_hari + 6) // 7
    )

    data, total, date_start, date_end = (
        ambil_pengeluaran_per_minggu(
            session["user_id"],
            bulan,
            minggu
        )
    )

    nama_bulan_list = [
        '',
        'Jan','Feb','Mar','Apr','Mei','Jun',
        'Jul','Agt','Sep','Okt','Nov','Des'
    ]

    minggu_options = []

    start = 1

    for w in range(
        1,
        jumlah_minggu + 1
    ):

        end = min(
            start + 6,
            jumlah_hari
        )

        minggu_options.append({
            "num": w,
            "label":
            f"Minggu {w} ({start} - {end} {nama_bulan_list[bln]})"
        })

        start = end + 1

    chart_labels = [
        d["hari"] + " " + d["tanggal"][8:]
        for d in data
    ]

    chart_keluar = [
        d["keluar"]
        for d in data
    ]

    chart_masuk = [
        d["masuk"]
        for d in data
    ]

    return render_template(
        "analisis_minggu.html",
        bulan=bulan,
        bulan_nama=bulan_nama,
        minggu=minggu,
        minggu_options=minggu_options,
        data=data,
        total=total,
        date_start=date_start,
        date_end=date_end,
        chart_labels=chart_labels,
        chart_keluar=chart_keluar,
        chart_masuk=chart_masuk
    )