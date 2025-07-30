# syft-objects utils - Utility functions for scanning and loading objects

from pathlib import Path
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .models import SyftObject


def scan_for_syft_objects(directory: str | Path, recursive: bool = True) -> List[Path]:
    """
    Scan a directory for .syftobject.yaml files
    
    Args:
        directory: Directory to scan
        recursive: Whether to scan subdirectories recursively
    
    Returns:
        List of paths to .syftobject.yaml files
    """
    directory = Path(directory)
    
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    if recursive:
        return list(directory.rglob("*.syftobject.yaml"))
    else:
        return list(directory.glob("*.syftobject.yaml"))


def load_syft_objects_from_directory(directory: str | Path, recursive: bool = True) -> List['SyftObject']:
    """
    Load all syft objects from a directory
    
    Args:
        directory: Directory to scan
        recursive: Whether to scan subdirectories recursively
    
    Returns:
        List of loaded SyftObject instances
    """
    from .models import SyftObject
    
    syft_files = scan_for_syft_objects(directory, recursive)
    objects = []
    
    for file_path in syft_files:
        try:
            obj = SyftObject.load_yaml(file_path)
            objects.append(obj)
        except Exception as e:
            print(f"Warning: Failed to load {file_path}: {e}")
    
    return objects 