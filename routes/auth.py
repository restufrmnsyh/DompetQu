from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session
)

from database.db import (
    cek_login,
    ganti_password,
    tambah_user
)

auth = Blueprint(
    "auth",
    __name__
)

@auth.route("/login", methods=["GET", "POST"])
def login():

    pesan = ""

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = cek_login(
            username,
            password
        )

        if user:

            session["login"] = True
            session["user_id"] = user[0]
            session["username"] = user[1]

            return redirect("/")

        else:

            pesan = "Username atau password salah"

    return render_template(
        "login.html",
        pesan=pesan
    )

@auth.route("/register", methods=["GET", "POST"])
def register():

    pesan = ""

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        berhasil = tambah_user(
            username,
            password
        )

        if berhasil:

            return redirect("/login")

        else:

            pesan = "Username sudah digunakan"

    return render_template(
        "register.html",
        pesan=pesan
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