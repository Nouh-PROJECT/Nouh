from flask import Blueprint, jsonify, request, redirect, url_for, render_template
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.utils.db import execute_query
from flask import render_template, request, session

bp = Blueprint('admin', __name__, url_prefix='/admin')

# 관리자 전용 페이지 접근 시 비관리자 리다이렉트
#def admin_required(func):
#    def wrapper(*args, **kwargs):
 #       if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
 #           return redirect(url_for('main.index'))  # 메인 페이지로 리다이렉트
  #      return func(*args, **kwargs)
   # wrapper.__name__ = func.__name__
   # return wrapper

@bp.route("/")
@login_required
#@admin_required
def index():
    return render_template('admin/admin.html')

# 멤버 목록 가져오기 엔드포인트
@bp.route('/member/get_members', methods=['GET'])
@login_required
#@admin_required
def get_members():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        offset = (page - 1) * per_page

        query = "SELECT id, name, login_id, login_pw, email, subscribe FROM users LIMIT %s OFFSET %s"
        rows = execute_query(query, (per_page, offset))

        total_query = "SELECT COUNT(*) as total FROM users"
        total_result = execute_query(total_query)
        total_count = total_result[0]['total'] if total_result else 0

        members = [{'id': row['id'], 'name': row['name'], 'login_id': row['login_id'], 'email': row['email'] or '-', 'subscribe': row['subscribe']} for row in rows]

        return jsonify({'members': members, 'total': total_count, 'page': page, 'per_page': per_page}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 구독 상태 업데이트 엔드포인트
@bp.route('/member/approve_subscription/<int:user_id>', methods=['POST'])
@login_required
#@admin_required
def approve_subscription(user_id):
    try:
        query = "UPDATE users SET subscribe = 1 WHERE id = %s AND subscribe = 2"
        rows = execute_query(query, (user_id,), commit=True)

        update_query = r"SELECT subscribe FROM users WHERE id=%s"
        rowss = execute_query(update_query, (current_user.id,))

        if rowss:
            subscribeResult = rowss[0] 
            session['isSubscribe'] = subscribeResult

            return jsonify({'status': 'success', 'message': '구독 승인 완료'}), 200
        
    except Exception as e:
        return jsonify({'status': 'failed', 'message': '구독 상태 업데이트 실패'}), 400

# 관리자 비밀번호 업데이트 엔드포인트
@bp.route('/update_admin_pw', methods=['POST'])
@login_required
#@admin_required
def update_admin_pw():
    new_pw = request.form.get('admin-new-pw')
    if not new_pw:
        return jsonify({'status': 'failed', 'message': '비밀번호를 입력해주세요.'}), 400

    hashed_pw = generate_password_hash(new_pw)
    try:
        query = "UPDATE users SET login_pw = %s WHERE login_id = 'admin'"
        rows = execute_query(query, (hashed_pw,), commit=True)
        if rows == 0:
            return jsonify({'status': 'failed', 'message': '비밀번호 업데이트 실패'}), 400
        return jsonify({'status': 'success', 'message': '비밀번호가 성공적으로 업데이트되었습니다.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 게시판 리스트
@bp.route('/board/get_boards', methods=['GET'])
@login_required
#@admin_required
def get_boards():
    try:
        # 페이지와 한 페이지당 항목 수를 가져옴
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        offset = (page - 1) * per_page

        # 게시글 ID, 제목, 작성자 이름을 조회하고 페이지에 맞게 제한
        sql = """
            SELECT board.id, board.title, users.name AS author
            FROM board
            JOIN users ON board.u_id = users.id
            ORDER BY board.created_at DESC
            LIMIT %s OFFSET %s
        """
        rows = execute_query(sql, (per_page, offset))

        # 총 게시글 수를 구하는 쿼리
        total_query = "SELECT COUNT(*) as total FROM board"
        total_result = execute_query(total_query)
        total_count = total_result[0]['total'] if total_result else 0

        # 게시글 리스트 생성
        posts = [{'id': row['id'], 'title': row['title'], 'author': row['author']} for row in rows]

        return jsonify({'posts': posts, 'total': total_count, 'page': page, 'per_page': per_page}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 게시글 삭제
@bp.route('/board/delete/<int:post_id>', methods=['DELETE'])
@login_required
#@admin_required
def delete_board_post(post_id):
    try:
        query = "DELETE FROM board WHERE id = %s"
        execute_query(query, (post_id,), commit=True)
        return '게시글 삭제가 완료되었습니다.', 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
