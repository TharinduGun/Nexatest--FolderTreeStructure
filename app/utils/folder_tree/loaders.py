import json
import logging
from pathlib import Path
from typing import Dict, Any

from .exceptions import ConfigError

logger = logging.getLogger(__name__)

def load_tree_from_json(file_path: str | Path) -> Dict[str, Any]:
    """
    Loads folder structure from a JSON file.
    """
    path = Path(file_path)
    if not path.exists():
        raise ConfigError(f"Config file not found: {path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in {path}: {e}")
    except Exception as e:
        raise ConfigError(f"Failed to load JSON {path}: {e}")


def load_tree_from_yaml(file_path: str | Path) -> Dict[str, Any]:
    """
    Loads folder structure from a YAML file.
    Requires PyYAML to be installed.
    """
    path = Path(file_path)
    if not path.exists():
        raise ConfigError(f"Config file not found: {path}")

    try:
        import yaml
    except ImportError:
        logger.error("PyYAML not installed. Cannot load YAML config.")
        raise ConfigError("PyYAML is required to load YAML files. Please pip install PyYAML.")

    try:
        with open(path, "r", encoding="utf-8") as f:
            # Safe load is recommended to avoid executing arbitrary code
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigError(f"Invalid YAML in {path}: {e}")
    except Exception as e:
        raise ConfigError(f"Failed to load YAML {path}: {e}")
