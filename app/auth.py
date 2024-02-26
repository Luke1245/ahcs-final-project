from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from werkzeug.security import check_password_hash
from .helpers import User, db_connect

auth = Blueprint("auth", __name__)


@auth.route("/login")
def login():
    # Checks if user is logged in or not
    try:
        if session["email"] is not None:
            flash("You need to be logged out to perform this action")
            return redirect(url_for("decks.list_decks"))
    # Handles no sessions exist edgecase
    except KeyError:
        pass

    return render_template("login.html")


@auth.route("/login", methods=["POST"])
def login_post():
    # Checks if user is logged in or not
    try:
        if session["email"] is not None:
            flash("You need to be logged out to perform this action")
            return redirect(url_for("decks.list_decks"))
    # Handles no sessions exist edgecase
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

    # Checks if supplied password matches users database password, via hash
    if not check_password_hash(user_data["password_hash"], password):
        flash("Invalid login details")
        # Redirect user to login page on invalid login
        return redirect(url_for("auth.login"))

    # Add this users login session to the list of sessions
    session["email"] = email

    # Redirect user to main decks page
    return redirect(url_for("decks.list_decks"))


@auth.route("/register")
def register():
    # Checks if user is logged in or not
    try:
        if session["email"] is not None:
            flash("You need to be logged out to perform this action")
            return redirect(url_for("decks.list_decks"))
        return render_template("register.html")
    # Handles no sessions exist edgecase
    except KeyError:
        # Render the register page
        return render_template("register.html")


@auth.route("/register", methods=["POST"])
def register_post():
    # Checks if user is logged in or not
    try:
        if session["email"] is not None:
            flash("You need to be logged out to perform this action")
            return redirect(url_for("decks.list_decks"))
    # Handles no sessions exist edgecase
    except KeyError:
        pass

    email = request.form.get("email")
    password = request.form.get("password")

    try:
        # Initalise user object with given values
        user = User(email, password)
    # Check if any values were unvalidated
    except ValueError as error:
        # Display respective validation error to user
        flash(str(error))
        # Redirect user to the register page
        return redirect(url_for("auth.register"))
    else:
        connection = db_connect()
        # Add user to databsse
        connection.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)",
            (user.get_email(), user.get_password_hash()),
        )
        connection.commit()
        connection.close()

        flash("Successfully registered your account")

    # Redirect user to the login page
    return redirect(url_for("auth.login"))


@auth.route("/logout")
def logout():
    # Checks if user is logged in or not
    try:
        if session["email"] is None:
            flash("You are not signed in")
            return redirect(url_for("auth.login"))
    # Handles no sessions exist edgecase
    except KeyError:
        return redirect(url_for("auth.login"))

    # Removes users session from list of sessions
    session["email"] = None
    flash("You have been logged out of your account")
    # Redirect user to login page
    return redirect(url_for("auth.login"))
