# syft-objects - Distributed file discovery and addressing system 

__version__ = "0.7.4"

# Internal imports (hidden from public API)
from . import models as _models
from . import data_accessor as _data_accessor
from . import factory as _factory
from . import collections as _collections
from . import utils as _utils
from . import client as _client
from . import auto_install as _auto_install
from . import permissions as _permissions
from . import file_ops as _file_ops
from . import display as _display

# Public API - only expose essential user-facing functionality
from .factory import syobj
from .collections import ObjectsCollection

# Create global objects collection instance
objects = ObjectsCollection()

# Create clearer API endpoints
def create_object(name=None, **kwargs):
    """Create a new SyftObject with explicit naming.
    
    This is an alias for syobj() with a clearer name.
    
    Args:
        name: Optional name for the object
        **kwargs: All the same arguments as syobj:
            - private_contents: String content for private file
            - mock_contents: String content for mock file
            - private_file: Path to private file
            - mock_file: Path to mock file
            - private_folder: Path to private folder
            - mock_folder: Path to mock folder
            - discovery_read: List of who can discover
            - mock_read: List of who can read mock
            - mock_write: List of who can write mock
            - private_read: List of who can read private
            - private_write: List of who can write private
            - metadata: Additional metadata dict
    
    Returns:
        SyftObject: The newly created object
    """
    # Use the internal factory module's syobj function
    return _factory.syobj(name, **kwargs)

def delete_object(uid):
    """Delete a SyftObject by UID.
    
    Args:
        uid: String UID of the object to delete
        
    Returns:
        bool: True if deletion was successful, False otherwise
        
    Raises:
        KeyError: If UID is not found
        TypeError: If uid is not a string
    """
    if not isinstance(uid, str):
        raise TypeError(f"UID must be str, not {type(uid).__name__}")
    
    try:
        obj = objects[uid]  # This uses the UID lookup
        result = obj.delete()
        if result:
            # Refresh the collection after successful deletion
            objects.refresh()
        return result
    except KeyError:
        raise KeyError(f"Object with UID '{uid}' not found")

# Export the essential public API
__all__ = [
    "create_object", # Function for creating objects
    "delete_object", # Function for deleting objects
    "objects",       # Global collection instance
]

# Internal setup (hidden from user)
_client.check_syftbox_status()
_auto_install.ensure_syftbox_app_installed(silent=True)

# Import startup banner (hidden)
from .client import _print_startup_banner
_print_startup_banner(only_if_needed=True)

# Clean up namespace - remove any accidentally exposed internal modules
import sys
_current_module = sys.modules[__name__]
_internal_modules = ['models', 'data_accessor', 'factory', 'collections', 'utils', 
                     'client', 'auto_install', 'permissions', 'file_ops', 'display',
                     'ObjectsCollection', 'sys', 'syobj']  # Hide all internal modules and factory function
for _attr_name in _internal_modules:
    if hasattr(_current_module, _attr_name):
        delattr(_current_module, _attr_name)

# Already defined above - remove this duplicate
# __all__ is defined earlier in the file
