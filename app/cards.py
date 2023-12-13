from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from .tools.utils import User, Deck, db_connect, getUserID, fetchDecks

cards = Blueprint("cards", __name__)


@cards.route("/add_card")
def add_card():
    if not session.get("email"):
        return redirect(url_for("auth.login"))

    try:
        decks = fetchDecks(session)
    except ValueError:
        return redirect(url_for("auth.login"))

    return render_template("add_card.html", decks=decks)
