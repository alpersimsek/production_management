from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
import shutil
from PIL import Image
import logging
from ..db import get_db
from ..models.attachment import Attachment
from ..utils.rbac import RBACManager, Permission
from ..security.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

# Configuration
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"]
ALLOWED_DOCUMENT_TYPES = ["application/pdf", "text/plain", "application/msword"]

def get_rbac_manager(db: Session = Depends(get_db)) -> RBACManager:
    return RBACManager(db)

def ensure_upload_dir():
    """Ensure upload directory exists"""
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

def compress_image(image_path: str, max_size: tuple = (1600, 1600)) -> str:
    """Compress image and return new path"""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            # Resize if too large
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Generate compressed file path
            compressed_path = image_path.replace(".", "_compressed.")
            if not compressed_path.endswith(".jpg"):
                compressed_path = compressed_path.rsplit(".", 1)[0] + ".jpg"
            
            # Save compressed image
            img.save(compressed_path, "JPEG", quality=85, optimize=True)
            
            # Remove original if compression was successful
            if compressed_path != image_path:
                os.remove(image_path)
                return compressed_path
            
            return image_path
    except Exception as e:
        logger.error(f"Image compression failed: {str(e)}")
        return image_path

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    reference_type: str = Form(...),
    reference_id: int = Form(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Upload a file"""
    if not rbac.has_permission(current_user["id"], Permission.FILE_UPLOAD):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Validate file size
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Validate file type
    if file.content_type not in ALLOWED_IMAGE_TYPES + ALLOWED_DOCUMENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not allowed"
        )
    
    ensure_upload_dir()
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    try:
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Compress image if it's an image
        if file.content_type in ALLOWED_IMAGE_TYPES:
            file_path = compress_image(file_path)
            unique_filename = os.path.basename(file_path)
        
        # Create attachment record
        attachment = Attachment(
            reference_type=reference_type,
            reference_id=reference_id,
            file_path=file_path,
            original_filename=file.filename,
            mime_type=file.content_type,
            file_size=os.path.getsize(file_path),
            uploaded_by=current_user["id"]
        )
        
        db.add(attachment)
        db.commit()
        db.refresh(attachment)
        
        return {
            "id": attachment.id,
            "uuid": str(attachment.uuid),
            "filename": attachment.original_filename,
            "file_path": attachment.file_path,
            "mime_type": attachment.mime_type,
            "file_size": attachment.file_size,
            "created_at": attachment.created_at
        }
        
    except Exception as e:
        # Clean up file if database operation fails
        if os.path.exists(file_path):
            os.remove(file_path)
        
        logger.error(f"File upload failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File upload failed"
        )

@router.post("/upload-multiple")
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    reference_type: str = Form(...),
    reference_id: int = Form(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Upload multiple files"""
    if not rbac.has_permission(current_user["id"], Permission.FILE_UPLOAD):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    if len(files) > 10:  # Limit to 10 files per request
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 files allowed per request"
        )
    
    uploaded_files = []
    failed_files = []
    
    for file in files:
        try:
            # Validate file size
            if file.size > MAX_FILE_SIZE:
                failed_files.append({
                    "filename": file.filename,
                    "error": f"File size exceeds maximum allowed size of {MAX_FILE_SIZE // (1024*1024)}MB"
                })
                continue
            
            # Validate file type
            if file.content_type not in ALLOWED_IMAGE_TYPES + ALLOWED_DOCUMENT_TYPES:
                failed_files.append({
                    "filename": file.filename,
                    "error": "File type not allowed"
                })
                continue
            
            ensure_upload_dir()
            
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(UPLOAD_DIR, unique_filename)
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Compress image if it's an image
            if file.content_type in ALLOWED_IMAGE_TYPES:
                file_path = compress_image(file_path)
                unique_filename = os.path.basename(file_path)
            
            # Create attachment record
            attachment = Attachment(
                reference_type=reference_type,
                reference_id=reference_id,
                file_path=file_path,
                original_filename=file.filename,
                mime_type=file.content_type,
                file_size=os.path.getsize(file_path),
                uploaded_by=current_user["id"]
            )
            
            db.add(attachment)
            db.commit()
            db.refresh(attachment)
            
            uploaded_files.append({
                "id": attachment.id,
                "uuid": str(attachment.uuid),
                "filename": attachment.original_filename,
                "file_path": attachment.file_path,
                "mime_type": attachment.mime_type,
                "file_size": attachment.file_size,
                "created_at": attachment.created_at
            })
            
        except Exception as e:
            # Clean up file if database operation fails
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
            
            logger.error(f"File upload failed for {file.filename}: {str(e)}")
            failed_files.append({
                "filename": file.filename,
                "error": "Upload failed"
            })
    
    return {
        "uploaded_files": uploaded_files,
        "failed_files": failed_files,
        "total_uploaded": len(uploaded_files),
        "total_failed": len(failed_files)
    }

@router.get("/{attachment_id}")
async def get_file(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Get file information"""
    if not rbac.has_permission(current_user["id"], Permission.FILE_DOWNLOAD):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return {
        "id": attachment.id,
        "uuid": str(attachment.uuid),
        "filename": attachment.original_filename,
        "mime_type": attachment.mime_type,
        "file_size": attachment.file_size,
        "reference_type": attachment.reference_type,
        "reference_id": attachment.reference_id,
        "uploaded_by": attachment.uploaded_by,
        "created_at": attachment.created_at
    }

@router.get("/{attachment_id}/download")
async def download_file(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Download file"""
    if not rbac.has_permission(current_user["id"], Permission.FILE_DOWNLOAD):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    if not os.path.exists(attachment.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk"
        )
    
    from fastapi.responses import FileResponse
    
    return FileResponse(
        path=attachment.file_path,
        filename=attachment.original_filename,
        media_type=attachment.mime_type
    )

@router.delete("/{attachment_id}")
async def delete_file(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Delete file"""
    if not rbac.has_permission(current_user["id"], Permission.FILE_DELETE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    try:
        # Delete file from disk
        if os.path.exists(attachment.file_path):
            os.remove(attachment.file_path)
        
        # Delete from database
        db.delete(attachment)
        db.commit()
        
        return {"message": "File deleted successfully"}
        
    except Exception as e:
        logger.error(f"File deletion failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File deletion failed"
        )

@router.get("/reference/{reference_type}/{reference_id}")
async def get_files_by_reference(
    reference_type: str,
    reference_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Get all files for a specific reference"""
    if not rbac.has_permission(current_user["id"], Permission.FILE_DOWNLOAD):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    attachments = db.query(Attachment).filter(
        Attachment.reference_type == reference_type,
        Attachment.reference_id == reference_id
    ).all()
    
    return [
        {
            "id": attachment.id,
            "uuid": str(attachment.uuid),
            "filename": attachment.original_filename,
            "mime_type": attachment.mime_type,
            "file_size": attachment.file_size,
            "uploaded_by": attachment.uploaded_by,
            "created_at": attachment.created_at
        }
        for attachment in attachments
    ]
