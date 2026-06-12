from flask import Blueprint, render_template, request, redirect, send_file, session, flash
from openpyxl import Workbook
from openpyxl.styles import Font
from io import BytesIO
import json
import sqlite3
from database.db import (
    ambil_semua_transaksi, 
    restore_transaksi,
    hitung_ringkasan,
    hitung_saldo,
    reset_transaksi
    )

laporan = Blueprint("laporan", __name__)


@laporan.route("/export")
def export_excel():
    if "login" not in session:
        return redirect("/login")

    transaksi = ambil_semua_transaksi(session["user_id"])

    pemasukan, pengeluaran = hitung_ringkasan(session["user_id"])
    saldo = hitung_saldo()

    wb = Workbook()
    ws = wb.active
    ws.title = "Laporan Keuangan"

    # Judul
    ws["A1"] = "LAPORAN KEUANGAN DOMPETQU"
    ws["A1"].font = Font(bold=True, size=16)

    # Ringkasan
    ws["A3"] = "Total Pemasukan"
    ws["B3"] = pemasukan

    ws["A4"] = "Total Pengeluaran"
    ws["B4"] = pengeluaran

    ws["A5"] = "Saldo"
    ws["B5"] = saldo

    # Header tabel
    ws.append([])
    ws.append(["No", "Tanggal", "Jenis", "Kategori", "Nominal", "Catatan"])
    for cell in ws[7]:
        cell.font = Font(bold=True)

    for i, t in enumerate(transaksi, 1):
        ws.append([i, t[1], t[2], t[3], t[4], t[5] or ""])

    for col in ws.columns:
        max_len = max((len(str(cell.value)) for cell in col if cell.value), default=10)
        ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 40)

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return send_file(
        output,
        download_name="laporan_keuangan.xlsx",
        as_attachment=True,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@laporan.route("/backup")
def backup():
    if "login" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transaksi WHERE user_id = ?", (session["user_id"],))
    data = [dict(row) for row in cursor.fetchall()]
    conn.close()

    output = BytesIO(json.dumps(data, ensure_ascii=False, indent=4).encode("utf-8"))
    output.seek(0)
    return send_file(
        output,
        download_name="backup_dompetku.json",
        as_attachment=True,
        mimetype="application/json"
    )


@laporan.route("/restore", methods=["GET", "POST"])
def restore():
    if "login" not in session:
        return redirect("/login")

    pesan = ""
    if request.method == "POST":
        file = request.files.get("file")
        if file:
            try:
                data = json.load(file)
                restore_transaksi(session["user_id"], data)
                return redirect("/")
            except Exception as e:
                pesan = f"Gagal restore: {str(e)}"

    return render_template("restore.html", pesan=pesan)

@laporan.route("/reset")
def reset():

    if "login" not in session:
        return redirect("/login")

    reset_transaksi(session["user_id"])

    flash("Semua transaksi berhasil dihapus")

    return redirect("/")