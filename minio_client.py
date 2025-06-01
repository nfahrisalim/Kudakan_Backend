import os
from minio import Minio
from minio.error import S3Error
from fastapi import HTTPException, UploadFile
import uuid
from typing import Optional

# MinIO configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"
BUCKET_NAME = "menu-images"

# Initialize MinIO client
minio_client = None

def get_minio_client():
    global minio_client
    if minio_client is None:
        minio_client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=MINIO_SECURE,
        )
    return minio_client

def init_minio():
    """Initialize MinIO bucket if it doesn't exist"""
    try:
        client = get_minio_client()
        
        # Check if bucket exists, create if not
        if not client.bucket_exists(BUCKET_NAME):
            client.make_bucket(BUCKET_NAME)
            print(f"Created bucket: {BUCKET_NAME}")
        else:
            print(f"Bucket {BUCKET_NAME} already exists")
            
    except S3Error as e:
        print(f"Error initializing MinIO: {e}")
    except Exception as e:
        print(f"MinIO connection error: {e}")
        print("MinIO will be initialized when first used")

async def upload_image(file: UploadFile) -> str:
    """Upload image to MinIO and return the URL"""
    try:
        client = get_minio_client()
        
        # Validate file type
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file.content_type} not allowed. Allowed types: {allowed_types}"
            )
        
        # Generate unique filename
        if file.filename and "." in file.filename:
            file_extension = file.filename.split(".")[-1]
        else:
            file_extension = "jpg"
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Upload to MinIO
        from io import BytesIO
        client.put_object(
            BUCKET_NAME,
            unique_filename,
            BytesIO(file_content),
            file_size,
            content_type=file.content_type
        )
        
        # Return the URL
        if MINIO_SECURE:
            protocol = "https"
        else:
            protocol = "http"
            
        return f"{protocol}://{MINIO_ENDPOINT}/{BUCKET_NAME}/{unique_filename}"
        
    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

def delete_image(image_url: str) -> bool:
    """Delete image from MinIO"""
    try:
        client = get_minio_client()
        
        # Extract filename from URL
        filename = image_url.split("/")[-1]
        
        # Delete from MinIO
        client.remove_object(BUCKET_NAME, filename)
        return True
        
    except S3Error as e:
        print(f"Error deleting file: {e}")
        return False

def get_image_url(filename: str) -> str:
    """Get presigned URL for image"""
    try:
        client = get_minio_client()
        
        # Generate presigned URL (valid for 24 hours)
        from datetime import timedelta
        url = client.presigned_get_object(BUCKET_NAME, filename, expires=timedelta(seconds=86400))
        return url
        
    except S3Error as e:
        raise HTTPException(status_code=404, detail=f"Image not found: {str(e)}")
