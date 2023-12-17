import sqlite3
from werkzeug.security import generate_password_hash

FAMILIARITY_MAPPINGS = {1: "Unfamiliar", 2: "Recognised", 3: "Familiar", 4: "Memorised"}


class User:
    def __init__(self, email, raw_password, user_id=0):
        self.user_id = user_id
        self.email = self._validate_email(email)
        self.password_hash = self._validate_and_hash_password(raw_password)

    def _validate_and_hash_password(self, raw_password):
        if len(raw_password) < 8:
            raise ValueError("Password must be 8 characters or greater")
        elif len(raw_password) > 72:
            raise ValueError("Password must be less than 72 characters")

        return generate_password_hash(raw_password)

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
    def __init__(
        self, user_id, deck_name, number_of_cards=0, deck_id=0, new_deck=False
    ):
        self.deck_id = deck_id
        self.user_id = user_id
        self.deck_name = self._validate_deck_name(deck_name, new_deck)
        self.number_of_cards = number_of_cards

    def _validate_deck_name(self, deck_name, new_deck):
        if new_deck is True:
            connection = db_connect()
            duplicate_amount = connection.execute(
                "SELECT COUNT(*) FROM decks WHERE deck_name = ? AND user_id = ?", (deck_name, self.user_id)
            ).fetchone()
            connection.close()

            if duplicate_amount[0] != 0:
                raise ValueError("This deck name is already in use")

        elif len(deck_name) <= 0:
            raise ValueError("Deck name cannot be empty")
        elif len(deck_name) > 50:
            raise ValueError("Deck name must be less than 50 characters")

        return deck_name


class Card:
    def __init__(self, deck_id, time_created, front, back, familiarity, card_id=0):
        self.card_id = card_id
        self.deck_id = self._validate_deck_id(deck_id)
        self.time_created = time_created
        self.front = self._validate_text(front)
        self.back = self._validate_text(back)
        self.familiarity = self._validate_familiarity(familiarity)

    def _validate_deck_id(self, deck_id):
        if deck_id is None:
            raise ValueError("You must choose a deck")

        return deck_id

    def _validate_text(self, text):
        if len(text) <= 0:
            raise ValueError("Card sides cannot be empty")
        elif len(text) > 2000:
            raise ValueError("Card sides must be less than 2000 characters")

        return text

    def _validate_familiarity(self, familiarity):
        for x in FAMILIARITY_MAPPINGS:
            if x == familiarity:
                return familiarity

        raise ValueError("Familiarity must be a valid value")


def fetch_decks(session):
    connection = db_connect()
    email = session.get("email")
    try:
        user_id = get_user_id(email)
    except ValueError:
        raise ValueError("No users in table")

    decks = connection.execute(
        "SELECT * FROM decks WHERE user_id = ? ", (user_id,)
    ).fetchall()
    connection.close()

    parsed_decks = []
    for deck in decks:
        parsed_deck = Deck(
            int(deck["user_id"]),
            deck["deck_name"],
            int(deck["number_of_cards"]),
            int(deck["deck_id"]),
        )
        parsed_decks.append(parsed_deck)

    return parsed_decks


def fetch_cards(deck_id):
    connection = db_connect()

    cards = connection.execute(
        "SELECT * FROM cards WHERE deck_id = ?", (deck_id,)
    ).fetchall()
    connection.close()

    parsed_cards = []
    for card in cards:
        parsed_card = Card(
            int(card["deck_id"]),
            card["time_created"],
            card["front"],
            card["back"],
            int(card["familiarity"]),
            int(card["card_id"]),
        )
        parsed_cards.append(parsed_card)

    return parsed_cards


def delete_card_from_database(card_id):
    connection = db_connect()
    deck_id = (
        connection.execute(
            "SELECT deck_id FROM cards WHERE card_id = ?", (card_id,)
        ).fetchone()
    )[0]

    current_number_of_cards = (
        connection.execute(
            "SELECT number_of_cards FROM decks WHERE deck_id = ?", (deck_id,)
        ).fetchone()
    )[0]
    decremented_number_of_cards = current_number_of_cards - 1

    connection.execute(
        "UPDATE decks SET number_of_cards = ? WHERE deck_id = ?",
        (decremented_number_of_cards, deck_id),
    )

    connection.execute("DELETE FROM cards WHERE card_id = ?", (card_id,))
    connection.commit()
    connection.close()


def get_user_id(email):
    connection = db_connect()
    user_id = connection.execute(
        "SELECT user_id FROM users WHERE email = ?", (email,)
    ).fetchone()

    if user_id is None:
        raise ValueError("No user found")
    else:
        return user_id[0]


def db_connect():
    connection = sqlite3.connect("database.db")
    # Allow dirrect access to returned data via name and index
    connection.row_factory = sqlite3.Row
    return connection
