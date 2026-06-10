from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    send_file
)
from flask import session
from openpyxl import Workbook

import json
import sqlite3

from database.db import (
    ambil_semua_transaksi,
    restore_transaksi
)

laporan = Blueprint(
    "laporan",
    __name__
)


@laporan.route("/export")
def export_excel():
    if "login" not in session:
        return redirect("/login")
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


@laporan.route("/backup")
def backup():
    if "login" not in session:
        return redirect("/login")
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM transaksi
    """)

    data = cursor.fetchall()

    conn.close()

    transaksi = []

    for row in data:
        transaksi.append(dict(row))

    with open(
        "backup_dompetku.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            transaksi,
            f,
            ensure_ascii=False,
            indent=4
        )

    return send_file(
        "backup_dompetku.json",
        as_attachment=True
    )


@laporan.route("/restore", methods=["GET", "POST"])
def restore():
    if "login" not in session:
        return redirect("/login")
    if request.method == "POST":

        file = request.files["file"]

        if file:

            data = json.load(file)

            restore_transaksi(data)

            return redirect("/")

    return render_template("restore.html")