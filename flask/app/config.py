import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(32))
    SESSION_TYPE = os.environ.get("SESSION_TYPE", "filesystem")
    SESSION_PERMANENT = os.environ.get("SESSION_PERMANENT", False)
    SESSION_USER_SIGNER = os.environ.get("SESSION_USE_SIGNER", True)
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "mysql")
    MYSQL_USER = os.environ.get("MYSQL_USER", "master")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "P@ss4MA")
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "webapp")
    MAX_CONTENT_LENGTH = os.environ.get("MAX_CONTENT_LENGTH", 1024 * 1024 * 1024)