from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
from database import get_db
from models import Menu, Kantin
from schemas import MenuCreate, MenuUpdate, MenuResponse, MenuWithKantin
from minio_client import upload_image, delete_image

router = APIRouter()

@router.post("/", response_model=MenuResponse, status_code=status.HTTP_201_CREATED)
async def create_menu(menu: MenuCreate, db: Session = Depends(get_db)):
    """Create a new menu item"""
    # Check if kantin exists
    kantin = db.query(Kantin).filter(Kantin.id_kantin == menu.id_kantin).first()
    if kantin is None:
        raise HTTPException(status_code=404, detail="Kantin not found")
    
    db_menu = Menu(
        id_kantin=menu.id_kantin,
        nama_menu=menu.nama_menu,
        harga=menu.harga,
        img_menu=menu.img_menu
    )
    
    db.add(db_menu)
    db.commit()
    db.refresh(db_menu)
    
    return db_menu

@router.post("/with-image", response_model=MenuResponse, status_code=status.HTTP_201_CREATED)
async def create_menu_with_image(
    id_kantin: int = Form(...),
    nama_menu: str = Form(...),
    harga: Decimal = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Create a new menu item with image upload"""
    # Check if kantin exists
    kantin = db.query(Kantin).filter(Kantin.id_kantin == id_kantin).first()
    if kantin is None:
        raise HTTPException(status_code=404, detail="Kantin not found")
    
    img_url = None
    if image:
        img_url = await upload_image(image)
    
    db_menu = Menu(
        id_kantin=id_kantin,
        nama_menu=nama_menu,
        harga=harga,
        img_menu=img_url
    )
    
    db.add(db_menu)
    db.commit()
    db.refresh(db_menu)
    
    return db_menu

@router.get("/", response_model=List[MenuResponse])
async def get_all_menu(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all menu items with pagination"""
    menu = db.query(Menu).offset(skip).limit(limit).all()
    return menu

@router.get("/kantin/{kantin_id}", response_model=List[MenuResponse])
async def get_menu_by_kantin(kantin_id: int, db: Session = Depends(get_db)):
    """Get all menu items for a specific kantin"""
    # Check if kantin exists
    kantin = db.query(Kantin).filter(Kantin.id_kantin == kantin_id).first()
    if kantin is None:
        raise HTTPException(status_code=404, detail="Kantin not found")
    
    menu = db.query(Menu).filter(Menu.id_kantin == kantin_id).all()
    return menu

@router.get("/{menu_id}", response_model=MenuResponse)
async def get_menu(menu_id: int, db: Session = Depends(get_db)):
    """Get menu item by ID"""
    menu = db.query(Menu).filter(Menu.id_menu == menu_id).first()
    if menu is None:
        raise HTTPException(status_code=404, detail="Menu not found")
    return menu

@router.get("/{menu_id}/with-kantin", response_model=MenuWithKantin)
async def get_menu_with_kantin(menu_id: int, db: Session = Depends(get_db)):
    """Get menu item with kantin information"""
    menu = db.query(Menu).filter(Menu.id_menu == menu_id).first()
    if menu is None:
        raise HTTPException(status_code=404, detail="Menu not found")
    return menu

@router.put("/{menu_id}", response_model=MenuResponse)
async def update_menu(
    menu_id: int, 
    menu_update: MenuUpdate, 
    db: Session = Depends(get_db)
):
    """Update menu item"""
    menu = db.query(Menu).filter(Menu.id_menu == menu_id).first()
    if menu is None:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    # Update fields if provided
    update_data = menu_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(menu, field, value)
    
    db.commit()
    db.refresh(menu)
    
    return menu

@router.put("/{menu_id}/image", response_model=MenuResponse)
async def update_menu_image(
    menu_id: int,
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Update menu item image"""
    menu = db.query(Menu).filter(Menu.id_menu == menu_id).first()
    if menu is None:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    # Delete old image if exists
    if menu.img_menu:
        delete_image(menu.img_menu)
    
    # Upload new image
    img_url = await upload_image(image)
    menu.img_menu = img_url
    
    db.commit()
    db.refresh(menu)
    
    return menu

@router.delete("/{menu_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu(menu_id: int, db: Session = Depends(get_db)):
    """Delete menu item"""
    menu = db.query(Menu).filter(Menu.id_menu == menu_id).first()
    if menu is None:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    # Delete image if exists
    if menu.img_menu:
        delete_image(menu.img_menu)
    
    db.delete(menu)
    db.commit()
    
    return None

@router.get("/search/{query}", response_model=List[MenuResponse])
async def search_menu(query: str, db: Session = Depends(get_db)):
    """Search menu items by name"""
    menu = db.query(Menu).filter(Menu.nama_menu.ilike(f"%{query}%")).all()
    return menu
