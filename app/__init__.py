from flask import Flask
from flask_session import Session
from .auth import auth as auth_blueprint
from .main import main as main_blueprint
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")


def create_app():
    app = Flask(__name__)

    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    app.config["SECRET_KEY"] = SECRET_KEY

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)

    return app
