from flask import Blueprint
from flask import render_template, request, session, flash, current_app
from flask_login import current_user
from app.utils.db import execute_query

bp = Blueprint('main', __name__)


@bp.route("/", methods=['GET', 'POST'])
def index():
    return render_template('index.html')
    