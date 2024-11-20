import os
import string
import secrets
import datetime
from flask import Blueprint
from flask import request, session
from flask import render_template, url_for, redirect, jsonify
from flask_login import login_required
from flask_login import current_user
from functools import wraps
from app.utils.db import execute_query
from bs4 import BeautifulSoup


bp = Blueprint('board', __name__)


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



# CASE WHEN (1=1) THEN 1 ELSE (SELECT 1 UNION SELECT 2) END
# CASE WHEN (1=2) THEN 1 ELSE (SELECT 1 UNION SELECT 2) END
@bp.route("/lists")
def board_lists():
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

    count_query = f"SELECT COUNT(*) num FROM board"
    query = r"SELECT id, (SELECT name FROM users WHERE id=u_id) AS writer, title, content, DATE_FORMAT(created_at, '%%Y-%%m-%%d') AS created_at FROM board "
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
    
    total_posts = rows[0]["num"] if (rows:=execute_query(count_query+condition, params)) else 0
    total_pages = (total_posts + per_page - 1) // per_page
    posts = rows if (rows:=execute_query(query+condition+limit, params)) else []

    start_page = max(page - 2, 1)
    end_page = min(page + 2, total_pages)

    if (end_page - start_page) < 4:
        if start_page == 1:
            end_page = min(start_page + 4, total_pages)
        elif end_page == total_pages:
            start_page = max(end_page - 4, 1)

    data = {
        "posts": posts,
        "page": page,
        "total_pages": total_pages,
        "start_page": start_page,
        "end_page": end_page
    }
        
    return render_template("board/lists.html", **data)


@bp.route("/write", methods=["GET", "POST"])
def board_write():
    if request.method == "POST":
        u_id = current_user.id
        title = request.form.get("title", "", type=str)
        content = request.form.get("content", "", type=str)
        file = request.files.get("file")
        f_id = -1
        
        if not title:
            return jsonify({"status": "F", "message": "제목을 입력해주세요!"})
        if not content:
            return jsonify({"status": "F", "message": "내용을 입력해주세요!"})
        if file and file.filename:
            try:
                chars = string.ascii_letters + string.digits
                old_filename = file.filename
                new_filename = f"{''.join(secrets.choice(chars) for _ in range(20))}.{old_filename.rsplit('.', 1)[1]}"
                save_path = os.path.join(os.getcwd(), "app", "uploads", new_filename)
                file.save(save_path)
            except Exception as e:
                return jsonify({"status": "F", "message": "게시글 작성 실패"})

            if not (f_id:=execute_query(r"INSERT INTO yfile VALUES (NULL, %s, %s)", (old_filename, new_filename))):
                return jsonify({"status": "F", "message": "게시글 작성 실패"})

        soup = BeautifulSoup(content, "html.parser")
        for div in soup.find_all("div"):
            div.decompose()
        content = soup.prettify()

        if not execute_query(r"INSERT INTO board VALUES (NULL, %s, %s, %s, %s, NOW())", (u_id, title, content, None if f_id < 0 else f_id)):
            return jsonify({"status": "F", "message": "게시글 작성 실패"})
        return jsonify({"status": "S", "message": "게시글 작성 완료!"})

    return render_template("board/write.html")


@bp.route("/view/<idx>")
def board_view(idx: int):
    query = r"SELECT b.id, b.u_id, (SELECT name FROM users WHERE id=u_id) AS writer, b.title, b.content, b.created_at, "
    query += r"f.old_filename, f.new_filename FROM board AS b LEFT JOIN yfile AS f ON b.f_id=f.id WHERE b.id=%s"
    post = rows[0] if (rows:=execute_query(query, (idx,))) else None
    
    if post is None:
        return redirect(url_for("board.board_lists"))
    return render_template("board/view.html", post=post)


@bp.route("/modify/<idx>")
def board_modify(idx: int):
    query = r"SELECT b.id, b.u_id, (SELECT name FROM users WHERE id=u_id) AS writer, b.title, b.content, b.created_at, "
    query += r"f.old_filename, f.new_filename FROM board AS b LEFT JOIN yfile AS f ON b.f_id=f.id WHERE b.id=%s"
    post = rows[0] if (rows:=execute_query(query, (idx,))) else None

    if post is None:
        return redirect(url_for("board.board_lists"))
    return render_template("board/modify.html", post=post)


