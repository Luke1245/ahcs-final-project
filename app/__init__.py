from flask import Flask
from flask_session import Session
from .auth import auth as auth_blueprint
from .decks import decks as decks_blueprint
from .cards import cards as cards_blueprint
import os
from dotenv import load_dotenv

# Load the env variables file
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")


def create_app():
    app = Flask(__name__)
    # Store sessions on filesystem
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    app.config["SECRET_KEY"] = SECRET_KEY

    # Add site routes
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(decks_blueprint)
    app.register_blueprint(cards_blueprint)

    return app
