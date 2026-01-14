class FolderTreeError(Exception):
    """Base exception for all folder tree errors."""
    pass

class ConfigError(FolderTreeError):
    """Raised when the configuration (YAML/JSON/Dict) is invalid."""
    pass

class ValidationError(FolderTreeError):
    """Raised when the folder structure validation fails."""
    pass
