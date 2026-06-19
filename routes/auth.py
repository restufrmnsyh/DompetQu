from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session
)

import os
import uuid
from PIL import Image

from werkzeug.utils import secure_filename

from database.db import (
    cek_login,
    ganti_password,
    tambah_user,
    ambil_foto_profil,
    update_foto_profil
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
            session["foto_profil"] = ambil_foto_profil(user[0])
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
        konfirmasi = request.form.get("konfirmasi_password", "")

        if len(username) < 3:
            pesan = "Username minimal 3 karakter!"
        elif len(password) < 4:
            pesan = "Password minimal 4 karakter!"
        elif password != konfirmasi:
            pesan = "Password dan konfirmasi password tidak cocok!"
        else:
            berhasil = tambah_user(username, password)
            if berhasil:
                return redirect("/login")
            else:
                pesan = "Username sudah digunakan, coba yang lain!"

    return render_template("register.html", pesan=pesan)

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

    foto_profil = ambil_foto_profil(
        session["user_id"]
    )
    return render_template(
        "profil.html",
        username=session["username"],
        pesan=pesan,
        foto_profil=foto_profil
    )

@auth.route("/profil/foto", methods=["POST"])
def upload_foto():

    if "login" not in session:
        return redirect("/login")

    file = request.files.get("foto")

    if not file or file.filename == "":
        return redirect("/profil")

    ekstensi = file.filename.rsplit(".", 1)[1].lower()

    if ekstensi not in ["jpg", "jpeg", "png", "webp"]:
        return redirect("/profil")

    nama_file = (
        str(uuid.uuid4())
        + "."
        + ekstensi
    )

    folder_upload = os.path.join(
        "static",
        "uploads",
        "profil"
    )

    os.makedirs(
        folder_upload,
        exist_ok=True
    )

    lokasi = os.path.join(
        folder_upload,
        nama_file
    )

    foto_lama = ambil_foto_profil(
        session["user_id"]
    )

    img = Image.open(file)

    img = img.convert("RGB")

    img.thumbnail(
        (300, 300),
        Image.LANCZOS
    )

    img.save(
        lokasi,
        quality=85,
        optimize=True
    )

    update_foto_profil(
        session["user_id"],
        f"/static/uploads/profil/{nama_file}"
    )

    session["foto_profil"] = (
        f"/static/uploads/profil/{nama_file}"
    )

    if foto_lama:
        path_lama = foto_lama.lstrip("/")
        if os.path.exists(path_lama):
            try:
                os.remove(path_lama)
            except:
                pass

    return redirect("/profil")