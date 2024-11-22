import os
import json
from flask import Blueprint
from flask import request, session
from flask import render_template, url_for, redirect, jsonify
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
        return redirect("/")
    return wrapper


@bp.route("/lists")
@login_required
def lecture_lists():
    subjects = execute_query(r"SELECT id, name FROM subjects")
    if subjects is False:
        return redirect("/")
    
    page = request.args.get("page", 1, type=int)
    keyword = request.args.get("keyword", "", type=str)
    sort_by = request.args.get("sortBy", "DESC", type=str)
    search_by = request.args.get("searchBy", 0, type=int)

    # 페이지네이션
    total_pages = 0 # 전체 게시글 수
    start_page = 0  # 표시할 첫번째 페이지
    end_page = 0    # 표시할 마지막 페이지
    per_page = 10   # 한 페이지에 표시할 게시글 수
    offset = (page - 1) * per_page # 페이지 오프셋

    count_query = f"SELECT COUNT(*) num FROM lecture"
    query = r"SELECT id, (SELECT name FROM users WHERE id=u_id) AS writer, title, content, DATE_FORMAT(created_at, '%%Y-%%m-%%d') AS created_at FROM lecture "
    if search_by == 0:
        condition = f" WHERE title LIKE %s OR content LIKE %s ORDER BY 1 {sort_by}"
        params = (f"%{keyword}%", f"%{keyword}%")
    elif search_by == 1:
        condition = f" WHERE title LIKE %s ORDER BY 1 {sort_by}"
        params = (f"%{keyword}%",)
    elif search_by == 2:
        condition = f" WHERE content LIKE %s ORDER BY 1 {sort_by}"
        params = (f"%{keyword}%",)
    limit = f" LIMIT {per_page} OFFSET {offset}"
    
    total_lectures = rows[0]["num"] if (rows:=execute_query(count_query+condition, params)) else 0
    total_pages = (total_lectures + per_page - 1) // per_page
    lectures = rows if (rows:=execute_query(query+condition+limit, params)) else []

    start_page = max(page - 2, 1)
    end_page = min(page + 2, total_pages)

    if (end_page - start_page) < 4:
        if start_page == 1:
            end_page = min(start_page + 4, total_pages)
        elif end_page == total_pages:
            start_page = max(end_page - 4, 1)

    data = {
        "subjects": subjects,
        "lectures": lectures,
        "page": page,
        "total_pages": total_pages,
        "start_page": start_page,
        "end_page": end_page
    }
    return render_template("lecture/lists.html", **data)


@bp.route("/view")
@login_required
def lecture_view():
    return render_template("lecture/view.html")


@bp.route("/create")
@login_required
@check_authority
def lecture_create():
    
    return jsonify({"status": "F", "message": "강의 등록에 실패했습니다."})


@bp.route("/modify")
@login_required
@check_authority
def lecture_modify():
    return jsonify({"status": "F", "message": "강의 등록에 실패했습니다."})



