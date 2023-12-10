import sqlite3

def db_connect():
    connection = sqlite3.connect('database.db')
    # Allow dirrect access to returned data via name and index
    connection.row_factory = sqlite3.Row
    return connection