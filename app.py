from flask import Flask, session

from routes.laporan import laporan
from routes.keuangan import keuangan
from routes.transaksi import transaksi
from routes.auth import auth
from routes.kategori import kategori

from dotenv import load_dotenv
import os

load_dotenv()

from database.db import init_db

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default_secret_key")

app.register_blueprint(transaksi)
app.register_blueprint(laporan)
app.register_blueprint(keuangan)
app.register_blueprint(auth)
app.register_blueprint(kategori)

init_db()


@app.template_filter("rupiah")
def rupiah(angka):
    try:
        return "{:,.0f}".format(float(angka)).replace(",", ".")
    except (ValueError, TypeError):
        return "0"


@app.template_filter("min")
def filter_min(lst):
    return min(lst)

@app.context_processor
def inject_user():
    return {
        "current_user": session.get("username")
    }

if __name__ == "__main__":
    app.run(debug=True)