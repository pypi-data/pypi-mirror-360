"""
Security utilities for file system operations.
"""
from pathlib import Path
from typing import Union

# Global variable to store allowed base directory
_ALLOWED_BASE_DIR = None


def init_security(allowed_base_dir: Union[str, Path]) -> None:
    """Initialize security with allowed base directory."""
    global _ALLOWED_BASE_DIR
    _ALLOWED_BASE_DIR = Path(allowed_base_dir).resolve()


def get_allowed_base_dir() -> Path:
    """Get the current allowed base directory."""
    if _ALLOWED_BASE_DIR is None:
        raise ValueError("Security not initialized. Call init_security() first.")
    return _ALLOWED_BASE_DIR


def set_allowed_base_dir(allowed_base_dir: Union[str, Path]) -> Path:
    """Set a new allowed base directory."""
    global _ALLOWED_BASE_DIR
    old_dir = _ALLOWED_BASE_DIR
    _ALLOWED_BASE_DIR = Path(allowed_base_dir).resolve()
    return old_dir


def is_path_allowed(file_path: str) -> bool:
    """Check if the given path is within the allowed base directory."""
    try:
        resolved_path = Path(file_path).resolve()
        return resolved_path.is_relative_to(_ALLOWED_BASE_DIR)
    except Exception:
        return False


def get_safe_path(file_path: str) -> Path:
    """Get a safe path within the allowed directory."""
    if not is_path_allowed(file_path):
        raise ValueError(f"Access denied: Path '{file_path}' is outside allowed directory '{_ALLOWED_BASE_DIR}'")
    return Path(file_path).resolve()
