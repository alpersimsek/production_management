from fastapi import APIRouter, UploadFile, HTTPException, Request, status, Depends
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
        self.post("/")(self.get_user_files)
        self.post("/upload", response_model=FileResponse)(self.upload_file)
        self.post("/process/{file_id}")(self.process_file)
        self.delete("/delete/{file_id}")(self.delete_file)
        self.get("/download/{file_id}")(self.download_file)

    def upload_file(self, req: Request, file: UploadFile):
        try:
            user = req.state.user
            session = req.state.db
            file_service = FileService(session=session, user=user)
            
            if file_service.compute_used_space(user) > settings.USER_FILES_SIZE_LIMIT:
                raise HTTPException(status.HTTP_507_INSUFFICIENT_STORAGE, f"Not enough free space")
            
            file_obj = file_service.save_file(self.storage, file)
            return FileResponse.model_validate(file_obj)
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="")

    def get_user_files(self, req: Request):
        user = req.state.user
        session = req.state.db
        file_service = FileService(session=session, user=user)
        try:
            files = file_service.get_by_user(user)
        except:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"No files found for user {user.username}")
        return files

    def delete_file(self, filename: str, req: Request):
        try:
            user = req.state.user
            session = req.state.db
            file_service = FileService(session=session, user=user)
            # TODO
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="")

    def download_file(self, filename: str, req: Request):
        try:
            user = req.state.user
            session = req.state.db
            file_service = FileService(session=session, user=user)
            # TODO
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="")

    # Start file processing
    def process_file(self, req: Request, file_id: str):
        try:
            user = req.state.user
            session = req.state.db
            file_service = FileService(session=session, user=user)
            file_service.process_file(file_id)
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="")
