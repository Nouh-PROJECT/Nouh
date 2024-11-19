from flask import Blueprint
from flask import render_template, request, session
from flask_login import login_user, current_user
from app.models import User
from app.utils.db import execute_query


bp = Blueprint('subscribe', __name__)


@bp.route("/payment", methods=['GET', "POST"])
def payment():
    user = execute_query(r"SELECT name, email, phone FROM users WHERE id=%s", (current_user.id))
    return render_template("subscribe/payment.html", user=user)

@bp.route("/popup", methods=['GET', "POST"])
def paymentPopup():
    return render_template("subscribe/paymentPopup.html")

@bp.route("/popup/complete", methods=['GET', 'POST'])
def paymentComplete():
    execute_query(r"UPDATE users SET subscribe = 2 WHERE id=%s", (current_user.id), True)
    query = r"SELECT subscribe FROM users WHERE id=%s"
    rows = execute_query(query, (current_user.id,))

    if rows:
        subscribeResult = rows[0] 
        session['isSubscribe'] = subscribeResult

    return render_template("subscribe/paymentComplete.html")