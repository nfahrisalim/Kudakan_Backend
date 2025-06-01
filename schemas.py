from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from enum import Enum

class StatusPesananEnum(str, Enum):
    proses = "proses"
    selesai = "selesai"

# Mahasiswa schemas
class MahasiswaBase(BaseModel):
    nama: str
    email: EmailStr
    nim: str

class MahasiswaCreate(MahasiswaBase):
    password: str

class MahasiswaUpdate(BaseModel):
    nama: Optional[str] = None
    email: Optional[EmailStr] = None
    nim: Optional[str] = None
    password: Optional[str] = None

class MahasiswaResponse(MahasiswaBase):
    id_mahasiswa: int
    
    class Config:
        from_attributes = True

# Kantin schemas
class KantinBase(BaseModel):
    nama_kantin: str
    email: EmailStr

class KantinCreate(KantinBase):
    password: str

class KantinUpdate(BaseModel):
    nama_kantin: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class KantinResponse(KantinBase):
    id_kantin: int
    
    class Config:
        from_attributes = True

# Menu schemas
class MenuBase(BaseModel):
    nama_menu: str
    harga: Decimal
    img_menu: Optional[str] = None

class MenuCreate(MenuBase):
    id_kantin: int

class MenuUpdate(BaseModel):
    nama_menu: Optional[str] = None
    harga: Optional[Decimal] = None
    img_menu: Optional[str] = None

class MenuResponse(MenuBase):
    id_menu: int
    id_kantin: int
    
    class Config:
        from_attributes = True

# Pesanan schemas
class PesananBase(BaseModel):
    id_kantin: int
    id_mahasiswa: int
    status: StatusPesananEnum = StatusPesananEnum.proses

class PesananCreate(PesananBase):
    pass

class PesananUpdate(BaseModel):
    status: Optional[StatusPesananEnum] = None

class PesananResponse(PesananBase):
    id_pesanan: int
    tanggal: datetime
    
    class Config:
        from_attributes = True

# Detail Pesanan schemas
class DetailPesananBase(BaseModel):
    id_menu: int
    jumlah: int
    harga_total: Decimal

class DetailPesananCreate(DetailPesananBase):
    id_pesanan: int

class DetailPesananUpdate(BaseModel):
    jumlah: Optional[int] = None
    harga_total: Optional[Decimal] = None

class DetailPesananResponse(DetailPesananBase):
    id_detail: int
    id_pesanan: int
    
    class Config:
        from_attributes = True

# Complex response schemas with relationships
class PesananWithDetails(PesananResponse):
    detail_pesanan: List[DetailPesananResponse] = []
    mahasiswa: Optional[MahasiswaResponse] = None
    kantin: Optional[KantinResponse] = None

class MenuWithKantin(MenuResponse):
    kantin: Optional[KantinResponse] = None

class KantinWithMenus(KantinResponse):
    menu: List[MenuResponse] = []
