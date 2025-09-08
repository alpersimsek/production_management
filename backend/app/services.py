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

import zipfile
import tarfile
import tempfile
import json
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
from gdpr.processors import BaseProcessor, TextProcessor, PcapProcessor
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
import tenacity
import magic
import os
from sqlalchemy import and_

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

    def create(self, db_obj: T) -> T:
        """Create a new database object with ID conflict resolution."""
        try:
            table_name = db_obj.__class__.__tablename__
            
            # Handle auto-increment tables (presets, products, rules, masking_map)
            if hasattr(db_obj, 'id') and table_name in ['presets', 'products', 'rules', 'masking_map']:
                # Always calculate and set the next available ID for auto-increment tables
                try:
                    max_id = self.session.query(db_obj.__class__.id).order_by(
                        db_obj.__class__.id.desc()
                    ).first()
                    next_id = (max_id[0] + 1) if max_id else 1
                    
                    # Set the ID to avoid sequence conflicts
                    db_obj.id = next_id
                    print(f"Info: {table_name} - Setting ID to {next_id} to avoid sequence conflicts")
                    
                except Exception as e:
                    print(f"Warning: Could not determine next ID for {table_name}: {e}")
                    # Fallback: let PostgreSQL handle it (might still fail)
            
            self.session.add(db_obj)
            self.session.flush()
            return db_obj
        except Exception as e:
            # Rollback on any error to prevent PendingRollbackError
            self.session.rollback()
            raise e

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

class HeaderMatcher:
    """Utility class for substring matching of file headers against preset headers."""
    
    def __init__(self):
        pass

    def match_header(self, file_header: str, preset_header: str) -> bool:
        """Check if preset header is a substring of file header."""
        if preset_header is None:
            return False
        return preset_header in file_header
    
    def is_valid_pcap(self, file_path) -> bool:
        """Check if a file is a valid PCAP file by reading its magic number."""
        try:
            with open(file_path, 'rb') as file:
                magic_bytes = file.read(4)
                magic_hex = magic_bytes.hex()
                valid_pcap_magics = [
                    "a1b2c3d4",  # Standard PCAP (Little Endian)
                    "d4c3b2a1",  # Swapped PCAP (Big Endian)
                    "0a0d0d0a",  # PCAP-NG format
                ]
                return magic_hex in valid_pcap_magics
        except Exception:
            return False

class FileService(BaseService[File]):
    # Default limits for archive extraction
    MAX_NESTING_DEPTH = 5  # Maximum depth for nested archives
    MAX_EXTRACTED_SIZE = 1024 * 1024 * 1024  # 1GB limit for total extracted size
    MAX_EXTRACTED_FILES = 1000  # Maximum number of extracted files per archive

    def __init__(self, session: Session, user: User, storage: FileStorage):
        self.user = user
        self.storage = storage
        self.header_matcher = HeaderMatcher()
        self.preset_cache = {}
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

    def get_preset(self, file_id: str, file_type: str) -> Optional[Preset]:
        """Match preset headers as substrings in file header; use default preset (header='') if no match."""
        if file_type == ContentType.TEXT.value:
            try:
                src = self.storage.get(file_id)
                encoding_res = from_path(src).best()
                if not encoding_res:
                    logger.error({
                        "event": "encoding_detection_failed",
                        "file_id": file_id,
                        "error": "Cannot detect file encoding",
                    })
                    return None
                encoding = encoding_res.encoding

                with src.open("r", encoding=encoding) as file:
                    header = file.readline().strip()
                
                logger.debug({
                    "event": "file_header_read",
                    "file_id": file_id,
                    "file_type": file_type,
                    "header": header,
                })

                if file_type not in self.preset_cache:
                    presets = self.session.query(Preset).filter(
                        Preset.header != None
                    ).order_by(Preset.id).all()
                    default_preset = next(
                        (p for p in presets if p.header == ''),
                        None
                    )
                    self.preset_cache[file_type] = {
                        'presets': presets,
                        'default': default_preset
                    }
                else:
                    presets = self.preset_cache[file_type]['presets']
                    default_preset = self.preset_cache[file_type]['default']

                if not presets:
                    logger.warning({
                        "event": "no_presets_available",
                        "file_id": file_id,
                        "file_type": file_type,
                    })
                    return None

                if not default_preset:
                    logger.warning({
                        "event": "no_default_preset",
                        "file_id": file_id,
                        "file_type": file_type,
                    })
                    return None

                for preset in presets:
                    if preset.header == "":
                        continue
                    if self.header_matcher.match_header(header, preset.header):
                        logger.info({
                            "event": "preset_matched",
                            "file_id": file_id,
                            "file_type": file_type,
                            "file_header": header,
                            "preset_id": str(preset.id),
                            "preset_name": preset.name,
                            "preset_header": preset.header,
                        })
                        return preset

                logger.info({
                    "event": "default_preset_assigned",
                    "file_id": file_id,
                    "file_type": file_type,
                    "file_header": header,
                    "preset_id": str(default_preset.id),
                    "preset_name": default_preset.name,
                    "preset_header": default_preset.header,
                })
                return default_preset

            except Exception as ex:
                logger.error({
                    "event": "preset_assignment_failed",
                    "file_id": file_id,
                    "file_type": file_type,
                    "error": str(ex),
                })
                return None

        elif file_type == ContentType.PCAP.value:
            try:
                src = self.storage.get(file_id)
                # Read first 4 bytes for PCAP magic number
                with src.open("rb") as file:  # Note: binary mode
                    magic_bytes = file.read(4)
                    magic_hex = magic_bytes.hex()
                
                logger.debug({
                    "event": "pcap_header_read",
                    "file_id": file_id,
                    "file_type": file_type,
                    "magic_hex": magic_hex,
                })
                
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
                        logger.info({
                            "event": "pcap_preset_assigned",
                            "file_id": file_id,
                            "file_type": file_type,
                            "preset_id": str(preset.id),
                            "preset_name": preset.name,
                            "magic_hex": magic_hex,
                            "format": "PCAP-NG" if magic_hex == "0a0d0d0a" else "PCAP",
                        })
                        return preset
                    else:
                        logger.warning({
                            "event": "pcap_preset_not_found",
                            "file_id": file_id,
                            "file_type": file_type,
                        })
                        return None
                else:
                    # Not a valid PCAP file
                    logger.warning({
                        "event": "invalid_pcap_file",
                        "file_id": file_id,
                        "file_type": file_type,
                        "magic_hex": magic_hex,
                        "expected": valid_pcap_magics,
                    })
                    return None
                    
            except Exception as ex:
                logger.error({
                    "event": "pcap_header_read_failed",
                    "file_id": file_id,
                    "file_type": file_type,
                    "error": str(ex),
                })
                return None

        else:
            logger.debug({
                "event": "preset_assignment_skipped",
                "file_id": file_id,
                "file_type": file_type,
            })
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
        elif finfo.ftype in self.storage.ARCHIVE_TYPES:
            content_type = ContentType.ARCHIVE
        else:
            self.storage.delete(finfo.fid)
            raise ValueError(f"Unsupported file type: {finfo.ftype}")

        file_obj = File(
            id=finfo.fid,
            filename=finfo.fname,
            file_size=finfo.fsize,
            content_type=content_type,
            user=self.user,
            preset=None,  # No preset assignment during upload
            product=None,  # No product assignment during upload
            archive_id=archive_id,
        )
        self.create(file_obj)
        return file_obj

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
                try:
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
                        "event": "partial_unpack_failed",
                        "file_id": file.id,
                        "filename": file.filename,
                        "child_fid": finfo.fid,
                        "child_filename": finfo.fname,
                        "nesting_level": nesting_level,
                        "error": str(e),
                    }, extra={"context": {"file_id": file.id}})
                    continue
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

    def process_file(self, file_id: str):
        """Process a file, handling archives and individual files without validation."""
        file = self.get_by_id(file_id)
        if not file:
            logger.error({
                "event": "process_failed",
                "file_id": file_id,
                "error": "File not found",
            })
            raise ValueError("File not found")

        if file.status is not FileStatus.CREATED:
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

        is_archive = file.content_type == ContentType.ARCHIVE
        files = []

        try:
            if is_archive:
                files = self.unpack_file(file)
                if files:
                    file.extracted_size = sum(f.file_size for f in files)
                    file.status = FileStatus.IN_PROGRESS
                    file.completed_size = 0
                    file.time_remaining = 0
                    self.session.commit()
                    logger.debug({
                        "event": "archive_unpacked",
                        "file_id": file_id,
                        "filename": file.filename,
                        "extracted_size": file.extracted_size,
                        "file_count": len(files),
                    })
                else:
                    logger.info({
                        "event": "archive_empty",
                        "file_id": file_id,
                        "filename": file.filename,
                        "message": "No files extracted, proceeding with empty archive",
                    })
                    file.status = FileStatus.DONE
                    file.completed_size = file.file_size
                    file.time_remaining = 0
                    self.session.commit()
                    return file
            else:
                files = [file]

            try:
                task_configs = self.make_task_config(files)
                for task_config in task_configs:
                    self.preprocess_file(**task_config)
            except Exception as e:
                file.status = FileStatus.ERROR
                self.session.commit()
                logger.error({
                    "event": "preprocess_failed",
                    "file_id": file_id,
                    "filename": file.filename,
                    "error": str(e),
                })
                raise ValueError(f"Failed to preprocess files: {str(e)}")

            if is_archive and files:
                try:
                    self.storage.repack(file)
                    file.status = FileStatus.DONE
                    file.completed_size = file.file_size
                    file.time_remaining = 0
                    self.session.commit()
                    for child in file.archive_files:
                        self.delete_file(child.id)
                    logger.info({
                        "event": "archive_repacked",
                        "file_id": file_id,
                        "filename": file.filename,
                    })
                except Exception as e:
                    file.status = FileStatus.ERROR
                    self.session.commit()
                    logger.error({
                        "event": "repack_failed",
                        "file_id": file_id,
                        "filename": file.filename,
                        "error": str(e),
                    })
                    raise ValueError(f"Failed to repack archive: {str(e)}")

            return file

        except ValueError as e:
            raise
        except Exception as e:
            file.status = FileStatus.ERROR
            self.session.commit()
            logger.error({
                "event": "process_failed",
                "file_id": file_id,
                "filename": file.filename,
                "error": str(e),
            })
            raise ValueError(f"Processing failed: {str(e)}")

    def process_file_with_product(self, file_id: str, product_id: int):
        """Process a file using product-specific presets and rules."""
        file = self.get_by_id(file_id)
        if not file:
            logger.error({
                "event": "process_failed",
                "file_id": file_id,
                "error": "File not found",
            })
            raise ValueError("File not found")

        if file.status is not FileStatus.CREATED:
            logger.error({
                "event": "process_failed",
                "file_id": file_id,
                "error": "File processing is already started",
            })
            raise ValueError("File processing is already started")

        # Get product name for logging
        product = self.session.query(Product).filter(Product.id == product_id).first()
        product_name = product.name if product else f"Unknown Product (ID: {product_id})"
        
        logger.info({
            "event": "product_process_started",
            "file_id": file_id,
            "filename": file.filename,
            "content_type": file.content_type.value,
            "product_id": product_id,
            "product_name": product_name,
        })

        is_archive = file.content_type == ContentType.ARCHIVE
        files = []

        try:
            if is_archive:
                files = self.unpack_file(file)
                if files:
                    file.extracted_size = sum(f.file_size for f in files)
                    file.status = FileStatus.IN_PROGRESS
                    file.completed_size = 0
                    file.time_remaining = 0
                    self.session.commit()
                    logger.debug({
                        "event": "archive_unpacked",
                        "file_id": file_id,
                        "filename": file.filename,
                        "extracted_size": file.extracted_size,
                        "file_count": len(files),
                    })
                else:
                    logger.info({
                        "event": "archive_empty",
                        "file_id": file_id,
                        "filename": file.filename,
                        "message": "No files extracted, proceeding with empty archive",
                    })
                    file.status = FileStatus.DONE
                    file.completed_size = file.file_size
                    file.time_remaining = 0
                    self.session.commit()
                    return file
            else:
                files = [file]

            try:
                # Use product-specific preset selection and rules
                task_configs = self.make_product_task_config(files, product_id)
                for task_config in task_configs:
                    self.preprocess_file(**task_config)
            except Exception as e:
                file.status = FileStatus.ERROR
                self.session.commit()
                logger.error({
                    "event": "preprocess_failed",
                    "file_id": file_id,
                    "filename": file.filename,
                    "error": str(e),
                })
                raise ValueError(f"Failed to preprocess files: {str(e)}")

            if is_archive and files:
                try:
                    self.storage.repack(file)
                    file.status = FileStatus.DONE
                    file.completed_size = file.file_size
                    file.time_remaining = 0
                    self.session.commit()
                    for child in file.archive_files:
                        self.delete_file(child.id)
                    logger.info({
                        "event": "archive_repacked",
                        "file_id": file_id,
                        "filename": file.filename,
                    })
                except Exception as e:
                    file.status = FileStatus.ERROR
                    self.session.commit()
                    logger.error({
                        "event": "repack_failed",
                        "file_id": file_id,
                        "filename": file.filename,
                        "error": str(e),
                    })
                    raise ValueError(f"Failed to repack archive: {str(e)}")

            return file

        except ValueError as e:
            raise
        except Exception as e:
            file.status = FileStatus.ERROR
            self.session.commit()
            logger.error({
                "event": "process_failed",
                "file_id": file_id,
                "filename": file.filename,
                "error": str(e),
            })
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

    def preprocess_file(self, files: Dict[str, str], rules_configs: Dict[str, List]):
        """Preprocess a list of files with the given rules configurations."""
        try:
            start_time = time.time()
            configs = {}
            for file_id, preset_id in files.items():
                config = configs.get(preset_id)
                if not config:
                    config = ProcessingConfig(
                        rules_config=rules_configs[preset_id],
                        maskingMapService=MaskingMapService(self.session),
                    )
                    configs[preset_id] = config
                self._process_file(config, file_id)

                processed_file = self.get_by_id(file_id)
                if processed_file and processed_file.archive_id:
                    parent = processed_file.archive
                    if parent.status == FileStatus.IN_PROGRESS:
                        processed_size = sum(
                            child.file_size
                            for child in parent.archive_files
                            if child.status == FileStatus.DONE
                        )
                        parent.completed_size = processed_size
                        if processed_size > 0:
                            elapsed = time.time() - start_time
                            if elapsed > 0:
                                rate = processed_size / elapsed
                                remaining = parent.extracted_size - processed_size
                                parent.time_remaining = (
                                    int(remaining / rate) if rate > 0 else 0
                                )
                        self.session.commit()
                        logger.debug({
                            "event": "archive_progress_updated",
                            "file_id": file_id,
                            "parent_id": parent.id,
                            "completed_size": parent.completed_size,
                            "time_remaining": parent.time_remaining,
                        })

        except Exception as e:
            file_ids = list(files.keys())
            logger.error({
                "event": "preprocess_failed",
                "file_ids": file_ids,
                "error": str(e),
            }, extra={"context": {"file_id": file_ids}})
            self.session.query(File).filter(
                (File.status != FileStatus.DONE) & File.id.in_(file_ids)
            ).update({"status": FileStatus.ERROR})
            self.session.commit()
            raise ValueError(f"Preprocessing failed: {str(e)}")

    def _process_file(self, config: ProcessingConfig, file_id: str) -> None:
        """Process a single file with the given configuration."""
        file_obj = self.get_by_id(file_id)
        if not file_obj:
            logger.error({
                "event": "process_failed",
                "file_id": file_id,
                "error": "File not found",
            })
            raise FileNotFoundError(f"File with id {file_id} not found.")

        file_obj.status = FileStatus.IN_PROGRESS
        content_type = file_obj.content_type
        src = self.storage.get(file_id)

        if not src.exists():
            logger.error({
                "event": "process_failed",
                "file_id": file_id,
                "filename": file_obj.filename,
                "error": f"Source file does not exist: {src}",
            })
            file_obj.status = FileStatus.ERROR
            self.session.commit()
            raise FileNotFoundError(f"Source file does not exist: {src}")

        mime = magic.from_file(str(src), mime=True)
        file_type_description = magic.from_file(str(src))
        is_capture_file = mime == "application/vnd.tcpdump.pcap"
        logger.info({
            "event": "file_processing_started",
            "file_id": file_id,
            "filename": file_obj.filename,
            "content_type": file_type_description,
            "mime_type": mime,
            "file_type_description": file_type_description,
            "is_capture_file": is_capture_file,
        })

        processor = config.make_processor(content_type=content_type.value)

        base, ext = os.path.splitext(file_obj.filename)
        ext = ext.lower()
        if ext in ['.txt', '.csv', '.pcap', '.json', '.log']:
            dst_filename = f"{base}_masked{ext}" if not base.endswith('_masked') else file_obj.filename
        else:
            file_type = self.storage.get_type(file_id)
            dst_filename = f"{base}_masked.pcap" if file_type == self.storage.T_PCAP else f"{base}_masked.txt"

        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_masked{ext}", dir=self.storage.base_dir) as temp_file:
            temp_dst = pathlib.Path(temp_file.name)
            try:
                if content_type == ContentType.TEXT:
                    encoding_res = from_path(src).best()
                    if not encoding_res:
                        logger.error({
                            "event": "process_failed",
                            "file_id": file_id,
                            "filename": file_obj.filename,
                            "error": "Cannot detect encoding for file",
                        })
                        raise PcapProcessingError("Cannot detect encoding for file")
                    encoding = encoding_res.encoding
                    done_size = 0
                    unreported = 0
                    total_size = self.storage.get_size(file_id)
                    max_report_num = int(total_size / settings.REPORT_STEP)
                    process_time = 0
                    report_count = 1
                    with temp_dst.open("w", newline="", encoding=encoding) as f_dst:
                        with src.open("r", newline="", encoding=encoding) as f_src:
                            operation_time = time.time()
                            for chunk in processor.feed(f_src):
                                f_dst.write(chunk)
                                chunk_bytes_len = len(chunk.encode())
                                done_size += chunk_bytes_len
                                unreported += chunk_bytes_len
                                if unreported >= settings.REPORT_STEP:
                                    process_time += time.time() - operation_time
                                    average_process_time = process_time / report_count
                                    operation_time = time.time()
                                    chunk_num = max_report_num - report_count
                                    time_remain = int(chunk_num * average_process_time)
                                    file_obj.completed_size = done_size
                                    file_obj.time_remaining = time_remain
                                    self.session.commit()
                                    logger.debug({
                                        "event": "progress_update",
                                        "file_id": file_id,
                                        "completed_size": done_size,
                                        "time_remaining": time_remain,
                                    })
                                    report_count += 1
                                    unreported = 0

                elif content_type == ContentType.PCAP:
                    done_size = 0
                    total_size = self.storage.get_size(file_id)
                    operation_time = time.time()
                    for item in processor.feed(src):
                        if len(item) != 3:
                            logger.error({
                                "event": "invalid_packet_tuple",
                                "file_id": file_id,
                                "filename": file_obj.filename,
                                "tuple": str(item),
                                "expected": "(ts, output_path, linktype)",
                            })
                            raise PcapProcessingError(f"Invalid packet tuple: {item}")
                        _ts, output_path, _linktype = item
                        done_size = os.path.getsize(output_path)
                        os.rename(output_path, temp_dst)
                        logger.info({
                            "event": "pcap_processed",
                            "file_id": file_id,
                            "filename": file_obj.filename,
                            "total_size": done_size,
                            "output_file": str(temp_dst),
                        })
                        break
                    file_obj.completed_size = done_size
                    file_obj.time_remaining = 0
                    self.session.commit()

                else:
                    logger.error({
                        "event": "process_failed",
                        "file_id": file_id,
                        "filename": file_obj.filename,
                        "error": f"Unsupported content type: {content_type}",
                    })
                    raise PcapProcessingError(f"Unsupported content type: {content_type}")

                logger.info({
                    "event": "file_processed",
                    "file_id": file_id,
                    "filename": file_obj.filename,
                    "new_filename": dst_filename,
                    "src_path": str(temp_dst),
                    "dst_path": str(src),
                })
                temp_dst.rename(src)
                file_obj.filename = dst_filename
                file_obj.status = FileStatus.DONE
                file_obj.completed_size = done_size
                file_obj.time_remaining = 0
                file_obj.file_size = self.storage.get_size(file_id)
                self.session.commit()

            except Exception as ex:
                logger.error({
                    "event": "process_error",
                    "file_id": file_id,
                    "filename": file_obj.filename,
                    "error": str(ex),
                })
                path = pathlib.Path(file_obj.filename)
                path_parts = list(path.parts)
                path_parts[-1] = "failed_" + path_parts[-1]
                filename = "/".join(path_parts)
                file_obj.status = FileStatus.ERROR
                file_obj.filename = filename
                if temp_dst.exists():
                    temp_dst.unlink()
                self.session.commit()
                raise PcapProcessingError(f"Error processing file {file_id}: {str(ex)}")

    def get_rule_config(self, presetRule: PresetRule):
        cfg = presetRule.rule.config
        cfg["category"] = presetRule.rule.category
        cfg["patcher_cfg"] = presetRule.action
        return cfg

    def make_task_config(self, file_objs: list[File]):
        """Make task config."""
        file_wo_preset = (
            self.session.query(File)
            .filter(
                File.id.in_([file_obj.id for file_obj in file_objs]),
                File.preset == None,
            )
            .all()
        )
        if file_wo_preset:
            raise Exception(f"{file_wo_preset[0].filename} has no assigned preset")

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

        preset_files_map = collections.defaultdict(list)
        files_items = sorted(files.items(), key=lambda x: -x[1]["size"])
        for file_id, file_info in files_items:
            preset_files_map[file_info["preset_id"]].append(file_id)

        tasks_configs = []
        group_files = {}
        group_rules = {}
        for preset_id, file_ids in preset_files_map.items():
            group_rules[preset_id] = presets_cfgs[preset_id]
            for file_id in file_ids:
                group_files[file_id] = preset_id
        tasks_configs.append({"files": group_files, "rules_configs": group_rules})

        return tasks_configs

    def make_product_task_config(self, file_objs: list[File], product_id: int):
        """Make task config using product-specific presets and rules with header matching."""
        try:
            # Get all presets for the specified product
            product_presets = self.session.query(Preset).filter(Preset.product_id == product_id).all()
            
            if not product_presets:
                logger.warning({
                    "event": "no_product_presets",
                    "product_id": product_id,
                    "message": "No presets found for product, using default processing"
                })
                # Fall back to default processing if no product presets
                return self.make_task_config(file_objs)
            
            logger.info({
                "event": "product_presets_loaded",
                "product_id": product_id,
                "preset_count": len(product_presets),
                "preset_names": [p.name for p in product_presets]
            })
            
            # For each file, try to match headers with product presets
            file_preset_map = {}
            any_header_match = False
            
            for file_obj in file_objs:
                matched_preset = self.match_file_with_product_presets(file_obj, product_presets)
                if matched_preset:
                    file_preset_map[file_obj.id] = matched_preset
                    any_header_match = True
                    logger.info({
                        "event": "preset_matched_for_file",
                        "file_id": file_obj.id,
                        "filename": file_obj.filename,
                        "preset_id": matched_preset.id,
                        "preset_name": matched_preset.name,
                        "product_id": product_id
                    })
                else:
                    # If no header match, use the first preset (will be updated below if no matches found)
                    file_preset_map[file_obj.id] = product_presets[0]
            
            # Log header matching summary
            if any_header_match:
                logger.info({
                    "event": "header_matching_summary",
                    "product_id": product_id,
                    "total_files": len(file_objs),
                    "files_with_header_match": len([f for f in file_objs if self.match_file_with_product_presets(f, product_presets)]),
                    "action": "Using matched presets for files with header matches"
                })
            else:
                logger.info({
                    "event": "header_matching_summary",
                    "product_id": product_id,
                    "total_files": len(file_objs),
                    "files_with_header_match": 0,
                    "action": "No header matches found - combining all preset rules into single processing task"
                })
                
            
            # Create task configurations - use same structure as make_task_config
            tasks_configs = []
            
            # Handle the case where no header match was found (combine all preset rules)
            if not any_header_match:
                # Combine all rules from all presets into a single task configuration
                # This prevents duplicate file processing
                combined_rules = []
                preset_id = "combined"  # Use a single preset ID for combined rules
                
                for preset in product_presets:
                    preset_rules = [self.get_rule_config(pr) for pr in preset.rules]
                    combined_rules.extend(preset_rules)
                    logger.info({
                        "event": "preset_rules_combined",
                        "preset_id": preset.id,
                        "preset_name": preset.name,
                        "rules_count": len(preset_rules)
                    })
                
                # Create single task configuration with all files and combined rules
                group_files = {}
                for file_obj in file_objs:
                    group_files[file_obj.id] = preset_id
                
                tasks_configs.append({
                    "files": group_files, 
                    "rules_configs": {preset_id: combined_rules}
                })
                
                logger.info({
                    "event": "combined_rules_created",
                    "total_presets": len(product_presets),
                    "total_combined_rules": len(combined_rules),
                    "files_count": len(file_objs)
                })
            else:
                # Normal processing - files have specific preset assignments
                files = {}
                presets_cfgs = {}
                
                for file_obj in file_objs:
                    preset = file_preset_map[file_obj.id]
                    preset_id = str(preset.id)
                    if preset_id not in presets_cfgs:
                        preset_rules = [self.get_rule_config(pr) for pr in preset.rules]
                        presets_cfgs[preset_id] = preset_rules
                    files[file_obj.id] = {"preset_id": preset_id, "size": file_obj.file_size}

                # Group files by preset
                preset_files_map = collections.defaultdict(list)
                files_items = sorted(files.items(), key=lambda x: -x[1]["size"])
                for file_id, file_info in files_items:
                    preset_files_map[file_info["preset_id"]].append(file_id)

                # Create single task configuration
                group_files = {}
                group_rules = {}
                for preset_id, file_ids in preset_files_map.items():
                    group_rules[preset_id] = presets_cfgs[preset_id]
                    for file_id in file_ids:
                        group_files[file_id] = preset_id
                tasks_configs.append({"files": group_files, "rules_configs": group_rules})
            
            logger.info({
                "event": "product_task_config_created",
                "product_id": product_id,
                "file_count": len(file_objs),
                "task_config_count": len(tasks_configs)
            })
            
            return tasks_configs
            
        except Exception as e:
            logger.error({
                "event": "product_task_config_failed",
                "product_id": product_id,
                "error": str(e)
            })
            # Fall back to default processing on error
            return self.make_task_config(file_objs)

    def match_file_with_product_presets(self, file_obj: File, product_presets: list[Preset]) -> Optional[Preset]:
        """Match a file with product presets using header matching."""
        try:
            if file_obj.content_type == ContentType.TEXT:
                # Read file header for text files
                src = self.storage.get(file_obj.id)
                encoding_res = from_path(src).best()
                if not encoding_res:
                    logger.error({
                        "event": "encoding_detection_failed",
                        "file_id": file_obj.id,
                        "error": "Cannot detect file encoding",
                    })
                    return None
                encoding = encoding_res.encoding

                with src.open("r", encoding=encoding) as file:
                    header = file.readline().strip()
                
                logger.debug({
                    "event": "file_header_read",
                    "file_id": file_obj.id,
                    "filename": file_obj.filename,
                    "header": header,
                })

                # Try to match header with product presets
                for preset in product_presets:
                    if preset.header and preset.header in header:
                        logger.info({
                            "event": "header_match_found",
                            "file_id": file_obj.id,
                            "preset_id": preset.id,
                            "preset_name": preset.name,
                            "header": header,
                            "preset_header": preset.header
                        })
                        return preset
                
                # No header match found
                logger.debug({
                    "event": "no_header_match",
                    "file_id": file_obj.id,
                    "filename": file_obj.filename,
                    "header": header,
                    "available_headers": [p.header for p in product_presets if p.header]
                })
                return None

            elif file_obj.content_type == ContentType.PCAP:
                # For PCAP files, look for PCAP-specific preset within product
                for preset in product_presets:
                    if preset.name.lower() == "pcap":
                        logger.info({
                            "event": "pcap_preset_found",
                            "file_id": file_obj.id,
                            "preset_id": preset.id,
                            "preset_name": preset.name
                        })
                        return preset
                return None

            else:
                # For other file types, return the first preset
                logger.debug({
                    "event": "default_preset_for_file_type",
                    "file_id": file_obj.id,
                    "content_type": file_obj.content_type.value
                })
                return product_presets[0] if product_presets else None

        except Exception as e:
            logger.error({
                "event": "preset_matching_failed",
                "file_id": file_obj.id,
                "error": str(e)
            })
            return None

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

