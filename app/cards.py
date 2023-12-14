from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from .tools.utils import (
    User,
    Deck,
    Card,
    db_connect,
    getUserID,
    fetchDecks,
    fetchCards,
    FAMILIARITY_MAPPINGS,
    deleteCard
)
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

    currentNumberOfCards = (
        connection.execute(
            "SELECT numberOfCards FROM decks WHERE deckID = ?", (card.deckID)
        ).fetchone()
    )[0]
    incrementedNumberOfCards = currentNumberOfCards + 1

    connection.execute(
        "INSERT INTO cards (deckID, timeCreated, front, back, familiarity) VALUES (?, ?, ?, ?, ?)",
        (card.deckID, card.timeCreated, card.front, card.back, card.familiarity),
    )
    connection.execute(
        "UPDATE decks SET numberOfCards = ? WHERE deckID = ?",
        (incrementedNumberOfCards, card.deckID),
    )
    connection.commit()
    connection.close()
    return redirect(url_for("cards.add_card"))


@cards.route("/list_cards", methods=["GET"])
def list_cards():
    if not session.get("email"):
        return redirect(url_for("auth.login"))

    args = request.args
    deckID = args.get("deckid")
    deckName = args.get("deckname")

    cards = fetchCards(deckID)

    # Convert int card familiarities into their text varients
    for card in cards:
        card.familiarity = FAMILIARITY_MAPPINGS[card.familiarity]

    return render_template("list_cards.html", cards=cards, deck=deckName)


@cards.route("/delete_card", methods=["GET"])
def delete_card():
    if not session.get("email"):
        return redirect(url_for("auth.login"))
    
    args = request.args
    cardID = args.get("cardid")

    deleteCard(str(cardID))

    flash("Card deleted")
    return redirect(url_for("decks.list_decks"))
