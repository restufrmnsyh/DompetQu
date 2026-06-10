from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session
)

from database.db import (
    ambil_kategori,
    tambah_kategori,
    hapus_kategori
)

kategori = Blueprint(
    "kategori",
    __name__
)

@kategori.route("/kategori", methods=["GET", "POST"])
def kelola_kategori():

    if "login" not in session:
        return redirect("/login")

    if request.method == "POST":

        nama = request.form["nama"]

        tambah_kategori(nama)

        return redirect("/kategori")

    data = ambil_kategori()

    return render_template(
        "kategori.html",
        kategori=data
    )

@kategori.route("/hapus-kategori/<int:id>")
def hapus(id):

    if "login" not in session:
        return redirect("/login")

    hapus_kategori(id)
    return redirect("/kategori")