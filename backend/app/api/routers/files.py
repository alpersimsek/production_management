from fastapi import APIRouter, UploadFile, HTTPException, Request, status
from fastapi.responses import StreamingResponse, JSONResponse
import urllib.parse
from storage import FileStorage
from services import FileService
from api.schemas import FileResponse
import settings
from typing import Dict
from database.models import Role

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
            return FileResponse.model_validate(file_obj)
        except HTTPException as ex:
            raise ex
        except Exception as ex:
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
            file_service.delete_file(file_id)
        except Exception as ex:
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
                data={"file_id": file_id, "sub": "file_download"},
                expires_delta=settings.SIGNED_URL_EXPIRY_MINUTES,
            )

            # Build the signed URL with JWT token
            base_url = str(req.base_url).rstrip("/")
            signed_url = f"{base_url}/api/v1/files/download/{file_id}?token={token}"

            return {"signedUrl": signed_url}

        except HTTPException as ex:
            raise ex
        except Exception as ex:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex)
            )

    # Start file processing
    def process_file(self, req: Request, file_id: str):
        try:
            user = req.state.user
            session = req.state.db
            file_service = FileService(session, user, self.storage)
            file = file_service.process_file(file_id)
            return {"detail": f"Processing {file.filename} completed"}
        except Exception as ex:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex)
            )
