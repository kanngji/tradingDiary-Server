from pydantic import BaseModel, EmailStr

class SignupRequest(BaseModel):
    email: EmailStr
    password: str

class SignupResponse(BaseModel):
    message: str