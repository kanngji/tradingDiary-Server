import pymysql
import os

# MySQL 접속 정보
MYSQL_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "kangji"),
    "password": os.getenv("DB_PASSWORD", "147601"),
    "database": os.getenv("DB_NAME", "tradingDiary"),
}

# 연결 함수
def get_connection():
    return pymysql.connect(
        host=MYSQL_CONFIG["host"],
        port=MYSQL_CONFIG["port"],
        user=MYSQL_CONFIG["user"],
        password=MYSQL_CONFIG["password"],
        database=MYSQL_CONFIG["database"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )