from flask import Blueprint, render_template, request, redirect, session
from database.db import (
    ambil_target, 
    ambil_budget, 
    simpan_budget,
    simpan_target,
    hitung_ringkasan
)

from utils.waktu import sekarang_wib

keuangan = Blueprint("keuangan", __name__)

@keuangan.route("/keuangan", methods=["GET", "POST"])
def halaman_keuangan():
    if "login" not in session:
        return redirect("/login")

    now = sekarang_wib()
    bulan_ini = now.strftime("%Y-%m")

    if request.method == "POST":

        form_type = request.form.get(
            "form_type"
        )

        if form_type == "budget":

            bulan = request.form["bulan"]
            jumlah_budget = int(
                request.form["jumlah_budget"]
            )

            simpan_budget(
                session["user_id"],
                bulan,
                jumlah_budget
            )

        elif form_type == "target":

            nama_target = request.form[
                "nama_target"
            ]

            target_nominal = int(
                request.form["target_nominal"]
            )

            nominal_terkumpul = int(
                request.form["nominal_terkumpul"]
            )

            simpan_target(
                session["user_id"],
                nama_target,
                target_nominal,
                nominal_terkumpul
            )

        return redirect("/keuangan")
    

    # Budget
    data_budget = ambil_budget(session["user_id"], bulan_ini) or ambil_budget(session["user_id"])
    _, pengeluaran = hitung_ringkasan(session["user_id"], bulan=bulan_ini)
    persentase = 0
    status = ""
    if data_budget and data_budget[2] > 0:
        persentase = (pengeluaran / data_budget[2]) * 100
        status = "over" if persentase >= 100 else "warning" if persentase >= 80 else ""

    # Target
    target_data = ambil_target(session["user_id"])
    progress = 0
    if target_data and target_data[2] > 0:
        progress = (target_data[3] / target_data[2]) * 100

    return render_template(
        "keuangan.html",
        budget=data_budget,
        pengeluaran=pengeluaran,
        persentase=persentase,
        status=status,
        target=target_data,
        progress=progress,
    )