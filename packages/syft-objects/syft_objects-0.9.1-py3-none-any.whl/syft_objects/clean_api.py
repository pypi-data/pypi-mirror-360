"""Clean API wrapper for SyftObject that exposes only the desired methods."""

from typing import Any, Optional
from datetime import datetime
from pathlib import Path


class CleanSyftObject:
    """Clean API wrapper that exposes only the methods we want users to see."""
    
    def __init__(self, syft_obj):
        """Initialize with a raw SyftObject instance."""
        # Use object.__setattr__ to bypass our custom __setattr__
        object.__setattr__(self, '_CleanSyftObject__obj', syft_obj)
    
    # ===== Getter Methods =====
    def get_uid(self) -> str:
        """Get the object's unique identifier"""
        return str(self._CleanSyftObject__obj.uid)
    
    def get_name(self) -> str:
        """Get the object's name"""
        return self._CleanSyftObject__obj.name
    
    def get_description(self) -> str:
        """Get the object's description"""
        return self._CleanSyftObject__obj.description
    
    def get_created_at(self) -> datetime:
        """Get the object's creation timestamp"""
        return self._CleanSyftObject__obj.created_at
    
    def get_updated_at(self) -> datetime:
        """Get the object's last update timestamp"""
        return self._CleanSyftObject__obj.updated_at
    
    def get_metadata(self) -> dict:
        """Get the object's metadata"""
        return self._CleanSyftObject__obj.metadata.copy()
    
    def get_file_type(self) -> str:
        """Get the file type (extension) of the object"""
        if self._CleanSyftObject__obj.is_folder:
            return "folder"
        # Extract extension from private URL
        parts = self._CleanSyftObject__obj.private_url.split("/")[-1].split(".")
        if len(parts) > 1:
            return parts[-1]
        return ""
    
    def get_info(self) -> dict:
        """Get a dictionary of object information"""
        return {
            "uid": str(self._CleanSyftObject__obj.uid),
            "name": self._CleanSyftObject__obj.name,
            "description": self._CleanSyftObject__obj.description,
            "created_at": self._CleanSyftObject__obj.created_at.isoformat() if self._CleanSyftObject__obj.created_at else None,
            "updated_at": self._CleanSyftObject__obj.updated_at.isoformat() if self._CleanSyftObject__obj.updated_at else None,
            "is_folder": self._CleanSyftObject__obj.is_folder,
            "metadata": self._CleanSyftObject__obj.metadata,
            "permissions": self.get_permissions()
        }
    
    def get_path(self) -> str:
        """Get the primary (mock) path of the object"""
        return self._CleanSyftObject__obj.mock_path
    
    def get_permissions(self) -> dict:
        """Get all permissions for the object"""
        return {
            "syftobject": {
                "read": self._CleanSyftObject__obj.syftobject_permissions.copy()
            },
            "mock": {
                "read": self._CleanSyftObject__obj.mock_permissions.copy(),
                "write": self._CleanSyftObject__obj.mock_write_permissions.copy()
            },
            "private": {
                "read": self._CleanSyftObject__obj.private_permissions.copy(),
                "write": self._CleanSyftObject__obj.private_write_permissions.copy()
            }
        }
    
    def get_urls(self) -> dict:
        """Get all URLs for the object"""
        return {
            "private": self._CleanSyftObject__obj.private_url,
            "mock": self._CleanSyftObject__obj.mock_url,
            "syftobject": self._CleanSyftObject__obj.syftobject
        }
    
    # ===== Setter Methods =====
    def set_name(self, name: str) -> None:
        """Set the object's name"""
        self._CleanSyftObject__obj.name = name
        from .models import utcnow
        self._CleanSyftObject__obj.updated_at = utcnow()
    
    def set_description(self, description: str) -> None:
        """Set the object's description"""
        self._CleanSyftObject__obj.description = description
        from .models import utcnow
        self._CleanSyftObject__obj.updated_at = utcnow()
    
    def set_metadata(self, metadata: dict) -> None:
        """Set the object's metadata (replaces existing)"""
        self._CleanSyftObject__obj.metadata = metadata.copy()
        from .models import utcnow
        self._CleanSyftObject__obj.updated_at = utcnow()
    
    def update_metadata(self, metadata: dict) -> None:
        """Update the object's metadata (merges with existing)"""
        self._CleanSyftObject__obj.metadata.update(metadata)
        from .models import utcnow
        self._CleanSyftObject__obj.updated_at = utcnow()
    
    # ===== Accessor Properties =====
    @property
    def mock(self):
        """Access mock-related properties and methods"""
        return MockAccessor(self._CleanSyftObject__obj)
    
    @property
    def private(self):
        """Access private-related properties and methods"""
        return PrivateAccessor(self._CleanSyftObject__obj)
    
    @property
    def syftobject_config(self):
        """Access syftobject configuration properties and methods"""
        return SyftObjectConfigAccessor(self._CleanSyftObject__obj)
    
    # ===== Actions =====
    def delete_obj(self, user_email: str = None) -> bool:
        """Delete this object with permission checking"""
        return self._CleanSyftObject__obj.delete_obj(user_email)
    
    def set_permissions(self, file_type: str, read: list[str] = None, write: list[str] = None) -> None:
        """Set permissions for this object"""
        self._CleanSyftObject__obj.set_permissions(file_type, read, write)
    
    @property
    def type(self) -> str:
        """Get the object type"""
        return self._CleanSyftObject__obj.object_type
    
    # ===== Special Methods =====
    def __repr__(self) -> str:
        """String representation"""
        return f"<SyftObject uid={self.get_uid()} name='{self.get_name()}'>"
    
    def __str__(self) -> str:
        """String representation"""
        return self.__repr__()
    
    def _repr_html_(self) -> str:
        """Rich HTML representation for Jupyter notebooks"""
        # Delegate to the wrapped object's display
        return self._CleanSyftObject__obj._repr_html_()
    
    def __dir__(self):
        """Show only the clean API methods"""
        return [
            # Getters
            'get_uid', 'get_name', 'get_description', 'get_created_at',
            'get_updated_at', 'get_metadata', 'get_file_type', 'get_info',
            'get_path', 'get_permissions', 'get_urls',
            # Setters
            'set_name', 'set_description', 'set_metadata', 'update_metadata',
            'set_permissions',
            # Accessors
            'mock', 'private', 'syftobject_config',
            # Actions
            'delete_obj',
            # Type
            'type'
        ]
    
    def __getattr__(self, name):
        """Block access to internal attributes"""
        if name == '_obj':
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")


# ===== Accessor Classes =====
class MockAccessor:
    """Accessor for mock-related properties and methods"""
    
    def __init__(self, syft_obj):
        self._CleanSyftObject__obj = syft_obj
    
    def get_path(self) -> str:
        """Get the local file path for the mock data"""
        return self._CleanSyftObject__obj.mock_path
    
    def get_url(self) -> str:
        """Get the syft:// URL for the mock data"""
        return self._CleanSyftObject__obj.mock_url
    
    def get_permissions(self) -> list[str]:
        """Get read permissions for the mock data"""
        return self._CleanSyftObject__obj.mock_permissions.copy()
    
    def get_write_permissions(self) -> list[str]:
        """Get write permissions for the mock data"""
        return self._CleanSyftObject__obj.mock_write_permissions.copy()


class PrivateAccessor:
    """Accessor for private-related properties and methods"""
    
    def __init__(self, syft_obj):
        self._CleanSyftObject__obj = syft_obj
    
    def get_path(self) -> str:
        """Get the local file path for the private data"""
        return self._CleanSyftObject__obj.private_path
    
    def get_url(self) -> str:
        """Get the syft:// URL for the private data"""
        return self._CleanSyftObject__obj.private_url
    
    def get_permissions(self) -> list[str]:
        """Get read permissions for the private data"""
        return self._CleanSyftObject__obj.private_permissions.copy()
    
    def get_write_permissions(self) -> list[str]:
        """Get write permissions for the private data"""
        return self._CleanSyftObject__obj.private_write_permissions.copy()
    
    def save(self, file_path: str | Path = None, create_syftbox_permissions: bool = True) -> None:
        """Save the syft object (alias for save_yaml)"""
        if file_path is None:
            # Use the syftobject path if available
            if hasattr(self._CleanSyftObject__obj, 'syftobject_path') and self._CleanSyftObject__obj.syftobject_path:
                file_path = self._CleanSyftObject__obj.syftobject_path
            else:
                raise ValueError("No file path provided and no syftobject_path available")
        self._CleanSyftObject__obj.save_yaml(file_path, create_syftbox_permissions)


class SyftObjectConfigAccessor:
    """Accessor for syftobject configuration properties and methods"""
    
    def __init__(self, syft_obj):
        self._CleanSyftObject__obj = syft_obj
    
    def get_path(self) -> str:
        """Get the local file path for the syftobject configuration"""
        return self._CleanSyftObject__obj.syftobject_path
    
    def get_url(self) -> str:
        """Get the syft:// URL for the syftobject configuration"""
        return self._CleanSyftObject__obj.syftobject
    
    def get_permissions(self) -> list[str]:
        """Get permissions for the syftobject configuration (discovery)"""
        return self._CleanSyftObject__obj.syftobject_permissions.copy()


def wrap_syft_object(obj) -> CleanSyftObject:
    """Wrap a SyftObject in the clean API wrapper."""
    if isinstance(obj, CleanSyftObject):
        return obj
    return CleanSyftObject(obj)