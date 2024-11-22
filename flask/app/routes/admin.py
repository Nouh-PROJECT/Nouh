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



@bp.route("/")
@login_required
@check_authority
def admin_get_users():
    page = 1
    total_pages = 0
    per_page = 10
    offset = (page - 1) * per_page
    
    query = f"SELECT * FROM users LIMIT {per_page} OFFSET {offset}"
    users = rows if (rows:=execute_query(query)) else []
    data = {
    }
    
    return jsonify({"status": "S", "data": data})