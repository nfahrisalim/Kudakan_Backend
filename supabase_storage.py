import os
import uuid
from fastapi import UploadFile, HTTPException
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_BUCKET_NAME = os.getenv("SUPABASE_BUCKET_NAME", "menu-images")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError("Missing Supabase credentials in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

async def upload_image(file: UploadFile) -> str:
    try:
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Invalid image format.")

        ext = file.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        data = await file.read()

        res = supabase.storage.from_(SUPABASE_BUCKET_NAME).upload(
            path=filename,
            file=data,
            file_options={"content-type": file.content_type},
        )

        if "error" in res:
            raise Exception(res["error"]["message"])

        public_url = supabase.storage.from_(SUPABASE_BUCKET_NAME).get_public_url(filename)
        return public_url

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


def delete_image(public_url: str) -> bool:
    try:
        filename = public_url.split("/")[-1]
        supabase.storage.from_(SUPABASE_BUCKET_NAME).remove([filename])
        return True
    except Exception as e:
        print(f"Delete failed: {e}")
        return False
