from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Mahasiswa
from schemas import MahasiswaCreate, MahasiswaUpdate, MahasiswaResponse
from auth import get_password_hash, get_current_mahasiswa, get_current_user

router = APIRouter()

@router.post("/", response_model=MahasiswaResponse, status_code=status.HTTP_201_CREATED)
async def create_mahasiswa(mahasiswa: MahasiswaCreate, db: Session = Depends(get_db)):
    """Create a new mahasiswa"""
    # Check if email already exists
    db_mahasiswa = db.query(Mahasiswa).filter(Mahasiswa.email == mahasiswa.email).first()
    if db_mahasiswa:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Hash password and create mahasiswa
    hashed_password = get_password_hash(mahasiswa.password)
    db_mahasiswa = Mahasiswa(
        nama=mahasiswa.nama,
        email=mahasiswa.email,
        password=hashed_password,
        nim=mahasiswa.nim
    )
    
    db.add(db_mahasiswa)
    db.commit()
    db.refresh(db_mahasiswa)
    
    return db_mahasiswa

@router.get("/", response_model=List[MahasiswaResponse])
async def get_all_mahasiswa(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Get all mahasiswa with pagination"""
    mahasiswa = db.query(Mahasiswa).offset(skip).limit(limit).all()
    return mahasiswa

@router.get("/{mahasiswa_id}", response_model=MahasiswaResponse)
async def get_mahasiswa(mahasiswa_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Get mahasiswa by ID"""
    mahasiswa = db.query(Mahasiswa).filter(Mahasiswa.id_mahasiswa == mahasiswa_id).first()
    if mahasiswa is None:
        raise HTTPException(status_code=404, detail="Mahasiswa not found")
    return mahasiswa

@router.put("/{mahasiswa_id}", response_model=MahasiswaResponse)
async def update_mahasiswa(
    mahasiswa_id: int, 
    mahasiswa_update: MahasiswaUpdate, 
    db: Session = Depends(get_db),
    current_mahasiswa: Mahasiswa = Depends(get_current_mahasiswa)
):
    """Update mahasiswa"""
    # Only allow mahasiswa to update their own data
    if current_mahasiswa.id_mahasiswa != mahasiswa_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile"
        )
    
    mahasiswa = current_mahasiswa
    
    # Update fields if provided
    update_data = mahasiswa_update.dict(exclude_unset=True)
    
    # Check email uniqueness if email is being updated
    if "email" in update_data:
        existing_mahasiswa = db.query(Mahasiswa).filter(
            Mahasiswa.email == update_data["email"],
            Mahasiswa.id_mahasiswa != mahasiswa_id
        ).first()
        if existing_mahasiswa:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password if being updated
    if "password" in update_data:
        update_data["password"] = get_password_hash(update_data["password"])
    
    for field, value in update_data.items():
        setattr(mahasiswa, field, value)
    
    db.commit()
    db.refresh(mahasiswa)
    
    return mahasiswa

@router.delete("/{mahasiswa_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mahasiswa(mahasiswa_id: int, db: Session = Depends(get_db), current_mahasiswa: Mahasiswa = Depends(get_current_mahasiswa)):
    """Delete mahasiswa"""
    # Only allow mahasiswa to delete their own account
    if current_mahasiswa.id_mahasiswa != mahasiswa_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own account"
        )
    
    mahasiswa = current_mahasiswa
    
    db.delete(mahasiswa)
    db.commit()
    
    return None

@router.get("/email/{email}", response_model=MahasiswaResponse)
async def get_mahasiswa_by_email(email: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Get mahasiswa by email"""
    mahasiswa = db.query(Mahasiswa).filter(Mahasiswa.email == email).first()
    if mahasiswa is None:
        raise HTTPException(status_code=404, detail="Mahasiswa not found")
    return mahasiswa
