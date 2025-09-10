"""
GDPR Tool Files Router - File Management API Endpoints

This module provides REST API endpoints for file management operations in the GDPR compliance tool.
It handles file upload, processing, download, and deletion with comprehensive security features.

Key Endpoints:
- GET /files/: Retrieve user's uploaded files
- POST /files/upload: Upload new files with storage limit validation
- POST /files/process/{file_id}: Process files with product-based or default processing
- DELETE /files/delete/{file_id}: Delete specific files
- DELETE /files/all_delete: Admin endpoint to delete all files
- GET /files/download/{file_id}: Download files with token-based authentication
- GET /files/get_download_url/{file_id}: Generate signed download URLs

File Processing Features:
- Product-Based Processing: New system for product-specific preset selection and rule application
- Default Processing: Fallback to traditional preset-based processing
- Archive Support: Handles ZIP, TAR, and other archive formats with recursive extraction
- Progress Tracking: Real-time processing status and progress updates
- Error Handling: Comprehensive error handling with detailed error messages

Security Features:
- JWT Token Authentication: All endpoints require valid authentication tokens
- Signed URLs: Secure file download with time-limited JWT tokens
- Admin Access Control: Admin-only endpoints for system management
- Storage Limits: User storage quota enforcement
- File Validation: File type and size validation

File Operations:
- Upload: Multi-format file upload with type detection
- Processing: Intelligent preset selection based on product and file headers
- Download: Secure file download with token validation
- Deletion: Safe file removal with proper cleanup
- Management: User file listing and admin bulk operations

The router integrates with the FileService for business logic and FileStorage for
file operations, providing a secure and efficient file management system.
"""

from fastapi import APIRouter, UploadFile, HTTPException, Request, status, Body
from fastapi.responses import StreamingResponse, JSONResponse
import urllib.parse
from storage import FileStorage
from services import FileService
from api.schemas import FileResponse
import settings
from typing import Dict, Optional
from database.models import Role
from logger import logger

router = APIRouter()


class FilesRouter(APIRouter):

    def __init__(self, storage: FileStorage):
        self.storage = storage
        super().__init__()
        self.prefix = "/files"

        # Routes
        self.get("/", response_model=list[FileResponse])(self.get_user_files)
        self.post("/upload", response_model=FileResponse)(self.upload_file)
        self.post("/process/{file_id}")(self.process_file)
        self.post("/cancel/{file_id}")(self.cancel_file_processing)
        self.delete("/delete/{file_id}")(self.delete_file)
        self.get("/download/{file_id}")(self.download_file)
        self.delete("/all_delete")(self.delete_all_files)  # New endpoint
        self.get("/get_download_url/{file_id}")(self.get_download_url)

    def upload_file(self, req: Request, file: UploadFile):
        try:
            user = req.state.user
            session = req.state.db
            file_service = FileService(session, user, self.storage)

            if file_service.compute_used_space() > settings.USER_STORAGE_LIMIT:
                raise HTTPException(
                    status.HTTP_507_INSUFFICIENT_STORAGE, f"Not enough free space"
                )

            file_obj = file_service.save_file(file)
            
            # Log successful upload
            logger.info({
                "event": "file_uploaded",
                "filename": file.filename,
                "file_size": file_obj.file_size,
                "file_type": file_obj.content_type.value,
                "username": user.username
            })
            
            return FileResponse.model_validate(file_obj)
        except HTTPException as ex:
            raise ex
        except Exception as ex:
            logger.error({
                "event": "file_upload_failed",
                "filename": file.filename if file else "unknown",
                "error": str(ex)
            })
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex)
            )

    def get_user_files(self, req: Request):
        user = req.state.user
        file_service = FileService(req.state.db, user, self.storage)
        try:
            files = file_service.get_by_user()
            return [FileResponse.model_validate(file) for file in files]
        except HTTPException as ex:
            raise ex
        except Exception as ex:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))

    def delete_file(self, file_id: str, req: Request):
        try:
            user = req.state.user
            session = req.state.db
            file_service = FileService(session, user, self.storage)
            
            # Get file info before deletion for logging
            file_obj = file_service.get_by_id(file_id)
            if not file_obj:
                logger.warning({
                    "event": "file_delete_failed",
                    "filename": f"file_id_{file_id}",
                    "username": user.username,
                    "reason": "file_not_found"
                })
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="File not found"
                )
            
            file_service.delete_file(file_id)
            
            # Log successful deletion
            logger.info({
                "event": "file_deleted",
                "filename": file_obj.filename,
                "file_size": file_obj.file_size,
                "file_type": file_obj.content_type.value,
                "username": user.username
            })
            
        except HTTPException as ex:
            raise ex
        except Exception as ex:
            logger.error({
                "event": "file_delete_failed",
                "filename": f"file_id_{file_id}",
                "username": user.username,
                "error": str(ex)
            })
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex)
            )

    def delete_all_files(self, req: Request):
        """Delete all files for all users. Admin access required."""
        try:
            if not req.state.user or req.state.user.role != Role.ADMIN:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
                )

            session = req.state.db
            file_service = FileService(session, req.state.user, self.storage)
            files = file_service.get_all()
            if not files:
                return JSONResponse({"message": "No files to delete"})

            for file in files:
                file_service.delete_file(file.id)
            
            return JSONResponse({"message": "All files deleted successfully"})
        except HTTPException as ex:
            raise ex
        except Exception as ex:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))
    
    def download_file(self, file_id: str, req: Request, token: str):
        """Download file with a token"""
        try:
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Token is required"
                )

            session = req.state.db
            file_service = FileService(session, None, self.storage)
            # Verify the token
            payload = file_service.validate_token(token)
            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid or expired download token",
                )

            if payload.get("sub") != "file_download":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid token purpose",
                )

            if payload.get("file_id") != file_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File ID mismatch",
                )

            file_obj = file_service.get_by_id(file_id)

            if not file_obj:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND,
                    detail=f"File with ID {file_id} not found",
                )

            file_stream = self.storage.get(file_obj.id).open("rb")

            # Encode filename properly for download
            filename = urllib.parse.quote(file_obj.filename)
            
            # Log successful download
            logger.info({
                "event": "file_downloaded",
                "filename": file_obj.filename,
                "file_size": file_obj.file_size,
                "file_type": file_obj.content_type.value,
                "username": payload.get("username", "unknown")
            })

            return StreamingResponse(
                file_stream,
                media_type="application/octet-stream",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}",
                    "Content-Length": str(file_obj.file_size),
                },
            )
        except HTTPException as ex:
            raise ex
        except Exception as ex:
            logger.error({
                "event": "file_download_failed",
                "filename": f"file_id_{file_id}",
                "error": str(ex)
            })
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex)
            )

    # Generate signed URL endpoint
    def get_download_url(self, file_id: str, req: Request) -> Dict[str, str]:
        """Generate a JWT-based signed URL for file download"""
        try:
            user = req.state.user
            session = req.state.db
            file_service = FileService(session, user, self.storage)
            file_obj = file_service.get_by_id(file_id)

            if not file_obj:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND,
                    detail=f"File with ID {file_id} not found",
                )

            token = file_service.create_token(
                data={"file_id": file_id, "sub": "file_download", "username": user.username},
                expires_delta=settings.SIGNED_URL_EXPIRY_MINUTES,
            )

            # Build the signed URL with JWT token
            base_url = str(req.base_url).rstrip("/")
            signed_url = f"{base_url}/api/v1/files/download/{file_id}?token={token}"
            
            # Log download URL generation
            logger.info({
                "event": "download_url_generated",
                "filename": file_obj.filename,
                "file_size": file_obj.file_size,
                "file_type": file_obj.content_type.value,
                "username": user.username,
                "expires_in_minutes": settings.SIGNED_URL_EXPIRY_MINUTES
            })

            return {"signedUrl": signed_url}

        except HTTPException as ex:
            raise ex
        except Exception as ex:
            logger.error({
                "event": "download_url_generation_failed",
                "filename": f"file_id_{file_id}",
                "username": user.username if user else "unknown",
                "error": str(ex)
            })
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex)
            )

    # Start file processing
    def process_file(self, req: Request, file_id: str, process_options: Optional[dict] = Body(None)):
        try:
            user = req.state.user
            session = req.state.db
            file_service = FileService(session, user, self.storage)
            
            if process_options and process_options.get('productId'):
                # Product-based processing
                file = file_service.process_file_with_product(file_id, process_options['productId'])
            else:
                # Default processing (fallback)
                file = file_service.process_file(file_id)
                
            return {"detail": f"Processing {file.filename} completed"}
        except Exception as ex:
            logger.error({
                "event": "file_processing_failed",
                "file_id": file_id,
                "error": str(ex)
            })
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex)
            )

    def cancel_file_processing(self, file_id: str, req: Request):
        """Cancel file processing and set status to CANCELLED."""
        try:
            user = req.state.user
            session = req.state.db
            file_service = FileService(session)
            
            # Cancel the file processing
            file = file_service.cancel_file_processing(file_id)
            
            return {"detail": f"Processing of {file.filename} cancelled"}
        except Exception as ex:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex)
            )
