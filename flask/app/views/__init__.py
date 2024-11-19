from flask import Blueprint


def register_routes(app):
    from .main import bp as main_bp
    from .auth import bp as auth_bp
    from .quiz import bp as quiz_bp
    from .exam import bp as exam_bp
    from .chatbot import bp as chatbot_bp
    from .test import bp as test_bp
    from .lecture import bp as lecture_bp
    from .board import bp as board_bp
    from .subscribe import bp as subscribe_bp
    from .admin import bp as admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(test_bp)
    app.register_blueprint(chatbot_bp, url_prefix='/chatbot')
    app.register_blueprint(lecture_bp)
    app.register_blueprint(board_bp, url_prefix='/board')
    app.register_blueprint(quiz_bp, url_prefix='/quiz')
    app.register_blueprint(exam_bp, url_prefix='/exam')
    app.register_blueprint(subscribe_bp, url_prefix='/subscribe')
    app.register_blueprint(admin_bp, url_prefix='/admin')
