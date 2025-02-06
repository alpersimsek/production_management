from sqlalchemy.orm import Session
from sqlalchemy import func
from database.models import (
    User, 
    File, 
    Product, 
    Preset, 
    Rule, 
    PresetRule, 
    FileStatus,
    MaskingMap
)
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
import settings
from storage import FileStorage
from typing import Type, TypeVar, Generic
from fastapi import UploadFile


T = TypeVar("T")


class BaseService(Generic[T]):
    def __init__(self, model: Type[T], session: Session):
        self.model = model
        self.session = session

    def create(self, db_obj: T) -> T:
        self.session.add(db_obj)
        return db_obj
    
    def get_by_id(self, id: int) -> T | None:
        return self.session.get(self.model, id)

    def get_all(self) -> list[T]:
        return self.session.query(self.model).all()

    def update(self, db_obj: T, obj_data: dict) -> T:
        for key, value in obj_data.items():
            setattr(db_obj, key, value)
        return db_obj

    def delete(self, id: int) -> None:
        db_obj = self.get_by_id(id)
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

    def get_by_user(self, user: User) -> list[File]:
        return user.files
    
    def compute_used_space(self, user: User):
        used_space = (
            self.session.query(func.sum(File.file_size))
            .join(User)
            .filter(User.id == user.id)
            .scalar()
        )
        if not used_space:
            used_space = 0
        return used_space

    def save_file(self, storage: FileStorage, file: UploadFile):
        file_id = storage.save_file(file)
        file_obj = File(
                    id=file_id,
                    filename=file.filename,
                    file_size=file.size,
                    content_type=file.content_type,
                    user_id=self.user.id,
                )
        self.create(file_obj)
        
        # files_db = self.add_saved_file(storage, file_id, filename)
        return file_obj

    def add_saved_file(self, storage: FileStorage, file_id, filename):
        files_db = []
        for file_info in storage.unpack(file_id, filename):
            file_obj = File(
                id=file_info.fid,
                filename=file_info.fname,
                total_size=file_info.fsize,
                user_id=self.user.id,
                archive_id = file_info.archive_id
            )
            self.create(file_obj)
            files_db.append(file_obj)
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

    def set_preset(self, file_id: int, preset_id: int):
        """Assigns a preset to a file."""
        file = self.get_by_id(file_id)
        if not file:
            raise Exception("File not found.")
        file.preset_id = preset_id

    def detect_logtype(self, storage, file_info):
        """Guess content type to choose correct processor later."""
        content_type = ContentTypes.DEFAULT
        with storage.get(file_info.fid).open('rb') as file:
            # Get first 3 lines
            header = list(itertools.islice((x.strip() for x in file), 3))
            if header in POSTGRES_TEXT_DUMP_HEADERS:
                content_type = ContentType.POSTGRES_TEXT
        return content_type.value

    def process_file(self, file_id: str, storage: FileStorage):
        file = self.get_by_id(file_id)

        if file.user != self.user:
            raise Exception(f"Something wrong! User {self.user.usename} does not have access to file {file.filename}")

        if file is None:
            raise Exception(f"File {file.filename} could not be found")
        
        ftype = storage.get_type(file.id)
        if ftype in storage.ARCHIVE_TYPES:
            files = []
            # unpack files
            for file_info in storage.unpack(file_id, file.filename):
                file_obj = File(
                    id=file_info.fid,
                    filename=file_info.fname,
                    file_size=file_info.fsize,
                    user_id=self.user.id,
                    archive_id = file_id
                )
                self.create(file_obj)
                files.append(file_obj)
                if self.user.files.count() > settings.MAX_USER_FILES:
                    for file in files:
                        self.delete_file(storage, file.id)
                    raise Exception(
                        f"Files per user limit ({settings.MAX_USER_FILES}) is exceeded"
                    ) 
        """Make task config."""
        if file.status is not FileStatus.CREATED:
            raise Exception("Batch is already started")
        if not self.files.exists():
            raise Exception("No files in a batch")
        if self.files.filter(preset=None).exists():
            file_wo_preset = self.files.filter(preset=None).first()
            raise Exception(f"{file_wo_preset.filename}  has no assigned preset")

        # Create configs for processing
        files = {}
        presets_cfgs = {}
        for file in self.files:
            preset_id = str(file.preset_id)
            if preset_id not in presets_cfgs:
                rules_config, allow_parallel = file.preset.get_rules_config()
                presets_cfgs[preset_id] = (rules_config, allow_parallel)
            files[file.id] = {'cfg_id': preset_id, 'size': file.total_size}
        tasks_config = self._split_to_tasks(files, presets_cfgs)
        return tasks_config


class ProductService(BaseService[Product]):
    def __init__(self, session: Session):
        super().__init__(Product, session)


class PresetService(BaseService[Preset]):
    def __init__(self, session: Session):
        super().__init__(Preset, session)

    def get_rules_config(self):
        """Generate processing config for preset."""
        preset_rules = self.rules.order_by(PresetRule.order.asc())
        config = [x.get_config() for x in preset_rules]
        allow_parallel = all(x.allow_parallel for x in preset_rules)
        return config, allow_parallel


class RuleService(BaseService[Rule]):
    
    TYPE_IPV4_ADDR = 'ipv4_addr'
    TYPE_MAC_ADDR = 'mac_addr'
    TYPE_EMAIL = 'email'
    TYPE_REGEX = 'regex'

    def __init__(self, session: Session):
        super().__init__(Rule, session)

    def get_config(self):
        """Generate rule config to processing."""
        cfg = self.session.query(Rule).filter()
        return self.model.config


class PresetRuleService(BaseService[PresetRule]):
    def __init__(self, session: Session):
        super().__init__(PresetRule, session)

    def get_config(self):
        """Generate rule/action config for preset rule."""
        cfg = self.model.rule.get_config()
        cfg['patcher_cfg'] = self.action
        return cfg
    

class MaskingMapService(BaseService[MaskingMap]):
    """Service class to interact with MaskingMap table."""

    def __init__(self, model: MaskingMap, session: Session):
        super().__init__(model, session)

    def get_masked_value(self, original: str) -> str | None:
        """Check if the original string has an existing masked value."""
        entry = self.session.query(MaskingMap).filter_by(original=original).first()
        return entry.masked if entry else None

    def count_entries(self, data_type: str) -> int:
        """Count number of existing masked values for a given entity type."""
        return self.session.query(MaskingMap).filter_by(data_type=data_type).count()

    def store_masked_value(self, original: str, masked: str, data_type: str):
        """Store a new masked value in the database."""
        new_entry = MaskingMap(original=original, masked=masked, data_type=data_type)
        self.session.add(new_entry)
        self.session.commit()