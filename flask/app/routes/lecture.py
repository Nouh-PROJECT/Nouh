from flask import Blueprint
from flask import request, session
from flask import render_template, url_for, redirect
from flask_login import login_required
from flask_login import current_user
from functools import wraps
from app.utils.db import execute_query


bp = Blueprint('lecture', __name__)


def check_authority(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            query = r"SELECT 1 FROM admin WHERE id=%s"
            if execute_query(query, (current_user.id)):
                return func(*args, **kwargs)
            
            query = r"SELECT u_id FROM board WHERE id=%s"
            rows = execute_query(query, (kwargs.get('idx')))
            if rows and (rows[0]["u_id"] == (current_user.id)):
                return func(*args, **kwargs)
        return redirect("/")
    return wrapper



@bp.route("/create")
@login_required
@check_authority
def lecture_create():
    return json.dumps({"status": "F", "message": "강의 등록에 실패했습니다."})


@bp.route("/modify")
@login_required
@check_authority
def lecture_modify():
    return json.dumps({"status": "F", "message": "강의 등록에 실패했습니다."})


@bp.route("/lists")
@login_required
@check_authority
def lecture_lists():
    return render_template("lecture/lists.html")


