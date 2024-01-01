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
    # Checks if user is logged in or not
    if not session.get("email"):
        # Redirect user to login page
        return redirect(url_for("auth.login"))

    try:
        # Retrieve the users decks
        decks = fetch_decks(session)
    except ValueError:
        return redirect(url_for("auth.login"))

    # Render the decks list with the users fetched decks
    return render_template("add_card.html", decks=decks)


@cards.route("/add_card", methods=["POST"])
def add_card_post():
    # Checks if user is logged in or not
    if not session.get("email"):
        # Redirect user to login page
        return redirect(url_for("auth.login"))

    deck_id = request.form.get("deck_id")
    front = request.form.get("front")
    back = request.form.get("back")
    familiarity = int(request.form.get("familiarity"))
    # Get current time in ISO 8601 format
    time_created = datetime.datetime.utcnow().isoformat()

    try:
        # Initalise card object with supplied values
        card = Card(deck_id, time_created, front, back, familiarity)
    # Check for data validation errors
    except ValueError as error:
        # Show user respective validation error
        flash(error)
        return redirect(url_for("cards.add_card"))

    connection = db_connect()

    # Get current number of cards that are in the deck
    current_number_of_cards = (
        connection.execute(
            "SELECT number_of_cards FROM decks WHERE deck_id = ?", (card.deck_id)
        ).fetchone()
    )[0]

    # Create seperate incremented variable for readability reasons
    incremented_number_of_cards = current_number_of_cards + 1

    # Add the new card into the decks
    connection.execute(
        "INSERT INTO cards (deck_id, time_created, front, back, familiarity) VALUES (?, ?, ?, ?, ?)",
        (card.deck_id, card.time_created, card.front, card.back, card.familiarity),
    )
    # Update the number of cards within the deck
    connection.execute(
        "UPDATE decks SET number_of_cards = ? WHERE deck_id = ?",
        (incremented_number_of_cards, card.deck_id),
    )
    connection.commit()
    connection.close()
    # Redirect user to add another card
    return redirect(url_for("cards.add_card"))


@cards.route("/list_cards", methods=["GET"])
def list_cards():
    # Checks if user is logged in or not
    if not session.get("email"):
        # Redirect user to login page
        return redirect(url_for("auth.login"))

    args = request.args
    deck_id = args.get("deck_id")
    deck_name = args.get("deck_name")

    # Check if user supplied a deck of cards to view
    if deck_id is None:
        flash("You need to select a deck")
        # Redirect user to the list of decks
        return redirect(url_for("decks.list_decks"))

    cards = fetch_cards(deck_id)

    # Convert int card familiaritiy values into their text versions
    for card in cards:
        card.familiarity = FAMILIARITY_MAPPINGS[card.familiarity]

    for card in cards:
        # Check if the card text is greater than 30
        if len(card.front) > 30:
            # Trim the card length with ellipses
            card.front = card.front[:30] + "..."
        if len(card.back) > 30:
            card.back = card.back[:30] + "..."

    # Render the list of cards for user supplied deck
    return render_template("list_cards.html", cards=cards, deck=deck_name)


@cards.route("/delete_card", methods=["GET"])
def delete_card():
    # Checks if user is logged in or not
    if not session.get("email"):
        # Redirect user to login page
        return redirect(url_for("auth.login"))

    args = request.args
    card_id = args.get("card_id")

    # Check if user supplied a card to delete
    if card_id is None:
        flash("You need to select a card to delete")
        # Redirect user to their list of decks
        return redirect(url_for("decks.list_decks"))

    # Delete card from database
    delete_card_from_database(str(card_id))

    flash("Card deleted")
    # Redirect user to their list of decks
    return redirect(url_for("decks.list_decks"))


@cards.route("/process_next_card", methods=["POST"])
def process_next_card():
    # Checks if user is logged in or not
    if not session.get("email"):
        # Redirect user to login page
        return redirect(url_for("auth.login"))

    deck_id = request.form.get("deck_id")
    next_card_id = request.form.get("next_card_id")
    current_card_id = request.form.get("current_card_id")
    current_familiarity = int(request.form.get("current_familiarity"))
    familiarity_update = request.form.get("familiarity_update")
    # Handles case of the familiarity values being at either extremes
    new_familiarity = current_familiarity

    # Check conditions of the users familiarity with the card
    if familiarity_update == "known" and current_familiarity < 4:
        # Increase the users familiarity
        new_familiarity = current_familiarity + 1
    elif familiarity_update == "unknown" and current_familiarity > 1:
        # Decrease the users familiarity
        new_familiarity = current_familiarity - 1

    connection = db_connect()
    # Change card familiarity in the database
    connection.execute(
        "UPDATE cards SET familiarity = ? WHERE card_id = ?",
        (new_familiarity, current_card_id),
    )
    connection.commit()
    connection.close()

    # Redirect user to the next card in the deck
    return redirect(url_for("decks.revise_deck", deck_id=deck_id, card_id=next_card_id))
