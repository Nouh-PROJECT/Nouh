from flask import Flask
from flask_session import Session
from .config import Config
from .utils.db import get_db, close_db
from .routes import register_routes, init_login_manager


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Session(app)

    with app.app_context():
        get_db()

    # Blueprint
    register_routes(app)

    # Flask_login
    init_login_manager(app)

    app.teardown_appcontext(close_db)
    return app
