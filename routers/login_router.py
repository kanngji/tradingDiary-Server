from fastapi import APIRouter, HTTPException, Response
from passlib.context import CryptContext
from models.user import LoginRequest
from db.mssqldatabase import get_connection
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

router = APIRouter(prefix="/api", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

@router.post("/login")
async def login(user: LoginRequest, response: Response):
    conn = get_connection()
    cursor = conn.cursor()

    # 사용자 정보 조회
    cursor.execute("SELECT id, email, hashed_password FROM users WHERE email = ?", (user.email,))
    db_user = cursor.fetchone()
    conn.close()

    if not db_user:
        raise HTTPException(status_code=400, detail="이메일 또는 비밀번호가 일치하지 않습니다.")

    user_id, email, hashed_pw = db_user
    if not pwd_context.verify(user.password, hashed_pw):
        raise HTTPException(status_code=400, detail="이메일 또는 비밀번호가 일치하지 않습니다.")

    # JWT 토큰 생성
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = jwt.encode({"sub": email, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

    # 쿠키에 저장
    response.set_cookie(
    key="access_token",
    value=token,
    httponly=True,
    max_age=3600,
    samesite="None",  # None 대신 Lax 사용
    secure=True
    )

    return {"message":"로그인 성공","user_email":email}

@router.get("/api/test-cookie")
def test_cookie(response: Response):
    response.set_cookie(
        key="access_token",
        value="hello-cookie",
        httponly=True,
        samesite="None",
        secure=False
    )
    return {"message": "test cookie set"}