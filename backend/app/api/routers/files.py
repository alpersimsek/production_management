from fastapi import APIRouter, UploadFile, HTTPException, Request, status
from storage import FileStorage
from services import FileService


router = APIRouter()

class FilesRouter(APIRouter):

    def __init__(self, storage: FileStorage):
        self.storage = storage
        super().__init__()

        # Routes
        self.post("/upload")(self.upload_file)
        self.post("/{username}")(self.get_user_files)
        self.delete("/delete/{username}/{filename}")(self.delete_file)
        self.get("/download/{username}/{filename}")(self.download_file)
        self.post("/process/{filename}")(self.process_file)

    def upload_file(self, file: UploadFile, req: Request):
        try:
            user = req.state.user
            session = req.state.db
            file_service = FileService(session=session, user=user)
            return file_service.save_file(self.storage, file, file.filename)
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="")

    def get_user_files(self, req: Request):
        try:
            user = req.state.user
            session = req.state.db
            file_service = FileService(session=session, user=user)
            # TODO
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="")

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
    def process_file(self, filename: str, req: Request):
        try:
            user = req.state.user
            session = req.state.db
            file_service = FileService(session=session, user=user)
            # TODO
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="")
