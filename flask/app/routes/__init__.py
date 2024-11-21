from flask import redirect
from flask_login import UserMixin, LoginManager
from app.utils.db import execute_query


class User(UserMixin):
    def __init__(self, id, name, user_id, is_admin):
        self.id = id
        self.name = name
        self.user_id = user_id
        self.is_admin = is_admin


def register_routes(app):
    from .main import bp as main_bp
    from .admin import bp as admin_bp
    from .member import bp as member_bp
    from .quiz import bp as quiz_bp
    from .exam import bp as exam_bp
    from .board import bp as board_bp
    from .lecture import bp as lecture_bp
    from .chatbot import bp as chatbot_bp
    from .test import bp as test_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(member_bp, url_prefix='/member')
    app.register_blueprint(quiz_bp, url_prefix='/quiz')
    app.register_blueprint(exam_bp, url_prefix='/exam')
    app.register_blueprint(board_bp, url_prefix='/board')
    app.register_blueprint(lecture_bp, url_prefix='/lecture')
    app.register_blueprint(chatbot_bp, url_prefix='/chatbot')
    app.register_blueprint(test_bp, url_prefix='/test')


def init_login_manager(app):
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_no):
        query = r"SELECT id, name, login_id, (SELECT 1 FROM admin WHERE admin.id=users.id)is_admin FROM users WHERE id=%s"
        user = rows[0] if (rows := execute_query(query, (user_no,))) else []
        if user:
            return User(user["id"], user["name"], user["login_id"], user["is_admin"])
        return None

    @login_manager.unauthorized_handler
    def unauthorized():
        return redirect("/")

    return login_manager