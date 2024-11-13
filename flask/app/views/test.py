from flask import Blueprint
from flask import render_template, request, session
from flask_login import login_user, current_user
from app.models import User
from app.utils.db import execute_query


bp = Blueprint('test', __name__)


@bp.route("/test01", methods=["GET", "POST"])
def test01():
    login_user(User(1, "게스트", "guest"))
    session["data"] = current_user.name
        
    return render_template("test/testpage01.html")
