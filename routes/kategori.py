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
    hapus_kategori,
    ambil_kategori_by_id,
    kategori_dipakai
)

kategori = Blueprint(
    "kategori",
    __name__
)

@kategori.route("/kategori", methods=["GET", "POST"])
def kelola_kategori():
    print("USER LOGIN:", session.get("user_id"))

    if "login" not in session:
        return redirect("/login")

    if request.method == "POST":

        nama = request.form["nama"]

        tambah_kategori(
            session["user_id"],
            nama
        )

        return redirect("/kategori")

    data = ambil_kategori(
        session["user_id"]
    )

    return render_template(
        "kategori.html",
        kategori=data
    )

@kategori.route("/hapus-kategori/<int:id>")
def hapus(id):

    if "login" not in session:
        return redirect("/login")

    data = ambil_kategori_by_id(
        session["user_id"],
        id
    )

    if not data:
        return redirect("/kategori")

    nama_kategori = data[1]

    if kategori_dipakai(
        session["user_id"],
        nama_kategori
    ):
        return redirect("/kategori")

    hapus_kategori(
        session["user_id"],
        id
    )

    return redirect("/kategori")