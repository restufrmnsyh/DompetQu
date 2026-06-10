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
    ambil_pengeluaran_per_kategori,
    ambil_kategori
)

from flask import session

transaksi = Blueprint(
    "transaksi",
    __name__
)

@transaksi.route("/")
def dashboard():
    if "login" not in session:
        return redirect("/login")

    transaksi_data = ambil_semua_transaksi()

    saldo = hitung_saldo()

    pemasukan, pengeluaran = hitung_ringkasan()

    kategori_data = ambil_pengeluaran_per_kategori()

    labels = []
    values = []

    for item in kategori_data:

        labels.append(item[0])
        values.append(item[1])

    print("LABELS =", labels)
    print("VALUES =", values)
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

    if "login" not in session:
        return redirect("/login")

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
    kategori = ambil_kategori()
    return render_template(
        "tambah.html", 
        kategori=kategori
    )

@transaksi.route("/hapus/<int:id>")
def hapus(id):

    if "login" not in session:
        return redirect("/login")

    hapus_transaksi(id)

    return redirect("/")