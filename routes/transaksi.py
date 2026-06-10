from flask import (
    Blueprint,
    render_template,
    request,
    redirect
)

from database.db import (
    ambil_semua_transaksi,
    hitung_saldo,
    tambah_transaksi,
    hapus_transaksi,
    hitung_ringkasan,
    ambil_pengeluaran_per_kategori
)

transaksi = Blueprint(
    "transaksi",
    __name__
)

@transaksi.route("/")
def dashboard():

    transaksi_data = ambil_semua_transaksi()

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
        transaksi=transaksi_data,
        saldo=saldo,
        pemasukan=pemasukan,
        pengeluaran=pengeluaran,
        labels=labels,
        values=values
    )

@transaksi.route("/tambah", methods=["GET", "POST"])
def tambah():

    if request.method == "POST":

        tanggal = request.form["tanggal"]

        jenis = request.form["jenis"]

        kategori = request.form["kategori"]

        nominal = int(
            request.form["nominal"]
        )

        catatan = request.form["catatan"]

        tambah_transaksi(
            tanggal,
            jenis,
            kategori,
            nominal,
            catatan
        )

        return redirect("/")

    return render_template(
        "tambah.html"
    )

@transaksi.route("/hapus/<int:id>")
def hapus(id):

    hapus_transaksi(id)

    return redirect("/")