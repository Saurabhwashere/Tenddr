# Supabase Storage Operations for PDFs
# Upload, download, and manage PDF files

import os
import hashlib
from typing import Optional, BinaryIO
from supabase_client import get_supabase_client

STORAGE_BUCKET = "contract-pdfs"

def calculate_file_hash(file_content: bytes) -> str:
    """Calculate SHA-256 hash of file content for duplicate detection."""
    return hashlib.sha256(file_content).hexdigest()

def upload_pdf(
    contract_id: str,
    file_content: bytes,
    filename: str
) -> str:
    """
    Upload PDF to Supabase Storage.
    
    Args:
        contract_id: Unique contract identifier
        file_content: PDF file bytes
        filename: Original filename
        
    Returns: Storage path
    """
    supabase = get_supabase_client()
    
    # Create storage path: contract-id/filename.pdf
    storage_path = f"{contract_id}/{filename}"
    
    try:
        # Upload to Supabase Storage
        supabase.storage.from_(STORAGE_BUCKET).upload(
            path=storage_path,
            file=file_content,
            file_options={"content-type": "application/pdf"}
        )
        
        print(f"✅ Uploaded PDF to storage: {storage_path}")
        return storage_path
        
    except Exception as e:
        print(f"❌ Storage upload error: {e}")
        raise

def download_pdf(storage_path: str) -> bytes:
    """
    Download PDF from Supabase Storage.
    
    Args:
        storage_path: Path in storage bucket
        
    Returns: PDF file bytes
    """
    supabase = get_supabase_client()
    
    try:
        # Download from Supabase Storage
        response = supabase.storage.from_(STORAGE_BUCKET).download(storage_path)
        return response
        
    except Exception as e:
        print(f"❌ Storage download error: {e}")
        raise

def get_pdf_url(storage_path: str, expires_in: int = 3600) -> str:
    """
    Get a signed URL for PDF access (expires after 1 hour by default).
    
    Args:
        storage_path: Path in storage bucket
        expires_in: Expiration time in seconds
        
    Returns: Signed URL
    """
    supabase = get_supabase_client()
    
    try:
        # Create signed URL (private access)
        response = supabase.storage.from_(STORAGE_BUCKET).create_signed_url(
            path=storage_path,
            expires_in=expires_in
        )
        
        return response.get("signedURL")
        
    except Exception as e:
        print(f"❌ Error creating signed URL: {e}")
        raise

def delete_pdf(storage_path: str) -> bool:
    """
    Delete PDF from Supabase Storage.
    
    Args:
        storage_path: Path in storage bucket
        
    Returns: True if successful
    """
    supabase = get_supabase_client()
    
    try:
        supabase.storage.from_(STORAGE_BUCKET).remove([storage_path])
        print(f"🗑️  Deleted PDF from storage: {storage_path}")
        return True
        
    except Exception as e:
        print(f"❌ Storage delete error: {e}")
        return False

