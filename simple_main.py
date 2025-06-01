import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import mahasiswa, kantin, menu, pesanan, detail_pesanan

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="University Canteen API",
    description="FastAPI backend untuk sistem pemesanan kantin universitas dengan MinIO storage",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers untuk semua operasi CRUD
app.include_router(mahasiswa.router, prefix="/api/v1/mahasiswa", tags=["Mahasiswa"])
app.include_router(kantin.router, prefix="/api/v1/kantin", tags=["Kantin"])
app.include_router(menu.router, prefix="/api/v1/menu", tags=["Menu"])
app.include_router(pesanan.router, prefix="/api/v1/pesanan", tags=["Pesanan"])
app.include_router(detail_pesanan.router, prefix="/api/v1/detail-pesanan", tags=["Detail Pesanan"])

@app.get("/")
async def root():
    return {
        "message": "University Canteen API",
        "description": "API CRUD lengkap untuk sistem kantin universitas",
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "running",
        "endpoints": {
            "mahasiswa": "/api/v1/mahasiswa",
            "kantin": "/api/v1/kantin", 
            "menu": "/api/v1/menu",
            "pesanan": "/api/v1/pesanan",
            "detail_pesanan": "/api/v1/detail-pesanan"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

if __name__ == "__main__":
    uvicorn.run(
        "simple_main:app",
        host="0.0.0.0",
        port=5000,
        reload=True
    )