
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Union
from datetime import timedelta
from database import get_db
from models import Mahasiswa, Kantin
from schemas import MahasiswaResponse, KantinResponse
from auth_schemas import LoginRequest, TokenResponse, ChangePasswordRequest
from auth import (
    verify_password, get_password_hash, create_access_token, 
    get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login for both mahasiswa and kantin"""
    
    # Try to find user in mahasiswa table
    mahasiswa = db.query(Mahasiswa).filter(Mahasiswa.email == login_data.email).first()
    if mahasiswa and verify_password(login_data.password, mahasiswa.password):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": mahasiswa.id_mahasiswa, "user_type": "mahasiswa"},
            expires_delta=access_token_expires
        )
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_type="mahasiswa",
            user_info={
                "id": mahasiswa.id_mahasiswa,
                "nama": mahasiswa.nama,
                "email": mahasiswa.email,
                "nim": mahasiswa.nim
            }
        )
    
    # Try to find user in kantin table
    kantin = db.query(Kantin).filter(Kantin.email == login_data.email).first()
    if kantin and verify_password(login_data.password, kantin.password):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": kantin.id_kantin, "user_type": "kantin"},
            expires_delta=access_token_expires
        )
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_type="kantin",
            user_info={
                "id": kantin.id_kantin,
                "nama_kantin": kantin.nama_kantin,
                "email": kantin.email
            }
        )
    
    # If no user found or password incorrect
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password"
    )

@router.get("/me")
async def get_current_user_info(current_user: Union[Mahasiswa, Kantin] = Depends(get_current_user)):
    """Get current user information"""
    if isinstance(current_user, Mahasiswa):
        return {
            "user_type": "mahasiswa",
            "user_info": MahasiswaResponse.from_orm(current_user)
        }
    else:
        return {
            "user_type": "kantin",
            "user_info": KantinResponse.from_orm(current_user)
        }

@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: Union[Mahasiswa, Kantin] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.password = get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "Password updated successfully"}
