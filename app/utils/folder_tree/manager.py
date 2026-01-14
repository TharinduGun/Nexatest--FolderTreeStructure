import logging
import os
from pathlib import Path
from typing import Dict, Union, Any, Optional

from .exceptions import FolderTreeError

logger = logging.getLogger(__name__)

# Type alias for the tree structure
TreeStructure = Dict[str, Union[Dict, Any]]

def _resolve_path(path: Union[str, Path]) -> Path:
    """Helper to resolve paths with env vars and user expansion."""
    s = str(path)
    s = os.path.expandvars(s)
    s = os.path.expanduser(s)
    return Path(s).resolve()

def create_folder_tree(
    base_path: Union[str, Path],
    structure: TreeStructure,
    overwrite: bool = False,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    recursively creates a folder tree starting from base_path.

    Args:
        base_path: The root directory where folders will be created.
        structure: Nested dictionary representing the folder structure.
                   Special keys like '_perms' can be used for configuration.
        overwrite: If True, this would technically allow overwriting, but for folders
                   it mainly implies we don't error if it exists. (Handled by exist_ok=True)
        dry_run: If True, simulates creation without modifying the filesystem.

    Returns:
        A nested dictionary matching the input structure, but with values 
        replaced by pathlib.Path objects for the created directories.
    """
    base = _resolve_path(base_path)
    
    if not dry_run:
        try:
            base.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise FolderTreeError(f"Failed to create base directory {base}: {e}")

    result_paths = {}

    for key, value in structure.items():
        # Skip special configuration keys starting with underscore (e.g., _perms)
        if key.startswith("_"):
            continue

        current_path = base / key
        
        # Determine if this is a file or a folder
        # If value is a dict, it's a folder.
        # If value is NOT a dict (e.g., None, "file", or string content), it's a file.
        is_folder = isinstance(value, dict)

        if dry_run:
            logger.info(f"[DRY-RUN] Would create: {current_path}")
        else:
            try:
                if is_folder:
                    current_path.mkdir(parents=True, exist_ok=True)
                    logger.debug(f"Created/Verified Folder: {current_path}")
                    
                    # Basic permission support
                    if isinstance(value, dict) and "_perms" in value:
                        perms = value["_perms"]
                        if isinstance(perms, int):
                            os.chmod(current_path, perms)
                else:
                    # It's a file
                    # Ensure parent exists (should be handled by recursion loop, but safe to check)
                    current_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Create empty file or write content if string provided
                    if not current_path.exists() or overwrite:
                        content = value if isinstance(value, str) and value not in ("file", "") else ""
                        with open(current_path, "w", encoding="utf-8") as f:
                            f.write(content)
                        action = "Updated" if current_path.exists() else "Created"
                        logger.debug(f"{action} File: {current_path}")
                    
                    # If file exists, we do nothing (idempotent) unless we want to force content update
                    # For now, we respect existing files.

            except OSError as e:
                logger.error(f"Error creating {current_path}: {e}")
                raise FolderTreeError(f"Failed to create {current_path}: {e}")

        # Recurse if the value is a dictionary (sub-folders)
        if is_folder:
            sub_results = create_folder_tree(current_path, value, overwrite, dry_run)
            result_paths[key] = sub_results
        else:
            # It's a leaf node key (file), just store the path
            result_paths[key] = current_path

    return result_paths

def generate_tree_summary(structure: TreeStructure, indent: str = "", last: bool = True) -> str:
    """
    Generates a human-readable string representation of the tree structure.
    Similar to the unix 'tree' command.
    """
    summary = ""
    
    # Filter out configuration keys for display
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

def cleanup_folder_tree(
    base_path: Union[str, Path],
    structure: TreeStructure,
    confirm: bool = False
):
    """
    Recursively deletes folders defined in the structure. 
    EXPERIMENTAL: Use with caution. 
    
    Args:
        base_path: Root of the tree.
        structure: Tree structure to delete.
        confirm: Safety flag. Must be set to True to execute deletion.
    """
    if not confirm:
        logger.warning("cleanup_folder_tree called without confirm=True. Returning.")
        return

    base = _resolve_path(base_path)
    
    # We create a list of paths to verify/delete, then sort them by length descending
    # to delete children before parents (post-order).
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
    
    # Sort by path length descending so children come before parents
    paths_to_delete.sort(key=lambda p: len(str(p)), reverse=True)

    for p in paths_to_delete:
        if p.exists():
            try:
                if p.is_file():
                    p.unlink()
                    logger.debug(f"Deleted file: {p}")
                elif p.is_dir():
                    # rmdir only works if empty.
                    p.rmdir()
                    logger.info(f"Deleted folder: {p}")
            except OSError as e:
                logger.warning(f"Could not delete {p}: {e}")


def get_flat_path_map(
    base_path: Union[str, Path],
    structure: TreeStructure,
    separator: str = "_",
    parent_key: str = ""
) -> Dict[str, Path]:
    """
    Returns a flattened dictionary of paths for easy lookup.
    Example:
        {
            "uploads_raw": Path("/base/uploads/raw"),
            "processed_text": Path("/base/processed/text")
        }
    """
    base = _resolve_path(base_path)
    flat_map = {}

    for key, value in structure.items():
        if key.startswith("_"):
            continue

        full_key = f"{parent_key}{separator}{key}" if parent_key else key
        current_path = base / key

        # Add the current path
        flat_map[full_key] = current_path

        # Recurse if children exist
        if isinstance(value, dict):
            child_map = get_flat_path_map(current_path, value, separator, full_key)
            flat_map.update(child_map)

    return flat_map

def validate_folder_tree(
    base_path: Union[str, Path],
    structure: TreeStructure
) -> bool:
    """
    Validates that the folder structure exists on disk.
    
    Args:
        base_path: Root directory.
        structure: Nested dictionary of the tree.
        
    Returns:
        True if all folders exist.
        
    Raises:
        ValidationError: If any folder is missing.
    """
    base = _resolve_path(base_path)
    
    if not base.exists():
         raise FolderTreeError(f"Base path does not exist: {base}")

    missing = []

    def _check(current_base: Path, sub_struct: Dict):
        for key, value in sub_struct.items():
            if key.startswith("_"):
                continue
            
            p = current_base / key
            if not p.exists():
                missing.append(str(p))
            
            if isinstance(value, dict):
                _check(p, value)

    _check(base, structure)

    if missing:
        from .exceptions import ValidationError
        raise ValidationError(f"Missing {len(missing)} folders: {', '.join(missing[:5])}...")
    
    return True

