from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class StatusPesananEnum(enum.Enum):
    proses = "proses"
    selesai = "selesai"

class Mahasiswa(Base):
    __tablename__ = "mahasiswa"
    
    id_mahasiswa = Column(Integer, primary_key=True, index=True)
    nama = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    nim = Column(String(50), nullable=False)
    
    # Relationships
    pesanan = relationship("Pesanan", back_populates="mahasiswa")

class Kantin(Base):
    __tablename__ = "kantin"
    
    id_kantin = Column(Integer, primary_key=True, index=True)
    nama_kantin = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    
    # Relationships
    menu = relationship("Menu", back_populates="kantin")
    pesanan = relationship("Pesanan", back_populates="kantin")

class Menu(Base):
    __tablename__ = "menu"
    
    id_menu = Column(Integer, primary_key=True, index=True)
    id_kantin = Column(Integer, ForeignKey("kantin.id_kantin"), nullable=False)
    nama_menu = Column(String(255), nullable=False)
    harga = Column(Numeric(10, 2), nullable=False)
    img_menu = Column(String(500), nullable=True) 
    
    # Relationships
    kantin = relationship("Kantin", back_populates="menu")
    detail_pesanan = relationship("DetailPesanan", back_populates="menu")

class Pesanan(Base):
    __tablename__ = "pesanan"
    
    id_pesanan = Column(Integer, primary_key=True, index=True)
    id_kantin = Column(Integer, ForeignKey("kantin.id_kantin"), nullable=False)
    id_mahasiswa = Column(Integer, ForeignKey("mahasiswa.id_mahasiswa"), nullable=False)
    tanggal = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Enum(StatusPesananEnum), nullable=False, default=StatusPesananEnum.proses)
    
    # Relationships
    kantin = relationship("Kantin", back_populates="pesanan")
    mahasiswa = relationship("Mahasiswa", back_populates="pesanan")
    detail_pesanan = relationship("DetailPesanan", back_populates="pesanan")

class DetailPesanan(Base):
    __tablename__ = "detail_pesanan"
    
    id_detail = Column(Integer, primary_key=True, index=True)
    id_pesanan = Column(Integer, ForeignKey("pesanan.id_pesanan"), nullable=False)
    id_menu = Column(Integer, ForeignKey("menu.id_menu"), nullable=False)
    jumlah = Column(Integer, nullable=False)
    harga_total = Column(Numeric(10, 2), nullable=False)
    
    # Relationships
    pesanan = relationship("Pesanan", back_populates="detail_pesanan")
    menu = relationship("Menu", back_populates="detail_pesanan")
