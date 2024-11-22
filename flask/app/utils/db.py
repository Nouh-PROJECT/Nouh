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


def execute_query(sql: str, params=None):
    db = get_db()
    if not db:
        return False
    
    with db.cursor() as cursor:
        try:
            cursor.execute(sql, params)
            
            command = sql.strip().lower()
            if command.startswith("select"):
                return cursor.fetchall()

            try:
                db.commit()
                if command.startswith("insert"):
                    return cursor.lastrowid
                if command.startswith("update") or command.startswith("delete"):
                    return True
            except Exception as commit_error:
                db.rollback()
                return False
                return f"{commit_error}"
        except Exception as query_error:
            return False
            return f"{query_error}"
