"""
GDPR Tool Storage - File Storage and Archive Management

This module provides comprehensive file storage and archive handling capabilities for the GDPR tool.
It supports multiple archive formats, file type detection, and recursive archive extraction.

Key Components:
- FileStorage: Main storage class for file operations and archive handling
- FileInfo: Data class for file metadata (ID, name, size, type)
- BaseStorage: Base class for storage implementations

Supported File Types:
- Text Files: Plain text, JSON, CSV, log files
- PCAP Files: Network packet capture files
- Archive Files: ZIP, TAR, GZIP, BZIP2, XZ

Archive Processing Features:
- Recursive Extraction: Supports nested archives with depth limits
- Multiple Formats: Handles 5 different archive formats
- Type Detection: Uses MIME types, magic signatures, and file extensions
- Sanitization: Prevents path traversal attacks in archive contents
- Error Handling: Graceful handling of corrupted or unsupported archives
- Repacking: Recreates archives after processing with original format

File Operations:
- Upload: Temporary file storage with unique ID generation
- Type Detection: Multi-layered detection (MIME, magic, extension)
- Size Calculation: Accurate file size tracking
- Deletion: Safe file removal with error handling
- Path Management: Secure file path handling and sanitization

The storage system is designed to handle large files efficiently while maintaining
security and providing comprehensive archive support for GDPR data processing.
"""

from dataclasses import dataclass
import pathlib
import gzip
import tempfile
import magic
import zipfile
import tarfile
import shutil
import os
import json
import re
from charset_normalizer import from_bytes
try:
    import lzma
except ImportError:
    lzma = None
from database.models import MimeType
from typing import List, Iterator, Optional
from database.models import File
from logger import logger

@dataclass
class FileInfo:
    fid: str
    fname: Optional[str] = None
    fsize: Optional[int] = None
    ftype: Optional[str] = None

class BaseStorage:
    def __init__(self, base_dir: str | pathlib.Path):
        self.base_dir = pathlib.Path(base_dir)
        if not self.base_dir.exists():
            self.base_dir.mkdir(parents=True)

class FileStorage(BaseStorage):

    T_TEXT = "text"
    T_PCAP = "pcap"
    T_ZIP = "zip"
    T_TAR = "tar"
    T_GZIP = "gzip"
    T_BZIP2 = "bzip2"
    T_XZ = "xz"
    T_UNKNOWN = "unknown"

    FILE_TYPES = [T_TEXT, T_PCAP]
    ARCHIVE_TYPES = [
        T_ZIP, T_TAR, T_GZIP, T_BZIP2, T_XZ
    ]

    MIME_TYPES = {
        "application/zip": T_ZIP,
        "application/x-zip-compressed": T_ZIP,
        "application/x-tar": T_TAR,
        "application/gzip": T_GZIP,
        "application/x-gzip": T_GZIP,
        "application/x-bzip2": T_BZIP2,
        "application/x-xz": T_XZ,
        "application/vnd.tcpdump.pcap": T_PCAP,
        "application/octet-stream": None,  # Handled by magic signature
        "application/json": T_TEXT,  # Handle JSON as text
        "application/x-ndjson": T_TEXT,  # Handle NDJSON as text
    }

    EXTENSIONS = {
        ".zip": T_ZIP,
        ".tar": T_TAR,
        ".gz": T_GZIP,
        ".tgz": T_GZIP,
        ".tar.gz": T_GZIP,
        ".bz2": T_BZIP2,
        ".tar.bz2": T_BZIP2,
        ".xz": T_XZ,
        ".tar.xz": T_XZ,
        ".pcap": T_PCAP,
        ".pcapng": T_PCAP,
    }

    def save_file(self, file) -> str:
        dst = tempfile.NamedTemporaryFile(dir=self.base_dir, delete=False)
        try:
            with dst, file as src:
                shutil.copyfileobj(src, dst)
        except Exception:
            pathlib.Path(dst.name).unlink(missing_ok=True)
            raise
        return pathlib.Path(dst.name).name[3:]

    def get(self, file_id: str) -> pathlib.Path:
        path = self.base_dir.joinpath(f"tmp{file_id}")
        return path

    def get_size(self, file_id: str) -> int:
        file = self.get(file_id)
        return file.stat().st_size if file.exists() else 0
    
    def get_encoding(self, src: pathlib.Path) -> str:
        """Detects file encoding using first 4KB of the file"""
        with src.open("rb") as file:
            bytes = file.read(4096)
            
        res = from_bytes(bytes).best()
        encoding = res.encoding if res else None
        
        # File encoding can be detected as ASCII when it contains 
        # mostly ASCII characters with some UTF-8 characters mixed in (elasticDump).
        # If detected as ASCII, promote encoding to UTF-8
        if encoding and encoding.lower() == 'ascii':
            encoding = 'utf-8'
        return encoding

    def get_type(self, file_id: str) -> str:
        """Get file type based on MIME, magic signature, or extension."""
        path = self.get(file_id)
        if not path.exists():
            logger.error({
                "event": "get_type_failed",
                "file_id": file_id,
                "error": f"File does not exist: {path}"
            })
            return self.T_UNKNOWN

        try:
            mime = magic.from_file(str(path), mime=True)
            magic_sig = magic.from_file(str(path))
        except Exception as e:
            logger.error({
                "event": "get_type_failed",
                "file_id": file_id,
                "error": f"Failed to detect MIME type: {str(e)}"
            })
            mime = self.T_UNKNOWN
            magic_sig = ""

        # MIME-based detection
        if mime in self.MIME_TYPES:
            file_type = self.MIME_TYPES[mime]
            if file_type:
                return file_type

        # Special cases for octet-stream
        if mime == "application/octet-stream":
            if "pcapng capture file" in magic_sig.lower():
                return self.T_PCAP

        if mime in (MimeType.JSON.value, MimeType.TEXT.value, MimeType.TEXTX.value):
            return self.T_TEXT

        # Extension-based fallback
        ext = pathlib.Path(path.name).suffix.lower()
        for ext_key, ext_type in self.EXTENSIONS.items():
            if path.name.lower().endswith(ext_key):
                return ext_type

        logger.warning({
            "event": "get_type_unknown",
            "file_id": file_id,
            "path": str(path),
            "mime_type": mime,
            "magic_signature": magic_sig
        })
        return self.T_UNKNOWN

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filenames to prevent path traversal."""
        filename = re.sub(r'[^\w\-\_\.\\/]', '_', filename)
        filename = os.path.basename(filename)
        if not filename or filename in ('.', '..'):
            return f"unnamed_{os.urandom(4).hex()}"
        return filename

    def _unpack_zip(self, file_id: str, base: str, nesting_level: int) -> List[FileInfo]:
        path = self.get(file_id)
        if not path.exists():
            raise FileNotFoundError(f"Archive file does not exist: {path}")
        archive_info = []
        with tempfile.TemporaryDirectory(dir=self.base_dir) as temp_dir:
            try:
                with zipfile.ZipFile(path, 'r') as arc:
                    arc.extractall(temp_dir)
                for extracted in pathlib.Path(temp_dir).rglob("*"):
                    if extracted.is_file():
                        fname = self._sanitize_filename(os.path.relpath(extracted, temp_dir))
                        with extracted.open("rb") as stream:
                            fid = self.save_file(stream)
                        info = FileInfo(
                            fid=fid,
                            fname=os.path.join(base, fname),
                            fsize=extracted.stat().st_size,
                            ftype=self.get_type(fid)
                        )
                        archive_info.append(info)
            except zipfile.BadZipFile as e:
                logger.warning({
                    "event": "zip_unpack_failed",
                    "file_id": file_id,
                    "path": str(path),
                    "error": str(e)
                })
        return archive_info

    def _unpack_tar(self, file_id: str, base: str, nesting_level: int) -> List[FileInfo]:
        path = self.get(file_id)
        if not path.exists():
            raise FileNotFoundError(f"Archive file does not exist: {path}")
        archive_info = []
        with tempfile.TemporaryDirectory(dir=self.base_dir) as temp_dir:
            try:
                mode = 'r:*'
                with tarfile.open(path, mode) as arc:
                    arc.extractall(temp_dir)
                for extracted in pathlib.Path(temp_dir).rglob("*"):
                    if extracted.is_file():
                        fname = self._sanitize_filename(os.path.relpath(extracted, temp_dir))
                        with extracted.open("rb") as stream:
                            fid = self.save_file(stream)
                        info = FileInfo(
                            fid=fid,
                            fname=os.path.join(base, fname),
                            fsize=extracted.stat().st_size,
                            ftype=self.get_type(fid)
                        )
                        archive_info.append(info)
            except tarfile.TarError as e:
                logger.warning({
                    "event": "tar_unpack_failed",
                    "file_id": file_id,
                    "path": str(path),
                    "error": str(e)
                })
        return archive_info

    def _unpack_gzip(self, file_id: str, base: str, nesting_level: int) -> List[FileInfo]:
        path = self.get(file_id)
        if not path.exists():
            raise FileNotFoundError(f"Archive file does not exist: {path}")
        filename = base[:-3] if base.lower().endswith(".gz") else base
        with tempfile.NamedTemporaryFile(dir=self.base_dir, delete=False) as temp_file:
            try:
                with gzip.open(path) as stream:
                    shutil.copyfileobj(stream, temp_file)
                fid = pathlib.Path(temp_file.name).name[3:]
                info = FileInfo(
                    fid=fid,
                    fname=filename,
                    fsize=pathlib.Path(temp_file.name).stat().st_size,
                    ftype=self.get_type(fid)
                )
                return [info]
            except gzip.BadGzipFile as e:
                logger.warning({
                    "event": "gzip_unpack_failed",
                    "file_id": file_id,
                    "path": str(path),
                    "error": str(e)
                })
                return []

    def _unpack_bzip2(self, file_id: str, base: str, nesting_level: int) -> List[FileInfo]:
        path = self.get(file_id)
        if not path.exists():
            raise FileNotFoundError(f"Archive file does not exist: {path}")
        filename = base[:-4] if base.lower().endswith(".bz2") else base
        with tempfile.NamedTemporaryFile(dir=self.base_dir, delete=False) as temp_file:
            try:
                with open(path, 'rb') as src, open(temp_file.name, 'wb') as dst:
                    shutil.copyfileobj(src, dst)
                fid = pathlib.Path(temp_file.name).name[3:]
                info = FileInfo(
                    fid=fid,
                    fname=filename,
                    fsize=pathlib.Path(temp_file.name).stat().st_size,
                    ftype=self.get_type(fid)
                )
                return [info]
            except Exception as e:
                logger.warning({
                    "event": "bzip2_unpack_failed",
                    "file_id": file_id,
                    "path": str(path),
                    "error": str(e)
                })
                return []

    def _unpack_xz(self, file_id: str, base: str, nesting_level: int) -> List[FileInfo]:
        path = self.get(file_id)
        if not path.exists():
            raise FileNotFoundError(f"Archive file does not exist: {path}")
        filename = base[:-3] if base.lower().endswith(".xz") else base
        with tempfile.NamedTemporaryFile(dir=self.base_dir, delete=False) as temp_file:
            try:
                with lzma.open(path) as stream:
                    shutil.copyfileobj(stream, temp_file)
                fid = pathlib.Path(temp_file.name).name[3:]
                info = FileInfo(
                    fid=fid,
                    fname=filename,
                    fsize=pathlib.Path(temp_file.name).stat().st_size,
                    ftype=self.get_type(fid)
                )
                return [info]
            except lzma.LZMAError as e:
                logger.warning({
                    "event": "xz_unpack_failed",
                    "file_id": file_id,
                    "path": str(path),
                    "error": str(e)
                })
                return []





    def _unpack_file(self, file_id: str, ftype: str, base: str, nesting_level: int) -> List[FileInfo]:
        """Unpack archive based on file type."""
        if ftype not in self.ARCHIVE_TYPES:
            raise ValueError(f"Invalid archive type: {ftype}")
        method = getattr(self, f"_unpack_{ftype.lower()}")
        archive_info = method(file_id, base, nesting_level)
        return archive_info

    def unpack(self, file_id: str, filename: str, nesting_level: int = 0) -> Iterator[FileInfo]:
        """Unpack archive recursively, yielding FileInfo for each extracted file."""
        file_size = self.get_size(file_id)
        files = [FileInfo(file_id, filename, file_size)]
        try:
            while files:
                f_info = files.pop(0)
                f_type = self.get_type(f_info.fid)
                f_info.ftype = f_type
                if f_type not in self.ARCHIVE_TYPES:
                    yield f_info
                else:
                    try:
                        new_files = self._unpack_file(f_info.fid, f_type, f_info.fname, nesting_level)
                        if new_files:
                            # Recursively unpack nested archives
                            for new_file in new_files:
                                if self.get_type(new_file.fid) in self.ARCHIVE_TYPES:
                                    files.append(new_file)
                                else:
                                    yield new_file
                    except Exception as e:
                        logger.warning({
                            "event": "archive_unpack_failed",
                            "file_id": f_info.fid,
                            "filename": f_info.fname,
                            "nesting_level": nesting_level,
                            "error": str(e)
                        })
                        continue
        except GeneratorExit:
            for f_info in files:
                self.delete(f_info.fid)

    def repack(self, file: File):
        if not file.archive_files:
            raise ValueError("No extracted files found for the archive.")

        format = None
        base = file.filename
        for ext, ftype in self.EXTENSIONS.items():
            if file.filename.lower().endswith(ext) and ftype in self.ARCHIVE_TYPES:
                base = file.filename[:-len(ext)]
                format = ftype
                break
        if not format:
            format = "zip"

        src = self.get(file.id)
        dst = src.parent.joinpath(f"{src.name}.new")

        try:
            if format == "zip":
                with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as archive:
                    for child in file.archive_files:
                        file_path = self.get(child.id)
                        if not file_path.exists():
                            logger.error({
                                "event": "repack_failed",
                                "file_id": file.id,
                                "child_id": child.id,
                                "error": f"Child file does not exist: {file_path}"
                            })
                            raise FileNotFoundError(f"Child file does not exist: {file_path}")
                        archive.write(file_path, arcname=child.filename)
            elif format in ("tar", "gzip"):
                mode = "w:gz" if format == "gzip" else "w"
                with tarfile.open(dst, mode) as archive:
                    for child in file.archive_files:
                        file_path = self.get(child.id)
                        if not file_path.exists():
                            logger.error({
                                "event": "repack_failed",
                                "file_id": file.id,
                                "child_id": child.id,
                                "error": f"Child file does not exist: {file_path}"
                            })
                            raise FileNotFoundError(f"Child file does not exist: {file_path}")
                        archive.add(file_path, arcname=child.filename)
            elif format == "bzip2":
                with tarfile.open(dst, "w:bz2") as archive:
                    for child in file.archive_files:
                        file_path = self.get(child.id)
                        if not file_path.exists():
                            logger.error({
                                "event": "repack_failed",
                                "file_id": file.id,
                                "child_id": child.id,
                                "error": f"Child file does not exist: {file_path}"
                            })
                            raise FileNotFoundError(f"Child file does not exist: {file_path}")
                        archive.add(file_path, arcname=child.filename)
            elif format == "xz":
                with tarfile.open(dst, "w:xz") as archive:
                    for child in file.archive_files:
                        file_path = self.get(child.id)
                        if not file_path.exists():
                            logger.error({
                                "event": "repack_failed",
                                "file_id": file.id,
                                "child_id": child.id,
                                "error": f"Child file does not exist: {file_path}"
                            })
                            raise FileNotFoundError(f"Child file does not exist: {file_path}")
                        archive.add(file_path, arcname=child.filename)
            else:
                raise ValueError(f"Unsupported archive format for repacking: {format}")

            dst.rename(src)
            file.filename = f"{base}.{format}"
            if file.file_size != src.stat().st_size:
                file.file_size = src.stat().st_size

        except Exception as e:
            if dst.exists():
                dst.unlink(missing_ok=True)
            raise

    def delete(self, file_id):
        file_path = self.get(file_id)
        try:
            file_path.unlink()
        except FileNotFoundError:
            pass  # File already deleted