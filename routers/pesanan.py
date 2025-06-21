from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from database import get_db
from models import Pesanan, Mahasiswa, Kantin, StatusPesananEnum
from schemas import PesananCreate, PesananUpdate, PesananResponse, PesananWithDetails

router = APIRouter()

@router.post("/", response_model=PesananResponse, status_code=status.HTTP_201_CREATED)
async def create_pesanan(pesanan: PesananCreate, db: Session = Depends(get_db)):
    """Create a new pesanan"""
    # Check if mahasiswa exists
    mahasiswa = db.query(Mahasiswa).filter(Mahasiswa.id_mahasiswa == pesanan.id_mahasiswa).first()
    if mahasiswa is None:
        raise HTTPException(status_code=404, detail="Mahasiswa not found")
    
    # Check if kantin exists
    kantin = db.query(Kantin).filter(Kantin.id_kantin == pesanan.id_kantin).first()
    if kantin is None:
        raise HTTPException(status_code=404, detail="Kantin not found")
    
    db_pesanan = Pesanan(
        id_kantin=pesanan.id_kantin,
        id_mahasiswa=pesanan.id_mahasiswa,
        status=pesanan.status
    )
    
    db.add(db_pesanan)
    db.commit()
    db.refresh(db_pesanan)
    
    return db_pesanan

@router.get("/", response_model=List[PesananResponse])
async def get_all_pesanan(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all pesanan with pagination"""
    pesanan = db.query(Pesanan).offset(skip).limit(limit).all()
    return pesanan

@router.get("/{pesanan_id}", response_model=PesananResponse)
async def get_pesanan(pesanan_id: int, db: Session = Depends(get_db)):
    """Get pesanan by ID"""
    pesanan = db.query(Pesanan).filter(Pesanan.id_pesanan == pesanan_id).first()
    if pesanan is None:
        raise HTTPException(status_code=404, detail="Pesanan not found")
    return pesanan

@router.get("/{pesanan_id}/with-details", response_model=PesananWithDetails)
async def get_pesanan_with_details(pesanan_id: int, db: Session = Depends(get_db)):
    """Get pesanan with all details, mahasiswa, and kantin information"""
    pesanan = db.query(Pesanan).options(
        joinedload(Pesanan.detail_pesanan),
        joinedload(Pesanan.mahasiswa),
        joinedload(Pesanan.kantin)
    ).filter(Pesanan.id_pesanan == pesanan_id).first()
    
    if pesanan is None:
        raise HTTPException(status_code=404, detail="Pesanan not found")
    return pesanan

@router.get("/mahasiswa/{mahasiswa_id}", response_model=List[PesananResponse])
async def get_pesanan_by_mahasiswa(mahasiswa_id: int, db: Session = Depends(get_db)):
    """Get all pesanan for a specific mahasiswa"""
    # Check if mahasiswa exists
    mahasiswa = db.query(Mahasiswa).filter(Mahasiswa.id_mahasiswa == mahasiswa_id).first()
    if mahasiswa is None:
        raise HTTPException(status_code=404, detail="Mahasiswa not found")
    
    pesanan = db.query(Pesanan).filter(Pesanan.id_mahasiswa == mahasiswa_id).all()
    return pesanan

@router.get("/kantin/{kantin_id}", response_model=List[PesananResponse])
async def get_pesanan_by_kantin(kantin_id: int, db: Session = Depends(get_db)):
    """Get all pesanan for a specific kantin"""
    # Check if kantin exists
    kantin = db.query(Kantin).filter(Kantin.id_kantin == kantin_id).first()
    if kantin is None:
        raise HTTPException(status_code=404, detail="Kantin not found")
    
    pesanan = db.query(Pesanan).filter(Pesanan.id_kantin == kantin_id).all()
    return pesanan

@router.get("/status/{status}", response_model=List[PesananResponse])
async def get_pesanan_by_status(status: StatusPesananEnum, db: Session = Depends(get_db)):
    """Get all pesanan by status"""
    pesanan = db.query(Pesanan).filter(Pesanan.status == status).all()
    return pesanan

@router.put("/{pesanan_id}", response_model=PesananResponse)
async def update_pesanan(
    pesanan_id: int, 
    pesanan_update: PesananUpdate, 
    db: Session = Depends(get_db)
):
    """Update pesanan (mainly status)"""
    pesanan = db.query(Pesanan).filter(Pesanan.id_pesanan == pesanan_id).first()
    if pesanan is None:
        raise HTTPException(status_code=404, detail="Pesanan not found")
    
    # Update fields if provided
    update_data = pesanan_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(pesanan, field, value)
    
    db.commit()
    db.refresh(pesanan)
    
    return pesanan

@router.delete("/{pesanan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pesanan(pesanan_id: int, db: Session = Depends(get_db)):
    """Delete pesanan"""
    pesanan = db.query(Pesanan).filter(Pesanan.id_pesanan == pesanan_id).first()
    if pesanan is None:
        raise HTTPException(status_code=404, detail="Pesanan not found")
    
    db.delete(pesanan)
    db.commit()
    
    return None

@router.put("/{pesanan_id}/status/{status}", response_model=PesananResponse)
async def update_pesanan_status(
    pesanan_id: int, 
    status: StatusPesananEnum, 
    db: Session = Depends(get_db)
):
    """Update pesanan status directly"""
    pesanan = db.query(Pesanan).filter(Pesanan.id_pesanan == pesanan_id).first()
    if pesanan is None:
        raise HTTPException(status_code=404, detail="Pesanan not found")
    
    pesanan.status = status
    db.commit()
    db.refresh(pesanan)
    
    return pesanan
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from database import get_db
from models import Pesanan, Mahasiswa, Kantin
from schemas import PesananCreate, PesananUpdate, PesananResponse, PesananWithDetails
from auth import get_current_mahasiswa, get_current_kantin, get_current_user

router = APIRouter()

@router.post("/", response_model=PesananResponse, status_code=status.HTTP_201_CREATED)
async def create_pesanan(
    pesanan: PesananCreate, 
    db: Session = Depends(get_db),
    current_mahasiswa: Mahasiswa = Depends(get_current_mahasiswa)
):
    """Create a new pesanan (mahasiswa only)"""
    # Only allow mahasiswa to create pesanan for themselves
    if current_mahasiswa.id_mahasiswa != pesanan.id_mahasiswa:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create pesanan for yourself"
        )
    
    # Check if kantin exists
    kantin = db.query(Kantin).filter(Kantin.id_kantin == pesanan.id_kantin).first()
    if kantin is None:
        raise HTTPException(status_code=404, detail="Kantin not found")
    
    db_pesanan = Pesanan(
        id_kantin=pesanan.id_kantin,
        id_mahasiswa=pesanan.id_mahasiswa,
        status=pesanan.status
    )
    
    db.add(db_pesanan)
    db.commit()
    db.refresh(db_pesanan)
    
    return db_pesanan

@router.get("/", response_model=List[PesananResponse])
async def get_all_pesanan(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all pesanan (filtered by user type)"""
    if isinstance(current_user, Mahasiswa):
        # Mahasiswa can only see their own pesanan
        pesanan = db.query(Pesanan).filter(
            Pesanan.id_mahasiswa == current_user.id_mahasiswa
        ).offset(skip).limit(limit).all()
    elif isinstance(current_user, Kantin):
        # Kantin can only see pesanan for their kantin
        pesanan = db.query(Pesanan).filter(
            Pesanan.id_kantin == current_user.id_kantin
        ).offset(skip).limit(limit).all()
    
    return pesanan

@router.get("/{pesanan_id}", response_model=PesananResponse)
async def get_pesanan(
    pesanan_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get pesanan by ID"""
    pesanan = db.query(Pesanan).filter(Pesanan.id_pesanan == pesanan_id).first()
    if pesanan is None:
        raise HTTPException(status_code=404, detail="Pesanan not found")
    
    # Check access permissions
    if isinstance(current_user, Mahasiswa):
        if pesanan.id_mahasiswa != current_user.id_mahasiswa:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own pesanan"
            )
    elif isinstance(current_user, Kantin):
        if pesanan.id_kantin != current_user.id_kantin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view pesanan for your kantin"
            )
    
    return pesanan

@router.get("/{pesanan_id}/with-details", response_model=PesananWithDetails)
async def get_pesanan_with_details(
    pesanan_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get pesanan with all details"""
    pesanan = db.query(Pesanan).options(
        joinedload(Pesanan.detail_pesanan),
        joinedload(Pesanan.mahasiswa),
        joinedload(Pesanan.kantin)
    ).filter(Pesanan.id_pesanan == pesanan_id).first()
    
    if pesanan is None:
        raise HTTPException(status_code=404, detail="Pesanan not found")
    
    # Check access permissions
    if isinstance(current_user, Mahasiswa):
        if pesanan.id_mahasiswa != current_user.id_mahasiswa:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own pesanan"
            )
    elif isinstance(current_user, Kantin):
        if pesanan.id_kantin != current_user.id_kantin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view pesanan for your kantin"
            )
    
    return pesanan

@router.put("/{pesanan_id}", response_model=PesananResponse)
async def update_pesanan(
    pesanan_id: int, 
    pesanan_update: PesananUpdate, 
    db: Session = Depends(get_db),
    current_kantin: Kantin = Depends(get_current_kantin)
):
    """Update pesanan status (kantin only)"""
    pesanan = db.query(Pesanan).filter(Pesanan.id_pesanan == pesanan_id).first()
    if pesanan is None:
        raise HTTPException(status_code=404, detail="Pesanan not found")
    
    # Only allow kantin to update pesanan for their kantin
    if pesanan.id_kantin != current_kantin.id_kantin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update pesanan for your kantin"
        )
    
    # Update fields if provided
    update_data = pesanan_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(pesanan, field, value)
    
    db.commit()
    db.refresh(pesanan)
    
    return pesanan

@router.delete("/{pesanan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pesanan(
    pesanan_id: int, 
    db: Session = Depends(get_db),
    current_mahasiswa: Mahasiswa = Depends(get_current_mahasiswa)
):
    """Delete pesanan (mahasiswa only)"""
    pesanan = db.query(Pesanan).filter(Pesanan.id_pesanan == pesanan_id).first()
    if pesanan is None:
        raise HTTPException(status_code=404, detail="Pesanan not found")
    
    # Only allow mahasiswa to delete their own pesanan
    if pesanan.id_mahasiswa != current_mahasiswa.id_mahasiswa:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own pesanan"
        )
    
    db.delete(pesanan)
    db.commit()
    
    return None

@router.get("/mahasiswa/{mahasiswa_id}", response_model=List[PesananResponse])
async def get_pesanan_by_mahasiswa(
    mahasiswa_id: int, 
    db: Session = Depends(get_db),
    current_mahasiswa: Mahasiswa = Depends(get_current_mahasiswa)
):
    """Get all pesanan for a specific mahasiswa"""
    # Only allow mahasiswa to view their own pesanan
    if current_mahasiswa.id_mahasiswa != mahasiswa_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own pesanan"
        )
    
    pesanan = db.query(Pesanan).filter(Pesanan.id_mahasiswa == mahasiswa_id).all()
    return pesanan

@router.get("/kantin/{kantin_id}", response_model=List[PesananResponse])
async def get_pesanan_by_kantin(
    kantin_id: int, 
    db: Session = Depends(get_db),
    current_kantin: Kantin = Depends(get_current_kantin)
):
    """Get all pesanan for a specific kantin"""
    # Only allow kantin to view pesanan for their kantin
    if current_kantin.id_kantin != kantin_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view pesanan for your kantin"
        )
    
    pesanan = db.query(Pesanan).filter(Pesanan.id_kantin == kantin_id).all()
    return pesanan
