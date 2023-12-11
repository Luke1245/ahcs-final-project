from flask import Blueprint, render_template, redirect, url_for, request, flash
from .tools.utils import User, db_connect

auth = Blueprint("auth", __name__)

@auth.route("/login")
def login():
    return render_template("index.html")

@auth.route("/register")
def register():
    return render_template("register.html")

@auth.route("/register", methods=["POST"])
def register_post():
    email = request.form.get('email')
    password = request.form.get('password')

    try:
        user = User(email, password)
    except ValueError as error:
        flash(str(error))
    else:
        connection = db_connect()
        connection.execute("INSERT INTO users (email, passwordHash) VALUES (?, ?)", (user.email, user.passwordHash))
        connection.commit()
        connection.close()

        flash("Successfully registered new user")

    return redirect(url_for('auth.login'))

@auth.route("/logout")
def logout():
    pass