import json
from flask import render_template, redirect, url_for, request, flash, Blueprint, current_app, session, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app.utils.db import execute_query


bp = Blueprint('auth', __name__)


@bp.route('/register', methods=['POST'])
def register():
    name = request.form.get('register-user-name')
    user_id = request.form.get('register-user-id')
    user_pw = request.form.get('register-user-pw')
    check_pw = request.form.get('register-check-pw')
    hashed_pw = generate_password_hash(user_pw)
    email = request.form.get('register-user-email')
    phone = request.form.get('register-user-phone')

    data = {'status': 'failed', 'message': ''}

    if (len(name) < 2) or (8 < len(name)):
        data['message'] = '이름은 2 ~ 8자만 입력 가능합니다.'
    elif (len(user_id) < 5) or (16 < len(user_id)):
        data['message'] = '아이디는 5 ~ 16자만 입력 가능합니다.'
    elif user_pw != check_pw:
        data['message'] = '비밀번호가 일치하지 않습니다.'
    elif (len(user_pw) < 6) or (16 < len(user_pw)):
        data['message'] = '비밀번호는 6 ~ 16자만 입력 가능합니다.'
    else:
        if execute_query(r"SELECT id FROM users WHERE login_id=%s", (user_id,)):
            data['message'] = '중복된 아이디입니다.'
        else:
            execute_query(r"INSERT INTO users VALUES (NULL, %s, %s, %s, %s, %s, 0)", (name, user_id, hashed_pw, email, phone, ), True)
            data['status'] = 'success'
            data['message'] = '회원가입 완료!'
                       

    return json.dumps(data)


@bp.route('/login', methods=['POST'])
def login():
    user_id = request.form.get('login-user-id')
    user_pw = request.form.get('login-user-pw')

    #구독여부
    query = r"SELECT subscribe FROM users WHERE login_id=%s"
    rows = execute_query(query, (user_id))
    subscribeResult = rows[0] if rows else None

    # 로그인 정보
    result = execute_query(r"SELECT * FROM users WHERE login_id=%s", (user_id,))

    if not result:
        data = {
            'status': 'failed',
            'message': '아이디 또는 비밀번호가 올바르지 않습니다.'
        }
        return json.dumps(data)

    user = result[0]
    if check_password_hash(user['login_pw'], user_pw):
        login_user(User(user['id'], user['name'], user_id))
        data = {
            'status': 'success',
            'message': f"{user['name']}님 환영합니다!"
        }
        session['isSubscribe'] = subscribeResult
    else:
        data = {
            'status': 'failed',
            'message': '아이디 또는 비밀번호가 올바르지 않습니다.'
        }
    return json.dumps(data)


@bp.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    data = {
        'status': 'success',
        'message': '로그아웃 완료!'
    }
    return json.dumps(data)


@bp.route('/mypage', methods=['GET'])
@login_required
def mypage():
    query = r"SELECT * FROM users WHERE id=%s"
    rows = execute_query(query, (current_user.id))
    user = rows[0] if rows else None

    return render_template("auth/mypage.html", user=user)


@bp.route('/update_mypage', methods=['POST'])
@login_required
def update_mypage():
    rows = execute_query(r"SELECT * FROM users WHERE id=%s", (current_user.id))
    user = rows[0] if rows else None

    current_pw = request.form.get("user-cpw")
    new_pw = request.form.get("user-npw")
    check_pw = request.form.get("user-npw-check")

    data = {'status': 'failed', 'message': ''}
    if not user:
        data['message'] = "비정상적인 접근입니다."
    elif not check_password_hash(user['user_pw'], current_pw):
        data['message'] = "비밀번호가 올바르지 않습니다."
    elif new_pw != check_pw:
        data['message'] = "새 비밀번호를 확인해주세요."
    else:
        execute_query(r"UPDATE users SET login_pw=%s WHERE id=%s", (generate_password_hash(new_pw), current_user.id), True)
        data = {'status': 'success', 'message': '회원 정보 수정 완료!'}
    
    return json.dumps(data)

@bp.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    try:
        rows = execute_query(r"DELETE FROM users WHERE id=%s", (current_user.id),True)

        if rows == 0:
            flash("회원 탈퇴에 실패했습니다. 다시 시도해주세요.", "error")
            return redirect(url_for("auth.mypage"))

        logout_user()
        session.clear()

        return jsonify({"message": "Account deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500