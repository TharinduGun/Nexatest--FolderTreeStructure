import pytest
import shutil
import os
from pathlib import Path
from app.utils.folder_tree.adapters import LocalFileSystemAdapter

@pytest.fixture
def adapter():
    return LocalFileSystemAdapter()

@pytest.fixture
def temp_path(tmp_path):
    return tmp_path

def test_local_mkdir(adapter, temp_path):
    new_dir = temp_path / "new_dir"
    adapter.mkdir(new_dir)
    assert new_dir.is_dir()

def test_local_mkdir_parents(adapter, temp_path):
    nested_dir = temp_path / "parent" / "child"
    adapter.mkdir(nested_dir, parents=True)
    assert nested_dir.is_dir()

def test_local_exists(adapter, temp_path):
    test_file = temp_path / "exists.txt"
    test_file.write_text("hello")
    assert adapter.exists(test_file)
    assert not adapter.exists(temp_path / "not_exists.txt")

def test_local_is_file_is_dir(adapter, temp_path):
    test_file = temp_path / "file.txt"
    test_file.write_text("hello")
    test_dir = temp_path / "subdir"
    test_dir.mkdir()
    
    assert adapter.is_file(test_file)
    assert not adapter.is_file(test_dir)
    assert adapter.is_dir(test_dir)
    assert not adapter.is_dir(test_file)

def test_local_write_file(adapter, temp_path):
    test_file = temp_path / "write.txt"
    adapter.write_file(test_file, "content")
    assert test_file.read_text() == "content"
    
    # Test overwrite
    adapter.write_file(test_file, "new content", overwrite=True)
    assert test_file.read_text() == "new content"
    
    # Test no overwrite
    adapter.write_file(test_file, "should not see this", overwrite=False)
    assert test_file.read_text() == "new content"

def test_local_remove_file(adapter, temp_path):
    test_file = temp_path / "delete.txt"
    test_file.write_text("delete me")
    adapter.remove(test_file)
    assert not test_file.exists()

def test_local_remove_dir(adapter, temp_path):
    test_dir = temp_path / "delete_dir"
    test_dir.mkdir()
    (test_dir / "file.txt").write_text("inside")
    
    # Non-recursive remove should fail if not empty (standard behavior)
    with pytest.raises(OSError):
        adapter.remove(test_dir, recursive=False)
        
    adapter.remove(test_dir, recursive=True)
    assert not test_dir.exists()

def test_local_move(adapter, temp_path):
    src = temp_path / "move_src"
    src.mkdir()
    (src / "file.txt").write_text("data")
    dst = temp_path / "move_dst"
    
    adapter.move(src, dst)
    assert not src.exists()
    assert dst.exists()
    assert (dst / "file.txt").read_text() == "data"

@pytest.mark.skipif(os.name == 'nt', reason="chmod works differently on Windows")
def test_local_chmod(adapter, temp_path):
    test_dir = temp_path / "perm_dir"
    test_dir.mkdir()
    adapter.chmod(test_dir, 0o700)
    assert (test_dir.stat().st_mode & 0o777) == 0o700

def test_stubs():
    from app.utils.folder_tree.adapters import S3StorageAdapter, GCSStorageAdapter
    s3 = S3StorageAdapter("bucket")
    gcs = GCSStorageAdapter("bucket")
    
    # Just call methods to cover lines since they are stubs
    adapters = [s3, gcs]
    for a in adapters:
        a.mkdir("path")
        assert a.exists("path") is False
        assert a.is_file("path") is False
        assert a.is_dir("path") is False
        a.write_file("path", "content")
        a.remove("path")
        a.move("src", "dst")
        a.chmod("path", 0o777)
