import pymysql.cursors
from flask import current_app as app, g


def get_db():
    if "db" not in g:
        try:
            g.db = pymysql.connect(
                host=app.config["MYSQL_HOST"],
                user=app.config["MYSQL_USER"],
                password=app.config["MYSQL_PASSWORD"],
                database=app.config["MYSQL_DATABASE"],
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor
            )
        except Exception as e:
            print(f"Database connection error: {e}")
            g.db = None
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def execute_query(sql, params=None, commit=False, return_last_id=False):
    db = get_db()
    if not db:
        return None
    with db.cursor() as cursor:
        try:
            cursor.execute(sql, params)
            if commit:
                db.commit()
                if return_last_id:
                    return cursor.lastrowid  # 마지막으로 삽입된 ID 반환
            return cursor.fetchall() if not commit else None
        except Exception as e:
            print(f"Query execution error: {e}")
            if commit:
                db.rollback()
            return None
