import os
import shutil
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Union, List, Optional
import logging

logger = logging.getLogger(__name__)

class BaseStorageAdapter(ABC):
    """Abstract base class for all storage operations."""
    
    @abstractmethod
    def mkdir(self, path: Union[str, Path], parents: bool = True, exist_ok: bool = True):
        """Create a directory."""
        pass

    @abstractmethod
    def exists(self, path: Union[str, Path]) -> bool:
        """Check if a path exists."""
        pass

    @abstractmethod
    def is_file(self, path: Union[str, Path]) -> bool:
        """Check if path is a file."""
        pass

    @abstractmethod
    def is_dir(self, path: Union[str, Path]) -> bool:
        """Check if path is a directory."""
        pass

    @abstractmethod
    def write_file(self, path: Union[str, Path], content: str, overwrite: bool = False):
        """Write content to a file."""
        pass

    @abstractmethod
    def remove(self, path: Union[str, Path], recursive: bool = False):
        """Remove a file or directory."""
        pass

    @abstractmethod
    def move(self, src: Union[str, Path], dst: Union[str, Path]):
        """Move/Rename a file or directory."""
        pass

    @abstractmethod
    def chmod(self, path: Union[str, Path], mode: int):
        """Change permissions."""
        pass


class LocalFileSystemAdapter(BaseStorageAdapter):
    """Implementation for local filesystem using pathlib and os."""

    def mkdir(self, path: Union[str, Path], parents: bool = True, exist_ok: bool = True):
        Path(path).mkdir(parents=parents, exist_ok=exist_ok)

    def exists(self, path: Union[str, Path]) -> bool:
        return Path(path).exists()

    def is_file(self, path: Union[str, Path]) -> bool:
        return Path(path).is_file()

    def is_dir(self, path: Union[str, Path]) -> bool:
        return Path(path).is_dir()

    def write_file(self, path: Union[str, Path], content: str, overwrite: bool = False):
        p = Path(path)
        if not p.exists() or overwrite:
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write(content)

    def remove(self, path: Union[str, Path], recursive: bool = False):
        p = Path(path)
        if p.is_file():
            p.unlink()
        elif p.is_dir():
            if recursive:
                shutil.rmtree(p)
            else:
                p.rmdir()

    def move(self, src: Union[str, Path], dst: Union[str, Path]):
        shutil.move(str(src), str(dst))

    def chmod(self, path: Union[str, Path], mode: int):
        os.chmod(path, mode)


class S3StorageAdapter(BaseStorageAdapter):
    """Stub for AWS S3 Storage."""
    def __init__(self, bucket_name: str, prefix: str = ""):
        self.bucket_name = bucket_name
        self.prefix = prefix
        logger.warning("S3StorageAdapter is currently a STUB.")

    def mkdir(self, path: Union[str, Path], parents: bool = True, exist_ok: bool = True):
        pass # S3 doesn't have real folders

    def exists(self, path: Union[str, Path]) -> bool:
        return False

    def is_file(self, path: Union[str, Path]) -> bool:
        return False

    def is_dir(self, path: Union[str, Path]) -> bool:
        return False

    def write_file(self, path: Union[str, Path], content: str, overwrite: bool = False):
        pass

    def remove(self, path: Union[str, Path], recursive: bool = False):
        pass

    def move(self, src: Union[str, Path], dst: Union[str, Path]):
        pass

    def chmod(self, path: Union[str, Path], mode: int):
        pass


class GCSStorageAdapter(BaseStorageAdapter):
    """Stub for GCP Storage."""
    def __init__(self, bucket_name: str, prefix: str = ""):
        self.bucket_name = bucket_name
        self.prefix = prefix
        logger.warning("GCSStorageAdapter is currently a STUB.")

    def mkdir(self, path: Union[str, Path], parents: bool = True, exist_ok: bool = True):
        pass

    def exists(self, path: Union[str, Path]) -> bool:
        return False

    def is_file(self, path: Union[str, Path]) -> bool:
        return False

    def is_dir(self, path: Union[str, Path]) -> bool:
        return False

    def write_file(self, path: Union[str, Path], content: str, overwrite: bool = False):
        pass

    def remove(self, path: Union[str, Path], recursive: bool = False):
        pass

    def move(self, src: Union[str, Path], dst: Union[str, Path]):
        pass

    def chmod(self, path: Union[str, Path], mode: int):
        pass
