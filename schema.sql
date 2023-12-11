DROP TABLE IF EXISTS decks;
DROP TABLE IF EXISTS cards;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    userID INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    passwordHash TEXT NOT NULL
);

CREATE TABLE decks (
    deckID INTEGER PRIMARY KEY AUTOINCREMENT,
    userID INTEGER
    timeCreated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deckName TEXT NOT NULL,
    numberOfCards INTEGER NOT NULL DEFAULT 0,

    FOREIGN KEY(userID) REFERENCES users(userID)
);


CREATE TABLE cards (
    cardID INTEGER PRIMARY KEY AUTOINCREMENT,
    deckID INTEGER,
    timeCreated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    front TEXT NOT NULL,
    back TEXT NOT NULL,
    familiarity INTEGER NOT NULL DEFAULT 0,
    
    FOREIGN KEY(deckID) REFERENCES decks(deckID)
);

