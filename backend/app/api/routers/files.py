from fastapi import APIRouter, UploadFile, HTTPException, Request, status
from fastapi.responses import StreamingResponse
import urllib.parse
from storage import FileStorage
from services import FileService
from api.schemas import FileResponse
import settings


router = APIRouter()

class FilesRouter(APIRouter):

    def __init__(self, storage: FileStorage):
        self.storage = storage
        super().__init__()

        # Routes
        self.get("/", response_model=list[FileResponse])(self.get_user_files)
        self.post("/upload", response_model=FileResponse)(self.upload_file)
        self.post("/process/{file_id}")(self.process_file)
        self.delete("/delete/{file_id}")(self.delete_file)
        self.get("/download/{file_id}")(self.download_file)

    def upload_file(self, req: Request, file: UploadFile):
        try:
            user = req.state.user
            session = req.state.db
            file_service = FileService(session, user, self.storage)
            
            if file_service.compute_used_space() > settings.USER_STORAGE_LIMIT:
                raise HTTPException(status.HTTP_507_INSUFFICIENT_STORAGE, f"Not enough free space")
            
            file_obj = file_service.save_file(file)
            return FileResponse.model_validate(file_obj)
        except HTTPException as ex:
            raise ex
        except Exception as ex:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))

    def get_user_files(self, req: Request):
        user = req.state.user
        try:
            files = user.files
            if not files:
                raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"No files found for user {user.username}")
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
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))

    def download_file(self, file_id: str, req: Request):
        try:
            user = req.state.user
            session = req.state.db
            file_service = FileService(session, user, self.storage)
            file_obj = file_service.get_by_id(file_id)
            if not file_obj:
                raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"File with ID {file_id} not found")
            file_path = self.storage.get(file_obj.id)
            file_stream = file_path.open("rb")
        
            # Encode filename properly for download
            filename = urllib.parse.quote(file_obj.filename)

            return StreamingResponse(
                file_stream,
                media_type="application/octet-stream",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        except HTTPException as ex:
            raise ex
        except Exception as ex:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))

    # Start file processing
    def process_file(self, req: Request, file_id: str):
        try:
            user = req.state.user
            session = req.state.db
            file_service = FileService(session, user, self.storage)
            file = file_service.process_file(file_id)
            return {"detail": f"Processing {file.filename} completed"}
        except Exception as ex:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))
