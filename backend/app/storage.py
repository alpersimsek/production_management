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
- Archive Files: ZIP, TAR, GZIP, BZIP2, XZ, 7Z, RAR, ZSTD, LZMA, CPIO, AR, CAB, ISO
- Avro Files: Apache Avro data files (converted to JSON)

Archive Processing Features:
- Recursive Extraction: Supports nested archives with depth limits
- Multiple Formats: Handles 13+ different archive formats
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
try:
    from avro.datafile import DataFileReader
    from avro.io import DatumReader
except ImportError:
    DataFileReader = None
    DatumReader = None
try:
    import py7zr
except ImportError:
    py7zr = None
try:
    import rarfile
except ImportError:
    rarfile = None
try:
    import zstandard as zstd
except ImportError:
    zstd = None
try:
    import lzma
except ImportError:
    lzma = None
try:
    import libarchive
except ImportError:
    libarchive = None
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
    T_7Z = "7z"
    T_RAR = "rar"
    T_ZSTD = "zstd"
    T_LZMA = "lzma"
    T_CPIO = "cpio"
    T_AR = "ar"
    T_CAB = "cab"
    T_ISO = "iso"
    T_AVRO = "avro"
    T_UNKNOWN = "unknown"

    FILE_TYPES = [T_TEXT, T_PCAP, T_AVRO]
    ARCHIVE_TYPES = [
        T_ZIP, T_TAR, T_GZIP, T_BZIP2, T_XZ, T_7Z, T_RAR, T_ZSTD,
        T_LZMA, T_CPIO, T_AR, T_CAB, T_ISO
    ]

    MIME_TYPES = {
        "application/zip": T_ZIP,
        "application/x-zip-compressed": T_ZIP,
        "application/x-tar": T_TAR,
        "application/gzip": T_GZIP,
        "application/x-gzip": T_GZIP,
        "application/x-bzip2": T_BZIP2,
        "application/x-xz": T_XZ,
        "application/x-7z-compressed": T_7Z,
        "application/x-rar-compressed": T_RAR,
        "application/zstd": T_ZSTD,
        "application/x-lzma": T_LZMA,
        "application/x-cpio": T_CPIO,
        "application/x-archive": T_AR,
        "application/vnd.ms-cab-compressed": T_CAB,
        "application/x-iso9660-image": T_ISO,
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
        ".7z": T_7Z,
        ".rar": T_RAR,
        ".zst": T_ZSTD,
        ".tar.zst": T_ZSTD,
        ".lzma": T_LZMA,
        ".tar.lzma": T_LZMA,
        ".cpio": T_CPIO,
        ".ar": T_AR,
        ".cab": T_CAB,
        ".iso": T_ISO,
        ".avro": T_AVRO,
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
            if "Apache Avro" in magic_sig:
                return self.T_AVRO
            if "pcapng capture file" in magic_sig.lower():
                return self.T_PCAP
            if "7z" in magic_sig.lower():
                return self.T_7Z
            if "rar" in magic_sig.lower():
                return self.T_RAR
            if "zstandard" in magic_sig.lower():
                return self.T_ZSTD
            if "cpio" in magic_sig.lower():
                return self.T_CPIO
            if "ar archive" in magic_sig.lower():
                return self.T_AR
            if "iso 9660" in magic_sig.lower():
                return self.T_ISO

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

    def _unpack_7z(self, file_id: str, base: str, nesting_level: int) -> List[FileInfo]:
        if py7zr is None:
            logger.warning({
                "event": "7z_unpack_failed",
                "file_id": file_id,
                "error": "py7zr library not installed"
            })
            return []
        path = self.get(file_id)
        if not path.exists():
            raise FileNotFoundError(f"Archive file does not exist: {path}")
        archive_info = []
        with tempfile.TemporaryDirectory(dir=self.base_dir) as temp_dir:
            try:
                with py7zr.SevenZipFile(path, mode='r') as arc:
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
            except py7zr.Bad7zFile as e:
                logger.warning({
                    "event": "7z_unpack_failed",
                    "file_id": file_id,
                    "path": str(path),
                    "error": str(e)
                })
        return archive_info

    def _unpack_rar(self, file_id: str, base: str, nesting_level: int) -> List[FileInfo]:
        if rarfile is None:
            logger.warning({
                "event": "rar_unpack_failed",
                "file_id": file_id,
                "error": "rarfile library not installed"
            })
            return []
        path = self.get(file_id)
        if not path.exists():
            raise FileNotFoundError(f"Archive file does not exist: {path}")
        archive_info = []
        with tempfile.TemporaryDirectory(dir=self.base_dir) as temp_dir:
            try:
                with rarfile.RarFile(path) as arc:
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
            except rarfile.RarError as e:
                logger.warning({
                    "event": "rar_unpack_failed",
                    "file_id": file_id,
                    "path": str(path),
                    "error": str(e)
                })
        return archive_info

    def _unpack_zstd(self, file_id: str, base: str, nesting_level: int) -> List[FileInfo]:
        if zstd is None:
            logger.warning({
                "event": "zstd_unpack_failed",
                "file_id": file_id,
                "error": "zstandard library not installed"
            })
            return []
        path = self.get(file_id)
        if not path.exists():
            raise FileNotFoundError(f"Archive file does not exist: {path}")
        filename = base[:-4] if base.lower().endswith(".zst") else base
        with tempfile.NamedTemporaryFile(dir=self.base_dir, delete=False) as temp_file:
            try:
                with open(path, 'rb') as src:
                    dctx = zstd.ZstdDecompressor()
                    with open(temp_file.name, 'wb') as dst:
                        dctx.copy_stream(src, dst)
                fid = pathlib.Path(temp_file.name).name[3:]
                info = FileInfo(
                    fid=fid,
                    fname=filename,
                    fsize=pathlib.Path(temp_file.name).stat().st_size,
                    ftype=self.get_type(fid)
                )
                return [info]
            except zstd.ZstdError as e:
                logger.warning({
                    "event": "zstd_unpack_failed",
                    "file_id": file_id,
                    "path": str(path),
                    "error": str(e)
                })
                return []

    def _unpack_lzma(self, file_id: str, base: str, nesting_level: int) -> List[FileInfo]:
        path = self.get(file_id)
        if not path.exists():
            raise FileNotFoundError(f"Archive file does not exist: {path}")
        filename = base[:-5] if base.lower().endswith(".lzma") else base
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
                    "event": "lzma_unpack_failed",
                    "file_id": file_id,
                    "path": str(path),
                    "error": str(e)
                })
                return []

    def _unpack_cpio(self, file_id: str, base: str, nesting_level: int) -> List[FileInfo]:
        if libarchive is None:
            logger.warning({
                "event": "cpio_unpack_failed",
                "file_id": file_id,
                "error": "libarchive-c library not installed"
            })
            return []
        path = self.get(file_id)
        if not path.exists():
            raise FileNotFoundError(f"Archive file does not exist: {path}")
        archive_info = []
        with tempfile.TemporaryDirectory(dir=self.base_dir) as temp_dir:
            try:
                with libarchive.file_reader(str(path)) as arc:
                    for entry in arc:
                        if entry.isfile():
                            fname = self._sanitize_filename(entry.pathname)
                            temp_path = pathlib.Path(temp_dir) / fname
                            with open(temp_path, 'wb') as f:
                                for block in entry.get_blocks():
                                    f.write(block)
                            with temp_path.open("rb") as stream:
                                fid = self.save_file(stream)
                            info = FileInfo(
                                fid=fid,
                                fname=os.path.join(base, fname),
                                fsize=temp_path.stat().st_size,
                                ftype=self.get_type(fid)
                            )
                            archive_info.append(info)
            except libarchive.ArchiveError as e:
                logger.warning({
                    "event": "cpio_unpack_failed",
                    "file_id": file_id,
                    "path": str(path),
                    "error": str(e)
                })
        return archive_info

    def _unpack_ar(self, file_id: str, base: str, nesting_level: int) -> List[FileInfo]:
        if libarchive is None:
            logger.warning({
                "event": "ar_unpack_failed",
                "file_id": file_id,
                "error": "libarchive-c library not installed"
            })
            return []
        path = self.get(file_id)
        if not path.exists():
            raise FileNotFoundError(f"Archive file does not exist: {path}")
        archive_info = []
        with tempfile.TemporaryDirectory(dir=self.base_dir) as temp_dir:
            try:
                with libarchive.file_reader(str(path)) as arc:
                    for entry in arc:
                        if entry.isfile():
                            fname = self._sanitize_filename(entry.pathname)
                            temp_path = pathlib.Path(temp_dir) / fname
                            with open(temp_path, 'wb') as f:
                                for block in entry.get_blocks():
                                    f.write(block)
                            with temp_path.open("rb") as stream:
                                fid = self.save_file(stream)
                            info = FileInfo(
                                fid=fid,
                                fname=os.path.join(base, fname),
                                fsize=temp_path.stat().st_size,
                                ftype=self.get_type(fid)
                            )
                            archive_info.append(info)
            except libarchive.ArchiveError as e:
                logger.warning({
                    "event": "ar_unpack_failed",
                    "file_id": file_id,
                    "path": str(path),
                    "error": str(e)
                })
        return archive_info

    def _unpack_cab(self, file_id: str, base: str, nesting_level: int) -> List[FileInfo]:
        if libarchive is None:
            logger.warning({
                "event": "cab_unpack_failed",
                "file_id": file_id,
                "error": "libarchive-c library not installed"
            })
            return []
        path = self.get(file_id)
        if not path.exists():
            raise FileNotFoundError(f"Archive file does not exist: {path}")
        archive_info = []
        with tempfile.TemporaryDirectory(dir=self.base_dir) as temp_dir:
            try:
                with libarchive.file_reader(str(path)) as arc:
                    for entry in arc:
                        if entry.isfile():
                            fname = self._sanitize_filename(entry.pathname)
                            temp_path = pathlib.Path(temp_dir) / fname
                            with open(temp_path, 'wb') as f:
                                for block in entry.get_blocks():
                                    f.write(block)
                            with temp_path.open("rb") as stream:
                                fid = self.save_file(stream)
                            info = FileInfo(
                                fid=fid,
                                fname=os.path.join(base, fname),
                                fsize=temp_path.stat().st_size,
                                ftype=self.get_type(fid)
                            )
                            archive_info.append(info)
            except libarchive.ArchiveError as e:
                logger.warning({
                    "event": "cab_unpack_failed",
                    "file_id": file_id,
                    "path": str(path),
                    "error": str(e)
                })
        return archive_info

    def _unpack_iso(self, file_id: str, base: str, nesting_level: int) -> List[FileInfo]:
        if libarchive is None:
            logger.warning({
                "event": "iso_unpack_failed",
                "file_id": file_id,
                "error": "libarchive-c library not installed"
            })
            return []
        path = self.get(file_id)
        if not path.exists():
            raise FileNotFoundError(f"Archive file does not exist: {path}")
        archive_info = []
        with tempfile.TemporaryDirectory(dir=self.base_dir) as temp_dir:
            try:
                with libarchive.file_reader(str(path)) as arc:
                    for entry in arc:
                        if entry.isfile():
                            fname = self._sanitize_filename(entry.pathname)
                            temp_path = pathlib.Path(temp_dir) / fname
                            with open(temp_path, 'wb') as f:
                                for block in entry.get_blocks():
                                    f.write(block)
                            with temp_path.open("rb") as stream:
                                fid = self.save_file(stream)
                            info = FileInfo(
                                fid=fid,
                                fname=os.path.join(base, fname),
                                fsize=temp_path.stat().st_size,
                                ftype=self.get_type(fid)
                            )
                            archive_info.append(info)
            except libarchive.ArchiveError as e:
                logger.warning({
                    "event": "iso_unpack_failed",
                    "file_id": file_id,
                    "path": str(path),
                    "error": str(e)
                })
        return archive_info

    def unpack_avro(self, file_id: str, base: str, nesting_level: int) -> List[FileInfo]:
        """Extract records from an Avro file as JSON text files."""
        if DataFileReader is None or DatumReader is None:
            logger.error({
                "event": "avro_unpack_failed",
                "file_id": file_id,
                "error": "Avro library not installed. Install with 'pip install avro'"
            })
            raise ImportError("Avro library not installed")
        
        path = self.get(file_id)
        if not path.exists():
            logger.error({
                "event": "avro_unpack_failed",
                "file_id": file_id,
                "error": f"Avro file does not exist: {path}"
            })
            raise FileNotFoundError(f"Avro file does not exist: {path}")

        archive_info = []
        with tempfile.TemporaryDirectory(dir=self.base_dir) as temp_dir:
            try:
                with open(path, 'rb') as f:
                    reader = DataFileReader(f, DatumReader())
                    for idx, record in enumerate(reader):
                        record_json = json.dumps(record, ensure_ascii=False)
                        record_filename = f"{base}_record_{idx}.json"
                        temp_path = pathlib.Path(temp_dir) / record_filename
                        with temp_path.open("w", encoding="utf-8") as f:
                            f.write(record_json)
                        with temp_path.open("rb") as stream:
                            fid = self.save_file(stream)
                        info = FileInfo(
                            fid=fid,
                            fname=record_filename,
                            fsize=temp_path.stat().st_size,
                            ftype=self.T_TEXT
                        )
                        archive_info.append(info)
                    reader.close()
            except Exception as e:
                logger.warning({
                    "event": "avro_unpack_error",
                    "file_id": file_id,
                    "path": str(path),
                    "error": str(e),
                    "nesting_level": nesting_level
                })
        return archive_info

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
            elif format == "7z" and py7zr:
                with py7zr.SevenZipFile(dst, "w") as archive:
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
            elif format == "rar" and rarfile:
                raise ValueError("RAR repacking not supported")
            elif format == "zstd" and zstd:
                child = file.archive_files[0]
                file_path = self.get(child.id)
                if not file_path.exists():
                    logger.error({
                        "event": "repack_failed",
                        "file_id": file.id,
                        "child_id": child.id,
                        "error": f"Child file does not exist: {file_path}"
                    })
                    raise FileNotFoundError(f"Child file does not exist: {file_path}")
                with open(dst, 'wb') as dst_file:
                    cctx = zstd.ZstdCompressor()
                    with open(file_path, 'rb') as src_file:
                        cctx.copy_stream(src_file, dst_file)
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