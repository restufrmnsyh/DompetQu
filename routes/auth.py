from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session
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

        if username == "restu" and password == "12345":

            session["login"] = True

            return redirect("/")

    return render_template("login.html")


@auth.route("/logout")
def logout():

    session.clear()

    return redirect("/login")