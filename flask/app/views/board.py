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
    #query = r"SELECT id, name FROM subjects"
    #results = execute_query(query)
    #subjects = [(row['id'], row['name']) for row in results] if results else []

    if request.method == 'POST':
        writer = current_user.id
        title = request.form.get('title')
        content = request.form.get('content')
        #file = request.form.get('file')
        if title:
            query = r"INSERT INTO board VALUES (NULL, %s, %s, %s, NOW())"
            execute_query(query, (writer, title, content), True)
        #if file:


            # 등록 시 등록 성공 같은 메세지
        
        return render_template("board/add.html")

    return render_template("board/add.html")

# 
@bp.route("/detail/<idx>", methods=['GET'])
@login_required
def board_detail(idx: str):
    query = r"SELECT id, (select name from users where id = u_id) as uname, title, content, created_at FROM board WHERE id=%s"
    rows = execute_query(query, (idx))
    board = rows[0] if rows else []

    if not board:
        return redirect("/")

    return render_template("board/detail.html", board=board)


@bp.route("/edit/<idx>", methods=['GET', 'POST'])
@login_required
@check_board_owner
def board_edit(idx: int):
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        query = r"UPDATE board SET title=%s, content=%s WHERE id=%s"
        param = (title, content, idx)
        execute_query(query, param, True)

    query = r"SELECT id, (select name from users where id = u_id) as uname, title, content, created_at FROM board WHERE id=%s"
    rows = execute_query(query, (idx))
    board = rows[0] if rows else []

    if not board:
        return redirect("/")

    # # Subject Info
    # rows = execute_query(r"SELECT id, name FROM subjects")
    # subjects = [(row['id'], row['name']) for row in rows] if rows else []

    return render_template("board/edit.html", board=board)


@bp.route("/delete/<idx>", methods=['GET'])
@login_required
@check_board_owner
def board_delete(idx: str):
    query = r"DELETE FROM board WHERE id=%s"
    execute_query(query, (idx,), True)
    return redirect(url_for('board.board_list', deleted="true"))
