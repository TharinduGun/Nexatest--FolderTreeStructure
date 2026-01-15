import pytest
import logging
from unittest.mock import MagicMock
from pathlib import Path
from app.utils.folder_tree.manager import FolderTreeManager
from app.utils.folder_tree.exceptions import FolderTreeError, ValidationError, MigrationError

@pytest.fixture
def mock_adapter():
    return MagicMock()

@pytest.fixture
def manager(mock_adapter):
    return FolderTreeManager(adapter=mock_adapter)

def test_create_folder_tree_exception(manager, mock_adapter):
    mock_adapter.mkdir.side_effect = Exception("creation failed")
    with pytest.raises(FolderTreeError, match="Failed to create"):
        manager.create_folder_tree("/base", {"dir": {}})

def test_validate_folder_tree_base_exists_error(manager, mock_adapter):
    mock_adapter.exists.return_value = False
    with pytest.raises(FolderTreeError, match="Base path does not exist"):
        manager.validate_folder_tree("/base", {})

def test_cleanup_no_confirm(manager, caplog):
    with caplog.at_level(logging.WARNING):
        manager.cleanup_folder_tree("/base", {}, confirm=False)
    assert "called without confirm=True" in caplog.text

def test_migrate_source_not_found(manager, mock_adapter):
    mock_adapter.exists.return_value = False
    with pytest.raises(MigrationError, match="Source path does not exist"):
        manager.migrate("/src", "/dst")

def test_migrate_failure(manager, mock_adapter):
    mock_adapter.exists.return_value = True
    mock_adapter.move.side_effect = Exception("move failed")
    with pytest.raises(MigrationError, match="Failed to migrate"):
        manager.migrate("/src", "/dst")

def test_cleanup_with_underscore_keys(manager, mock_adapter):
    # Should skip keys starting with _
    structure = {"_perms": 0o777, "dir": {}}
    mock_adapter.exists.return_value = True
    manager.cleanup_folder_tree("/base", structure, confirm=True)
    # mkdir should NOT be called for _perms, but for dir it should be removed
    # Actually cleanup calls exists then remove. 
    # Check that remove was called for /base/dir but not /base/_perms
    # Need to check call arguments
    called_paths = [call.args[0] for call in mock_adapter.remove.call_args_list]
    assert any("dir" in str(p) for p in called_paths)
    assert not any("_perms" in str(p) for p in called_paths)

def test_cleanup_failure_logging(manager, mock_adapter, caplog):
    mock_adapter.exists.return_value = True
    mock_adapter.remove.side_effect = Exception("delete failed")
    with caplog.at_level(logging.WARNING):
        manager.cleanup_folder_tree("/base", {"dir": {}}, confirm=True)
    assert "Could not delete" in caplog.text
