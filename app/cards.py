from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from .tools.utils import User, Deck, Card, db_connect, getUserID, fetchDecks
import datetime

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


@cards.route("/add_card", methods=["POST"])
def add_card_post():
    if not session.get("email"):
        return redirect(url_for("auth.login"))

    deckID = request.form.get("deck")
    front = request.form.get("front")
    back = request.form.get("back")
    familiarity = int(request.form.get("familiarity"))
    time = datetime.datetime.utcnow().isoformat()

    try:
        card = Card(deckID, time, front, back, familiarity)
    except ValueError as error:
        flash(error)
        return redirect(url_for("cards.add_card"))

    connection = db_connect()
    connection.execute(
        "INSERT INTO cards (deckID, timeCreated, front, back, familiarity) VALUES (?, ?, ?, ?, ?)",
        (card.deckID, card.timeCreated, card.front, card.back, card.familiarity),
    )
    connection.commit()
    connection.close()
    return redirect(url_for("cards.add_card"))
