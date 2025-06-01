import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import engine, Base
from routers import mahasiswa, kantin, menu, pesanan, detail_pesanan
from minio_client import init_minio

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="University Canteen API",
    description="FastAPI backend for university canteen ordering system with MinIO storage",
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

# Initialize MinIO (optional - will retry when needed)
try:
    init_minio()
except Exception as e:
    print(f"MinIO not available at startup: {e}")

# Include routers
app.include_router(mahasiswa.router, prefix="/api/v1/mahasiswa", tags=["Mahasiswa"])
app.include_router(kantin.router, prefix="/api/v1/kantin", tags=["Kantin"])
app.include_router(menu.router, prefix="/api/v1/menu", tags=["Menu"])
app.include_router(pesanan.router, prefix="/api/v1/pesanan", tags=["Pesanan"])
app.include_router(detail_pesanan.router, prefix="/api/v1/detail-pesanan", tags=["Detail Pesanan"])

@app.get("/")
async def root():
    return {
        "message": "University Canteen API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=True
    )
