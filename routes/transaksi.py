from flask import Blueprint, render_template, request, redirect, session
from database.db import (
    ambil_semua_transaksi, hitung_saldo, tambah_transaksi, hapus_transaksi,
    hitung_ringkasan, ambil_pengeluaran_per_kategori, ambil_kategori,
    ambil_ringkasan_bulanan, edit_transaksi, ambil_transaksi_by_id, ambil_statistik_dashboard, ambil_insight
)
from utils.waktu import sekarang_wib


transaksi = Blueprint("transaksi", __name__)


@transaksi.route("/")
def dashboard():
    if "login" not in session:
        return redirect("/login")

    bulan_filter = request.args.get("bulan", "")
    jenis_filter = request.args.get("jenis", "")
    page = int(
        request.args.get("page", 1)
    )

    semua_transaksi = ambil_semua_transaksi(
        session["user_id"],
        bulan=bulan_filter or None,
        jenis=jenis_filter or None
    )

    per_page = 10
    start = (page - 1) * per_page
    end = start + per_page
    transaksi_data = semua_transaksi[start:end]

    total_data = len(semua_transaksi)
    total_page = (
        total_data + per_page - 1
    ) // per_page

    saldo = hitung_saldo(
        session["user_id"]
    )
    pemasukan, pengeluaran = hitung_ringkasan(session["user_id"], bulan=bulan_filter or None)
    kategori_data = ambil_pengeluaran_per_kategori( session["user_id"], bulan=bulan_filter or None)
    ringkasan_bulanan = ambil_ringkasan_bulanan(session["user_id"])

    labels = [item[0] for item in kategori_data]
    values = [item[1] for item in kategori_data]

    bulan_labels = [item[0] for item in reversed(ringkasan_bulanan)]
    bulan_pemasukan = [item[1] for item in reversed(ringkasan_bulanan)]
    bulan_pengeluaran = [item[2] for item in reversed(ringkasan_bulanan)]

    bulan_ini = sekarang_wib().strftime("%Y-%m")

    (
        total_transaksi,
        kategori_terbesar,
        rata_pengeluaran,
        bulan_aktif
    ) = ambil_statistik_dashboard(session["user_id"])

    (
        kategori_terbesar,
        persentase_pengeluaran
    ) = ambil_insight(session["user_id"])
    return render_template(
        "dashboard.html",
        transaksi=transaksi_data,
        saldo=saldo,
        pemasukan=pemasukan,
        pengeluaran=pengeluaran,
        labels=labels,
        values=values,
        bulan_labels=bulan_labels,
        bulan_pemasukan=bulan_pemasukan,
        bulan_pengeluaran=bulan_pengeluaran,
        bulan_filter=bulan_filter,
        jenis_filter=jenis_filter,
        bulan_ini=bulan_ini,
        total_transaksi=total_transaksi,
        kategori_terbesar=kategori_terbesar,
        rata_pengeluaran=rata_pengeluaran,
        bulan_aktif=bulan_aktif,
        page=page,
        total_page=total_page,
        persentase_pengeluaran=persentase_pengeluaran
    )


@transaksi.route("/tambah", methods=["GET", "POST"])
def tambah():
    if "login" not in session:
        return redirect("/login")

    if request.method == "POST":
        tanggal = sekarang_wib().strftime("%Y-%m-%d")

        jenis = request.form["jenis"]
        kategori = request.form["kategori"]
        nominal = int(request.form["nominal"])
        catatan = request.form.get("catatan", "")

        tambah_transaksi(
            session["user_id"],
            tanggal,
            jenis,
            kategori,
            nominal,
            catatan
        )
        return redirect("/")

    kategori = ambil_kategori(session["user_id"])
    today = sekarang_wib().strftime("%Y-%m-%d")
    return render_template("tambah.html", kategori=kategori, today=today)


@transaksi.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    if "login" not in session:
        return redirect("/login")

    if request.method == "POST":
        tanggal = request.form["tanggal"]
        jenis = request.form["jenis"]
        kategori = request.form["kategori"]
        nominal = int(request.form["nominal"])
        catatan = request.form.get("catatan", "")
        edit_transaksi(session["user_id"], id, tanggal, jenis, kategori, nominal, catatan)
        return redirect("/")

    data = ambil_transaksi_by_id(session["user_id"], id)
    if not data:
        return redirect("/")
    kategori = ambil_kategori(session["user_id"])
    return render_template("edit.html", t=data, kategori=kategori)


@transaksi.route("/hapus/<int:id>")
def hapus(id):
    if "login" not in session:
        return redirect("/login")
    hapus_transaksi(session["user_id"],id)
    return redirect("/")