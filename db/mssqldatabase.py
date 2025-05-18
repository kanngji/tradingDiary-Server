import pyodbc


# MSSQL 접속 정보
MSSQL_CONFIG = {
    "DRIVER": "ODBC Driver 18 for SQL Server",
    "SERVER": "host.docker.internal,1433",
    "DATABASE": "tradingDiary",
    "UID": "administrator",
    "PWD": "rkdwlgns123!",
}

# 연결 함수
def get_connection():
    conn_str = (
        f"DRIVER={{{MSSQL_CONFIG['DRIVER']}}};"
        f"SERVER={MSSQL_CONFIG['SERVER']};"
        f"DATABASE={MSSQL_CONFIG['DATABASE']};"
        f"UID={MSSQL_CONFIG['UID']};"
        f"PWD={MSSQL_CONFIG['PWD']};"
        f"TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)