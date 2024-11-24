from flask import redirect
from flask_login import UserMixin, LoginManager
from app.utils.db import execute_query


class User(UserMixin):
    def __init__(self, id, name, login_id, is_admin, is_subscribe):
        self.id = id
        self.name = name
        self.user_id = login_id
        self.is_admin = is_admin
        self.is_subscribe = is_subscribe
    
    @staticmethod
    def get(user_no):
        query = r"SELECT u.id, u.name, u.login_id, COALESCE(a.id, 0) AS is_admin, COALESCE(s.status, 0) AS is_subscribe"
        query += r" FROM users AS u LEFT JOIN admin AS a ON a.id=u.id LEFT JOIN subscribe AS s ON s.id=u.id WHERE u.id=%s"
        user = rows[0] if (rows:=execute_query(query, (user_no,))) else []
        print(user_no, user)
        if user:
            return User(**user)

    def update_subscribe_status(self):
        self.is_subscribe = rows[0]["status"] if (rows:=execute_query(r"SELECT status FROM subscribe WHERE id = %s", (self.id,))) else 0
        return ""


def register_routes(app):
    from .main import bp as main_bp
    from .admin import bp as admin_bp
    from .member import bp as member_bp
    from .quiz import bp as quiz_bp
    from .exam import bp as exam_bp
    from .board import bp as board_bp
    from .lecture import bp as lecture_bp
    from .chatbot import bp as chatbot_bp
    from .subscribe import bp as subscribe_bp
    from .test import bp as test_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(member_bp, url_prefix='/member')
    app.register_blueprint(quiz_bp, url_prefix='/quiz')
    app.register_blueprint(exam_bp, url_prefix='/exam')
    app.register_blueprint(board_bp, url_prefix='/board')
    app.register_blueprint(lecture_bp, url_prefix='/lecture')
    app.register_blueprint(chatbot_bp, url_prefix='/chatbot')
    app.register_blueprint(subscribe_bp, url_prefix='/subscribe')
    app.register_blueprint(test_bp, url_prefix='/test')


def init_login_manager(app):
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_no):
        return User.get(user_no)

    @login_manager.unauthorized_handler
    def unauthorized():
        return redirect("/")

    return login_manager