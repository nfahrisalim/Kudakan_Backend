from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from decimal import Decimal
from database import get_db
from models import DetailPesanan, Pesanan, Menu
from schemas import DetailPesananCreate, DetailPesananUpdate, DetailPesananResponse

router = APIRouter()

@router.post("/", response_model=DetailPesananResponse, status_code=status.HTTP_201_CREATED)
async def create_detail_pesanan(detail: DetailPesananCreate, db: Session = Depends(get_db)):
    """Create a new detail pesanan"""
    # Check if pesanan exists
    pesanan = db.query(Pesanan).filter(Pesanan.id_pesanan == detail.id_pesanan).first()
    if pesanan is None:
        raise HTTPException(status_code=404, detail="Pesanan not found")
    
    # Check if menu exists
    menu = db.query(Menu).filter(Menu.id_menu == detail.id_menu).first()
    if menu is None:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    # Validate that harga_total matches menu price * quantity
    expected_total = menu.harga * detail.jumlah
    if detail.harga_total != expected_total:
        raise HTTPException(
            status_code=400, 
            detail=f"Harga total tidak sesuai. Expected: {expected_total}, Got: {detail.harga_total}"
        )
    
    db_detail = DetailPesanan(
        id_pesanan=detail.id_pesanan,
        id_menu=detail.id_menu,
        jumlah=detail.jumlah,
        harga_total=detail.harga_total
    )
    
    db.add(db_detail)
    db.commit()
    db.refresh(db_detail)
    
    return db_detail

@router.post("/auto-calculate", response_model=DetailPesananResponse, status_code=status.HTTP_201_CREATED)
async def create_detail_pesanan_auto_calculate(
    id_pesanan: int,
    id_menu: int,
    jumlah: int,
    db: Session = Depends(get_db)
):
    """Create detail pesanan with automatic price calculation"""
    # Check if pesanan exists
    pesanan = db.query(Pesanan).filter(Pesanan.id_pesanan == id_pesanan).first()
    if pesanan is None:
        raise HTTPException(status_code=404, detail="Pesanan not found")
    
    # Check if menu exists and get price
    menu = db.query(Menu).filter(Menu.id_menu == id_menu).first()
    if menu is None:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    # Calculate total price
    harga_total = menu.harga * jumlah
    
    db_detail = DetailPesanan(
        id_pesanan=id_pesanan,
        id_menu=id_menu,
        jumlah=jumlah,
        harga_total=harga_total
    )
    
    db.add(db_detail)
    db.commit()
    db.refresh(db_detail)
    
    return db_detail

@router.get("/", response_model=List[DetailPesananResponse])
async def get_all_detail_pesanan(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all detail pesanan with pagination"""
    details = db.query(DetailPesanan).offset(skip).limit(limit).all()
    return details

@router.get("/{detail_id}", response_model=DetailPesananResponse)
async def get_detail_pesanan(detail_id: int, db: Session = Depends(get_db)):
    """Get detail pesanan by ID"""
    detail = db.query(DetailPesanan).filter(DetailPesanan.id_detail == detail_id).first()
    if detail is None:
        raise HTTPException(status_code=404, detail="Detail pesanan not found")
    return detail

@router.get("/pesanan/{pesanan_id}", response_model=List[DetailPesananResponse])
async def get_detail_by_pesanan(pesanan_id: int, db: Session = Depends(get_db)):
    """Get all detail pesanan for a specific pesanan"""
    # Check if pesanan exists
    pesanan = db.query(Pesanan).filter(Pesanan.id_pesanan == pesanan_id).first()
    if pesanan is None:
        raise HTTPException(status_code=404, detail="Pesanan not found")
    
    details = db.query(DetailPesanan).filter(DetailPesanan.id_pesanan == pesanan_id).all()
    return details

@router.put("/{detail_id}", response_model=DetailPesananResponse)
async def update_detail_pesanan(
    detail_id: int, 
    detail_update: DetailPesananUpdate, 
    db: Session = Depends(get_db)
):
    """Update detail pesanan"""
    detail = db.query(DetailPesanan).filter(DetailPesanan.id_detail == detail_id).first()
    if detail is None:
        raise HTTPException(status_code=404, detail="Detail pesanan not found")
    
    # If updating quantity, recalculate total price
    update_data = detail_update.dict(exclude_unset=True)
    
    if "jumlah" in update_data and "harga_total" not in update_data:
        # Auto-recalculate price if only quantity is updated
        menu = db.query(Menu).filter(Menu.id_menu == detail.id_menu).first()
        if menu:
            update_data["harga_total"] = menu.harga * update_data["jumlah"]
    
    for field, value in update_data.items():
        setattr(detail, field, value)
    
    db.commit()
    db.refresh(detail)
    
    return detail

@router.delete("/{detail_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_detail_pesanan(detail_id: int, db: Session = Depends(get_db)):
    """Delete detail pesanan"""
    detail = db.query(DetailPesanan).filter(DetailPesanan.id_detail == detail_id).first()
    if detail is None:
        raise HTTPException(status_code=404, detail="Detail pesanan not found")
    
    db.delete(detail)
    db.commit()
    
    return None

@router.get("/pesanan/{pesanan_id}/total", response_model=dict)
async def get_pesanan_total(pesanan_id: int, db: Session = Depends(get_db)):
    """Get total amount for a pesanan"""
    # Check if pesanan exists
    pesanan = db.query(Pesanan).filter(Pesanan.id_pesanan == pesanan_id).first()
    if pesanan is None:
        raise HTTPException(status_code=404, detail="Pesanan not found")
    
    # Calculate total
    details = db.query(DetailPesanan).filter(DetailPesanan.id_pesanan == pesanan_id).all()
    total_amount = sum(detail.harga_total for detail in details)
    total_items = sum(detail.jumlah for detail in details)
    
    return {
        "id_pesanan": pesanan_id,
        "total_amount": total_amount,
        "total_items": total_items,
        "item_count": len(details)
    }
