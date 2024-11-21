from flask import Blueprint
from flask import request, session
from flask import redirect, render_template, jsonify
from flask_login import current_user
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.db import execute_query
from app.routes import User

bp = Blueprint('member', __name__)


@bp.route("/register", methods=["POST"])
def member_register():
    user_name = request.form.get("userName", "")
    user_id = request.form.get("userId", "")
    user_pw = request.form.get("userPw", "")
    check_pw = request.form.get("checkPw", "")
    user_email = request.form.get("userEmail", "NULL")
    user_phone = request.form.get("userPhone", "NULL")
    
    # 입력값 검증
    if not (user_name and user_id and user_pw and check_pw):
        return jsonify({"status":"F", "message":"필수 항목을 입력해주세요."})
    if user_pw != check_pw:
        return jsonify({"status":"F", "message":"비밀번호가 일치하지 않습니다."})
    if execute_query(r"SELECT 1 FROM users WHERE login_id=%s", (user_id,)):
        return jsonify({"status":"F", "message":"중복된 아이디입니다."})
    
    params = (user_name, user_id, generate_password_hash(user_pw), user_email, user_phone)
    if execute_query(r"INSERT INTO users VALUES (NULL, %s, %s, %s, %s, %s)", params):
        return jsonify({"status":"S", "message":"회원등록 완료"})
    return jsonify({"status":"F", "message":"회원등록 실패"})


@bp.route("/login", methods=["POST"])
def member_login():
    user_id = request.form.get("userId", "")
    user_pw = request.form.get("userPw", "")
    if (user_id and user_pw):
        query = r"SELECT id, name, login_pw, (SELECT 1 FROM admin WHERE admin.id=users.id)is_admin, "
        query += r"(SELECT 1 FROM subscribe WHERE subscribe.id=users.id)is_subscribe FROM users WHERE login_id=%s"
        user = rows[0] if (rows:=(execute_query(query, (user_id,)))) else []
        if user and check_password_hash(user["login_pw"], user_pw):
            session["subscribe"] = user["is_subscribe"]
            login_user(User(user["id"], user["name"], user_id, user["is_admin"]))
            return jsonify({"status":"S", "message": f"{user['name']}님 환영합니다!"})
    return jsonify({"status":"F", "message":"아이디 또는 비밀번호가 올바르지 않습니다."})


@bp.route("/logout", methods=["GET"])
@login_required
def member_logout():
    logout_user()
    session.clear()
    return jsonify({"status":"S", "message":"로그아웃 완료"})


@bp.route("/unregister")
@login_required
def member_unregister():
    if execute_query(r"DELETE FROM users WHERE id=%s", (current_user.id,)):
        logout_user()
        session.clear()
        return jsonify({"status":"S", "message":"회원탈퇴 완료"})
    return jsonify({"status":"F", "message":"회원탈퇴 실패."})


@bp.route("/mypage", methods=["GET", "POST"])
@login_required
def mypage():
    user = rows[0] if (rows:=execute_query(r"SELECT * FROM users WHERE id=%s", (current_user.id,))) else None
    if user is None:
        return redirect("/")

    if request.method == "POST":
        name = request.form.get("user-name")
        current_pw = request.form.get("user-cpw")
        new_pw = request.form.get("user-npw")
        check_pw = request.form.get("user-check-npw")
        email = request.form.get("user-email")
        phone = request.form.get("user-phone")

        if not check_password_hash(user['login_pw'], current_pw):
            return jsonify({"status": "F", "message": "올바르지 않은 비밀번호입니다."})
        if name and (name != user["name"]):
            if execute_query(r"SELECT 1 FROM users WHERE name=%s", (name,)):
                return jsonify({"status": "F", "message": "중복된 닉네임입니다."})
            if not execute_query(r"UPDATE users SET name=%s WHERE id=%s", (name, current_user.id)):
                return jsonify({"status": "F", "message": "회원정보 수정 실패"})
        if new_pw and (new_pw == check_pw):
            if not execute_query(r"UPDATE users SET login_pw=%s WHERE id=%s", (generate_password_hash(new_pw), current_user.id)):
                return jsonify({"status": "F", "message": "회원정보 수정 실패"})
        if email and (email != user["email"]):
            if execute_query(r"SELECT 1 FROM users WHERE email=%s", (email,)):
                return jsonify({"status": "F", "message": "중복된 이메일입니다."})
            if not execute_query(r"UPDATE users SET email=%s WHERE id=%s", (email, current_user.id)):
                return jsonify({"status": "F", "message": "회원정보 수정 실패"})
        if (phone != user["phone"]):
            if not execute_query(r"UPDATE users SET phone=%s WHERE id=%s", (phone, current_user.id)):
                return jsonify({"status": "F", "message": "회원정보 수정 실패"})
        return jsonify({"status": "S", "message": "회원정보 수정 완료"})
    return render_template("member/mypage.html", user=user)
