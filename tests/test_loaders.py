import pytest
import json
import yaml
from pathlib import Path
from app.utils.folder_tree.loaders import load_tree_from_json, load_tree_from_yaml
from app.utils.folder_tree.exceptions import ConfigError

@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path

def test_load_json_valid(temp_dir):
    data = {"a": {"b": {}}}
    json_file = temp_dir / "test.json"
    json_file.write_text(json.dumps(data))
    
    loaded = load_tree_from_json(json_file)
    assert loaded == data

def test_load_json_invalid(temp_dir):
    json_file = temp_dir / "invalid.json"
    json_file.write_text("{ invalid json }")
    
    with pytest.raises(ConfigError, match="Invalid JSON"):
        load_tree_from_json(json_file)

def test_load_json_not_found():
    with pytest.raises(ConfigError, match="Config file not found"):
        load_tree_from_json("non_existent.json")

def test_load_yaml_valid(temp_dir):
    data = {"parent": {"child": {"_perms": 0o755}}}
    yaml_file = temp_dir / "test.yaml"
    yaml_file.write_text(yaml.dump(data))
    
    loaded = load_tree_from_yaml(yaml_file)
    assert loaded == data

def test_load_yaml_invalid(temp_dir):
    yaml_file = temp_dir / "invalid.yaml"
    yaml_file.write_text("key: : invalid")
    
    with pytest.raises(ConfigError, match="Invalid YAML"):
        load_tree_from_yaml(yaml_file)

def test_load_yaml_not_found():
    with pytest.raises(ConfigError, match="Config file not found"):
        load_tree_from_yaml("non_existent.yaml")
