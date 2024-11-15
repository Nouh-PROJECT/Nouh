from flask import Flask, redirect
from flask_login import LoginManager
from flask_session import Session
from .models import User
from .views import register_routes
from .utils.db import *
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    Session(app)

    with app.app_context():
        get_db()

    # Blueprint
    register_routes(app)

    # flask_login
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_no):
        results = execute_query(r"SELECT * FROM users WHERE id=%s", (user_no,))
        if results:
            user = results[0]
            return User(user['id'], user['name'], user['login_id'])
        return None
    
    @login_manager.unauthorized_handler
    def unauthorized():
        return redirect("/")

    CORS(app)

    app.teardown_appcontext(close_db)

    return app
