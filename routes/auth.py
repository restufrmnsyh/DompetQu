from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session
)

from database.db import (
    cek_login,
    ganti_password
)

auth = Blueprint(
    "auth",
    __name__
)

@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = cek_login(
            username,
            password
        )

        if user:

            session["login"] = True

            session["username"] = username

            return redirect("/")

    return render_template(
        "login.html"
    )

@auth.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@auth.route("/profil", methods=["GET", "POST"])
def profil():

    if "login" not in session:
        return redirect("/login")

    pesan = ""

    if request.method == "POST":

        password_lama = request.form["password_lama"]

        password_baru = request.form["password_baru"]

        berhasil = ganti_password(

            session["username"],
            password_lama,
            password_baru

        )

        if berhasil:

            pesan = "Password berhasil diubah"

        else:

            pesan = "Password lama salah"

    return render_template(
        "profil.html",
        username=session["username"],
        pesan=pesan
    )