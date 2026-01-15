# Nexatest Folder Tree Manager

A robust Python utility module for defining, creating, and managing standardized folder structures across applications. It ensures consistency, scalability, and ease of maintenance by replacing ad-hoc directory creation with a centralized, declarative approach.

## 📦 Features

- **Recursive Folder Creation**: Automatically creates complex nested directory structures.
- **Multi-Storage Support**: Abstract storage layer using **Adapters** (Local, AWS S3, GCP GCS).
- **Folder Migration**: Easily move/migrate folders and files between locations.
- **File Creation**: Supports creating empty files or files with content (e.g., `.gitkeep`, `README.md`).
- **Idempotency**: Safe to run multiple times; checks existence before creation to prevent errors.
- **Configuration Support**: Load folder structures from **PYTHON DICT**, **JSON**, or **YAML** files.
- **Environment Awareness**: Supports environment variable expansion (e.g., `$HOME/data`) in paths.
- **Safety First**: Includes `dry_run` mode to preview changes without writing to disk.
- **Visualization**: `generate_tree_summary()` function to print a tree-like view of the structure.
- **Developer Tools**: Includes utilities for checking existence (`validate_folder_tree`) and cleanup (`cleanup_folder_tree`).

## 🚀 Installation

Ensure you have Python installed. The module is located in `app/utils/folder_tree`.

Required dependencies (optional, for YAML support):

```bash
pip install pyyaml
```

## 🛠️ Usage

### Quick Start (Local)

```python
from app.utils.folder_tree import FolderTreeManager

# 1. Initialize the manager (defaults to Local Storage)
manager = FolderTreeManager()

# 2. Define your structure
structure = {
    "uploads": {
        "raw": {},
        "processed": {
            "images": {},
            "reports": {}
        }
    },
    "README.txt": "This folder structure was generated automatically."
}

# 3. Create it!
base_path = "./project_data"
paths = manager.create_folder_tree(base_path, structure)

# 4. Use the paths
print(f"Uploads folder: {paths['uploads']['raw']}")
```

### Multi-Storage Support (Adapters)

You can switch the back-end storage by providing a different adapter.

```python
from app.utils.folder_tree import FolderTreeManager
from app.utils.folder_tree.adapters import S3StorageAdapter

# Use S3 Storage
s3_adapter = S3StorageAdapter(bucket_name="my-bucket")
manager = FolderTreeManager(adapter=s3_adapter)

# Same creation code works on S3!
manager.create_folder_tree("my-prefix", structure)
```

### Folder Migration (Move)

Move files or folders effortlessly:

```python
manager.migrate(src="project_data/uploads", dst="archive/uploads_v1")
```

## 🧩 API Reference

| Component / Function | Description |
| :--- | :--- |
| `FolderTreeManager(adapter=...)` | Central class to manage operations on a specific storage. |
| `create_folder_tree(...)` | Recursively creates folders/files. |
| `migrate(src, dst, ...)` | Moves a folder or file to a new location. |
| `validate_folder_tree(...)` | Checks if the defined structure exists on disk. |
| `get_flat_path_map(...)` | Returns a flattened dict (e.g., `uploads_raw: /path/to/raw`) for lookup. |
| `generate_tree_summary(...)` | Returns a string visualization of the folder tree. |
| `cleanup_folder_tree(...)` | Recursively deletes the defined folders (Use with caution!). |

## 🧪 Testing & Quality

Run the comprehensive test suite to verify functionality and code coverage:

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage report
python -m pytest --cov=app/utils/folder_tree tests/ --cov-report=term-missing
```

The module maintains **>95% code coverage** across all core storage and management logic.
