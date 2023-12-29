from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from .helpers import (
    Card,
    db_connect,
    fetch_decks,
    fetch_cards,
    FAMILIARITY_MAPPINGS,
    delete_card_from_database,
)
import datetime

cards = Blueprint("cards", __name__)


@cards.route("/add_card")
def add_card():
    if not session.get("email"):
        return redirect(url_for("auth.login"))

    try:
        decks = fetch_decks(session)
    except ValueError:
        return redirect(url_for("auth.login"))

    return render_template("add_card.html", decks=decks)


@cards.route("/add_card", methods=["POST"])
def add_card_post():
    if not session.get("email"):
        return redirect(url_for("auth.login"))

    deck_id = request.form.get("deck_id")
    front = request.form.get("front")
    back = request.form.get("back")
    familiarity = int(request.form.get("familiarity"))
    time_created = datetime.datetime.utcnow().isoformat()

    try:
        card = Card(deck_id, time_created, front, back, familiarity)
    except ValueError as error:
        flash(error)
        return redirect(url_for("cards.add_card"))

    connection = db_connect()

    current_number_of_cards = (
        connection.execute(
            "SELECT number_of_cards FROM decks WHERE deck_id = ?", (card.deck_id)
        ).fetchone()
    )[0]
    incremented_number_of_cards = current_number_of_cards + 1

    connection.execute(
        "INSERT INTO cards (deck_id, time_created, front, back, familiarity) VALUES (?, ?, ?, ?, ?)",
        (card.deck_id, card.time_created, card.front, card.back, card.familiarity),
    )
    connection.execute(
        "UPDATE decks SET number_of_cards = ? WHERE deck_id = ?",
        (incremented_number_of_cards, card.deck_id),
    )
    connection.commit()
    connection.close()
    return redirect(url_for("cards.add_card"))


@cards.route("/list_cards", methods=["GET"])
def list_cards():
    if not session.get("email"):
        return redirect(url_for("auth.login"))

    args = request.args
    deck_id = args.get("deck_id")
    deck_name = args.get("deck_name")

    if deck_id is None:
        flash("You need to select a deck")
        return redirect(url_for("decks.list_decks"))

    cards = fetch_cards(deck_id)

    # Convert int card familiarities into their text varients
    for card in cards:
        card.familiarity = FAMILIARITY_MAPPINGS[card.familiarity]

    for card in cards:
        if len(card.front) > 30:
            card.front = card.front[:30] + "..."
        if len(card.back) > 30:
            card.back = card.back[:30] + "..."

    return render_template("list_cards.html", cards=cards, deck=deck_name)


@cards.route("/delete_card", methods=["GET"])
def delete_card():
    if not session.get("email"):
        return redirect(url_for("auth.login"))

    args = request.args
    card_id = args.get("card_id")

    if card_id is None:
        flash("You need to select a card to delete")
        return redirect(url_for("decks.list_decks"))

    delete_card_from_database(str(card_id))

    flash("Card deleted")
    return redirect(url_for("decks.list_decks"))


@cards.route("/update_card", methods=["POST"])
def update_card():
    if not session.get("email"):
        return redirect(url_for("auth.login"))

    deck_id = request.form.get("deck_id")
    next_card_id = request.form.get("next_card_id")
    current_card_id = request.form.get("current_card_id")
    current_familiarity = int(request.form.get("current_familiarity"))
    familiarity_update = request.form.get("familiarity_update")
    new_familiarity = current_familiarity

    if familiarity_update == "known" and current_familiarity < 4:
        new_familiarity = current_familiarity + 1
    elif familiarity_update == "unknown" and current_familiarity > 1:
        new_familiarity = current_familiarity - 1

    connection = db_connect()
    connection.execute(
        "UPDATE cards SET familiarity = ? WHERE card_id = ?",
        (new_familiarity, current_card_id),
    )
    connection.commit()
    connection.close()

    print(next_card_id)
    return redirect(url_for("decks.revise_deck", deck_id = deck_id, card_id = next_card_id))
