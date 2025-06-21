
from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_type: str
    user_info: dict

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
