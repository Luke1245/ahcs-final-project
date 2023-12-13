import sqlite3
from werkzeug.security import generate_password_hash


class User:
    def __init__(self, email, rawPassword, userID=0):
        self.userID = userID
        self.email = self._validate_email(email)
        self.passwordHash = self._validate_and_hash_password(rawPassword)

    def _validate_and_hash_password(self, rawPassword):
        if len(rawPassword) < 8:
            raise ValueError("Password must be 8 characters or greater")
        elif len(rawPassword) > 72:
            raise ValueError("Password must be less than 72 characters")

        return generate_password_hash(rawPassword)

    def _validate_email(self, email):
        connection = db_connect()
        duplicate_amount = connection.execute(
            "SELECT COUNT(*) FROM users WHERE email = ?", (email,)
        ).fetchone()
        connection.close()

        if duplicate_amount[0] != 0:
            raise ValueError("This email is already registered")
        elif len(email) < 5:
            raise ValueError("Email must be 5 characters or greater")
        elif len(email) > 128:
            raise ValueError("Email must be less than 128 characters")

        return email


class Deck:
    def __init__(self, userID, deckName, numberOfCards=0, deckID=0, newDeck=False):
        self.deckID = deckID
        self.userID = userID
        self.deckName = self._validate_deck_name(deckName, newDeck)
        self.numberOfCards = numberOfCards

    def _validate_deck_name(self, deckName, newDeck):
        if newDeck is True:
            connection = db_connect()
            duplicate_amount = connection.execute(
                "SELECT COUNT(*) FROM decks WHERE deckName = ?", (deckName,)
            ).fetchone()
            connection.close()

            if duplicate_amount[0] != 0:
                raise ValueError("This deck name is already in use")

        elif len(deckName) <= 0:
            raise ValueError("Deck name cannot be empty")
        elif len(deckName) > 50:
            raise ValueError("Deck name must be less than 50 characters")

        return deckName


def fetchDecks(session):
    connection = db_connect()
    email = session.get("email")
    try:
        userID = getUserID(email)
    except ValueError:
        raise ValueError("No users in table")

    decks = connection.execute(
        "SELECT * FROM decks WHERE userID = ? ", (userID,)
    ).fetchall()
    connection.close()

    decks = parseDecks(decks)
    return decks


def parseDecks(decks):
    parsedDecks = []
    for deck in decks:
        parsedDeck = Deck(
            deck["userID"], deck["deckName"], deck["numberOfCards"], deck["deckID"]
        )
        parsedDecks.append(parsedDeck)

    return parsedDecks


def getUserID(email):
    connection = db_connect()
    userID = connection.execute(
        "SELECT userID FROM users WHERE email = ?", (email,)
    ).fetchone()

    if userID is None:
        raise ValueError("No user found")
    else:
        return userID[0]


def db_connect():
    connection = sqlite3.connect("database.db")
    # Allow dirrect access to returned data via name and index
    connection.row_factory = sqlite3.Row
    return connection
