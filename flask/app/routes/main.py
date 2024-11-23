from flask import Blueprint
from flask import render_template


bp = Blueprint('main', __name__)

@bp.route("/")
def index():
    return render_template('index.html')


@bp.route("/health")
def aws_health_check():
    return ""