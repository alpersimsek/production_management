"""
GDPR Tool Services - Core Business Logic

This module contains all the core business logic services for the GDPR compliance tool.
It provides comprehensive file processing, user management, and data masking capabilities.

Key Components:
- BaseService: Generic base class for all database services with CRUD operations
- ProcessingConfig: Configuration class for file processing with matchers, patchers, and processors
- UserService: User authentication, password management, and user CRUD operations
- FileService: File upload, processing, archive handling, and product-based preset selection
- ProductService: Product management with auto-increment ID handling
- PresetService: Preset management with sequence conflict resolution
- RuleService: Rule configuration and management
- PresetRuleService: Junction table service for preset-rule associations
- MaskingMapService: Data masking map storage and retrieval with search capabilities

Main Processing Features:
- File Upload & Storage: Handles file uploads with type detection and storage management
- Archive Processing: Supports ZIP/TAR archives with recursive extraction and repacking
- Product-Based Processing: New system for product-specific preset selection and rule application
- Header Matching: Intelligent preset selection based on file headers for text and PCAP files
- Data Masking: Comprehensive masking with regex, IP, and MAC address matchers
- Progress Tracking: Real-time processing progress with time estimation
- Error Handling: Robust error handling with detailed logging and status tracking

Processing Flow:
1. File Upload → Type Detection → Storage
2. Product Selection → Header Matching → Preset Assignment
3. Rule Application → Data Masking → Progress Tracking
4. Archive Repacking → Status Updates → Completion

The system supports both traditional preset-based processing and new product-based processing
with intelligent header matching and fallback strategies.
"""

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
    MaskingMap,
    Role,
    ContentType,
    RuleCategory,
)
from gdpr.processors import BaseProcessor, TextProcessor, PcapProcessor
from gdpr.matchers import RegexpMatcher, IPAddrMatcher, MacAddrMatcher
from gdpr.patchers import ReplacePatcher
import collections
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
import settings
from storage import FileStorage, FileInfo
from typing import Optional, Type, TypeVar, Generic, Any
from fastapi import UploadFile
from logger import logger
from charset_normalizer import from_path
from sqlalchemy import or_

T = TypeVar("T")

class PcapProcessingError(Exception):
    """Custom exception for PCAP processing errors."""
    pass

class ProcessingConfig:
    """Processing config class."""

    MATCHER_MAP = {
        "regex": RegexpMatcher,
        "ip_addr": IPAddrMatcher,
        "mac_addr": MacAddrMatcher,
    }

    PATCHERS_MAP = {
        "replace": ReplacePatcher,
    }

    PROC_CLS_MAP = {
        ContentType.TEXT.value: TextProcessor,
        ContentType.PCAP.value: PcapProcessor,
    }

    def __init__(
        self,
        rules_config: list[dict[str, Any]],
        maskingMapService,
    ):
        self.rules_config = rules_config
        self.maskingMapService = maskingMapService
        self._processor = None

    def make_patcher(self, cfg: dict[str, Any]):
        """Make a patcher instance from config."""
        patcher_type = cfg.pop("type")
        patcher_cls = self.PATCHERS_MAP[patcher_type]
        patcher = patcher_cls(self.maskingMapService, **cfg)
        return patcher

    def make_matcher(self, cfg: dict[str, Any]):
        """Create a rule instance with ``cfg``."""
        matcher_type = cfg.pop("type")
        matcher_cat = cfg.pop("category")
        patcher_cfg = cfg.pop("patcher_cfg", None)
        
        # Convert string category back to RuleCategory enum if needed
        if isinstance(matcher_cat, str):
            matcher_cat = RuleCategory(matcher_cat)
        
        patcher_cfg["category"] = matcher_cat
        matcher_cls = self.MATCHER_MAP[matcher_type]
        if patcher_cfg:
            patcher = self.make_patcher(patcher_cfg)
            cfg["patcher"] = patcher
        # Pass the category to the matcher for exception pattern checking
        cfg["category"] = matcher_cat
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

    # def create(self, db_obj: T) -> T:
    #     """Create a new database object with ID conflict resolution."""
    #     try:
    #         table_name = db_obj.__class__.__tablename__
            
    #         # Handle auto-increment tables (presets, products, rules, masking_map)
    #         if hasattr(db_obj, 'id') and table_name in ['presets', 'products', 'rules', 'masking_map']:
    #             # Always calculate and set the next available ID for auto-increment tables
    #             try:
    #                 max_id = self.session.query(db_obj.__class__.id).order_by(
    #                     db_obj.__class__.id.desc()
    #                 ).first()
    #                 next_id = (max_id[0] + 1) if max_id else 1
                    
    #                 # Set the ID to avoid sequence conflicts
    #                 db_obj.id = next_id
    #                 print(f"Info: {table_name} - Setting ID to {next_id} to avoid sequence conflicts")
                    
    #             except Exception as e:
    #                 print(f"Warning: Could not determine next ID for {table_name}: {e}")
    #                 # Fallback: let PostgreSQL handle it (might still fail)
            
    #         self.session.add(db_obj)
    #         self.session.flush()
    #         return db_obj
    #     except Exception as e:
    #         # Rollback on any error to prevent PendingRollbackError
    #         self.session.rollback()
    #         raise e

    def create(self, db_obj: T) -> T:
        self.session.add(db_obj)
        self.session.flush()
        return db_obj

    def get_by_id(self, id: str | int) -> T | None:
        return self.session.get(self.model, id)

    def get_all(self) -> list[T]:
        return self.session.query(self.model).all()

    def update(self, db_obj: T, obj_data: dict) -> T:
        for key, value in obj_data.items():
            setattr(db_obj, key, value)
        return db_obj

    def delete(self, id: str | int) -> None:
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
    # Default limits for archive extraction
    MAX_NESTING_DEPTH = 5  # Maximum depth for nested archives
    MAX_EXTRACTED_SIZE = 1024 * 1024 * 1024  # 1GB limit for total extracted size
    MAX_EXTRACTED_FILES = 1000  # Maximum number of extracted files per archive

    def __init__(self, session: Session, user: User, storage: FileStorage, product_id: int | None = None):
        self.user = user
        self.storage = storage
        self.product_id = product_id
        super().__init__(File, session)

    def get_by_user(self) -> list[File]:
        files = self.user.files
        return [file for file in files if file.archive_id is None]

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
    
    def get_preset(self, finfo: FileInfo) -> Optional[Preset]:
        """Match preset headers as substrings in file header"""
        try:
            if finfo.ftype == ContentType.TEXT.value:
                src = self.storage.get(finfo.fid)
                encoding_res = from_path(src).best()
                if not encoding_res:
                    # Get file object for filename
                    logger.error({
                        "event": "encoding_detection_failed",
                        "file_id": finfo.fid,
                        "filename": finfo.fname,
                        "error": "Cannot detect file encoding",
                    })
                    return None
                encoding = encoding_res.encoding

                with src.open("r", encoding=encoding) as file:
                    header = file.readline().strip()
                
                # File header read - removed verbose logging

                # Try to match header with product presets
                product_presets = self.session.query(Preset).filter(Preset.product_id == self.product_id).all()
                
                for preset in product_presets:
                    if preset.header and preset.header in header:
                        logger.info({
                            "event": "header_match_found",
                            "file_id": finfo.fid,
                            "preset_id": preset.id,
                            "event": "preset_matched",
                            "filename": finfo.fname,
                            "file_type": finfo.ftype,
                            "file_header": header,
                            "preset_id": str(preset.id),
                            "preset_name": preset.name,
                            "header": header,
                            "preset_header": preset.header
                        })
                        return preset
                
                # No header match found
                logger.debug({
                    "event": "no_header_match",
                    "file_id": finfo.fid,
                    "filename": finfo.fname,
                    "header": header,
                    "available_headers": [p.header for p in product_presets if p.header]
                })

                return None

            elif finfo.ftype == ContentType.PCAP.value:
                src = self.storage.get(finfo.fid)
                # Read first 4 bytes for PCAP magic number
                with src.open("rb") as file:  # Note: binary mode
                    magic_bytes = file.read(4)
                    magic_hex = magic_bytes.hex()
                
                # PCAP header read - removed verbose logging
                
                # Check if it's a valid PCAP file (multiple formats supported)
                valid_pcap_magics = [
                    "a1b2c3d4",  # Standard PCAP (Little Endian)
                    "d4c3b2a1",  # Swapped PCAP (Big Endian)
                    "0a0d0d0a",  # PCAP-NG format
                ]
                
                if magic_hex in valid_pcap_magics:
                    # Valid PCAP file - find PCAP preset
                    preset = self.session.query(Preset).filter(Preset.name == "pcap").first()
                    if preset:
                        # Get file object for filename
                        logger.info({
                            "event": "pcap_preset_assigned",
                            "file_id": finfo.fid,
                            "file_type": finfo.ftype,
                            "filename": finfo.fname,
                            "preset_id": str(preset.id),
                            "preset_name": preset.name,
                            "magic_hex": magic_hex,
                            "format": "PCAP-NG" if magic_hex == "0a0d0d0a" else "PCAP",
                        })
                        return preset
                    else:
                        logger.warning({
                            "event": "pcap_preset_not_found",
                            "filename": finfo.fname,
                            "file_type": finfo.ftype,
                        })
                        return None
                else:
                    # Not a valid PCAP file
                    # Get file object for filename
                    logger.warning({
                        "event": "invalid_pcap_file",
                        "filename": finfo.fname,
                        "file_type": finfo.ftype,
                        "magic_hex": magic_hex,
                        "expected": valid_pcap_magics,
                    })
                    return None
            
            else:
                return None
                    
        except Exception as ex:
            logger.error({
                "event": "pcap_header_read_failed",
                "filename": finfo.fname,
                "file_type": finfo.ftype,
                "error": str(ex),
            })

    def save_file(self, file: UploadFile) -> File:
        file_id = self.storage.save_file(file.file)
        file_size = self.storage.get_size(file_id)
        file_type = self.storage.get_type(file_id)
        finfo = FileInfo(file_id, file.filename, file_size, file_type)
        return self.add_file(finfo)

    def add_file(self, finfo: FileInfo, archive_id: str | None = None) -> File:
        preset = None
        product = None

        # product and preset is set during file process
        if self.product_id:
            product = self.session.query(Product).filter(Product.id == self.product_id).first()
            preset = self.get_preset(finfo)

        # set content_type
        if finfo.ftype in self.storage.FILE_TYPES:
            content_type = ContentType(finfo.ftype)
        elif finfo.ftype in self.storage.ARCHIVE_TYPES:
            content_type = ContentType.ARCHIVE
        else:
            self.storage.delete(finfo.fid)
            raise ValueError(f"Unsupported file type: {finfo.ftype}")
        
        file = File(
            id=finfo.fid,
            filename=finfo.fname,
            file_size=finfo.fsize,
            content_type=content_type,
            user=self.user,
            preset=preset,
            product=product,
            archive_id=archive_id,
        )
        self.create(file)
        return file

    def unpack_file(self, file: File, nesting_level: int = 0) -> list[File]:
        """Unpack an archive file recursively, continuing with extracted files even if errors occur."""
        if nesting_level > self.MAX_NESTING_DEPTH:
            logger.warning({
                "event": "unpack_skipped",
                "file_id": file.id,
                "filename": file.filename,
                "error": f"Maximum nesting depth ({self.MAX_NESTING_DEPTH}) exceeded",
            }, extra={"context": {"file_id": file.id}})
            return []

        files = []
        total_extracted_size = 0
        extracted_count = 0

        try:
            for finfo in self.storage.unpack(file.id, file.filename, nesting_level):
                file_obj = self.add_file(finfo, archive_id=file.id)
                files.append(file_obj)
                total_extracted_size += finfo.fsize or 0
                extracted_count += 1

                if total_extracted_size > self.MAX_EXTRACTED_SIZE:
                    for f in files:
                        self.delete_file(f.id)
                    logger.error({
                        "event": "unpack_failed",
                        "file_id": file.id,
                        "filename": file.filename,
                        "error": f"Extracted size exceeds limit ({self.MAX_EXTRACTED_SIZE})",
                    }, extra={"context": {"file_id": file.id}})
                    raise ValueError(f"Extracted size exceeds limit ({self.MAX_EXTRACTED_SIZE})")

                if extracted_count > self.MAX_EXTRACTED_FILES:
                    for f in files:
                        self.delete_file(f.id)
                    logger.error({
                        "event": "unpack_failed",
                        "file_id": file.id,
                        "filename": file.filename,
                        "error": f"Extracted file count exceeds limit ({self.MAX_EXTRACTED_FILES})",
                    }, extra={"context": {"file_id": file.id}})
                    raise ValueError(f"Extracted file count exceeds limit ({self.MAX_EXTRACTED_FILES})")

                if self.compute_used_space() > settings.USER_STORAGE_LIMIT:
                    for f in files:
                        self.delete_file(f.id)
                    logger.error({
                        "event": "unpack_failed",
                        "file_id": file.id,
                        "filename": file.filename,
                        "error": "Not enough free space in user storage",
                    }, extra={"context": {"file_id": file.id}})
                    raise ValueError("Not enough free space in user storage")

                if len(self.user.files) > settings.MAX_USER_FILES:
                    for f in files:
                        self.delete_file(f.id)
                    logger.error({
                        "event": "unpack_failed",
                        "file_id": file.id,
                        "filename": file.filename,
                        "error": f"Files per user limit ({settings.MAX_USER_FILES}) is exceeded",
                    }, extra={"context": {"file_id": file.id}})
                    raise ValueError(f"Files per user limit ({settings.MAX_USER_FILES}) is exceeded")
                    
        except Exception as e:
            logger.warning({
                "event": "unpack_error",
                "file_id": file.id,
                "filename": file.filename,
                "nesting_level": nesting_level,
                "error": str(e),
            }, extra={"context": {"file_id": file.id}})
            # Continue with any files extracted before the error

        if not files:
            logger.info({
                "event": "no_files_extracted",
                "file_id": file.id,
                "filename": file.filename,
                "nesting_level": nesting_level,
                "message": "No files found in archive",
            }, extra={"context": {"file_id": file.id}})

        return files

    def preprocess_file(self, file: File) -> list[File]:
        """Pre-Process a file, handling archives and individual files."""
        is_archive = file.content_type == ContentType.ARCHIVE
        files = []

        try:
            if is_archive:
                files = self.unpack_file(file)
                if files:
                    file.extracted_size = sum(f.file_size for f in files)
                    file.status = FileStatus.QUEUED
                    # set status for extracted files
                    for child in file.archive_files:
                        child.status = FileStatus.QUEUED
                    # file.completed_size = 0
                    # file.time_remaining = 0
                    self.session.commit()
                    logger.debug({
                        "event": "archive_unpacked",
                        "file_id": file.id,
                        "filename": file.filename,
                        "extracted_size": file.extracted_size,
                        "file_count": len(files),
                    })
                    return files
                else:
                    logger.info({
                        "event": "archive_empty",
                        "file_id": file.id,
                        "filename": file.filename,
                        "message": "No files extracted, proceeding with empty archive",
                    })
                    file.status = FileStatus.DONE
                    file.completed_size = file.file_size
                    file.time_remaining = 0
                    self.session.commit()
                    raise FileNotFoundError(f"Processing stopped for {file.filename}, empty archive!")
            else:
                # For non-archive files, try to assign preset since product_id is available now
                if self.product_id and file.preset is None:
                    file.product_id = self.product_id
                    file.status = FileStatus.QUEUED
                    finfo = FileInfo(file.id, file.filename, file.file_size, file.content_type.value)
                    preset = self.get_preset(finfo)
                    if preset:
                        file.preset = preset
                        logger.info({
                            "event": "preset_assigned_during_processing",
                            "file_id": file.id,
                            "filename": file.filename,
                            "preset_id": preset.id,
                            "preset_name": preset.name,
                            "product_id": self.product_id
                        })
                    self.session.commit()
                return [file]

        except Exception as e:
            file.status = FileStatus.ERROR
            self.session.commit()
            logger.error({
                "event": "process_failed",
                "file_id": file.id,
                "filename": file.filename,
                "error": str(e),
            })
            self.delete_file(file.id)
            raise ValueError(f"Processing failed: {str(e)}")

    def cancel_file_processing(self, file_id: str):
        """Cancel file processing and set status to CANCELLED."""
        file = self.get_by_id(file_id)
        if not file:
            raise ValueError("File not found")

        if file.status not in [FileStatus.CREATED, FileStatus.IN_PROGRESS]:
            raise ValueError("File processing cannot be cancelled in current status")

        # Set status to cancelled
        file.status = FileStatus.CANCELLED
        file.completed_size = 0
        file.time_remaining = 0
        self.session.commit()

        logger.info({
            "event": "processing_cancelled",
            "file_id": file_id,
            "filename": file.filename,
        })

        return file

    def get_rule_config(self, presetRule: PresetRule):
        cfg = presetRule.rule.config
        cfg["category"] = presetRule.rule.category.value
        cfg["patcher_cfg"] = presetRule.action
        return cfg

    def make_task_config(self, file_id: str):
        """Make task config."""
        file = self.get_by_id(file_id)
        if not file:
            logger.error({
                "event": "process_failed",
                "file_id": file_id,
                "error": "File not found",
            })
            raise ValueError("File not found")

        if file.status is FileStatus.IN_PROGRESS:
            logger.error({
                "event": "process_failed",
                "file_id": file_id,
                "error": "File processing is already started",
            })
            raise ValueError("File processing is already started")

        logger.info({
            "event": "process_started",
            "file_id": file_id,
            "filename": file.filename,
            "content_type": file.content_type.value,
        })

        # unpack, set preset/product info
        files = self.preprocess_file(file)

        files_preset_map = {}
        presets_cfgs = {}
        for file in files:
            if file.preset is not None:
                preset_id = str(file.preset_id)
                if preset_id not in presets_cfgs:
                    configs = [
                        self.get_rule_config(presetRule)
                        for presetRule in file.preset.rules
                    ]
                    presets_cfgs[preset_id] = configs
                files_preset_map[file.id] = {"preset_id": preset_id, "size": file.file_size}
            else:
                # If any file has no preset and we have a product context, combine unique rules
                # from all presets of that product.
                product_presets = (
                    self.session.query(Preset)
                    .filter(Preset.product_id == self.product_id)
                    .all()
                )

                if not product_presets:
                    raise Exception(f"No presets defined for {file.product.name}")

                combined_rules = []
                unique_rule_ids = set()
                for preset in product_presets:
                    for presetRule in preset.rules:
                        rule_id = presetRule.rule.id
                        if rule_id not in unique_rule_ids:
                            combined_rules.append(self.get_rule_config(presetRule))
                            unique_rule_ids.add(rule_id)
                preset_id = "combined"
                files_preset_map[file.id] = {"preset_id": preset_id, "size": file.file_size}
                presets_cfgs[preset_id] = combined_rules

        preset_files_map = collections.defaultdict(list)
        files_items = sorted(files_preset_map.items(), key=lambda x: -x[1]["size"])
        for file_id, file_info in files_items:
            preset_files_map[file_info["preset_id"]].append(file_id)

        tasks_configs = []
        group_files = {}
        group_rules = {}
        for preset_id, file_ids in preset_files_map.items():
            group_rules[preset_id] = presets_cfgs[preset_id]
            for file_id in file_ids:
                group_files[file_id] = preset_id
        tasks_configs.append({"files": group_files, "rules_configs": group_rules, "user_id": str(self.user.id)})            

        return tasks_configs

    def delete_file(self, file_id):
        """Delete db object and file from storage."""
        self.storage.delete(file_id)
        self.delete(file_id)

class ProductService(BaseService[Product]):
    def __init__(self, session: Session):
        super().__init__(Product, session)

    def get_next_available_id(self) -> int:
        """Get the next available ID for products table."""
        try:
            max_id = self.session.query(Product.id).order_by(Product.id.desc()).first()
            if max_id:
                return max_id[0] + 1
            else:
                return 1
        except Exception:
            return 1

    def create(self, db_obj: Product) -> Product:
        """Override create method to ensure proper ID assignment."""
        try:
            # Always ensure we have the next available ID
            next_id = self.get_next_available_id()
            db_obj.id = next_id
            print(f"Info: Product - Setting ID to {next_id} to avoid sequence conflicts")
            
            # Use the base create method
            return super().create(db_obj)
        except Exception as e:
            self.session.rollback()
            raise e

class PresetService(BaseService[Preset]):
    def __init__(self, session: Session):
        super().__init__(Preset, session)
        self.presetRule_service = PresetRuleService(self.session)
        self.rule_service = RuleService(self.session)

    def get_next_available_id(self) -> int:
        """Get the next available ID for presets table."""
        try:
            # Get the maximum ID currently in use
            max_id = self.session.query(Preset.id).order_by(Preset.id.desc()).first()
            if max_id:
                return max_id[0] + 1
            else:
                return 1
        except Exception as e:
            # Fallback: try to get the next sequence value
            try:
                result = self.session.execute("SELECT nextval('presets_id_seq')")
                return result.scalar()
            except:
                # If all else fails, start from 1
                return 1

    def get_database_state_info(self) -> dict:
        """Get information about the current database state for debugging."""
        try:
            # Get all preset IDs
            preset_ids = [p.id for p in self.session.query(Preset.id).order_by(Preset.id).all()]
            
            # Get sequence info if possible
            sequence_info = {}
            try:
                result = self.session.execute("SELECT last_value, is_called FROM presets_id_seq")
                row = result.fetchone()
                if row:
                    sequence_info = {
                        "last_value": row[0],
                        "is_called": row[1]
                    }
            except Exception:
                sequence_info = {"error": "Could not read sequence"}
            
            return {
                "existing_preset_ids": preset_ids,
                "next_available_id": self.get_next_available_id(),
                "sequence_info": sequence_info,
                "total_presets": len(preset_ids)
            }
        except Exception as e:
            return {"error": str(e)}

    def get_all_tables_state(self) -> dict:
        """Get information about all auto-increment tables."""
        try:
            from services import ProductService, RuleService, MaskingMapService
            
            product_service = ProductService(self.session)
            rule_service = RuleService(self.session)
            masking_service = MaskingMapService(self.session)
            
            return {
                "presets": {
                    "existing_ids": [p.id for p in self.session.query(Preset.id).order_by(Preset.id).all()],
                    "next_available_id": self.get_next_available_id()
                },
                "products": {
                    "existing_ids": [p.id for p in self.session.query(Product.id).order_by(Product.id).all()],
                    "next_available_id": product_service.get_next_available_id()
                },
                "rules": {
                    "existing_ids": [r.id for r in self.session.query(Rule.id).order_by(Rule.id).all()],
                    "next_available_id": rule_service.get_next_available_id()
                },
                "masking_map": {
                    "existing_ids": [m.id for m in self.session.query(MaskingMap.id).order_by(MaskingMap.id).all()],
                    "next_available_id": masking_service.get_next_available_id()
                }
            }
        except Exception as e:
            return {"error": str(e)}

    def fix_sequence(self) -> dict:
        """Manually fix the PostgreSQL sequence for presets table."""
        try:
            # Get the maximum ID currently in use
            max_id = self.session.query(Preset.id).order_by(Preset.id.desc()).first()
            if not max_id:
                return {"message": "No presets found", "sequence_set": 0}
            
            max_id_value = max_id[0]
            
            # Try to fix the sequence
            try:
                result = self.session.execute(
                    f"SELECT setval('presets_id_seq', {max_id_value})"
                )
                next_val = self.session.execute("SELECT nextval('presets_id_seq')").scalar()
                
                return {
                    "message": "Sequence fixed successfully",
                    "max_id_found": max_id_value,
                    "sequence_set_to": max_id_value,
                    "next_sequence_value": next_val,
                    "status": "success"
                }
            except Exception as seq_error:
                return {
                    "message": "Failed to fix sequence",
                    "max_id_found": max_id_value,
                    "sequence_error": str(seq_error),
                    "status": "error"
                }
        except Exception as e:
            return {"error": str(e), "status": "error"}

    def create(self, db_obj: Preset) -> Preset:
        """Override create method to ensure proper ID assignment."""
        try:
            # Always ensure we have the next available ID
            next_id = self.get_next_available_id()
            db_obj.id = next_id
            print(f"Info: Preset - Setting ID to {next_id} to avoid sequence conflicts")
            
            # Use the base create method
            return super().create(db_obj)
        except Exception as e:
            # Rollback on any error
            self.session.rollback()
            raise e

    def get_rules_config(self, preset: Preset):
        """Generate processing config for preset."""
        preset_rules = preset.rules
        config = None
        return config

class RuleService(BaseService[Rule]):
    def __init__(self, session: Session):
        super().__init__(Rule, session)

    def get_next_available_id(self) -> int:
        """Get the next available ID for rules table."""
        try:
            max_id = self.session.query(Rule.id).order_by(Rule.id.desc()).first()
            if max_id:
                return max_id[0] + 1
            else:
                return 1
        except Exception:
            return 1

    def create(self, db_obj: Rule) -> Rule:
        """Override create method to ensure proper ID assignment."""
        try:
            # Always ensure we have the next available ID
            next_id = self.get_next_available_id()
            db_obj.id = next_id
            print(f"Info: Rule - Setting ID to {next_id} to avoid sequence conflicts")
            
            # Use the base create method
            return super().create(db_obj)
        except Exception as e:
            self.session.rollback()
            raise e

    def get_config(self, rule_id: int):
        """Generate rule config to processing."""
        cfg = self.session.query(Rule).filter(Rule.id == rule_id).first()
        if not cfg:
            raise Exception(f"Rule with id {rule_id} not found")
        return cfg.config

class PresetRuleService(BaseService[PresetRule]):
    def __init__(self, session: Session):
        super().__init__(PresetRule, session)

    def create(self, db_obj: PresetRule) -> PresetRule:
        """Override create method to handle composite key table."""
        try:
            # For PresetRule, we don't need to set IDs as it uses composite keys
            # But we should verify the preset and rule exist
            from services import PresetService, RuleService
            
            preset_service = PresetService(self.session)
            rule_service = RuleService(self.session)
            
            # Verify preset exists
            preset = preset_service.get_by_id(db_obj.preset_id)
            if not preset:
                raise Exception(f"Preset with id {db_obj.preset_id} not found")
            
            # Verify rule exists
            rule = rule_service.get_by_id(db_obj.rule_id)
            if not rule:
                raise Exception(f"Rule with id {db_obj.rule_id} not found")
            
            # Use the base create method
            return super().create(db_obj)
        except Exception as e:
            self.session.rollback()
            raise e

    def get_config(self):
        """Generate rule/action config for preset rule."""
        cfg = self.model.rule.get_config(self.model.rule_id)
        cfg["patcher_cfg"] = self.model.action
        return cfg

class MaskingMapService(BaseService[MaskingMap]):
    """Service class to interact with MaskingMap table."""

    def __init__(self, session: Session):
        super().__init__(MaskingMap, session)

    def get_next_available_id(self) -> int:
        """Get the next available ID for masking_map table."""
        try:
            max_id = self.session.query(MaskingMap.id).order_by(MaskingMap.id.desc()).first()
            if max_id:
                return max_id[0] + 1
            else:
                return 1
        except Exception:
            return 1

    def create(self, db_obj: MaskingMap) -> MaskingMap:
        """Override create method to ensure proper ID assignment."""
        try:
            # Always ensure we have the next available ID
            next_id = self.get_next_available_id()
            db_obj.id = next_id
            print(f"Info: MaskingMap - Setting ID to {next_id} to avoid sequence conflicts")
            
            # Use the base create method
            return super().create(db_obj)
        except Exception as e:
            self.session.rollback()
            raise e

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
        # Use the create method to ensure proper ID assignment
        return self.create(new_entry)

    def search_masks(
        self,
        query: str | None = None,
        categories: list[str] | None = None,
        limit: Optional[int] = 100,
        offset: Optional[int] = 0,
        sort: Optional[str] = "created_at:desc",
    ) -> list[MaskingMap]:
        """Search for masking maps based on query and filters."""
        db_query = self.session.query(MaskingMap)
        
        if query:
            search_term = f"%{query}%"
            db_query = db_query.filter(
                or_(
                    MaskingMap.original_value.ilike(search_term),
                    MaskingMap.masked_value.ilike(search_term),
                )
            )
            
        if categories and len(categories) > 0:
            enum_categories = []
            for cat in categories:
                try:
                    enum_cat = RuleCategory(cat)
                    enum_categories.append(enum_cat)
                except ValueError:
                    continue
            if enum_categories:
                db_query = db_query.filter(MaskingMap.category.in_(enum_categories))
                
        if sort:
            parts = sort.split(":")
            if len(parts) == 2:
                field_name, direction = parts
                if hasattr(MaskingMap, field_name):
                    sort_column = getattr(MaskingMap, field_name)
                    if direction.lower() == "desc":
                        db_query = db_query.order_by(sort_column.desc())
                    else:
                        db_query = db_query.order_by(sort_column.asc())
            else:
                db_query = db_query.order_by(MaskingMap.created_at.desc())
                
        db_query = db_query.limit(limit).offset(offset)
        return db_query.all()

    def get_categories(self) -> list[str]:
        """Get all available categories that have masked values."""
        categories = self.session.query(MaskingMap.category).distinct().all()
        return [cat[0].value for cat in categories]

