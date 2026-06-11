from flask import Blueprint, render_template, request, redirect, session
from database.db import (
    ambil_target, simpan_target,
    ambil_budget, simpan_budget,
    hitung_ringkasan
)
from datetime import datetime

keuangan = Blueprint("keuangan", __name__)


@keuangan.route("/target", methods=["GET", "POST"])
def target():
    if "login" not in session:
        return redirect("/login")

    if request.method == "POST":
        nama_target = request.form["nama_target"]
        target_nominal = int(request.form["target_nominal"])
        nominal_terkumpul = int(request.form["nominal_terkumpul"])
        simpan_target(nama_target, target_nominal, nominal_terkumpul)
        return redirect("/target")

    target_data = ambil_target()
    progress = 0
    if target_data:
        if target_data[2] > 0:
            progress = (target_data[3] / target_data[2]) * 100

    return render_template("target.html", target=target_data, progress=progress)


@keuangan.route("/budget", methods=["GET", "POST"])
def budget():
    if "login" not in session:
        return redirect("/login")

    bulan_ini = datetime.now().strftime("%Y-%m")

    if request.method == "POST":
        bulan = request.form["bulan"]
        jumlah_budget = int(request.form["jumlah_budget"])
        simpan_budget(bulan, jumlah_budget)
        return redirect("/budget")

    data_budget = ambil_budget(bulan_ini)
    if not data_budget:
        data_budget = ambil_budget()

    _, pengeluaran = hitung_ringkasan(bulan=bulan_ini)

    persentase = 0
    status = ""
    if data_budget:
        batas_budget = data_budget[2]
        if batas_budget > 0:
            persentase = (pengeluaran / batas_budget) * 100
            if persentase >= 100:
                status = "over"
            elif persentase >= 80:
                status = "warning"

    return render_template(
        "budget.html",
        budget=data_budget,
        pengeluaran=pengeluaran,
        persentase=persentase,
        status=status
    )