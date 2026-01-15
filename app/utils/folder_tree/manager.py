import logging
import os
from pathlib import Path
from typing import Dict, Union, Any, Optional

from .exceptions import FolderTreeError, ValidationError, MigrationError
from .adapters import BaseStorageAdapter, LocalFileSystemAdapter

logger = logging.getLogger(__name__)

# Type alias for the tree structure
TreeStructure = Dict[str, Union[Dict, Any]]

def _resolve_path(path: Union[str, Path]) -> Path:
    """Helper to resolve paths with env vars and user expansion (Local only)."""
    s = str(path)
    s = os.path.expandvars(s)
    s = os.path.expanduser(s)
    return Path(s).resolve()

class FolderTreeManager:
    """
    Manager class to handle folder tree operations using various storage adapters.
    """
    def __init__(self, adapter: Optional[BaseStorageAdapter] = None):
        self.adapter = adapter or LocalFileSystemAdapter()

    def create_folder_tree(
        self,
        base_path: Union[str, Path],
        structure: TreeStructure,
        overwrite: bool = False,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Recursively creates a folder tree starting from base_path.
        """
        # If using local adapter, resolve the path
        if isinstance(self.adapter, LocalFileSystemAdapter):
            base = _resolve_path(base_path)
        else:
            base = Path(base_path)

        if not dry_run:
            try:
                self.adapter.mkdir(base, parents=True, exist_ok=True)
            except Exception as e:
                raise FolderTreeError(f"Failed to create base directory {base}: {e}")

        result_paths = {}

        for key, value in structure.items():
            if key.startswith("_"):
                continue

            current_path = base / key
            is_folder = isinstance(value, dict)

            if dry_run:
                logger.info(f"[DRY-RUN] Would create: {current_path}")
            else:
                try:
                    if is_folder:
                        self.adapter.mkdir(current_path, parents=True, exist_ok=True)
                        logger.debug(f"Created/Verified Folder: {current_path}")
                        
                        if "_perms" in value and isinstance(value["_perms"], int):
                            self.adapter.chmod(current_path, value["_perms"])
                    else:
                        # Ensure parent exists
                        self.adapter.mkdir(current_path.parent, parents=True, exist_ok=True)
                        
                        if not self.adapter.exists(current_path) or overwrite:
                            content = value if isinstance(value, str) and value not in ("file", "") else ""
                            self.adapter.write_file(current_path, content, overwrite=overwrite)
                            logger.debug(f"Created/Updated File: {current_path}")

                except Exception as e:
                    logger.error(f"Error creating {current_path}: {e}")
                    raise FolderTreeError(f"Failed to create {current_path}: {e}")

            if is_folder:
                sub_results = self.create_folder_tree(current_path, value, overwrite, dry_run)
                result_paths[key] = sub_results
            else:
                result_paths[key] = current_path

        return result_paths

    def validate_folder_tree(self, base_path: Union[str, Path], structure: TreeStructure) -> bool:
        """
        Validates that the folder structure exists.
        """
        base = _resolve_path(base_path) if isinstance(self.adapter, LocalFileSystemAdapter) else Path(base_path)
        
        if not self.adapter.exists(base):
             raise FolderTreeError(f"Base path does not exist: {base}")

        missing = []

        def _check(current_base: Path, sub_struct: Dict):
            for key, value in sub_struct.items():
                if key.startswith("_"):
                    continue
                p = current_base / key
                if not self.adapter.exists(p):
                    missing.append(str(p))
                if isinstance(value, dict):
                    _check(p, value)

        _check(base, structure)
        if missing:
            raise ValidationError(f"Missing {len(missing)} folders: {', '.join(missing[:5])}...")
        return True

    def cleanup_folder_tree(self
, base_path: Union[str, Path], structure: TreeStructure, confirm: bool = False):
        """
        Recursively deletes folders defined in the structure.
        """
        if not confirm:
            logger.warning("cleanup_folder_tree called without confirm=True. Returning.")
            return

        base = _resolve_path(base_path) if isinstance(self.adapter, LocalFileSystemAdapter) else Path(base_path)
        paths_to_delete = []

        def _collect(current_base: Path, sub_struct: Dict):
            for key, value in sub_struct.items():
                if key.startswith("_"):
                    continue
                p = current_base / key
                paths_to_delete.append(p)
                if isinstance(value, dict):
                    _collect(p, value)

        _collect(base, structure)
        paths_to_delete.sort(key=lambda p: len(str(p)), reverse=True)

        for p in paths_to_delete:
            if self.adapter.exists(p):
                try:
                    self.adapter.remove(p, recursive=False)
                    logger.info(f"Deleted: {p}")
                except Exception as e:
                    logger.warning(f"Could not delete {p}: {e}")

    def migrate(self, src: Union[str, Path], dst: Union[str, Path], dry_run: bool = False):
        """
        Moves a folder or file to a new location.
        """
        src_path = _resolve_path(src) if isinstance(self.adapter, LocalFileSystemAdapter) else Path(src)
        dst_path = _resolve_path(dst) if isinstance(self.adapter, LocalFileSystemAdapter) else Path(dst)

        if dry_run:
            logger.info(f"[DRY-RUN] Would move {src_path} to {dst_path}")
            return

        if not self.adapter.exists(src_path):
            raise MigrationError(f"Source path does not exist: {src_path}")

        try:
            # Ensure destination parent exists
            self.adapter.mkdir(dst_path.parent, parents=True, exist_ok=True)
            self.adapter.move(src_path, dst_path)
            logger.info(f"Migrated: {src_path} -> {dst_path}")
        except Exception as e:
            logger.error(f"Migration failed from {src_path} to {dst_path}: {e}")
            raise MigrationError(f"Failed to migrate: {e}")

# Functional interface for backward compatibility
def create_folder_tree(base_path, structure, overwrite=False, dry_run=False):
    return FolderTreeManager().create_folder_tree(base_path, structure, overwrite, dry_run)

def validate_folder_tree(base_path, structure):
    return FolderTreeManager().validate_folder_tree(base_path, structure)

def cleanup_folder_tree(base_path, structure, confirm=False):
    return FolderTreeManager().cleanup_folder_tree(base_path, structure, confirm)

def generate_tree_summary(structure: TreeStructure, indent: str = "", last: bool = True) -> str:
    """(Keep as is, since it's just a string generator)"""
    summary = ""
    items = {k: v for k, v in structure.items() if not k.startswith("_")}
    keys = list(items.keys())
    count = len(keys)
    for i, key in enumerate(keys):
        is_last_item = (i == count - 1)
        connector = "└── " if is_last_item else "├── "
        summary += f"{indent}{connector}{key}\n"
        value = items[key]
        if isinstance(value, dict):
            new_indent = indent + ("    " if is_last_item else "│   ")
            summary += generate_tree_summary(value, new_indent, is_last_item)
    return summary

def get_flat_path_map(base_path: Union[str, Path], structure: TreeStructure, separator: str = "_", parent_key: str = "") -> Dict[str, Path]:
    base = _resolve_path(base_path)
    flat_map = {}
    for key, value in structure.items():
        if key.startswith("_"): continue
        full_key = f"{parent_key}{separator}{key}" if parent_key else key
        current_path = base / key
        flat_map[full_key] = current_path
        if isinstance(value, dict):
            child_map = get_flat_path_map(current_path, value, separator, full_key)
            flat_map.update(child_map)
    return flat_map
