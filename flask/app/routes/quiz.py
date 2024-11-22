from flask import Blueprint
from flask import request, session
from flask import render_template, url_for, redirect, jsonify
from flask_login import login_required
from flask_login import current_user
from functools import wraps
from app.utils.db import execute_query


bp = Blueprint('quiz', __name__)


def check_authority(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            query = r"SELECT 1 FROM admin WHERE id=%s"
            if execute_query(query, (current_user.id)):
                return func(*args, **kwargs)
            
            query = r"SELECT u_id FROM quizzes WHERE id=%s"
            user_id = rows[0]["u_id"] if (rows:=execute_query(query, (kwargs.get("idx"),))) else ""
            if user_id == current_user.id:
                return func(*args, **kwargs)
        return redirect("/")
    return wrapper


@bp.route("/lists")
@login_required
def quiz_lists():
    subjects = execute_query(r"SELECT id, name FROM subjects")
    if subjects is False:
        return redirect("/")
    
    page = request.args.get("page", 1, type=int)
    keyword = request.args.get("keyword", "", type=str)
    sort_by = request.args.get("sortBy", "DESC", type=str)
    search_by = request.args.get("searchBy", 0, type=int)
    
    # 페이지네이션
    total_pages = 0
    start_page = 0
    end_page = 0
    per_page = 10
    offset = (page - 1) * per_page

    count_query = f"SELECT COUNT(*) num FROM quizzes"
    query = r"SELECT id, u_id, (SELECT name FROM subjects WHERE id=s_id) AS s, question AS q FROM quizzes "
    if search_by == 0:
        condition = f" WHERE question LIKE %s ORDER BY 1 {sort_by}"
        params = (f"%{keyword}%",)
    else:
        condition = f" WHERE question LIKE %s AND s_id=%s ORDER BY 1 {sort_by}"
        params = (f"%{keyword}%", search_by)
    limit = f" LIMIT {per_page} OFFSET {offset}"
    
    total_quizzes = rows[0]["num"] if (rows:=execute_query(count_query+condition, params)) else 0
    total_pages = (total_quizzes + per_page - 1) // per_page
    quizzes = rows if (rows:=execute_query(query+condition+limit, params)) else []
    
    # total_quizzes = rows[0]["num"] if (rows:=execute_query(r"SELECT COUNT(*) num FROM quizzes WHERE question LIKE %s", (f"%{keyword}%",))) else 0
    # total_pages = (total_quizzes + per_page - 1) // per_page

    # quizzes = execute_query(r"SELECT id, u_id, (SELECT name FROM subjects WHERE id=s_id)s, question q FROM quizzes WHERE question LIKE %s ORDER BY 1 DESC LIMIT %s OFFSET %s", (f"%{keyword}%", per_page, offset))

    start_page = max(page - 2, 1)
    end_page = min(page + 2, total_pages)
    
    if (end_page - start_page) < 4:
        if start_page == 1:
            end_page = min(start_page + 4, total_pages)
        elif end_page == total_pages:
            start_page = max(end_page - 4, 1)

    data = {
        "subjects": subjects,
        "quizzes": quizzes,
        "page": page,
        "total_pages": total_pages,
        "start_page": start_page,
        "end_page": end_page,
        "keyword": keyword,
        "sortBy": sort_by,
        "searchBy": search_by
    }
    return render_template("quiz/lists.html", **data)


@bp.route("/view/<idx>")
@login_required
def quiz_view(idx: str):
    query = r"SELECT id, u_id, s_id, (SELECT name FROM subjects WHERE id=s_id)s_name, question q, "
    query += r"answer a, opt1 o1, opt2 o2, opt3 o3, comment c FROM quizzes WHERE id=%s;"
    quiz = rows[0] if (rows:=execute_query(query, (idx,))) else None
    
    if quiz is None:
        return redirect("/quiz/lists")
    return render_template("quiz/view.html", quiz=quiz)


@bp.route("/create", methods=["GET", "POST"])
@login_required
def quiz_create():
    subjects = execute_query(r"SELECT id, name FROM subjects")
    if subjects is False:
        return redirect("/")
    
    if request.method == "POST":
        params = (
            current_user.id,
            request.form.get("quiz-s"),
            request.form.get("quiz-q"),
            request.form.get("quiz-a"),
            request.form.get("quiz-o1"),
            request.form.get("quiz-o2"),
            request.form.get("quiz-o3"),
            request.form.get("quiz-c")
        )
        
        if all(params[-1]) and execute_query(r"INSERT INTO quizzes VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, NOW())", params):
            return jsonify({"status": "S", "message": "문제 등록 성공"})
        return jsonify({"status": "F", "message": "문제 등록 실패"})
        
    return render_template("quiz/create.html", subjects=subjects)


@bp.route("/modify/<idx>", methods=["GET", "POST"])
@login_required
@check_authority
def quiz_modify(idx: int):
    subjects = execute_query(r"SELECT id, name FROM subjects")
    if not subjects:
        return redirect("/")

    query = r"SELECT id, u_id, s_id, (SELECT name FROM subjects WHERE id=s_id)s_name, question q, "
    query += r"answer a, opt1 o1, opt2 o2, opt3 o3, comment c FROM quizzes WHERE id=%s;"
    quiz = rows[0] if (rows:=execute_query(query, (idx,))) else []
    if not quiz:
        return redirect("/")

    if request.method == "POST":
        params = (
            request.form.get("quiz-s"),
            request.form.get("quiz-q"),
            request.form.get("quiz-a"),
            request.form.get("quiz-o1"),
            request.form.get("quiz-o2"),
            request.form.get("quiz-o3"),
            request.form.get("quiz-c"),
            idx
        )

        if execute_query(r"UPDATE quizzes SET s_id=%s, question=%s, answer=%s, opt1=%s, opt2=%s, opt3=%s, comment=%s WHERE id=%s", params):
            return jsonify({"status": "S", "message": "문제 수정 완료"})
        return jsonify({"status": "F", "message": "문제 수정 실패"})
    return render_template("quiz/modify.html", quiz=quiz, subjects=subjects)


@bp.route("/delete/<idx>")
@login_required
@check_authority
def quiz_delete(idx: int):
    if execute_query(r"DELETE FROM quizzes WHERE id=%s", (idx,)):
        return jsonify({"status": "S", "message": "문제 삭제 완료"})
    return jsonify({"status": "F", "message": "문제 삭제 실패"})