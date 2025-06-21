
from datetime import datetime, timedelta
from typing import Optional, Union
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from models import Mahasiswa, Kantin
from database import get_db
import os

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Union[Mahasiswa, Kantin]:
    """Get current authenticated user"""
    payload = verify_token(credentials.credentials)
    
    user_id: int = payload.get("sub")
    user_type: str = payload.get("user_type")
    
    if user_id is None or user_type is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    if user_type == "mahasiswa":
        user = db.query(Mahasiswa).filter(Mahasiswa.id_mahasiswa == user_id).first()
    elif user_type == "kantin":
        user = db.query(Kantin).filter(Kantin.id_kantin == user_id).first()
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user type",
        )
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user

def get_current_mahasiswa(
    current_user: Union[Mahasiswa, Kantin] = Depends(get_current_user)
) -> Mahasiswa:
    """Get current mahasiswa user"""
    if not isinstance(current_user, Mahasiswa):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Mahasiswa only"
        )
    return current_user

def get_current_kantin(
    current_user: Union[Mahasiswa, Kantin] = Depends(get_current_user)
) -> Kantin:
    """Get current kantin user"""
    if not isinstance(current_user, Kantin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Kantin only"
        )
    return current_user

def get_current_mahasiswa_with_profile(
    current_user: Union[Mahasiswa, Kantin] = Depends(get_current_user)
) -> Mahasiswa:
    """Get current mahasiswa user with complete profile"""
    if not isinstance(current_user, Mahasiswa):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Mahasiswa only"
        )
    if not current_user.is_profile_complete:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile not complete. Please complete your profile first with delivery address and phone number."
        )
    return current_user

def get_current_kantin_with_profile(
    current_user: Union[Mahasiswa, Kantin] = Depends(get_current_user)
) -> Kantin:
    """Get current kantin user with complete profile"""
    if not isinstance(current_user, Kantin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Kantin only"
        )
    if not current_user.is_profile_complete:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile not complete. Please complete your profile first with tenant name, owner details, and operational hours."
        )
    return current_user
