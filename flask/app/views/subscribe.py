from flask import Blueprint
from flask import render_template, request, session
from flask_login import login_user, current_user
from app.models import User
from app.utils.db import execute_query


bp = Blueprint('subscribe', __name__)


@bp.route("/payment", methods=['GET', "POST"])
def payment():
    user = {"name":"홍길동", "email":"guest@guest.com", "phone":"01011112222", "isSubscribe":"0" }
    return render_template("subscribe/payment.html", user=user)

@bp.route("/popup", methods=['GET', "POST"])
def paymentPopup():
    user = {"name":"홍길동", "email":"guest@guest.com", "phone":"01011112222" }
    return render_template("subscribe/paymentPopup.html")

@bp.route("/popup/complete", methods=['GET', 'POST'])
def paymentComplete():
    # u_id = request.form.get('login-user-id')
    # if u_id:
    execute_query(r"UPDATE users SET subscribe = 1 WHERE id=%s", (current_user.id))
    # user = rows[0] if rows else None
    # query = "UPDATE users SET subscribe = 1 WHERE login_id = %s"
    # execute_query(query, (current_user.id,))

    return render_template("subscribe/paymentComplete.html")