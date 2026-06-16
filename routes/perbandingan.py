from flask import Blueprint, render_template, session, redirect, request
from database.db import (
    hitung_ringkasan,
    ambil_pengeluaran_kategori_bulan,
)
from datetime import datetime

perbandingan = Blueprint("perbandingan", __name__)


@perbandingan.route("/perbandingan")
def halaman_perbandingan():
    if "login" not in session:
        return redirect("/login")

    sekarang = datetime.now()
    bulan = sekarang.month
    tahun = sekarang.year

    # Default: bulan ini vs bulan lalu
    if bulan == 1:
        default_b2 = f"{tahun - 1}-12"
    else:
        default_b2 = f"{tahun}-{bulan - 1:02d}"
    default_b1 = sekarang.strftime("%Y-%m")

    bulan1 = request.args.get("bulan1", default_b1)
    bulan2 = request.args.get("bulan2", default_b2)

    # Ringkasan masing-masing bulan
    p1, e1 = hitung_ringkasan(session["user_id"], bulan=bulan1)
    p2, e2 = hitung_ringkasan(session["user_id"], bulan=bulan2)

    # Kategori masing-masing bulan
    kat1 = ambil_pengeluaran_kategori_bulan(session["user_id"],bulan1)
    kat2 = ambil_pengeluaran_kategori_bulan(session["user_id"], bulan2)

    # Gabungkan semua kategori
    semua_kategori = sorted(set(list(kat1.keys()) + list(kat2.keys())))

    # Data perbandingan per kategori
    komparasi = []
    for kat in semua_kategori:
        val1 = kat1.get(kat, 0)
        val2 = kat2.get(kat, 0)
        selisih = val1 - val2
        if val2 > 0:
            pct = ((val1 - val2) / val2 * 100)
        elif val1 > 0:
            pct = 100.0
        else:
            pct = 0.0
        komparasi.append({
            "kategori": kat,
            "val1": val1,
            "val2": val2,
            "selisih": selisih,
            "pct": round(pct, 1),
        })

    # Sort by val1 desc
    komparasi.sort(key=lambda x: x["val1"], reverse=True)

    # Format nama bulan
    nama_bulan = ['','Jan','Feb','Mar','Apr','Mei','Jun',
                  'Jul','Agt','Sep','Okt','Nov','Des']
    def fmt_bulan(b):
        y, m = b.split('-')
        return f"{nama_bulan[int(m)]} {y}"

    # Chart data
    chart_labels = [k["kategori"] for k in komparasi]
    chart_val1   = [k["val1"] for k in komparasi]
    chart_val2   = [k["val2"] for k in komparasi]

    return render_template(
        "perbandingan.html",
        bulan1=bulan1, bulan2=bulan2,
        label1=fmt_bulan(bulan1),
        label2=fmt_bulan(bulan2),
        p1=p1, e1=e1,
        p2=p2, e2=e2,
        komparasi=komparasi,
        chart_labels=chart_labels,
        chart_val1=chart_val1,
        chart_val2=chart_val2,
    )