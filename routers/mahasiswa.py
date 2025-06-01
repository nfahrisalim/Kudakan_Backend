from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Mahasiswa
from schemas import MahasiswaCreate, MahasiswaUpdate, MahasiswaResponse
import hashlib

router = APIRouter()

def hash_password(password: str) -> str:
    """Simple password hashing (in production, use bcrypt or similar)"""
    return hashlib.sha256(password.encode()).hexdigest()

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
    hashed_password = hash_password(mahasiswa.password)
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
async def get_all_mahasiswa(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all mahasiswa with pagination"""
    mahasiswa = db.query(Mahasiswa).offset(skip).limit(limit).all()
    return mahasiswa

@router.get("/{mahasiswa_id}", response_model=MahasiswaResponse)
async def get_mahasiswa(mahasiswa_id: int, db: Session = Depends(get_db)):
    """Get mahasiswa by ID"""
    mahasiswa = db.query(Mahasiswa).filter(Mahasiswa.id_mahasiswa == mahasiswa_id).first()
    if mahasiswa is None:
        raise HTTPException(status_code=404, detail="Mahasiswa not found")
    return mahasiswa

@router.put("/{mahasiswa_id}", response_model=MahasiswaResponse)
async def update_mahasiswa(
    mahasiswa_id: int, 
    mahasiswa_update: MahasiswaUpdate, 
    db: Session = Depends(get_db)
):
    """Update mahasiswa"""
    mahasiswa = db.query(Mahasiswa).filter(Mahasiswa.id_mahasiswa == mahasiswa_id).first()
    if mahasiswa is None:
        raise HTTPException(status_code=404, detail="Mahasiswa not found")
    
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
        update_data["password"] = hash_password(update_data["password"])
    
    for field, value in update_data.items():
        setattr(mahasiswa, field, value)
    
    db.commit()
    db.refresh(mahasiswa)
    
    return mahasiswa

@router.delete("/{mahasiswa_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mahasiswa(mahasiswa_id: int, db: Session = Depends(get_db)):
    """Delete mahasiswa"""
    mahasiswa = db.query(Mahasiswa).filter(Mahasiswa.id_mahasiswa == mahasiswa_id).first()
    if mahasiswa is None:
        raise HTTPException(status_code=404, detail="Mahasiswa not found")
    
    db.delete(mahasiswa)
    db.commit()
    
    return None

@router.get("/email/{email}", response_model=MahasiswaResponse)
async def get_mahasiswa_by_email(email: str, db: Session = Depends(get_db)):
    """Get mahasiswa by email"""
    mahasiswa = db.query(Mahasiswa).filter(Mahasiswa.email == email).first()
    if mahasiswa is None:
        raise HTTPException(status_code=404, detail="Mahasiswa not found")
    return mahasiswa
