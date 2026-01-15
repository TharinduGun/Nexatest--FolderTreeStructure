import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from app.utils.folder_tree.manager import FolderTreeManager
from app.utils.folder_tree.adapters import BaseStorageAdapter

@pytest.fixture
def mock_adapter():
    return MagicMock(spec=BaseStorageAdapter)

@pytest.fixture
def manager(mock_adapter):
    return FolderTreeManager(adapter=mock_adapter)

def test_create_folder_tree_logic(manager, mock_adapter):
    structure = {
        "dir1": {
            "file1.txt": "content1"
        },
        "file2.txt": "content2"
    }
    base_path = Path("/mock/base")
    mock_adapter.exists.return_value = False
    
    manager.create_folder_tree(base_path, structure)
    
    # Check if adapter methods were called correctly
    mock_adapter.mkdir.assert_any_call(base_path, parents=True, exist_ok=True)
    mock_adapter.mkdir.assert_any_call(base_path / "dir1", parents=True, exist_ok=True)
    mock_adapter.write_file.assert_any_call(base_path / "dir1" / "file1.txt", "content1", overwrite=False)
    mock_adapter.write_file.assert_any_call(base_path / "file2.txt", "content2", overwrite=False)

def test_validate_folder_tree_logic(manager, mock_adapter):
    structure = {"a": {"b": {}}}
    base_path = Path("/mock/base")
    
    mock_adapter.exists.side_effect = lambda p: p in [base_path, base_path / "a"]
    
    from app.utils.folder_tree.exceptions import ValidationError
    with pytest.raises(ValidationError, match="Missing 1 folders"):
        manager.validate_folder_tree(base_path, structure)

def test_migrate_logic(manager, mock_adapter):
    src = Path("/src")
    dst = Path("/dst")
    
    mock_adapter.exists.return_value = True
    
    manager.migrate(src, dst)
    
    mock_adapter.mkdir.assert_called_with(dst.parent, parents=True, exist_ok=True)
    mock_adapter.move.assert_called_with(src, dst)

def test_dry_run_logic(manager, mock_adapter):
    structure = {"dir": {}}
    base_path = Path("/mock/base")
    
    manager.create_folder_tree(base_path, structure, dry_run=True)
    
    # Should NOT call adapter methods that modify state
    mock_adapter.mkdir.assert_not_called()
    mock_adapter.write_file.assert_not_called()
