from flask import Flask

from routes.laporan import laporan
from routes.keuangan import keuangan
from routes.transaksi import transaksi
from routes.auth import auth
from routes.kategori import kategori

from database.db import init_db

app = Flask(__name__)

app.secret_key = "dompetku123"

app.register_blueprint(transaksi)
app.register_blueprint(laporan)
app.register_blueprint(keuangan)
app.register_blueprint(auth)
app.register_blueprint(kategori)

init_db()


@app.template_filter("rupiah")
def rupiah(angka):
    return "{:,.0f}".format(float(angka)).replace(",", ".")


if __name__ == "__main__":
    app.run(debug=True)