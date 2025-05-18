from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from models.user import SignupRequest, SignupResponse
from db.mssqldatabase import get_connection
import pyodbc

router = APIRouter(prefix="/api", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/signup", response_model=SignupResponse)
async def signup(user: SignupRequest):
    conn = get_connection()
    cursor = conn.cursor()

    # 이메일 중복 확인
    cursor.execute("SELECT id FROM users WHERE email = ?", (user.email,))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")

    # 비밀번호 해시 후 저장
    hashed_pw = pwd_context.hash(user.password)
    cursor.execute(
        "INSERT INTO users (email, hashed_password) OUTPUT INSERTED.id VALUES (?, ?)",
        (user.email, hashed_pw)
    )
    new_user_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()

    return SignupResponse(id=new_user_id, email=user.email)