# 베이스 이미지
FROM python:3.11

# 작업 디렉토리 생성
WORKDIR /app

# 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사
COPY . .

# FastAPI 서버 실행 (hot reload는 dev 단계에서만 유용)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]