from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from .tools.utils import User, db_connect

main = Blueprint("main", __name__)


@main.route("/")
def list_decks():
    if not session.get("email"):
        return redirect(url_for("auth.login"))
    return render_template("index.html")


@main.route("/add_card", methods=["POST"])
def add_card_post():
    if not session.get("email"):
        return redirect(url_for("auth.login"))
    
    return redirect(url_for("main.list_decks"))
