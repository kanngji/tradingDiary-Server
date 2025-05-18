from pydantic import BaseModel, EmailStr

# 🔹 회원가입 요청용
class SignupRequest(BaseModel):
    email: EmailStr
    password: str  # 클라이언트는 원본 비밀번호를 보냄

# 🔹 회원가입 응답용
class SignupResponse(BaseModel):
    id: int
    email: EmailStr

# 🔹 내부에서 사용할 사용자 모델 (예: 로그인 검증 등)
class UserInDB(BaseModel):
    id: int
    email: EmailStr
    hashed_password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    