from flask import Blueprint
from flask import render_template, request, session
from flask_login import login_user, current_user
from app.models import User
from app.utils.db import execute_query


bp = Blueprint('board', __name__)


@bp.route("/list", methods=['GET', "POST"])
@login_required
def post_list():
    return render_template("board/post_list.html")
