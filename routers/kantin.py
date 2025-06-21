from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Kantin
from schemas import KantinCreate, KantinUpdate, KantinResponse, KantinWithMenus, KantinProfileUpdate
from auth import get_password_hash, get_current_kantin, get_current_user

router = APIRouter()

@router.post("/", response_model=KantinResponse, status_code=status.HTTP_201_CREATED)
async def create_kantin(kantin: KantinCreate, db: Session = Depends(get_db)):
    """Create a new kantin"""
    # Check if email already exists
    db_kantin = db.query(Kantin).filter(Kantin.email == kantin.email).first()
    if db_kantin:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Hash password and create kantin
    hashed_password = get_password_hash(kantin.password)
    db_kantin = Kantin(
        nama_kantin=kantin.nama_kantin,
        email=kantin.email,
        password=hashed_password
    )
    
    db.add(db_kantin)
    db.commit()
    db.refresh(db_kantin)
    
    return db_kantin

@router.get("/", response_model=List[KantinResponse])
async def get_all_kantin(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Get all kantin with pagination"""
    kantin = db.query(Kantin).offset(skip).limit(limit).all()
    return kantin

@router.get("/{kantin_id}", response_model=KantinResponse)
async def get_kantin(kantin_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Get kantin by ID"""
    kantin = db.query(Kantin).filter(Kantin.id_kantin == kantin_id).first()
    if kantin is None:
        raise HTTPException(status_code=404, detail="Kantin not found")
    return kantin

@router.get("/{kantin_id}/with-menus", response_model=KantinWithMenus)
async def get_kantin_with_menus(kantin_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Get kantin with all its menus"""
    kantin = db.query(Kantin).filter(Kantin.id_kantin == kantin_id).first()
    if kantin is None:
        raise HTTPException(status_code=404, detail="Kantin not found")
    return kantin

@router.put("/{kantin_id}", response_model=KantinResponse)
async def update_kantin(
    kantin_id: int, 
    kantin_update: KantinUpdate, 
    db: Session = Depends(get_db),
    current_kantin: Kantin = Depends(get_current_kantin)
):
    """Update kantin"""
    # Only allow kantin to update their own data
    if current_kantin.id_kantin != kantin_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile"
        )
    
    kantin = current_kantin
    
    # Update fields if provided
    update_data = kantin_update.dict(exclude_unset=True)
    
    # Check email uniqueness if email is being updated
    if "email" in update_data:
        existing_kantin = db.query(Kantin).filter(
            Kantin.email == update_data["email"],
            Kantin.id_kantin != kantin_id
        ).first()
        if existing_kantin:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password if being updated
    if "password" in update_data:
        update_data["password"] = get_password_hash(update_data["password"])
    
    for field, value in update_data.items():
        setattr(kantin, field, value)
    
    db.commit()
    db.refresh(kantin)
    
    return kantin

@router.delete("/{kantin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_kantin(kantin_id: int, db: Session = Depends(get_db), current_kantin: Kantin = Depends(get_current_kantin)):
    """Delete kantin"""
    # Only allow kantin to delete their own account
    if current_kantin.id_kantin != kantin_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own account"
        )
    
    kantin = current_kantin
    
    db.delete(kantin)
    db.commit()
    
    return None

@router.get("/email/{email}", response_model=KantinResponse)
async def get_kantin_by_email(email: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Get kantin by email"""
    kantin = db.query(Kantin).filter(Kantin.email == email).first()
    if kantin is None:
        raise HTTPException(status_code=404, detail="Kantin not found")
    return kantin

@router.put("/complete-profile", response_model=KantinResponse)
async def complete_kantin_profile(
    profile_data: KantinProfileUpdate,
    db: Session = Depends(get_db),
    current_kantin: Kantin = Depends(get_current_kantin)
):
    """Complete kantin profile with tenant name, owner details, and operational hours"""
    current_kantin.nama_tenant = profile_data.nama_tenant
    current_kantin.nama_pemilik = profile_data.nama_pemilik
    current_kantin.nomor_pemilik = profile_data.nomor_pemilik
    current_kantin.jam_operasional = profile_data.jam_operasional
    current_kantin.is_profile_complete = True
    
    db.commit()
    db.refresh(current_kantin)
    
    return current_kantin

@router.get("/profile-status", response_model=dict)
async def get_profile_status(current_kantin: Kantin = Depends(get_current_kantin)):
    """Check if kantin profile is complete"""
    return {
        "is_complete": current_kantin.is_profile_complete,
        "missing_fields": {
            "nama_tenant": current_kantin.nama_tenant is None,
            "nama_pemilik": current_kantin.nama_pemilik is None,
            "nomor_pemilik": current_kantin.nomor_pemilik is None,
            "jam_operasional": current_kantin.jam_operasional is None
        }
    }
