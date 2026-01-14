# Nexatest Folder Tree Manager

A robust Python utility module for defining, creating, and managing standardized folder structures across applications. It ensures consistency, scalability, and ease of maintenance by replacing ad-hoc directory creation with a centralized, declarative approach.

## 📦 Features

- **Recursive Folder Creation**: Automatically creates complex nested directory structures.
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

### Quick Start

```python
from app.utils.folder_tree import create_folder_tree, generate_tree_summary

# 1. Define your structure
structure = {
    "uploads": {
        "raw": {},
        "processed": {
            "images": {},
            "reports": {}
        }
    },
    "logs": {},
    "README.txt": "This folder structure was generated automatically."
}

# 2. Preview what will be created
print(generate_tree_summary(structure))
# Output:
# ├── uploads
# │   ├── raw
# │   └── processed
# ├── logs
# └── README.txt

# 3. Create it!
base_path = "./project_data"
paths = create_folder_tree(base_path, structure)

# 4. Use the paths
print(f"Uploads folder: {paths['uploads']['raw']}")
```

### Loading from Configuration

**structure.yaml**

```yaml
data:
  raw: {}
  processed:
    _perms: 0o755 # Optional permissions
```

**Python Code**

```python
from app.utils.folder_tree import load_tree_from_yaml, create_folder_tree

config = load_tree_from_yaml("structure.yaml")
create_folder_tree("./", config)
```

## 🧩 API Reference

| Function | Description |
| :--- | :--- |
| `create_folder_tree(base, structure, ...)` | Main function to create folders/files. Returns a dict of Paths. |
| `validate_folder_tree(base, structure)` | Checks if the defined structure exists on disk. |
| `get_flat_path_map(base, structure)` | Returns a flattened dict (e.g., `uploads_raw: /path/to/raw`) for easy lookup. |
| `generate_tree_summary(structure)` | Returns a string visualization of the folder tree. |
| `cleanup_folder_tree(base, structure)` | recursively deletes the defined folders (Use with caution!). |

## 🧪 Testing

Run the included test suite to verify functionality:

```bash
python -m pytest tests/test_folder_tree.py
```
