from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models.user import SignupRequest, SignupResponse
from models.user_db import User
from sqlitedatabase import SessionLocal
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/api", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# DB 세션 주입
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/signup", response_model=SignupResponse)
async def signup(user: SignupRequest, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(user.password)

    new_user = User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")

    return {"message": "회원가입 성공!"}