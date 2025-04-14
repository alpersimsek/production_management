from dataclasses import dataclass
import pathlib
import gzip
import tempfile
import magic
import zipfile
import tarfile
import shutil
import os
from database.models import MimeType
from typing import List, Iterator, Optional
from database.models import File


@dataclass
class FileInfo:
    fid: str
    fname: Optional[str] = None
    fsize: Optional[int] = None
    ftype: Optional[str] = None


class BaseStorage:
    def __init__(self, base_dir: str):
        self.base_dir = pathlib.Path(base_dir)
        if not self.base_dir.exists():
            self.base_dir.mkdir(parents=True)


class FileStorage(BaseStorage):

    T_TEXT = "text"
    T_PCAP = "pcap"
    T_ZIP = "zip"  # .zip
    T_TAR = "tar"  # .tar|.tar.gz
    T_GZIP = "gzip"  # .gz
    T_UNKNOWN = "unknown"

    FILE_TYPES = [T_TEXT, T_PCAP]
    ARCHIVE_TYPES = [T_ZIP, T_TAR, T_GZIP]

    def save_file(self, file) -> str:
        dst = tempfile.NamedTemporaryFile(dir=self.base_dir, delete=False)

        try:
            with dst, file as src:
                shutil.copyfileobj(src, dst)
        except Exception:
            pathlib.Path(dst.name).unlink(missing_ok=True)
            raise

        return pathlib.Path(dst.name).name[3:]

    def get(self, file_id) -> pathlib.Path:
        path = self.base_dir.joinpath(f"tmp{file_id}")
        return path

    def get_size(self, file_id: str) -> int:
        file = self.get(file_id)
        return file.stat().st_size

    def get_type(self, file_id: str) -> str:
        """Get file type."""
        path = self.get(file_id)
        mime = magic.from_file(str(path), mime=True)
        if mime == MimeType.TEXT.value:
            # Plain text
            return self.T_TEXT
        if mime == "application/vnd.tcpdump.pcap":
            # PCAP file
            return self.T_PCAP
        if mime == "application/zip":
            # Zip archive
            return self.T_ZIP
        if mime == "application/x-tar":
            # Uncompressed tar
            return self.T_TAR
        if mime == "application/gzip":
            with gzip.open(path) as f:
                sub_mime = magic.from_buffer(f.read(2048), mime=True)
            if sub_mime == "text/plain":
                # Compressed data
                return self.T_GZIP
            if sub_mime == "application/x-tar":
                # Compressed tar
                return self.T_TAR
        # Unsupported type
        return mime

    def _unpack_zip(self, file_id: str, base: str) -> List[FileInfo]:
        if base.lower().endswith(".zip"):
            base = base[:-4]
        path = self.get(file_id)
        archive_info = []
        with zipfile.ZipFile(path) as arc:
            for z_info in arc.infolist():
                if z_info.is_dir():
                    continue
                with arc.open(z_info) as stream:
                    fid = self.save_file(stream)
                filename = os.path.join(base, z_info.filename)
                info = FileInfo(fid=fid, fname=filename, fsize=z_info.file_size)
                archive_info.append(info)
        return archive_info

    def _unpack_tar(self, file_id: str, base: str) -> List[FileInfo]:
        if base.lower().endswith(".tar"):
            base = base[:-4]
        elif base.lower().endswith(".tar.gz"):
            base = base[:-7]

        path = self.get(file_id)
        archive_info = []

        with tarfile.open(path) as arc:
            while True:
                member = arc.next()
                if member is None:
                    break
                if member.isdir():
                    continue
                stream = arc.extractfile(member)
                fid = self.save_file(stream)
                filename = os.path.join(base, member.name)
                info = FileInfo(fid=fid, fname=filename, fsize=member.size)
                archive_info.append(info)
        return archive_info

    def _unpack_gzip(self, file_id: str, base: str) -> List[FileInfo]:
        path = self.get(file_id)
        with gzip.open(path) as stream:
            fid = self.save_file(stream)
        filename = base
        if filename.lower().endswith(".gz"):
            filename = filename[:-3]
        info = FileInfo(fid=fid, fname=filename, fsize=self.get_size(fid))
        return [info]

    def _unpack_file(self, file_id, ftype, base) -> List[FileInfo]:
        """Unpack archive."""
        if ftype not in self.ARCHIVE_TYPES:
            raise ValueError("Wrong file type")
        method = getattr(self, f"_unpack_{ftype}")
        archive_info = method(file_id, base)
        # self.delete(file_id)
        return archive_info

    def unpack(self, file_id, filename) -> Iterator[FileInfo]:
        file_size = self.get_size(file_id)
        files = [FileInfo(file_id, filename, file_size)]
        try:
            while files:
                f_info = files.pop(0)
                f_type = self.get_type(f_info.fid)
                if f_type not in self.ARCHIVE_TYPES:
                    f_info.ftype = f_type
                    yield f_info
                else:
                    new_files = self._unpack_file(f_info.fid, f_type, base=f_info.fname)
                    files.extend(new_files)
        except GeneratorExit:
            print(f"deleting unprocessed files: {files}")
            for f_info in files:
                self.delete(f_info.fid)

    def repack(self, file: File):
        if not file.archive_files:
            raise ValueError("No extracted files found for the archive.")

        # Determine output format based on original filename
        if file.filename.endswith(".zip"):
            format = "zip"
            base = file.filename[:-4]
        elif file.filename.endswith(".tar.gz") or file.filename.endswith(".tgz"):
            format = "tar.gz"
            base = file.filename[:-7]
        elif file.filename.endswith(".tgz"):
            format = "tgz"
            base = file.filename[:-4]
        elif file.filename.endswith(".gz"):
            format = "gz"
            base = file.filename[:-3]
        else:
            format = None

        # format = "zip"

        src = self.get(file.id)
        dst = src.parent.joinpath(f"{src.name}.new")

        # Simple approach: use the exact paths as stored in the database
        # if format == "zip":
        with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as archive:
            for child in file.archive_files:
                file_path = self.get(child.id)
                # Use the path exactly as stored in the database
                archive.write(file_path, arcname=child.filename)
        # elif format in ("tar", "tar.gz"):
        #     mode = "w:gz" if format == "tar.gz" else "w"
        #     with tarfile.open(dst, mode) as archive:
        #         for child in file.archive_files:
        #             file_path = self.get(child.id)
        #             archive.add(file_path, arcname=child.filename)
        # else:
        #     raise ValueError("Unsupported archive format")

        # Replace the original file with the new one
        dst.rename(src)
        file.filename = ".".join([base, "zip"])
        # Update the file size in the database to match the new file
        if file.file_size != src.stat().st_size:
            file.file_size = src.stat().st_size

    def delete(self, file_id):
        file_path = self.get(file_id)
        try:
            file_path.unlink()
        except FileNotFoundError:
            print("File %s already deleted", file_path)
