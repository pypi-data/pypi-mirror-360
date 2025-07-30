# syft-objects file_ops - File operations and URL generation utilities

import shutil
from pathlib import Path
from typing import Optional, Tuple

from .client import get_syftbox_client, SyftBoxClient, SyftBoxURL, SYFTBOX_AVAILABLE


def move_object_to_syftbox_location(local_path: Path, syft_url: str, syftbox_client: Optional[SyftBoxClient] = None) -> bool:
    """Move a file OR folder to the location specified by a syft:// URL"""
    if not SYFTBOX_AVAILABLE or not syftbox_client:
        return False
    
    try:
        syft_url_obj = SyftBoxURL(syft_url)
        target_path = syft_url_obj.to_local_path(datasites_path=syftbox_client.datasites)
        
        # Ensure target directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Handle folders differently
        if local_path.is_dir():
            if target_path.exists():
                shutil.rmtree(target_path)
            shutil.move(str(local_path), str(target_path))
        else:
            # Regular file move
            shutil.move(str(local_path), str(target_path))
        return True
    except Exception as e:
        print(f"Warning: Could not move object to SyftBox location: {e}")
        return False


def copy_object_to_syftbox_location(local_path: Path, syft_url: str, syftbox_client: Optional[SyftBoxClient] = None) -> bool:
    """Copy a file OR folder to the location specified by a syft:// URL"""
    if not SYFTBOX_AVAILABLE or not syftbox_client:
        return False
    
    try:
        syft_url_obj = SyftBoxURL(syft_url)
        target_path = syft_url_obj.to_local_path(datasites_path=syftbox_client.datasites)
        
        # Ensure target directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Handle folders differently
        if local_path.is_dir():
            if target_path.exists():
                shutil.rmtree(target_path)
            shutil.copytree(str(local_path), str(target_path))
        else:
            # Regular file copy
            shutil.copy2(str(local_path), str(target_path))
        return True
    except Exception as e:
        print(f"Warning: Could not copy object to SyftBox location: {e}")
        return False


def generate_syftbox_urls(email: str, filename: str, syftbox_client: Optional[SyftBoxClient] = None, mock_is_public: bool = True) -> Tuple[str, str]:
    """Generate proper syft:// URLs for private and mock files"""
    if syftbox_client:
        # Generate URLs that point to actual SyftBox structure
        private_url = f"syft://{email}/private/objects/{filename}"
        # Mock file location depends on permissions
        if mock_is_public:
            mock_url = f"syft://{email}/public/objects/{filename}"
        else:
            mock_url = f"syft://{email}/private/objects/{filename}"
    else:
        # Fallback to generic URLs
        private_url = f"syft://{email}/SyftBox/datasites/{email}/private/objects/{filename}"
        if mock_is_public:
            mock_url = f"syft://{email}/SyftBox/datasites/{email}/public/objects/{filename}"
        else:
            mock_url = f"syft://{email}/SyftBox/datasites/{email}/private/objects/{filename}"
    
    return private_url, mock_url


def generate_syftobject_url(email: str, filename: str, syftbox_client: Optional[SyftBoxClient] = None) -> str:
    """Generate proper syft:// URL for syftobject.yaml file"""
    if syftbox_client:
        # Generate URL that points to actual SyftBox structure
        return f"syft://{email}/public/objects/{filename}"
    else:
        # Fallback to generic URL
        return f"syft://{email}/SyftBox/datasites/{email}/public/objects/{filename}"


# Backward compatibility aliases
def move_file_to_syftbox_location(local_file: Path, syft_url: str, syftbox_client: Optional[SyftBoxClient] = None) -> bool:
    """Backward compatibility alias for move_object_to_syftbox_location"""
    return move_object_to_syftbox_location(local_file, syft_url, syftbox_client)


def copy_file_to_syftbox_location(local_file: Path, syft_url: str, syftbox_client: Optional[SyftBoxClient] = None) -> bool:
    """Backward compatibility alias for copy_object_to_syftbox_location"""
    return copy_object_to_syftbox_location(local_file, syft_url, syftbox_client) 