FROM python:3.11

WORKDIR /app

# 시스템 패키지 설치 및 Microsoft ODBC 드라이버 설치
RUN apt-get update && \
    apt-get install -y curl gnupg2 apt-transport-https ca-certificates gcc g++ && \
    apt-get remove -y libodbc2 libodbccr2 libodbcinst2 unixodbc-common && \
    curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/microsoft.gpg && \
    curl https://packages.microsoft.com/config/debian/11/prod.list -o /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc unixodbc-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
