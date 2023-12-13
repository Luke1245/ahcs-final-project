from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from .tools.utils import User, Deck, db_connect, parseDecks, getUserID
import json

decks = Blueprint("decks", __name__)


@decks.route("/")
def list_decks():
    if not session.get("email"):
        return redirect(url_for("auth.login"))

    connection = db_connect()
    email = session.get("email")
    try: 
        userID = getUserID(email)
    except ValueError:
        return redirect(url_for("auth.login"))
    
    decks = connection.execute(
        "SELECT * FROM decks WHERE userID = ? ", (userID,)
    ).fetchall()
    connection.close()
    decks = parseDecks(decks)

    return render_template("index.html", decks=decks)


@decks.route("/add_deck", methods=["POST"])
def add_deck_post():
    if not session.get("email"):
        return redirect(url_for("auth.login"))

    deckName = (json.loads(request.data))["name"]

    email = session.get("email")
    connection = db_connect()
    userID = (
        connection.execute(
            "SELECT userID FROM users WHERE email = ?", (email,)
        ).fetchone()
    )[0]
    connection.close
    try:
        deck = Deck(userID, deckName)
    except ValueError as error:
        flash(str(error))
        return "Couldn't add deck", 400
    else:
        connection = db_connect()
        connection.execute(
            "INSERT INTO decks (userID, deckName) VALUES (?, ?)",
            (deck.userID, deck.deckName),
        )
        flash("Added new deck")
        connection.commit()
        connection.close()

    return "Added deck"


@decks.route("/add_card", methods=["POST"])
def add_card_post():
    if not session.get("email"):
        return redirect(url_for("auth.login"))

    return redirect(url_for("main.list_decks"))

@decks.route("/delete_deck", methods=["GET"])
def delete_deck():
    if not session.get("email"):
        return redirect(url_for("auth.login"))
    
    args = request.args
    deckID = args.get("deckid")
    email = session.get("email")

    try: 
        userID = getUserID(email)
    except ValueError:
        return redirect(url_for("auth.login"))
    
    connection = db_connect()
    connection.execute("DELETE FROM decks WHERE deckID = ? AND userID = ?", (deckID, userID))
    connection.commit()
    flash("Deleted deck")
    return redirect(url_for("decks.list_decks"))
    
