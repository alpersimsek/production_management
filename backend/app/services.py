from sqlalchemy.orm import Session
from sqlalchemy import func, literal
from database.models import (
    User,
    File,
    Product,
    Preset,
    Rule,
    PresetRule,
    FileStatus,
    MaskingMap,
    Role,
    ContentType,
    RuleCategory,
)
from gdpr.processors import BaseProcessor, TextProcessor
from gdpr.matchers import RegexpMatcher, IPAddrMatcher, MacAddrMatcher
from gdpr.patchers import ReplacePatcher
import collections
import pathlib
import time
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
import settings
from storage import FileStorage, FileInfo
from typing import Optional, Type, TypeVar, Generic, Dict, List, Sequence, Mapping, Any
from fastapi import UploadFile
from logger import logger
from charset_normalizer import from_path
from sqlalchemy import or_


T = TypeVar("T")


class ProcessingConfig:
    """Processign config class."""

    MATCHER_MAP = {
        "regex": RegexpMatcher,
        "ip_addr": IPAddrMatcher,
        "mac_addr": MacAddrMatcher,
    }

    PATCHERS_MAP = {
        "replace": ReplacePatcher,
    }

    # Content type -> processor class maping
    PROC_CLS_MAP = {
        ContentType.TEXT.value: TextProcessor,
    }

    def __init__(
        self,
        rules_config: list[dict[str, Any]],
        maskingMapService,
        # replacer_state: Optional[Mapping[str, str]] = None
    ):
        self.rules_config = rules_config
        # self._replacer_state = replacer_state or {}
        self.maskingMapService = maskingMapService
        self._processor = None

    def make_patcher(self, cfg: dict[str, Any]):
        """Make a patcher instance from config."""
        patcher_type = cfg.pop("type")
        patcher_cls = self.PATCHERS_MAP[patcher_type]
        patcher = patcher_cls(self.maskingMapService, **cfg)
        # if isinstance(patcher, ReplacePatcher):
        #     # Set a shared state instance to replacer
        #     patcher.set_state(self._replacer_state)
        return patcher

    def make_matcher(self, cfg: dict[str, Any]):
        """Create a rule instance with ``cfg``."""
        matcher_type = cfg.pop("type")
        matcher_cat = cfg.pop("category")
        patcher_cfg = cfg.pop("patcher_cfg", None)
        patcher_cfg["category"] = matcher_cat
        matcher_cls = self.MATCHER_MAP[matcher_type]
        if patcher_cfg:
            patcher = self.make_patcher(patcher_cfg)
            cfg["patcher"] = patcher
        matcher = matcher_cls(**cfg)
        return matcher

    def make_processor(self, content_type=ContentType.TEXT.value) -> BaseProcessor:
        """Create a ``BaseProcessor`` instance."""
        if self._processor is None:
            rules = [self.make_matcher(cfg) for cfg in self.rules_config]
            proc_cls = self.PROC_CLS_MAP[content_type]
            processor = proc_cls(rules)
            self._processor = processor
        return self._processor


class BaseService(Generic[T]):
    def __init__(self, model: Type[T], session: Session):
        self.model = model
        self.session = session

    def create(self, db_obj: T) -> T:
        self.session.add(db_obj)
        self.session.flush()
        return db_obj

    def get_by_id(self, id: str) -> T | None:
        return self.session.get(self.model, id)

    def get_all(self) -> list[T]:
        return self.session.query(self.model).all()

    def update(self, db_obj: T, obj_data: dict) -> T:
        for key, value in obj_data.items():
            setattr(db_obj, key, value)
        return db_obj

    def delete(self, id: str) -> None:
        db_obj = self.get_by_id(id)
        if db_obj:
            self.session.delete(db_obj)

    def create_token(self, data: dict, expires_delta: int | None = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.TOKEN_EXPIRE_MINUTES
            )
        to_encode.update({"exp": expire})
        token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return token

    def validate_token(self, token: str):
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            return payload
        except JWTError:
            return False


class UserService(BaseService[User]):
    def __init__(self, session: Session):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        super().__init__(User, session)

    def get_user_by_username(self, username: str) -> User | None:
        return self.session.query(User).filter(User.username == username).first()

    def create_user(self, username: str, password: str, role: str) -> User | None:
        user = User(username=username, role=Role(role))
        user.password = self.hash_password(password=password)
        self.create(user)
        return user

    def update_password(self, userId: str, password: str) -> User | None:
        user = self.get_by_id(userId)
        if not user:
            return None
        data = dict(password=self.hash_password(password))
        return self.update(user, data)

    def delete_user(self, userId: str) -> None:
        user = self.get_by_id(userId)
        if not user:
            return
        if user.username == "admin":
            raise ValueError("Cannot delete the admin user")
        if user:
            self.delete(str(user.id))

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def authenticate(self, username: str, password: str) -> User | None:
        user = self.get_user_by_username(username)
        if not user:
            return None
        if not self.verify_password(password, user.password):
            return None
        return user


class FileService(BaseService[File]):
    def __init__(self, session: Session, user: User, storage: FileStorage):
        self.user = user
        self.storage = storage
        super().__init__(File, session)

    def get_by_user(self) -> list[File]:
        files = self.user.files
        return [file for file in files if file.archive_id is None]
        # return self.user.files

    def compute_used_space(self):
        used_space = (
            self.session.query(func.sum(File.file_size))
            .join(User)
            .filter(User.id == self.user.id)
            .scalar()
        )
        if not used_space:
            used_space = 0
        return used_space

    def get_preset(self, file_id: str, file_type: str) -> Preset | None:
        if file_type == ContentType.TEXT.value:
            with self.storage.get(file_id).open("r") as file:
                # Read first line
                header = file.readline().strip()
            preset = (
                self.session.query(Preset)
                .filter(
                    func.strpos(func.lower(literal(header)), func.lower(Preset.header))
                    > 0
                )
                .first()
            )
            return preset
        elif file_type == ContentType.PCAP.value:
            preset = self.session.query(Preset).filter(Preset.name == "pcap").first()
            return preset
        else:
            return None

    def save_file(self, file: UploadFile) -> File:
        file_id = self.storage.save_file(file.file)
        file_size = self.storage.get_size(file_id)
        file_type = self.storage.get_type(file_id)
        finfo = FileInfo(file_id, file.filename, file_size, file_type)
        return self.add_file(finfo)

    def add_file(self, finfo: FileInfo, archive_id: str | None = None) -> File:
        if finfo.ftype in self.storage.FILE_TYPES:
            content_type = ContentType(finfo.ftype)
            preset = self.get_preset(finfo.fid, finfo.ftype)
        elif finfo.ftype in self.storage.ARCHIVE_TYPES:
            content_type = ContentType.ARCHIVE
            preset = None
        else:
            # delete unsupported file from storage
            self.storage.delete(finfo.fid)
            raise ValueError(f"Unsupported file type: {finfo.ftype}")

        file_obj = File(
            id=finfo.fid,
            filename=finfo.fname,
            file_size=finfo.fsize,
            content_type=content_type,
            user=self.user,
            preset=preset,
            product=preset.product if preset else None,
            archive_id=archive_id,
        )
        self.create(file_obj)
        return file_obj

    def unpack_file(self, file: File) -> list[File]:
        files = []
        for finfo in self.storage.unpack(file.id, file.filename):
            # file_obj = self.add_file(file_info.fid, file_info.fname, archive_id=file.id)
            file_obj = self.add_file(finfo, archive_id=file.id)
            files.append(file_obj)

            if self.compute_used_space() > settings.USER_STORAGE_LIMIT:
                for file in files:
                    self.delete_file(file.id)
                raise Exception(f"Not enough free space in user storage")

            if len(self.user.files) > settings.MAX_USER_FILES:
                for file in files:
                    self.delete_file(file.id)
                raise Exception(
                    f"Files per user limit ({settings.MAX_USER_FILES}) is exceeded"
                )
        return files

    def process_file(self, file_id: str):
        file = self.get_by_id(file_id)

        if not file:
            raise Exception("File not found")

        if file.status is not FileStatus.CREATED:
            raise Exception("File processing is already started")

        # Track if this is an archive
        is_archive = file.content_type is ContentType.ARCHIVE

        if is_archive:
            files = self.unpack_file(file)
            # Set initial progress
            file.extracted_size = sum(f.file_size for f in files)
            file.status = FileStatus.IN_PROGRESS
            file.completed_size = 0
            file.time_remaining = 0
            self.session.commit()
        else:
            files = [file]

        task_configs = self.make_task_config(files)

        for task_config in task_configs:
            self.preprocess_file(**task_config)

        # Re-pack files after processing
        if is_archive:
            self.storage.repack(file)
            file.status = FileStatus.DONE
            file.completed_size = file.file_size
            file.time_remaining = 0
            # Commit the updated file size and status
            self.session.commit()

            for child in file.archive_files:
                self.delete_file(child.id)
        return file

    def preprocess_file(self, files: Dict[str, str], rules_configs: Dict[str, List]):
        try:
            start_time = time.time()
            configs = {}
            for file_id, preset_id in files.items():
                config = configs.get(preset_id)
                if not config:
                    # Init config with rules
                    config = ProcessingConfig(
                        rules_config=rules_configs[preset_id],
                        maskingMapService=MaskingMapService(self.session),
                    )
                    configs[preset_id] = config
                self._process_file(config, file_id)

                # After processing each file, update the parent archive's progress if applicable
                processed_file = self.get_by_id(file_id)

                # Check if this file is part of an archive
                if processed_file and processed_file.archive_id:
                    # Get the parent archive
                    parent = processed_file.archive

                    # If the parent is currently being processed
                    if parent.status == FileStatus.IN_PROGRESS:
                        # Calculate total extracted size from all files in the archive
                        # total_extracted_size = sum(
                        #     child.file_size for child in parent.archive_files
                        # )

                        # Calculate processed size across all completed files in the archive
                        processed_size = sum(
                            child.file_size
                            for child in parent.archive_files
                            if child.status == FileStatus.DONE
                        )

                        # Update parent archive progress
                        parent.completed_size = processed_size

                        # Calculate time remaining based on progress
                        if processed_size > 0:
                            # Use the parent's create_date as the start time reference
                            # start_time = parent.create_date.timestamp()
                            elapsed = time.time() - start_time

                            if elapsed > 0:
                                rate = processed_size / elapsed
                                remaining = parent.extracted_size - processed_size
                                parent.time_remaining = (
                                    int(remaining / rate) if rate > 0 else 0
                                )

                        self.session.commit()
                        logger.debug(
                            f"Updated archive {parent.id} progress after processing {file_id}: "
                            f"completed_size={parent.completed_size}, "
                            f"time_remaining={parent.time_remaining}"
                        )

        except Exception:
            # Set error for all non-done files
            file_ids = list(files.keys())
            logger.exception(f"Error processing files: {files}")
            self.session.query(File).filter(
                (File.status != FileStatus.DONE) & File.id.in_(file_ids)
            ).update({"status": FileStatus.ERROR})
            raise

    def _process_file(self, config: ProcessingConfig, file_id: str) -> None:
        file_obj = self.get_by_id(file_id)
        if not file_obj:
            raise FileNotFoundError(f"File with id {file_id} not found.")
        file_obj.status = FileStatus.IN_PROGRESS
        content_type = file_obj.content_type
        processor = config.make_processor(content_type=content_type.value)
        try:
            src = self.storage.get(file_id)
            dst = src.parent.joinpath(f"{src.name}.new")

            # Detect encoding
            encoding_res = from_path(src).best()
            if encoding_res:
                encoding = encoding_res.encoding
                confidence = 1 - encoding_res.chaos  # lower chaos = higher confidence
                language = encoding_res.language
            # encoding = enc_detector.result['encoding']
            if encoding_res is None:
                raise RuntimeError("Can't detect encoding for file")

            done_size = 0
            unreported = 0
            total_size = self.storage.get_size(file_id)
            max_report_num = int(total_size / settings.REPORT_STEP)

            # Process file
            # Dynamic report step based on file size
            # total_size = file_obj.file_size
            # if total_size > 1_000_000_000:  # > 1GB
            #     report_step = 10_000_000  # Report every 10MB
            # elif total_size > 100_000_000:  # > 100MB
            #     report_step = 5_000_000  # Report every 5MB
            # else:
            #     report_step = 1_000_000  # Report every 1MB

            process_time = 0
            report_count = 1
            with dst.open("w", newline="", encoding=encoding) as f_dst:
                with src.open("r", newline="", encoding=encoding) as f_src:
                    operation_time = time.time()
                    for chunk in processor.feed(f_src):
                        f_dst.write(chunk)
                        chunk_bytest_len = len(chunk.encode())
                        done_size += chunk_bytest_len
                        unreported += chunk_bytest_len
                        if unreported >= settings.REPORT_STEP:
                            process_time += time.time() - operation_time
                            average_process_time = process_time / report_count
                            operation_time = time.time()
                            chunk_num = max_report_num - report_count
                            time_remain = int(chunk_num * average_process_time)

                            file_obj.completed_size = done_size
                            file_obj.time_remaining = time_remain
                            self.session.commit()
                            logger.debug(
                                f"Progress update for {file_id}: completed_size={done_size}, time_remaining={time_remain}"
                            )
                            report_count += 1
                            unreported = 0
            logger.info("Renaming %s -> %s", dst, src)
            dst.rename(src)

            file_obj.status = FileStatus.DONE
            file_obj.completed_size = done_size
            file_obj.time_remaining = 0
            file_obj.file_size = self.storage.get_size(file_id)
        except Exception:
            logger.exception(f"Error processing file {file_id}")
            path = pathlib.Path(file_obj.filename)
            path_parts = list(path.parts)
            path_parts[-1] = "failed_" + path_parts[-1]
            filename = "/".join(path_parts)

            file_obj.status = FileStatus.ERROR
            file_obj.filename = filename
            if dst.exists():
                dst.unlink()

    def get_rule_config(self, presetRule: PresetRule):
        # config = []
        # for presetRule in preset_rules:
        cfg = presetRule.rule.config
        cfg["category"] = presetRule.rule.category
        cfg["patcher_cfg"] = presetRule.action
        # config.append(cfg)
        return cfg

    def make_task_config(self, file_objs: list[File]):
        """Make task config."""
        # make sure all files have assigned presets
        file_wo_preset = (
            self.session.query(File)
            .filter(
                File.id.in_([file_obj.id for file_obj in file_objs]),
                File.preset == None,
            )
            .all()
        )
        if file_wo_preset:
            raise Exception(f"{file_wo_preset[0].filename}  has no assigned preset")

        # Create configs for processing
        files = {}
        presets_cfgs = {}
        for file_obj in file_objs:
            preset_id = str(file_obj.preset_id)
            if preset_id not in presets_cfgs:
                configs = [
                    self.get_rule_config(presetRule)
                    for presetRule in file_obj.preset.rules
                ]
                presets_cfgs[preset_id] = configs
            files[file_obj.id] = {"preset_id": preset_id, "size": file_obj.file_size}

        # Create preset cfg -> list of files mapping
        preset_files_map = collections.defaultdict(list)
        files_items = sorted(files.items(), key=lambda x: -x[1]["size"])
        for file_id, file_info in files_items:
            preset_files_map[file_info["preset_id"]].append(file_id)

        tasks_configs = []

        # Create config
        group_files = {}
        group_rules = {}
        for preset_id, file_ids in preset_files_map.items():
            group_rules[preset_id] = presets_cfgs[preset_id]
            for file_id in file_ids:
                group_files[file_id] = preset_id
        tasks_configs.append({"files": group_files, "rules_configs": group_rules})

        return tasks_configs

    def delete_file(self, file_id):
        """Delete db object and file from the storage."""
        self.storage.delete(file_id)
        self.delete(file_id)


class ProductService(BaseService[Product]):
    def __init__(self, session: Session):
        super().__init__(Product, session)


class PresetService(BaseService[Preset]):
    def __init__(self, session: Session):
        super().__init__(Preset, session)
        self.presetRule_service = PresetRuleService(self.session)
        self.rule_service = RuleService(self.session)

    def get_rules_config(self, preset: Preset):
        """Generate processing config for preset."""
        preset_rules = preset.rules
        config = None
        return config


class RuleService(BaseService[Rule]):
    def __init__(self, session: Session):
        super().__init__(Rule, session)

    def get_config(self, rule_id: int):
        """Generate rule config to processing."""
        cfg = self.session.query(Rule).filter(Rule.id == rule_id).first()
        if not cfg:
            raise Exception(f"Rule with id {rule_id} not found")
        return cfg.config


class PresetRuleService(BaseService[PresetRule]):
    def __init__(self, session: Session):
        super().__init__(PresetRule, session)

    def get_config(self):
        """Generate rule/action config for preset rule."""
        cfg = self.model.rule.get_config(self.model.rule_id)
        cfg["patcher_cfg"] = self.model.action
        return cfg


class MaskingMapService(BaseService[MaskingMap]):
    """Service class to interact with MaskingMap table."""

    def __init__(self, session: Session):
        super().__init__(MaskingMap, session)

    def count_entries(self, category: RuleCategory) -> int:
        """Count number of existing masked values for a given entity type."""
        return self.session.query(MaskingMap).filter_by(category=category).count()

    def fetch_mask(self, original_value: str) -> str | None:
        """Check if the original string has an existing masked value."""
        entry = (
            self.session.query(MaskingMap)
            .filter_by(original_value=original_value)
            .first()
        )
        return entry.masked_value if entry else None

    def store_mask(
        self, original_value: str, masked_value: str, category: RuleCategory
    ):
        """Store a new masked value in the database."""
        new_entry = MaskingMap(
            original_value=original_value, masked_value=masked_value, category=category
        )
        self.session.add(new_entry)
        self.session.flush()

    def search_masks(
        self,
        query: str | None = None,
        categories: list[str] | None = None,
        limit: Optional[int] = 100,
        offset: Optional[int] = 0,
        sort: Optional[str] = "created_at:desc",
    ) -> list[MaskingMap]:
        """Search for masking maps based on query and filters."""
        # Start with a base query
        db_query = self.session.query(MaskingMap)

        # Apply text search if provided
        if query:
            search_term = f"%{query}%"
            db_query = db_query.filter(
                # Search in both original and masked values
                or_(
                    MaskingMap.original_value.ilike(search_term),
                    MaskingMap.masked_value.ilike(search_term),
                )
            )

        # Filter by categories if provided
        if categories and len(categories) > 0:
            # Convert string categories to RuleCategory enum
            enum_categories = []
            for cat in categories:
                try:
                    enum_categories.append(RuleCategory(cat))
                except ValueError:
                    # Skip invalid categories
                    continue

            if enum_categories:
                db_query = db_query.filter(MaskingMap.category.in_(enum_categories))

        # Apply sorting
        if sort:
            parts = sort.split(":")
            if len(parts) == 2:
                field_name, direction = parts

                # Get the actual column to sort by
                if hasattr(MaskingMap, field_name):
                    sort_column = getattr(MaskingMap, field_name)

                    # Apply sorting direction
                    if direction.lower() == "desc":
                        db_query = db_query.order_by(sort_column.desc())
                    else:
                        db_query = db_query.order_by(sort_column.asc())
            else:
                # Default sort by created_at descending
                db_query = db_query.order_by(MaskingMap.created_at.desc())

        # Apply pagination
        db_query = db_query.limit(limit).offset(offset)

        # Execute query and return results
        return db_query.all()

    def get_categories(self) -> list[str]:
        """Get all available categories that have masked values."""
        categories = self.session.query(MaskingMap.category).distinct().all()
        # Convert to list of strings
        return [cat[0].value for cat in categories]
