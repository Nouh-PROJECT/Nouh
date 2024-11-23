from flask import Blueprint
from flask import request, session
from flask import render_template, url_for, redirect, jsonify
from flask_login import login_required
from flask_login import current_user
from functools import wraps
from app.utils.db import execute_query


bp = Blueprint('subscribe', __name__)

def check_authority(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            if (current_user.is_admin or (session["is_subscribe"] == 2)):
                return func(*args, **kwargs)
        return redirect("/")
    return wrapper


@bp.route("/")
@login_required
def index():
    user = rows[0] if (rows:=execute_query(r"SELECT * FROM users WHERE id=%s", (current_user.id,))) else []
    return render_template("subscribe/index.html", user=user)


@bp.route("/popup")
@login_required
def subscribe_popup():
    return render_template("subscribe/popup.html")


@bp.route("/result")
@login_required
def subscribe_result():
    user = rows[0] if (rows:=execute_query(r"SELECT * FROM subscribe WHERE id=%s", (current_user.id,))) else []
    if not user:
        execute_query(r"INSERT INTO subscribe VALUES (%s, 1, NULL)", (current_user.id,))
    else:
        execute_query(r"UPDATE subscribe SET status=1 WHERE id=%s", (current_user.id,))
    session["is_subscribe"] = 1
    return render_template("subscribe/result.html")


@bp.route("/api/add/<user_id>")
@login_required
@check_authority
def subscribe_add(user_id: int):
    user = rows[0] if (rows:=execute_query(r"SELECT * FROM subscribe WHERE id=%s", (user_id,))) else []
    if not user:
        if (x:=execute_query(r"INSERT INTO subscribe VALUES (%s, 2, DATE_ADD(NOW(), INTERVAL 1 MONTH))", (user_id,))):
            return jsonify({"status": "F", "message": f"구독 실패{x}"})
    else:
        if not (execute_query(r"UPDATE subscribe SET status=2, expired_at=DATE_ADD(NOW(), INTERVAL 1 MONTH) WHERE id=%s", (user_id,))):
            return jsonify({"status": "F", "message": "구독 실패"})
    session['is_subscribe'] = 2
    return jsonify({"status": "S", "message": "구독 완료"})


@bp.route("/api/remove/<user_id>")
@login_required
@check_authority
def subscribe_remove(user_id: int):
    query = r"DELETE FROM subscribe WHERE id=%s"
    if execute_query(query, (user_id,)):
        session['is_subscribe'] = 0
        return jsonify({"status": "S", "message": "구독 해제"})
    return jsonify({"status": "F", "message": "구독 해제 실패"})

