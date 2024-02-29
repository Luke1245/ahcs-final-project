import sqlite3
from werkzeug.security import generate_password_hash

# Mapping of integer familiarity values to human readable text values
FAMILIARITY_MAPPINGS = {1: "Unfamiliar", 2: "Recognised", 3: "Familiar", 4: "Memorised"}


class User:
    def __init__(self, email, raw_password, user_id=0):
        self._user_id = user_id
        self._email = self._validate_email(email)
        self._password_hash = self._validate_and_hash_password(raw_password)

    def _validate_and_hash_password(self, raw_password):
        if len(raw_password) < 8:
            raise ValueError("Password must be 8 characters or greater")
        elif len(raw_password) > 72:
            raise ValueError("Password must be less than 72 characters")

        # Hash password using werkzueg security
        return generate_password_hash(raw_password)

    def _validate_email(self, email):
        connection = db_connect()
        # Retrieve amount of user records with current email in database
        duplicate_amount = connection.execute(
            "SELECT COUNT(*) FROM users WHERE email = ?", (email,)
        ).fetchone()
        connection.close()

        # If duplicate_amount is not 0 then this email is already in use
        if duplicate_amount[0] != 0:
            raise ValueError("This email is already registered")
        elif len(email) < 5:
            raise ValueError("Email must be 5 characters or greater")
        elif len(email) > 128:
            raise ValueError("Email must be less than 128 characters")

        return email

    def get_email(self):
        return self._email

    def get_password_hash(self):
        return self._password_hash


class Deck:
    def __init__(
        self, user_id, deck_name, number_of_cards=0, deck_id=0, new_deck=False
    ):
        self._deck_id = deck_id
        self._user_id = user_id
        self._deck_name = self._validate_deck_name(deck_name, new_deck)
        self._number_of_cards = number_of_cards

    def _validate_deck_name(self, deck_name, new_deck):
        # Only check if duplicate if class is being used to add a new deck
        if new_deck is True:
            connection = db_connect()
            # Retrieve amount of deck records with current deck name in database
            duplicate_amount = connection.execute(
                "SELECT COUNT(*) FROM decks WHERE deck_name = ? AND user_id = ?",
                (deck_name, self.get_user_id()),
            ).fetchone()
            connection.close()

            # If duplicate_amount is not 0 then this deck name is already in use
            if duplicate_amount[0] != 0:
                raise ValueError("This deck name is already in use")

        elif len(deck_name) <= 0:
            raise ValueError("Deck name cannot be empty")
        elif len(deck_name) > 50:
            raise ValueError("Deck name must be less than 50 characters")

        return deck_name

    def get_deck_id(self):
        return self._deck_id

    def get_user_id(self):
        return self._user_id

    def get_deck_name(self):
        return self._deck_name

    def get_number_of_cards(self):
        return self._number_of_cards


class Card:
    def __init__(self, deck_id, time_created, front, back, familiarity, card_id=0):
        self._card_id = card_id
        self._deck_id = self._validate_deck_id(deck_id)
        self._time_created = time_created
        self._front = self._validate_text(front)
        self._back = self._validate_text(back)
        self._familiarity = self._validate_familiarity(familiarity)

    def _validate_deck_id(self, deck_id):
        # Check if deck_id is supplied
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
        # Make sure familiarity is a valid value from 1 - 4
        for x in FAMILIARITY_MAPPINGS:
            if x == familiarity:
                return familiarity

        raise ValueError("Familiarity must be a valid value")

    def get_card_id(self):
        return self._card_id

    def get_deck_id(self):
        return self._deck_id

    def get_time_created(self):
        return self._time_created

    def get_front(self):
        return self._front

    def get_back(self):
        return self._back

    def get_familiarity(self):
        return self._familiarity

    def set_familiarity(self, familiarity):
        self._familiarity = familiarity

    def set_front(self, front):
        self._front = self._validate_text(front)

    def set_back(self, back):
        self._back = self._validate_text(back)


def fetch_decks(session):
    connection = db_connect()
    email = session.get("email")
    try:
        # Fetch user_id via users email
        user_id = get_user_id_by_email(email)
    except ValueError:
        raise ValueError("No users in found")

    # Get all decks that the user owns
    decks = connection.execute(
        "SELECT * FROM decks WHERE user_id = ? ", (user_id,)
    ).fetchall()
    connection.close()

    # Initalise empty array for the parsed decks
    parsed_decks = []

    # Convert each database deck entry into a deck class object
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

    # Retrieve all cards for given deck_id
    cards = connection.execute(
        "SELECT * FROM cards WHERE deck_id = ?", (deck_id,)
    ).fetchall()
    connection.close()

    # Initalise empty array for parsed_cards
    parsed_cards = []

    # Convert each database card entry into a card class object
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


def sort_cards(cards):
    # Bubble sort
    n = len(cards)
    swapped = False

    for i in range(n - 1):
        for j in range(0, n - i - 1):
            if cards[j].get_familiarity() > cards[j + 1].get_familiarity():
                swapped = True
                tmp = cards[j]

                cards[j] = cards[j + 1]
                cards[j + 1] = tmp

        if not swapped:
            return cards

    return cards


def delete_card_from_database(card_id):
    connection = db_connect()
    # Fetch deck_id for the given card to change amount of cards in deck later
    deck_id = (
        connection.execute(
            "SELECT deck_id FROM cards WHERE card_id = ?", (card_id,)
        ).fetchone()
    )[0]

    # Retrieve current number of cards in deck
    current_number_of_cards = (
        connection.execute(
            "SELECT number_of_cards FROM decks WHERE deck_id = ?", (deck_id,)
        ).fetchone()
    )[0]
    # Create seperate decremented variable for readability reasons
    decremented_number_of_cards = current_number_of_cards - 1

    # Update the number of cards within the deck
    connection.execute(
        "UPDATE decks SET number_of_cards = ? WHERE deck_id = ?",
        (decremented_number_of_cards, deck_id),
    )

    # Delete card from database
    connection.execute("DELETE FROM cards WHERE card_id = ?", (card_id,))
    connection.commit()
    connection.close()


def get_user_id_by_email(email):
    connection = db_connect()
    # Retrieve user_id via users email
    user_id = connection.execute(
        "SELECT user_id FROM users WHERE email = ?", (email,)
    ).fetchone()

    # Check if a user is registered with this email
    if user_id is None:
        raise ValueError("No user found")
    else:
        return user_id[0]


def db_connect():
    # Use sqlite to connect to SQ(Lite) database file
    connection = sqlite3.connect("database.db")
    # Allow dirrect access to returned data via name and index
    connection.row_factory = sqlite3.Row
    return connection
