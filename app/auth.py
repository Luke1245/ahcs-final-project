from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from werkzeug.security import check_password_hash
from .tools.utils import User, db_connect

auth = Blueprint("auth", __name__)


@auth.route("/login")
def login():
    return render_template("login.html")


@auth.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email")
    password = request.form.get("password")

    connection = db_connect()
    user_data = connection.execute(
        "SELECT * FROM users WHERE email = ?", (email,)
    ).fetchone()
    connection.close()

    if user_data is None:
        flash("Invalid login details")
        return redirect(url_for("auth.login"))

    if not check_password_hash(user_data["passwordHash"], password):
        flash("Invalid login details")
        return redirect(url_for("auth.login"))

    session["email"] = email

    return redirect(url_for("decks.list_decks"))


@auth.route("/register")
def register():
    return render_template("register.html")


@auth.route("/register", methods=["POST"])
def register_post():
    email = request.form.get("email")
    password = request.form.get("password")

    try:
        user = User(email, password)
    except ValueError as error:
        flash(str(error))
        return redirect(url_for("auth.register"))
    else:
        connection = db_connect()
        connection.execute(
            "INSERT INTO users (email, passwordHash) VALUES (?, ?)",
            (user.email, user.passwordHash),
        )
        connection.commit()
        connection.close()

        flash("Successfully registered new user")

    return redirect(url_for("auth.login"))


@auth.route("/logout")
def logout():
    if session["email"] is None:
        flash("Not signed in")
        return redirect(url_for("auth.login"))

    session["email"] = None
    flash("Logged out")
    return redirect(url_for("auth.login"))
