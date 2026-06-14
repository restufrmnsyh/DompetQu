from flask import Blueprint, render_template, session, redirect, request
from database.db import (
    ambil_pengeluaran_harian_minggu,
    ambil_pengeluaran_mingguan,
    ambil_tren_harian,
    ambil_statistik_hari,
    hitung_ringkasan
)
from datetime import datetime

analisis = Blueprint("analisis", __name__)


@analisis.route("/analisis")
def halaman_analisis():
    if "login" not in session:
        return redirect("/login")

    # Pengeluaran 7 hari terakhir (Senin-Minggu)
    data_mingguan, total_mingguan = ambil_pengeluaran_harian_minggu()
    hari_terboros = max(data_mingguan, key=lambda x: x[1]) if any(x[1] > 0 for x in data_mingguan) else ("–", 0)
    hari_labels = [x[0] for x in data_mingguan]
    hari_values = [x[1] for x in data_mingguan]

    # Tren 7 hari (pemasukan vs pengeluaran)
    tren = ambil_tren_harian(7)
    tren_labels = [x[0] for x in tren]
    tren_pemasukan = [x[1] for x in tren]
    tren_pengeluaran = [x[2] for x in tren]

    # Rata-rata per hari dalam seminggu (pola kebiasaan)
    statistik_hari = ambil_statistik_hari()
    stat_labels = [x[0] for x in statistik_hari]
    stat_values = [round(x[1]) for x in statistik_hari]

    # Ringkasan bulan ini vs bulan lalu
    bulan_ini = datetime.now().strftime("%Y-%m")
    bulan_lalu_dt = datetime.now().replace(day=1)
    import calendar
    bulan_lalu = (bulan_lalu_dt.replace(month=bulan_lalu_dt.month - 1)
                  if bulan_lalu_dt.month > 1
                  else bulan_lalu_dt.replace(year=bulan_lalu_dt.year - 1, month=12)).strftime("%Y-%m")

    p_ini, e_ini = hitung_ringkasan(session["user_id"], bulan=bulan_ini)
    p_lalu, e_lalu = hitung_ringkasan(session["user_id"], bulan=bulan_lalu)
    selisih_pengeluaran = e_ini - e_lalu
    selisih_persen = ((e_ini - e_lalu) / e_lalu * 100) if e_lalu > 0 else 0

    return render_template(
        "analisis.html",
        data_mingguan=data_mingguan,
        total_mingguan=total_mingguan,
        hari_terboros=hari_terboros,
        hari_labels=hari_labels,
        hari_values=hari_values,
        tren_labels=tren_labels,
        tren_pemasukan=tren_pemasukan,
        tren_pengeluaran=tren_pengeluaran,
        stat_labels=stat_labels,
        stat_values=stat_values,
        bulan_ini=bulan_ini,
        bulan_lalu=bulan_lalu,
        p_ini=p_ini, e_ini=e_ini,
        p_lalu=p_lalu, e_lalu=e_lalu,
        selisih_pengeluaran=selisih_pengeluaran,
        selisih_persen=selisih_persen,
    )