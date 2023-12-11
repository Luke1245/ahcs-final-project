from flask import Blueprint, render_template, redirect, url_for, request, flash
from .tools.utils import User, db_connect

main = Blueprint("main", __name__)

@main.route("/decks")
def decks():
    return render_template("decks.html")