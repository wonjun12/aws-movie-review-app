import mysql.connector
from config import Setting


def movie_mysql_connection():
    return mysql.connector.connect(
        host = Setting.HOST,
        database = Setting.DATABASE,
        user = Setting.DB_USER,
        password = Setting.DB_PASSWORD
    )