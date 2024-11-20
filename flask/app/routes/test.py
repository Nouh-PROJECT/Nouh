from flask import Blueprint
from flask import request, session
from flask import redirect, render_template, jsonify, render_template_string
from app.utils.db import execute_query


bp = Blueprint('test', __name__)


@bp.route("/ssti", methods=["GET"])
def ssti():
    data = request.args.get("data", "")
    template = '''
    <form>
        <input type="text" name="data" />
        <input type="submit" value="전송" />
    </form>
    <h1>''' + data + '''</h1>'''
    return render_template_string(template)


@bp.route("/sqli", methods=["GET"])
def sqli():
    template = '''
        <form>
            <input type="text" name="data" />
            <input type="submit" value="전송" />
        </form>
    '''

    data = request.args.get("data", None)
    if data:
        query = f"SELECT * FROM users WHERE login_id='{data}'"
        rows = execute_query(query)
        template = f"{template}<h1>{str(rows)}</h1>"
    return render_template_string(template)


@bp.route("/xss", methods=["GET"])
def xss():
    data = request.args.get("data", None)
    return render_template("test/xss.html", data=data)


@bp.route("/form")
def form():
    return render_template("test/form.html")