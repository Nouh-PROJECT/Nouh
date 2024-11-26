from flask import Blueprint
from flask import request, session
from flask import render_template, url_for, redirect, jsonify
from flask_login import login_required
from flask_login import current_user
from functools import wraps
from app.utils.db import execute_query


bp = Blueprint('admin', __name__)


def check_authority(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            query = r"SELECT 1 FROM admin WHERE id=%s"
            if execute_query(query, (current_user.id)):
                return func(*args, **kwargs)
        return redirect("/")
    return wrapper


@bp.route("/")
@login_required
@check_authority
def index():
    return render_template("admin/index.html")



@bp.route("/api/get_users")
@login_required
@check_authority
def admin_get_users():
    try:
        query = f"SELECT * FROM users"
        users = rows if (rows:=execute_query(query)) else []
        return jsonify(users)
    except Exception as e:
        return jsonify({"status": "F", "message": str(e), "users": []})


@bp.route("/api/get_subscribe_request")
@login_required
@check_authority
def admin_get_subscribe_request():
    try:
        query = r"SELECT id, (SELECT login_id FROM users WHERE id=subscribe.id)login_id, (SELECT name FROM users WHERE id=subscribe.id)name, DATE_FORMAT(expired_at, '%Y-%m-%d')expired_at FROM subscribe WHERE status=1"
        waiting = rows if (rows:=execute_query(query)) else []
        return jsonify(waiting)
    except Exception as e:
        return jsonify({"status": "F", "message": str(e), "users": []})


@bp.route("/get-data/dashboard")
@login_required
@check_authority
def admin_dashboard():
    try:
        query = r"SELECT t.status, COALESCE(COUNT(s.id), 0) AS num FROM "
        query += r"(SELECT 0 AS status UNION ALL SELECT 1 UNION ALL SELECT 2) AS t "
        query += r"LEFT JOIN subscribe s ON s.status = t.status GROUP BY t.status"
        
        data = {
            "num_of_users": rows[0]["num"] if (rows:=execute_query(r"SELECT COUNT(*) AS num FROM users")) else 0,
            "num_of_quizzes": rows[0]["num"] if (rows:=execute_query(r"SELECT COUNT(*) AS num FROM quizzes")) else 0,
            "num_of_subjects": rows[0]["num"] if (rows:=execute_query(r"SELECT COUNT(*) AS num FROM subjects")) else 0,
            "subscribe_info": rows if (rows:=execute_query(query)) else []
        }
        return jsonify({"status": "S", "message": "데이터 로딩 완료", "data": data})
    except Exception as e:
        return jsonify({"status": "F", "messasge": str(e)})


# @bp.route("/api/")
# @login_required
# @check_authority
# def admin_