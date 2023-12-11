from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from .tools.utils import User, db_connect

main = Blueprint("main", __name__)

@main.route("/")
def decks():
    if not session.get("email"):
        return redirect(url_for("auth.login"))
    return render_template("index.html")