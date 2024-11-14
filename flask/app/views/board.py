from flask import Blueprint
from flask import render_template, request, session
from flask_login import login_user, current_user
from app.models import User
from app.utils.db import execute_query


bp = Blueprint('board', __name__)


@bp.route("/list", methods=['GET', "POST"])
def post_list():
    return render_template("board/post_list.html")

@bp.route("/form", methods=['GET', "POST"])
def post_form():
    return render_template("board/post_form.html")

@bp.route("/success", methods=['GET', "POST"])
def post_success():
    return render_template("board/post_success.html")