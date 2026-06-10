from flask import Flask, render_template, request, redirect, send_file
from openpyxl import Workbook
import os

from database.db import (
    init_db,
    tambah_transaksi,
    ambil_semua_transaksi,
    hitung_saldo,
    hapus_transaksi,
    hitung_ringkasan,
    ambil_target,
    simpan_target,
    simpan_budget,
    ambil_budget,
    ambil_pengeluaran_per_kategori
)

app = Flask(__name__)

init_db()


@app.template_filter("rupiah")
def rupiah(angka):
    return "{:,.0f}".format(float(angka)).replace(",", ".")


@app.route("/")
def dashboard():

    transaksi = ambil_semua_transaksi()

    saldo = hitung_saldo()

    pemasukan, pengeluaran = hitung_ringkasan()
    kategori_data = ambil_pengeluaran_per_kategori()

    labels = []
    values = []

    for item in kategori_data:
        labels.append(item[0])
        values.append(item[1])
    return render_template(
        "dashboard.html",
        transaksi=transaksi,
        saldo=saldo,
        pemasukan=pemasukan,
        pengeluaran=pengeluaran,
        labels=labels,
        values=values
    )


@app.route("/tambah", methods=["GET", "POST"])
def tambah():

    if request.method == "POST":

        tanggal = request.form["tanggal"]
        jenis = request.form["jenis"]
        kategori = request.form["kategori"]
        nominal = int(request.form["nominal"])
        catatan = request.form["catatan"]

        tambah_transaksi(
            tanggal,
            jenis,
            kategori,
            nominal,
            catatan
        )

        return redirect("/")

    return render_template("tambah.html")


@app.route("/hapus/<int:id>")
def hapus(id):

    hapus_transaksi(id)

    return redirect("/")


@app.route("/target", methods=["GET", "POST"])
def target():

    if request.method == "POST":

        nama_target = request.form["nama_target"]

        target_nominal = int(
            request.form["target_nominal"]
        )

        nominal_terkumpul = int(
            request.form["nominal_terkumpul"]
        )

        simpan_target(
            nama_target,
            target_nominal,
            nominal_terkumpul
        )

        return redirect("/target")

    target_data = ambil_target()

    progress = 0

    if target_data:

        target_nominal = target_data[2]
        nominal_terkumpul = target_data[3]

        if target_nominal > 0:

            progress = (
                nominal_terkumpul /
                target_nominal
            ) * 100

    return render_template(
        "target.html",
        target=target_data,
        progress=progress
    )

@app.route("/budget", methods=["GET", "POST"])
def budget():

    if request.method == "POST":

        bulan = request.form["bulan"]

        jumlah_budget = int(
            request.form["jumlah_budget"]
        )

        simpan_budget(
            bulan,
            jumlah_budget
        )

        return redirect("/budget")

    data_budget = ambil_budget()

    pemasukan, pengeluaran = hitung_ringkasan()

    return render_template(
        "budget.html",
        budget=data_budget,
        pengeluaran=pengeluaran
    )

@app.route("/export")
def export_excel():

    transaksi = ambil_semua_transaksi()

    wb = Workbook()

    ws = wb.active

    ws.title = "Laporan Keuangan"

    ws.append([
        "Tanggal",
        "Jenis",
        "Kategori",
        "Nominal",
        "Catatan"
    ])

    for t in transaksi:

        ws.append([
            t[1],
            t[2],
            t[3],
            t[4],
            t[5]
        ])

    file_name = "laporan_keuangan.xlsx"

    wb.save(file_name)

    return send_file(
        file_name,
        as_attachment=True
    )

if __name__ == "__main__":
    app.run(debug=True)