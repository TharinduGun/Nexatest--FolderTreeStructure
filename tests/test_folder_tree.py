import os
import json
import shutil
import tempfile
import pytest
from pathlib import Path
from app.utils.folder_tree import (
    create_folder_tree, 
    get_flat_path_map, 
    validate_folder_tree, 
    cleanup_folder_tree,
    load_tree_from_json,
    generate_tree_summary,
    FolderTreeError
)

# Sample structure
SAMPLE_TREE = {
    "uploads": {
        "raw": {},
        "processed": {
            "images": {},
            "text": {},
            "readme.txt": "file"
        }
    },
    "logs": {},
    "config.json": "{}"
}

@pytest.fixture
def temp_base():
    # Create a temp directory
    tmp = tempfile.mkdtemp()
    yield Path(tmp)
    # Cleanup after test
    shutil.rmtree(tmp, ignore_errors=True)

def test_create_folder_tree(temp_base):
    paths = create_folder_tree(temp_base, SAMPLE_TREE)
    
    # Check if directories exist
    assert (temp_base / "uploads").exists()
    assert (temp_base / "uploads" / "raw").exists()
    assert (temp_base / "uploads" / "processed" / "images").exists()
    assert (temp_base / "logs").exists()
    
    # Check if files exist
    assert (temp_base / "uploads" / "processed" / "readme.txt").is_file()
    assert (temp_base / "config.json").is_file()
    
    # Check return values
    # Folders return a dict of their children
    assert isinstance(paths["uploads"]["raw"], dict)
    # Files return a Path object
    assert isinstance(paths["uploads"]["processed"]["readme.txt"], Path)

def test_get_flat_path_map(temp_base):
    # We don't need to create folders to get the map, but base needs to exist for resolution
    flat = get_flat_path_map(temp_base, SAMPLE_TREE)
    
    assert "uploads_raw" in flat
    assert flat["uploads_raw"] == (temp_base / "uploads" / "raw").resolve()
    assert "logs" in flat

def test_validate_folder_tree(temp_base):
    # 1. Create tree
    create_folder_tree(temp_base, SAMPLE_TREE)
    
    # 2. Validate - should pass
    assert validate_folder_tree(temp_base, SAMPLE_TREE) is True
    
    # 3. Delete a folder
    (temp_base / "logs").rmdir()
    
    # 4. Validate - should fail
    from app.utils.folder_tree import ValidationError
    with pytest.raises(ValidationError):
        validate_folder_tree(temp_base, SAMPLE_TREE)

def test_dry_run(temp_base):
    # Dry run should NOT create folders
    create_folder_tree(temp_base, SAMPLE_TREE, dry_run=True)
    
    assert not (temp_base / "uploads").exists()

def test_cleanup_folder_tree(temp_base):
    create_folder_tree(temp_base, SAMPLE_TREE)
    assert (temp_base / "uploads").exists()
    
    cleanup_folder_tree(temp_base, SAMPLE_TREE, confirm=True)
    
    assert not (temp_base / "uploads").exists()
    # Note: cleanup currently only removes directories via rmdir, not files (unless empty dirs).
    # Since we added files, rmdir might fail if dir not empty of files we created. 
    # But files logic usually implies we should clean them too? 
    # The initial spec for cleanup said "Recursively delete folders". 
    # For robust cleanup we might need rmtree, but 'manager.py' uses rmdir.
    # We accept that limitation or improve it. Given 'tests' usually use temp dirs that get wiped,
    # the module's cleanup is for specific controlled removal. 

def test_env_expansion(temp_base):
    # Set env var
    os.environ["TEST_ROOT"] = str(temp_base)
    
    # Use env var in base path
    base_with_env = "$TEST_ROOT/env_test"
    
    create_folder_tree(base_with_env, {"foo": {}})
    
    expected = temp_base / "env_test" / "foo"
    assert expected.exists()

def test_generate_tree_summary():
    summary = generate_tree_summary(SAMPLE_TREE)
    print(summary)
    assert "uploads" in summary
    assert "├── raw" in summary or "└── raw" in summary
    assert "logs" in summary
