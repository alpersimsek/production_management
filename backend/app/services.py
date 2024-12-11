from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.models import User, File
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
import settings
from storage import FileStorage
from typing import Type, TypeVar, Generic


T = TypeVar("T")


class BaseService(Generic[T]):
    def __init__(self, model: Type[T], session: Session):
        self.model = model
        self.session = session

    def get_by_id(self, id: int) -> T | None:
        return self.session.query(self.model).get(id)

    def get_all(self) -> list[T]:
        return self.session.query(self.model).all()

    def create(self, db_obj: T) -> T:
        self.session.add(db_obj)
        return db_obj

    def update(self, db_obj: T, obj_data: dict) -> T:
        for key, value in obj_data.items():
            setattr(db_obj, key, value)
        return db_obj

    def delete(self, id: int) -> None:
        db_obj = self.get(id)
        if db_obj:
            self.session.delete(db_obj)


class UserService(BaseService[User]):
    def __init__(self, session: Session):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        super().__init__(User, session)

    def get_user_by_id(self, user_id: str) -> User:
        return self.get_by_id(user_id)

    def get_user_by_username(self, username: str) -> User | None:
        return self.session.query(User).filter(User.username == username).first()
        
    def get_users(self) -> list[User]:
        return self.get_all()

    def create_user(self, username: str, password: str, role: str) -> User | None:
        user = User(username=username, role=role)
        user.password = self.hash_password(password=password)
        self.create(user)
        return user
    
    def update_password(self, username, password) -> None:
        user = self.get_user_by_username(username)
        if not user:
            return None
        data = dict(password=self.hash_password(password))
        return self.update(user, data)

    def delete_user(self, session: Session, username: str) -> None:
        user = self.get_user_by_username(username)
        if user:
            session.delete(user)

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_token(self, data: dict, expires_delta: timedelta = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.TOKEN_EXPIRE_MINUTES
            )
        to_encode.update({"exp": expire})
        token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return token

    def authenticate(self, username: str, password: str) -> User | None:
        user = self.get_user_by_username(username)
        if not user:
            return None
        if not self.verify_password(password, user.password):
            return None
        return user
    

class FileService(BaseService[File]):
    def __init__(self, user: User, session: Session):
        self.user = user
        super().__init__(File, session)

    def save_file(self, storage: FileStorage, file, filename):
        file_id = storage.save_file(file)
        files_db = self.add_saved_file(storage, file_id, filename)
        return files_db

    def add_saved_file(self, storage: FileStorage, file_id, filename):
        files_db = []
        for file_info in storage.unpack(file_id, filename):
            file_obj = File(
                id=file_info.fid,
                filename=file_info.fname,
                total_size=file_info.fsize,
                user_id=self.user.id
            )
            files_db.append(file_obj)
            # file_count = (
            #     self.session.query(func.count(File.id))
            #     .join(User)
            #     .filter(User.id == self.user.files.co)
            #     .scalar()
            # )
            if self.user.files.count() > settings.MAX_USER_FILES:
                for file in files_db:
                    self.delete_file(storage, file.id)
                raise Exception(
                    f"Files per user limit ({settings.MAX_USER_FILES}) is exceeded"
                )
        return files_db

    def delete_file(self, storage, file_id):
        """Delete file from the storage."""
        storage.delete(file_id)

    def set_preset(self, preset):
        """Set preset to file."""
        pass

    def process_file(self, file_id: str, storage: FileStorage):
        pass
