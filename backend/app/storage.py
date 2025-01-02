from dataclasses import dataclass
import pathlib
import gzip
import tempfile
# import magic
import filetype
import zipfile
import tarfile
import shutil
import os
from fastapi import UploadFile
from typing import List, Iterator


@dataclass
class FileInfo:
    fid: str
    fname: str = None
    fsize: int = None


class BaseStorage:
    def __init__(self, base_dir):
        self.base_dir = pathlib.Path(base_dir)
        if not self.base_dir.exists():
            self.base_dir.mkdir(parents=True)


class FileStorage(BaseStorage):

    T_PLAIN = "plain"
    T_ZIP = "zip"  # .zip
    T_TAR = "tar"  # .tar|.tar.gz
    T_GZIP = "gzip"  # .gz

    ARCHIVE_TYPES = {
        "application/zip": T_ZIP, 
        "application/x-tar": T_TAR, 
        "application/gzip": T_GZIP
    }

    ARCHIVE_HANDLERS = {
        "application/gzip": gzip.open,
    }

    def save_file(self, file: UploadFile) -> str:
        dst = tempfile.NamedTemporaryFile(dir=self.base_dir, delete=False)

        try:
            with dst, file.file as src:
                shutil.copyfileobj(src, dst)
        except Exception:
            pathlib.Path(dst.name).unlink(missing_ok=True)
            raise

        return pathlib.Path(dst.name).name[3:]

    def get(self, file_id) -> pathlib.Path:
        filename = os.path.join(self.base_dir, f"tmp{file_id}")
        return filename

    def get_size(self, file_id):
        filename = self.get(file_id)
        return filename.stat().st_size

    def get_type(self, file_id):
        """Get file type."""
        path = self.get(file_id)
        # mime = magic.from_file(str(path), mime=True)
        mime = filetype.guess_mime(path)
        if mime == "text/plain":
            # Plain text
            return self.T_PLAIN
        if mime == "application/zip":
            # Zip archive
            return self.T_ZIP
        if mime == "application/x-tar":
            # Uncompressed tar
            return self.T_TAR

        if mime in self.ARCHIVE_HANDLERS:
            with self.ARCHIVE_HANDLERS[mime](path) as f:
                # sub_mime = magic.from_buffer(f.read(2048), mime=True)
                sub_mime = filetype.guess_mime(f)
            if sub_mime == "text/plain":
                # Compressed data
                return self.ARCHIVE_TYPES[mime]
            if sub_mime == "application/x-tar":
                # Compressed tar
                return self.T_TAR
        # Fallback for unknown type
        return self.T_PLAIN

    def _unpack_zip(self, file_id, base):
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

    def _unpack_tar(self, file_id, base):
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

    def _unpack_gzip(self, file_id, base):
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
        self.delete(file_id)
        return archive_info

    def unpack(self, file_id, filename) -> Iterator[FileInfo]:
        file_size = self.get_size(file_id)
        files = [FileInfo(file_id, filename, file_size)]
        try:
            while files:
                f_info = files.pop(0)
                f_type = self.get_type(f_info.fid)
                if f_type not in self.ARCHIVE_TYPES:
                    yield f_info
                else:
                    new_files = self._unpack_file(
                        f_info.fid, f_type, base=f_info.fname
                    )
                    files.extend(new_files)
        except GeneratorExit:
            print(f"deleting unprocessed files: {files}")
            for f_info in files:
                self.delete(f_info.fid)

    def delete(self, file_id):
        filename = self.get(file_id)
        try:
            filename.unlink()
        except FileNotFoundError:
            print("File %s already deleted", filename)
