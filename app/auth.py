from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from werkzeug.security import check_password_hash
from .helpers import User, db_connect

auth = Blueprint("auth", __name__)


@auth.route("/login")
def login():
    try:
        if session["email"] is not None:
            flash("You need to be logged out to perform this action")
            return redirect(url_for("decks.list_decks"))
    except KeyError:
        pass

    return render_template("login.html")


@auth.route("/login", methods=["POST"])
def login_post():
    try:
        if session["email"] is not None:
            flash("You need to be logged out to perform this action")
            return redirect(url_for("decks.list_decks"))
    except KeyError:
        pass

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

    if not check_password_hash(user_data["password_hash"], password):
        flash("Invalid login details")
        return redirect(url_for("auth.login"))

    session["email"] = email

    return redirect(url_for("decks.list_decks"))


@auth.route("/register")
def register():
    try:
        if session["email"] is not None:
            flash("You need to be logged out to perform this action")
            return redirect(url_for("decks.list_decks"))
        return render_template("register.html")
    except KeyError:
        return render_template("register.html")


@auth.route("/register", methods=["POST"])
def register_post():
    try:
        if session["email"] is not None:
            flash("You need to be logged out to perform this action")
            return redirect(url_for("decks.list_decks"))
    except KeyError:
        pass

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
            "INSERT INTO users (email, password_hash) VALUES (?, ?)",
            (user.email, user.password_hash),
        )
        connection.commit()
        connection.close()

        flash("Successfully registered your account")

    return redirect(url_for("auth.login"))


@auth.route("/logout")
def logout():
    try:
        if session["email"] is None:
            flash("You are not signed in")
            return redirect(url_for("auth.login"))
    except KeyError:
        return redirect(url_for("auth.login"))

    session["email"] = None
    flash("You have been logged out of your account")
    return redirect(url_for("auth.login"))
