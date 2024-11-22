import os
import string
import secrets
import datetime
from flask import Blueprint
from flask import request, session
from flask import render_template, url_for, redirect, jsonify, send_file
from flask_login import login_required
from flask_login import current_user
from functools import wraps
from app.utils.db import execute_query


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



# soryBy SQL Injection
# (CASE WHEN (1=1) THEN 1 ELSE (SELECT 1 UNION SELECT 2) END)
# (CASE WHEN (1=2) THEN 1 ELSE (SELECT 1 UNION SELECT 2) END)
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


@bp.route("/download/<filename>")
def board_download(filename: str):
    query = r"SELECT o_filename FROM files WHERE e_filename=%s"
    file = rows[0] if (rows:=execute_query(query, (filename,))) else []
    file_path = os.path.join(os.getcwd(), "app", "uploads", filename)
    if os.path.isfile(file_path):
        return send_file(file_path, as_attachment=True, download_name=file["o_filename"])
    

@bp.route("/view/<idx>")
def board_view(idx: int):
    query = r"SELECT b.id, b.u_id, (SELECT name FROM users WHERE id=b.u_id) AS writer, b.title, b.content, b.created_at, "
    query += r"f.o_filename, f.e_filename FROM board AS b LEFT JOIN files AS f ON b.id=f.b_id WHERE b.id=%s"
    post = rows[0] if (rows:=execute_query(query, (idx,))) else None
    
    if post is None:
        return redirect(url_for("board.board_lists"))
    return render_template("board/view.html", post=post)


@bp.route("/write", methods=["GET", "POST"])
@login_required
def board_write():
    if request.method == "POST":
        # 작성자 아이디
        u_id = current_user.id
        # POST로 전송된 데이터(제목, 내용, 파일)
        title = request.form.get("title", "", type=str)
        content = request.form.get("content", "", type=str)
        file = request.files.get("file")
        
        # 입력값 검증
        if not title:
            return jsonify({"status": "F", "message": "제목을 입력해주세요!"})
        if not content:
            return jsonify({"status": "F", "message": "내용을 입력해주세요!"})
        if not (b_id:=execute_query(r"INSERT INTO board VALUES (NULL, %s, %s, %s, NOW())", (u_id, title, content))):
            return jsonify({"status": "F", "message": "게시글 작성 실패"})
        # 파일이 있는 경우
        if file and file.filename:
            try:
                # 파일 이름이 겹치지 않도록 하는 작업
                # 20글자의 영어 대소문자와 숫자로 이루어진 파일 이름으로 저장
                chars = string.ascii_letters + string.digits
                o_filename = file.filename
                e_filename = f"{''.join(secrets.choice(chars) for _ in range(20))}.{o_filename.rsplit('.', 1)[1]}"
                save_path = os.path.join(os.getcwd(), "app", "uploads", e_filename)
                file.save(save_path)
            except Exception as e:
                return jsonify({"status": "F", "message": "게시글 작성 실패"})
            if not (execute_query(r"INSERT INTO files VALUES (NULL, %s, %s, %s)", (b_id, o_filename, e_filename))):
                return jsonify({"status": "F", "message": "게시글 작성 실패"})
        return jsonify({"status": "S", "message": "게시글 작성 완료!"})

    return render_template("board/write.html")


@bp.route("/modify/<idx>", methods=["GET", "POST"])
@login_required
@check_authority
def board_modify(idx: int):
    query = r"SELECT b.id, b.u_id, (SELECT name FROM users WHERE id=b.u_id) AS writer, b.title, b.content, b.created_at, "
    query += r"f.o_filename, f.e_filename FROM board AS b LEFT JOIN files AS f ON b.id=f.b_id WHERE b.id=%s"
    post = rows[0] if (rows:=execute_query(query, (idx,))) else None

    if post is None:
        return redirect(url_for("board.board_lists"))

    if request.method == "POST":
        # 작성자 아이디
        u_id = current_user.id
        
        # POST 요청받은 데이터(제목, 내용, 파일)
        title = request.form.get("title", "", type=str)
        content = request.form.get("content", "", type=str)
        file = request.files.get("file")
        
        # 입력값 검증
        if not title:
            return jsonify({"status": "F", "message": "제목을 입력해주세요!"})
        if not content:
            return jsonify({"status": "F", "message": "내용을 입력해주세요!"})
        if not (b_id:=execute_query(r"UPDATE board SET title=%s, content=%s WHERE id=%s", (title, content, idx))):
            return jsonify({"status": "F", "message": "게시글 수정 실패"})

        # 새로운 파일이 등록된 경우
        if file and file.filename:
            try:
                # 기존 파일 삭제
                query = r"SELECT e_filename FROM files WHERE b_id=%s"
                if (old_file := rows[0]["e_filename"] if execute_query(query, (idx,)) else []):
                    file_path = os.path.join(os.getcwd(), "app", "uploads", old_file)
                    # 실제 파일 삭제
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    # 데이터베이스 정보 삭제
                    if not execute_query(r"DELETE FROM files WHERE b_id=%s", (idx,)):
                        return jsonify({"status": "F", "message": "게시글 수정 실패"})
                        

                # 파일 이름이 겹치는 경우를 막기 위한 작업
                # 20글자의 영어 대소문자와 숫자로 이름을 구성하여 파일 저장
                chars = string.ascii_letters + string.digits
                o_filename = file.filename
                e_filename = f"{''.join(secrets.choice(chars) for _ in range(20))}.{o_filename.rsplit('.', 1)[1]}"
                save_path = os.path.join(os.getcwd(), "app", "uploads", e_filename)
                file.save(save_path)
            except Exception as e:
                return jsonify({"status": "F", "message": "게시글 수정 실패"})
            if not (execute_query(r"INSERT INTO files VALUES (NULL, %s, %s, %s)", (idx, o_filename, e_filename))):
                return jsonify({"status": "F", "message": "게시글 작성 실패"})
        return jsonify({"status": "S", "message": "게시글 수정 완료!"})
    return render_template("board/modify.html", post=post)


@bp.route("/delete/<idx>")
@login_required
@check_authority
def board_delete(idx: int):
    filename = rows[0]["e_filename"] if (rows:=execute_query(r"SELECT e_filename FROM files WHERE b_id=%s", (idx,))) else ""
    if filename:
        file_path = os.path.join(os.getcwd(), "app", "uploads", filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
        if not execute_query(r"DELETE FROM files WHERE b_id=%s", (idx,)):
            return jsonify({"status": "F", "message": "파일 삭제 실패"})
    if execute_query(r"DELETE FROM board WHERE id=%s", (idx,)):
        return jsonify({"status": "S", "message": "게시글 삭제 완료"})
    return jsonify({"status": "F", "message": "게시글 삭제 실패"})
