# syft-objects - Distributed file discovery and addressing system 

__version__ = "0.6.11"

# Core imports
from .models import SyftObject
from .data_accessor import DataAccessor
from .factory import syobj
from .collections import ObjectsCollection
from .utils import scan_for_syft_objects, load_syft_objects_from_directory
from .client import check_syftbox_status, get_syft_objects_port, get_syft_objects_url
from .auto_install import ensure_syftbox_app_installed

# Create global objects collection instance
objects = ObjectsCollection()

# Export main classes and functions
__all__ = [
    "SyftObject", 
    "DataAccessor",
    "syobj", 
    "objects", 
    "ObjectsCollection",
    "scan_for_syft_objects",
    "load_syft_objects_from_directory",
    "get_syft_objects_port",
    "get_syft_objects_url"
]

# Check SyftBox status - only show banner if there are issues or delays
check_syftbox_status()
ensure_syftbox_app_installed(silent=True)

# Import _print_startup_banner here to avoid circular imports
from .client import _print_startup_banner
_print_startup_banner(only_if_needed=True)
