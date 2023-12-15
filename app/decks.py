from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from .helpers import (
    User,
    Deck,
    db_connect,
    fetch_decks,
    get_user_id,
    fetch_cards,
    delete_card_from_database,
)
import json

decks = Blueprint("decks", __name__)


@decks.route("/")
def list_decks():
    if not session.get("email"):
        return redirect(url_for("auth.login"))

    try:
        decks = fetch_decks(session)
    except ValueError:
        return redirect(url_for("auth.login"))

    return render_template("index.html", decks=decks)


@decks.route("/add_deck", methods=["POST"])
def add_deck_post():
    if not session.get("email"):
        return redirect(url_for("auth.login"))

    deck_name = (json.loads(request.data))["name"]

    email = session.get("email")
    connection = db_connect()
    user_id = (
        connection.execute(
            "SELECT user_id FROM users WHERE email = ?", (email,)
        ).fetchone()
    )[0]
    connection.close
    try:
        deck = Deck(user_id, deck_name, new_deck=True)
    except ValueError as error:
        flash(str(error))
        return "Error adding deck to database", 400
    else:
        connection = db_connect()
        connection.execute(
            "INSERT INTO decks (user_id, deck_name) VALUES (?, ?)",
            (deck.user_id, deck.deck_name),
        )
        flash("Added new deck")
        connection.commit()
        connection.close()

    return "Deck added to database"


@decks.route("/delete_deck", methods=["GET"])
def delete_deck():
    if not session.get("email"):
        return redirect(url_for("auth.login"))

    args = request.args
    deck_id = args.get("deck_id")
    email = session.get("email")

    try:
        user_id = get_user_id(email)
    except ValueError:
        return redirect(url_for("auth.login"))

    cards_to_delete = fetch_cards(deck_id)
    for card in cards_to_delete:
        delete_card_from_database(card.card_id)

    connection = db_connect()
    connection.execute(
        "DELETE FROM decks WHERE deck_id = ? AND user_id = ?", (deck_id, user_id)
    )
    connection.commit()
    flash("Deck deleted")
    return redirect(url_for("decks.list_decks"))
