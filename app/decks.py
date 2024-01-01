from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from .helpers import (
    Deck,
    db_connect,
    fetch_decks,
    get_user_id,
    fetch_cards,
    sort_cards,
    delete_card_from_database,
)
import json

decks = Blueprint("decks", __name__)


@decks.route("/")
def list_decks():
    # Checks if user is logged in or not
    if not session.get("email"):
        # Redirect user to login page
        return redirect(url_for("auth.login"))

    try:
        # Retrieve the users decks
        decks = fetch_decks(session)
    except ValueError:
        # Redirect user to login page if error in deck fetching
        return redirect(url_for("auth.login"))

    # Render list decks index page with the users decks
    return render_template("index.html", decks=decks)


@decks.route("/add_deck", methods=["POST"])
def add_deck_post():
    # Checks if user is logged in or not
    if not session.get("email"):
        # Redirect user to login page
        return redirect(url_for("auth.login"))

    # Retrieve deck name from add_deck() js function
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
        # Initalise deck object with duplicate deck name validation
        deck = Deck(user_id, deck_name, new_deck=True)
    except ValueError as error:
        # Display error to user
        flash(str(error))
        return "Error adding deck to database", 400
    else:
        connection = db_connect()
        # Add deck to database
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
    # Checks if user is logged in or not
    if not session.get("email"):
        # Redirect user to login page
        return redirect(url_for("auth.login"))

    args = request.args
    deck_id = args.get("deck_id")
    email = session.get("email")

    try:
        # Fetch user_id from databse via user email
        user_id = get_user_id(email)
    except ValueError:
        # Redirect user to login page
        return redirect(url_for("auth.login"))

    # Obtain array of card objects
    cards_to_delete = fetch_cards(deck_id)
    for card in cards_to_delete:
        # Delete current card from database, to avoid stranded data
        delete_card_from_database(card.card_id)

    connection = db_connect()
    # Finally, remove deck from database
    connection.execute(
        "DELETE FROM decks WHERE deck_id = ? AND user_id = ?", (deck_id, user_id)
    )
    connection.commit()
    flash("Deck deleted")
    return redirect(url_for("decks.list_decks"))


@decks.route("/revise_deck", methods=["GET"])
def revise_deck():
    # Checks if user is logged in or not
    if not session.get("email"):
        # Redirect user to login page
        return redirect(url_for("auth.login"))

    args = request.args
    deck_id = args.get("deck_id")
    current_card_id = args.get("card_id")

    # Check if card_id is supplied
    if current_card_id is not None:
        # Convert card_id to integer
        current_card_id = int(current_card_id)

    # -1 refers to the end of the deck, check if user has finished the deck
    if current_card_id == -1:
        flash("Deck reviewed")
        # Redirect user to the list of decks
        return redirect(url_for("decks.list_decks"))

    # Fetch cards using deck_id
    cards = fetch_cards(deck_id)
    # Use bubble sort algorithim to sort cards
    cards = sort_cards(cards)

    current_card = None

    # No card_id supplied means start of deck
    if current_card_id is None:
        # Set the current card to the least familiar card
        current_card = cards[0]
    else:
        # Find card within array of cards
        for card in cards:
            if card.card_id == current_card_id:
                current_card = card

    # If below loop doesn't find value, then deck is finished
    next_card_id = -1

    for i in range(len(cards)):
        # Locate current card within array
        if cards[i].card_id == current_card.card_id:
            try:
                # Set next_card_id to card after current card
                next_card_id = cards[i + 1].card_id
            # Handles end of deck
            except IndexError:
                break

    # Render the card to the user
    return render_template(
        "revise_deck.html", card=current_card, next_card_id=next_card_id
    )
