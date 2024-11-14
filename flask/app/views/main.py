from flask import Blueprint
from flask import render_template, request, session, flash, current_app


bp = Blueprint('main', __name__)


@bp.route("/", methods=['GET', 'POST'])
def index():
    session["subscribe"] = 0
    return render_template('index.html')
