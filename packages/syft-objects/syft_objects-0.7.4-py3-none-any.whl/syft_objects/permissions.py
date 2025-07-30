# syft-objects permissions - Permission management integration with syft-perm

from typing import List, Optional


# Global permission functions - will be set during initialization
set_file_permissions = None
get_file_permissions = None
remove_file_permissions = None
SYFTBOX_AVAILABLE = False


def _initialize_permissions():
    """Initialize permission functions from syft-perm package"""
    global set_file_permissions, get_file_permissions, remove_file_permissions, SYFTBOX_AVAILABLE
    
    try:
        from syft_perm import (
            set_file_permissions as _set_file_permissions,
            get_file_permissions as _get_file_permissions,
            remove_file_permissions as _remove_file_permissions,
            SYFTBOX_AVAILABLE as _SYFTBOX_AVAILABLE,
        )
        set_file_permissions = _set_file_permissions
        get_file_permissions = _get_file_permissions
        remove_file_permissions = _remove_file_permissions
        SYFTBOX_AVAILABLE = _SYFTBOX_AVAILABLE
        
    except ImportError:
        # Fallback if syft-perm is not available
        print("Warning: syft-perm not available. Install with: pip install syft-perm")
        SYFTBOX_AVAILABLE = False
        
        def set_file_permissions(*args, **kwargs):
            print("Warning: syft-perm not available. File permissions not set.")
            
        def get_file_permissions(*args, **kwargs):
            return None
            
        def remove_file_permissions(*args, **kwargs):
            print("Warning: syft-perm not available. File permissions not removed.")


def set_file_permissions_wrapper(file_path_or_url: str, read_permissions: List[str], write_permissions: Optional[List[str]] = None):
    """Wrapper to handle the syft-perm API with error handling"""
    try:
        set_file_permissions(file_path_or_url, read_permissions, write_permissions)
    except ValueError as e:
        if "Could not resolve file path" in str(e):
            # SyftBox not available, skip permission creation
            pass
        else:
            raise
    except Exception:
        # Other errors - log but don't crash
        pass


# Initialize permissions on module import
_initialize_permissions() 