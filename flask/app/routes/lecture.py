import os
import string
import secrets
import datetime
import mimetypes
from flask import Blueprint
from flask import request, session
from flask import render_template, url_for, redirect, jsonify, send_file, Response
from flask_login import login_required
from flask_login import current_user
from functools import wraps
from app.utils.db import execute_query


bp = Blueprint('lecture', __name__)


def check_authority(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            if current_user.is_admin or current_user.is_subscribe:
                return func(*args, **kwargs)
        return redirect("/")
    return wrapper


@bp.route("/lists")
@login_required
@check_authority
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


    count_query = f"SELECT COUNT(*) num FROM lectures"
    query = r"SELECT s.name AS subject, l.id, l.title, l.description, l.e_filename FROM lectures l LEFT JOIN subjects s ON l.s_id=s.id "
    if search_by == 0:
        condition = f" WHERE l.title LIKE %s OR l.description LIKE %s ORDER BY 1 {sort_by}"
        params = (f"%{keyword}%", f"%{keyword}%")
    elif search_by == 1:
        condition = f" WHERE l.title LIKE %s ORDER BY 1 {sort_by}"
        params = (f"%{keyword}%",)
    elif search_by == 2:
        condition = f" WHERE l.description LIKE %s ORDER BY 1 {sort_by}"
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


@bp.route("/view/<idx>")
@login_required
@check_authority
def lecture_view(idx: int):
    filename = request.args.get("filename")
    if not filename:
        return "<h1>Bad Request</h1>", 400

    filepath = os.path.join(os.getcwd(), "app", "uploads", filename)

    query = r"SELECT s.name AS subject, l.id, l.title, l.description, l.e_filename FROM lectures l LEFT JOIN subjects s ON l.s_id=s.id WHERE l.id=%s"
    lecture = rows[0] if (rows:=execute_query(query, (idx,))) else []
    if not lecture:
        return redirect(url_for("lecture.lecture_list"))

    data = {
        "lecture": lecture
    }
    return render_template("lecture/view.html", **data)


@bp.route("/view/play_video")
@login_required
@check_authority
def lecture_play_video():
    filename = request.args.get("filename")
    if not filename:
        return "<h1>Bad Request</h1>", 400
    
    file_path = os.path.join(os.getcwd(), "app", "uploads", filename)

    try:
        if os.path.isfile(file_path):
            m, _ = mimetypes.guess_type(file_path)
            with open(file_path, "rb") as f:
                return Response(f.read(), mimetype=m or "application/octet-stream")
    except Exception as e:
        return f"ERROR: {e}", 500



@bp.route("/create", methods=["GET", "POST"])
@login_required
@check_authority
def lecture_create():
    if request.method == "POST":
        subject = request.form.get("subject")
        title = request.form.get("title")
        description = request.form.get("description")
        file = request.files.get("file")

        try:
            chars = string.ascii_letters + string.digits
            o_filename = file.filename
            e_filename = f"{''.join(secrets.choice(chars) for _ in range(20))}.{o_filename.rsplit('.', 1)[1]}"
            save_path = os.path.join(os.getcwd(), "app", "uploads", e_filename)
            file.save(save_path)
        except Exception as e:
            return jsonify({"status": "F", "message": "강의 추가 실패"})
        if not (execute_query(r"INSERT INTO lectures VALUES (NULL, %s, %s, %s, %s, %s)", (subject, title, description, o_filename, e_filename))):
            return jsonify({"status": "F", "message": "강의 추가 실패"})
        return jsonify({"status": "S", "message": "강의 추가 완료"})

    data = {
        "subjects": rows if (rows:=execute_query(r"SELECT id, name FROM subjects")) else []
    }
    return render_template("lecture/create.html", **data)


@bp.route("/modify")
@login_required
@check_authority
def lecture_modify():
    return render_template("lecture/modify.html")



