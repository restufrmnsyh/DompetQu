from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    current_app,
    flash
)

import os
import uuid
from PIL import Image, ImageOps

from werkzeug.utils import secure_filename

from database.db import (
    cek_login,
    ganti_password,
    tambah_user,
    ambil_foto_profil,
    update_foto_profil,
    verifikasi_password,
    hapus_akun,
    update_username,
    username_sudah_ada
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

    if request.method == "POST":

        password_lama = request.form["password_lama"]

        password_baru = request.form["password_baru"]

        berhasil = ganti_password(

            session["username"],
            password_lama,
            password_baru

        )

        if berhasil:
            flash(
                "Password berhasil diubah",
                "success"
            )
        else:

            flash(
                "Password lama salah",
                "danger"
            )

    foto_profil = ambil_foto_profil(
        session["user_id"]
    )
    return render_template(
        "profil.html",
        username=session["username"],
        foto_profil=foto_profil
    )

@auth.route(
    "/profil/username",
    methods=["POST"]
)
def ganti_username():

    if "login" not in session:
        return redirect("/login")

    username_baru = request.form["username"].strip()

    if len(username_baru) < 3:

        flash(
            "Username minimal 3 karakter",
            "warning"
        )

        return redirect("/profil")

    if username_sudah_ada(username_baru):

        flash(
            "Username sudah digunakan",
            "danger"
        )

        return redirect("/profil")

    berhasil = update_username(
        session["user_id"],
        username_baru
    )

    if berhasil:

        session["username"] = username_baru

        flash(
            "Username berhasil diperbarui",
            "success"
        )

    else:

        flash(
            "Gagal mengubah username",
            "danger"
        )

    return redirect("/profil")


@auth.route(
    "/profil/hapus-akun",
    methods=["POST"]
)
def hapus_akun_route():

    if "login" not in session:
        return redirect("/login")

    password = request.form["password"]

    if not verifikasi_password(session["user_id"], password):
        flash(
            "Password yang Anda masukkan salah",
            "danger"
        )
        return redirect("/profil")

    foto = ambil_foto_profil(
        session["user_id"]
    )

    if foto:

        path = foto.lstrip("/")

        if os.path.exists(path):
            try:
                os.remove(path)
            except:
                pass

    hapus_akun(
        session["user_id"]
    )

    session.clear()

    return redirect("/login")

@auth.route("/profil/foto", methods=["POST"])
def upload_foto():

    if "login" not in session:
        return redirect("/login")

    file = request.files.get("foto")

    if not file or file.filename == "":
        current_app.logger.warning("Upload foto: tidak ada file terkirim")
        return redirect("/profil")

    if "." not in file.filename:
        current_app.logger.warning(f"Upload foto: filename tanpa ekstensi -> {file.filename}")
        return redirect("/profil")

    ekstensi = file.filename.rsplit(".", 1)[1].lower()

    if ekstensi not in ["jpg", "jpeg", "png", "webp"]:
        current_app.logger.warning(f"Upload foto: ekstensi ditolak -> {ekstensi}")
        return redirect("/profil")

    nama_file = (
        str(uuid.uuid4())
        + "."
        + ekstensi
    )

    # FIX #1: gunakan path absolut berbasis root aplikasi Flask,
    # bukan path relatif terhadap current working directory.
    # PENTING di PythonAnywhere: current_app.root_path HARUS mengarah
    # ke folder yang sama persis dengan path yang di-set di
    # dashboard Web -> Static files mapping untuk URL "/static/".
    folder_upload = os.path.join(
        current_app.root_path,
        "static",
        "uploads",
        "profil"
    )

    current_app.logger.info(f"Upload foto: menyimpan ke folder -> {folder_upload}")

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

    # FIX #2: hanya buka file SEKALI. Membuka FileStorage dua kali
    # bisa gagal karena stream sudah terbaca habis di pembukaan pertama.
    try:
        img = Image.open(file)
        img = img.convert("RGB")
        img = ImageOps.fit(
            img,
            (300, 300),
            method=Image.LANCZOS
        )
        img.save(
            lokasi,
            quality=85,
            optimize=True
        )
        current_app.logger.info(f"Upload foto: berhasil disimpan -> {lokasi}")
    except Exception as e:
        current_app.logger.error(f"Upload foto: GAGAL memproses gambar -> {e}")
        return redirect("/profil")

    update_foto_profil(
        session["user_id"],
        f"/static/uploads/profil/{nama_file}"
    )

    session["foto_profil"] = (
        f"/static/uploads/profil/{nama_file}"
    )

    # Hapus foto lama setelah foto baru berhasil disimpan
    if foto_lama:
        path_lama = os.path.join(
            current_app.root_path,
            foto_lama.lstrip("/")
        )
        if os.path.exists(path_lama):
            try:
                os.remove(path_lama)
            except Exception:
                pass

    return redirect("/profil")

@auth.route(
    "/profil/hapus-foto",
    methods=["POST"]
)
def hapus_foto():

    if "login" not in session:
        return redirect("/login")

    foto = ambil_foto_profil(
        session["user_id"]
    )

    if foto:

        path = os.path.join(
            current_app.root_path,
            foto.lstrip("/")
        )

        if os.path.exists(path):
            try:
                os.remove(path)
            except:
                pass

        update_foto_profil(
            session["user_id"],
            None
        )

        session["foto_profil"] = None

        flash(
            "Foto profil berhasil dihapus",
            "success"
        )

    return redirect("/profil")