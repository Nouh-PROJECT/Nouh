import os
import re
import json
from functools import wraps
from flask import Blueprint
from flask import render_template, url_for, redirect, request, session, current_app, flash
from flask_login import login_required, current_user
from app.models import User
from openpyxl import Workbook, load_workbook
from app.utils.db import execute_query
from flask import jsonify
from flask import send_file
import time

bp = Blueprint('board', __name__)

def check_board_owner(func):# 완료
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.id != 1:
            query = r"SELECT u_id FROM board WHERE id=%s"
            rows = execute_query(query, (kwargs.get('idx')))

            if (not rows) or (rows[0]['u_id'] != current_user.id):
                return redirect("/board/list")
        return func(*args, **kwargs)
    return wrapper

 
@bp.route("/list", methods=['GET'])
@login_required
def board_list(): #완료
    display_type = request.args.get('type', 'authorized', type=str)
    keyword = request.args.get('keyword', type=str)

    # 페이지네이션
    page = request.args.get("page", 1, type=int)
    total_pages = 0
    start_page = 0
    end_page = 0
    per_page = 10
    offset = (page - 1) * per_page

    count_query = r"SELECT COUNT(*) num FROM board"
    query = r"SELECT id, (select name from users where id = u_id) as uname, title, content, created_at FROM board"
    param = []

    if keyword:
        query += r" WHERE title LIKE %s"
        count_query += r" WHERE title LIKE %s"
        param = [f"%{keyword}%"]

    # 페이지 계산
    rows = execute_query(count_query, tuple(param))
    total_board = rows[0]['num'] if rows else 0
    total_pages = (total_board + per_page - 1) // per_page

    start_page = max(page - 2, 1)
    end_page = min(page + 2, total_pages)

    # 페이지 데이터 불러오기
    query += r" order by id desc LIMIT %s OFFSET %s "
    param.append(per_page)
    param.append(offset)
    boards = execute_query(query, tuple(param))
    boards = boards if boards else []

    if (end_page - start_page) < 4:
        if start_page == 1:
            end_page = min(start_page + 4, total_pages)
        elif end_page == total_pages:
            start_page = max(end_page - 4, 1)

    return render_template("board/list.html", boards=boards, type=display_type, page=page, total_pages=total_pages, start_page=start_page, end_page=end_page)

# 일부 완
# 만약 첨부파일이 있다면, 첨부파일도 올리기
@bp.route("/add", methods=['GET', 'POST'])
@login_required
def board_add():
    if request.method == 'POST':
        writer = current_user.id
        title = request.form.get('title')
        content = request.form.get('content')
        file = request.files.get('file')

        # 게시글 삽입
        if title:
            query = r"INSERT INTO board (u_id, title, content, created_at) VALUES (%s, %s, %s, NOW())"
            board_id = execute_query(query, (writer, title, content), True, return_last_id=True)  # board_id 반환

        # 파일 처리
        if file and file.filename:
            real_file = file.filename
            timestamp = time.strftime('%Y-%m-%d-%H%M%S')  # 현재 시간을 이용해 타임스탬프 생성
            enc_file = f"{real_file.rsplit('.', 1)[0]}_{timestamp}.{real_file.rsplit('.', 1)[1]}"

            # 파일 저장
            save_path = os.path.join(os.getcwd(), "app", "uploads", enc_file)
            file.save(save_path)

            # yfile 테이블에 삽입
            query = r"INSERT INTO yfile (b_id, real_file, enc_file) VALUES (%s, %s, %s)"
            execute_query(query, (board_id, real_file, enc_file), True)

        return redirect(url_for('board.board_list'))

    return render_template("board/add.html")

# 
@bp.route("/detail/<idx>", methods=['GET'])
@login_required
def board_detail(idx: str):
    # 게시글 정보 가져오기
    query = r"""
        SELECT 
            b.id, (SELECT name FROM users WHERE id = b.u_id) AS uname, 
            b.title, b.content, b.created_at, 
            y.real_file, y.enc_file
        FROM board b 
        LEFT JOIN yfile y ON b.id = y.b_id
        WHERE b.id=%s
    """
    rows = execute_query(query, (idx,))
    board = rows[0] if rows else []

    if not board:
        return redirect("/board/list")

    return render_template("board/detail.html", board=board)


@bp.route("/download/<enc_file>", methods=['GET'])
@login_required
def download_file(enc_file: str):
    # yfile 테이블에서 real_file 가져오기
    query = "SELECT real_file FROM yfile WHERE enc_file=%s"
    rows = execute_query(query, (enc_file,))
    if not rows:
        flash("파일이 존재하지 않습니다.")
        return redirect(url_for("board.board_list"))

    real_file = rows[0]['real_file']

    # 파일 경로 확인
    file_path = os.path.join(os.getcwd(), "app", "uploads", enc_file)
    if not os.path.isfile(file_path):
        flash("파일이 존재하지 않습니다.")
        return redirect(url_for("board.board_list"))

    # 파일 다운로드 (원래 이름으로 제공)
    return send_file(file_path, as_attachment=True, download_name=real_file)


@bp.route("/edit/<idx>", methods=['GET', 'POST'])
@login_required
@check_board_owner
def board_edit(idx: int):
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        file = request.files.get('file')  # 새로운 파일이 업로드 되었는지 확인

        # 게시글 업데이트
        query = r"UPDATE board SET title=%s, content=%s WHERE id=%s"
        param = (title, content, idx)
        execute_query(query, param, True)

        if file and file.filename:
            # 기존 첨부파일 삭제
            query = r"SELECT enc_file FROM yfile WHERE b_id=%s"
            rows = execute_query(query, (idx,))
            if rows:
                # 기존 첨부파일 삭제
                enc_file = rows[0]['enc_file']
                file_path = os.path.join(os.getcwd(), "app", "uploads", enc_file)
                if os.path.isfile(file_path):
                    os.remove(file_path)

            # 새로운 파일 처리
            real_file = file.filename
            timestamp = time.strftime('%Y-%m-%d-%H%M%S')
            enc_file = f"{real_file.rsplit('.', 1)[0]}_{timestamp}.{real_file.rsplit('.', 1)[1]}"

            # 파일 저장
            save_path = os.path.join(os.getcwd(), "app", "uploads", enc_file)
            file.save(save_path)

            # yfile 테이블에 새로운 파일 정보 업데이트
            query = r"""
                INSERT INTO yfile (b_id, real_file, enc_file)
                VALUES (%s, %s, %s)
            """
            execute_query(query, (idx, real_file, enc_file), True)

    # 게시글 정보 및 첨부파일 정보 가져오기
    query = r"""
        SELECT b.id, (SELECT name FROM users WHERE id = b.u_id) AS uname, 
            b.title, b.content, b.created_at, 
            y.real_file, y.enc_file
        FROM board b 
        LEFT JOIN yfile y ON b.id = y.b_id
        WHERE b.id=%s
    """
    rows = execute_query(query, (idx,))
    board = rows[0] if rows else []

    if not board:
        return redirect("/")

    return render_template("board/edit.html", board=board)



@bp.route("/delete/<idx>", methods=['GET'])
@login_required
@check_board_owner
def board_delete(idx: str):
    query = r"DELETE FROM board WHERE id=%s"
    execute_query(query, (idx,), True)
    return redirect(url_for('board.board_list', deleted="true"))
