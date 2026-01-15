import pytest
import shutil
from pathlib import Path
from app.utils.folder_tree.manager import FolderTreeManager, create_folder_tree
from app.utils.folder_tree.exceptions import MigrationError

@pytest.fixture
def temp_dir(tmp_path):
    """Provides a temporary directory for testing."""
    return tmp_path

def test_migrate_folder(temp_dir):
    manager = FolderTreeManager()
    
    # 1. Create a source folder structure
    src = temp_dir / "source"
    structure = {
        "sub": {
            "file.txt": "hello"
        }
    }
    manager.create_folder_tree(src, structure)
    
    # 2. Migrate to destination
    dst = temp_dir / "destination"
    manager.migrate(src, dst)
    
    # 3. Verify
    assert not src.exists()
    assert dst.exists()
    assert (dst / "sub" / "file.txt").exists()
    assert (dst / "sub" / "file.txt").read_text() == "hello"

def test_migrate_single_file(temp_dir):
    manager = FolderTreeManager()
    
    src_file = temp_dir / "old.txt"
    src_file.write_text("data")
    
    dst_file = temp_dir / "new.txt"
    manager.migrate(src_file, dst_file)
    
    assert not src_file.exists()
    assert dst_file.exists()
    assert dst_file.read_text() == "data"

def test_migrate_nonexistent_src(temp_dir):
    manager = FolderTreeManager()
    with pytest.raises(MigrationError):
        manager.migrate(temp_dir / "nonexistent", temp_dir / "target")

def test_migrate_dry_run(temp_dir):
    manager = FolderTreeManager()
    src = temp_dir / "src_test"
    src.mkdir()
    dst = temp_dir / "dst_test"
    
    manager.migrate(src, dst, dry_run=True)
    
    assert src.exists()
    assert not dst.exists()
