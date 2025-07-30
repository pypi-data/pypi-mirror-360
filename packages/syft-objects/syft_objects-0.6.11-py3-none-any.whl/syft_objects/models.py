# syft-objects models - Core SyftObject class and related models

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import UUID, uuid4
import yaml

from pydantic import BaseModel, Field, model_validator

from .client import get_syftbox_client, extract_local_path_from_syft_url
from .permissions import set_file_permissions_wrapper
from .display import create_html_display
from .data_accessor import DataAccessor


def utcnow():
    """Get current UTC timestamp"""
    return datetime.now(tz=timezone.utc)


class SyftObject(BaseModel):
    """
    A distributed object with mock/real pattern for file discovery and addressing
    """
    # Mandatory metadata
    uid: UUID = Field(default_factory=uuid4, description="Unique identifier for the object")
    private_url: str = Field(description="Syft:// path to the private object", alias="private")
    mock_url: str = Field(description="Syft:// path to the public/mock object", alias="mock")
    syftobject: str = Field(description="Syft:// path to the .syftobject.yaml metadata file")
    created_at: datetime = Field(default_factory=utcnow, description="Creation timestamp")
    
    # Object type - new field for folder support
    object_type: str = Field(
        default="file", 
        description="Type of object: 'file' or 'folder'"
    )
    
    # Permission metadata - who can access what (read/write granularity)
    syftobject_permissions: list[str] = Field(
        default_factory=lambda: ["public"], 
        description="Who can read the .syftobject.yaml file (know the object exists)"
    )
    mock_permissions: list[str] = Field(
        default_factory=lambda: ["public"], 
        description="Who can read the mock/fake version of the object"
    )
    mock_write_permissions: list[str] = Field(
        default_factory=list,
        description="Who can write/update the mock/fake version of the object"
    )
    private_permissions: list[str] = Field(
        default_factory=list, 
        description="Who can read the private/real data"
    )
    private_write_permissions: list[str] = Field(
        default_factory=list,
        description="Who can write/update the private/real data"
    )
    
    # Recommended metadata
    name: Optional[str] = Field(None, description="Human-readable name for the object")
    description: Optional[str] = Field(None, description="Description of the object")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    # Arbitrary metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata")
    
    @property
    def is_folder(self) -> bool:
        """Check if this object represents a folder."""
        return self.object_type == "folder"
    
    # Data accessor properties
    @property
    def private(self) -> DataAccessor:
        """Get data accessor for private data with .obj, .file, .path, .url properties"""
        return DataAccessor(self.private_url, self)
    
    @property
    def mock(self) -> DataAccessor:
        """Get data accessor for mock data with .obj, .file, .path, .url properties"""
        return DataAccessor(self.mock_url, self)
    
    # Convenience properties for backward compatibility
    @property
    def private_path(self) -> str:
        """Get the full local file path for the private object"""
        return self._get_local_file_path(self.private_url)
    
    @property
    def mock_path(self) -> str:
        """Get the full local file path for the mock object"""
        return self._get_local_file_path(self.mock_url)
    
    @property
    def syftobject_path(self) -> str:
        """Get the full local file path for the .syftobject.yaml file"""
        # First try to get path from the syftobject field
        if hasattr(self, 'syftobject') and self.syftobject:
            return self._get_local_file_path(self.syftobject)
        
        # Fall back to metadata if available
        file_ops = self.metadata.get("_file_operations", {})
        syftobject_yaml_path = file_ops.get("syftobject_yaml_path")
        if syftobject_yaml_path:
            return syftobject_yaml_path
        return ""
    
    @property
    def file_type(self) -> str:
        """Get the file extension from mock/private URLs"""
        # Folders don't have file extensions
        if self.is_folder:
            return ""
            
        try:
            # Try to extract file extension from private URL first, then mock URL
            for url in [self.private_url, self.mock_url]:
                if not url:
                    continue
                
                # Get just the filename from the URL
                filename = url.split("/")[-1]
                
                # Check if filename has an extension (dot not at start)
                if "." in filename and not filename.startswith("."):
                    parts = filename.split(".")
                    if len(parts) > 1 and parts[-1]:  # Ensure there's an actual extension
                        return f".{parts[-1].lower()}"
            return ""
        except:
            return ""
    
    @model_validator(mode='after')
    def validate_urls(self):
        """Validate URLs match object type"""
        if self.is_folder:
            # Folders must end with /
            if not self.private_url.endswith('/'):
                self.private_url += '/'
            if not self.mock_url.endswith('/'):
                self.mock_url += '/'
        else:
            # Files must NOT end with /
            if self.private_url.endswith('/'):
                raise ValueError("File URLs cannot end with /")
            if self.mock_url.endswith('/'):
                raise ValueError("File URLs cannot end with /")
        return self
    
    @model_validator(mode='after')
    def validate_file_extensions(self):
        """Validate that mock and private files have matching extensions"""
        # Skip validation for folders - they don't have extensions
        if self.is_folder:
            return self
            
        def extract_extension(url: str) -> str:
            """Extract file extension from a URL filename"""
            if not url:
                return ""
            
            # Get just the filename from the URL
            filename = url.split("/")[-1]
            
            # Check if filename has an extension (dot not at start)
            if "." in filename and not filename.startswith("."):
                parts = filename.split(".")
                if len(parts) > 1 and parts[-1]:  # Ensure there's an actual extension
                    return parts[-1].lower()
            return ""
        
        mock_ext = extract_extension(self.mock_url)
        private_ext = extract_extension(self.private_url)
        
        # Only validate if BOTH files have extensions - they must match
        if mock_ext and private_ext and mock_ext != private_ext:
            raise ValueError(
                f"Mock and private files must have matching extensions. "
                f"Mock file has '.{mock_ext}' but private file has '.{private_ext}'. "
                f"Mock: {self.mock_url}, Private: {self.private_url}"
            )
        
        return self
    
    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True  # Allow using both field name and alias
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
    
    def _repr_html_(self) -> str:
        """Rich HTML representation for Jupyter notebooks"""
        return create_html_display(self)
    
    def _check_file_exists(self, syft_url: str) -> bool:
        """Check if a file exists locally (for display purposes)"""
        try:
            syftbox_client = get_syftbox_client()
            if syftbox_client:
                local_path = extract_local_path_from_syft_url(syft_url)
                if local_path:
                    return local_path.exists()
            
            # Fallback: check if it's in tmp directory
            from pathlib import Path
            filename = syft_url.split("/")[-1]
            tmp_path = Path("tmp") / filename
            return tmp_path.exists()
        except Exception:
            return False
    
    def _get_local_file_path(self, syft_url: str) -> str:
        """Get the local file path for a syft:// URL"""
        try:
            # Check for folder paths in metadata first
            if self.is_folder and "_folder_paths" in self.metadata:
                folder_paths = self.metadata["_folder_paths"]
                if syft_url == self.private_url and "private" in folder_paths:
                    return folder_paths["private"]
                elif syft_url == self.mock_url and "mock" in folder_paths:
                    return folder_paths["mock"]
            
            syftbox_client = get_syftbox_client()
            if syftbox_client:
                local_path = extract_local_path_from_syft_url(syft_url)
                if local_path and local_path.exists():
                    return str(local_path.absolute())
            
            # Fallback: check if it's in tmp directory
            from pathlib import Path
            filename = syft_url.split("/")[-1].rstrip('/')  # Remove trailing slash for folders
            tmp_path = Path("tmp") / filename
            if tmp_path.exists():
                return str(tmp_path.absolute())
            
            return ""
        except Exception:
            return ""
    
    def _get_file_preview(self, file_path: str, max_chars: int = 1000) -> str:
        """Get a preview of file content (first N characters)"""
        try:
            from pathlib import Path
            path = Path(file_path)
            
            if not path.exists():
                return f"File not found: {file_path}"
            
            # Try to read as text
            try:
                content = path.read_text(encoding='utf-8')
                if len(content) <= max_chars:
                    return content
                else:
                    return content[:max_chars] + f"\n\n... (truncated, showing first {max_chars} characters of {len(content)} total)"
            except UnicodeDecodeError:
                # If it's a binary file, show file info instead
                size = path.stat().st_size
                return f"Binary file: {path.name}\nSize: {size} bytes\nPath: {file_path}\n\n(Binary files cannot be previewed as text)"
        except Exception as e:
            return f"Error reading file: {str(e)}"


    def save_yaml(self, file_path: str | Path, create_syftbox_permissions: bool = True) -> None:
        """Save the syft object to a YAML file with .syftobject.yaml extension and create SyftBox permission files"""
        file_path = Path(file_path)
        
        # Ensure the file ends with .syftobject.yaml
        if not file_path.name.endswith('.syftobject.yaml'):
            if file_path.suffix == '.yaml':
                # Replace .yaml with .syftobject.yaml
                file_path = file_path.with_suffix('.syftobject.yaml')
            elif file_path.suffix == '':
                # Add .syftobject.yaml extension
                file_path = file_path.with_suffix('.syftobject.yaml')
            else:
                # Add .syftobject.yaml to existing extension
                file_path = Path(str(file_path) + '.syftobject.yaml')
        
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dict and handle datetime/UUID serialization
        data = self.model_dump(mode='json')
        
        # Write to YAML file
        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=True, indent=2)
        
        # Create SyftBox permission files if requested
        if create_syftbox_permissions:
            self._create_syftbox_permissions(file_path)

    @classmethod
    def load_yaml(cls, file_path: str | Path) -> 'SyftObject':
        """Load a syft object from a .syftobject.yaml file"""
        file_path = Path(file_path)
        
        # Validate that the file has the correct extension
        if not file_path.name.endswith('.syftobject.yaml'):
            raise ValueError(f"File must have .syftobject.yaml extension, got: {file_path.name}")
        
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        return cls(**data)

    def _create_syftbox_permissions(self, syftobject_file_path: Path) -> None:
        """Create SyftBox permission files for the syft object"""
        # Create permissions for the .syftobject.yaml file itself (discovery)
        set_file_permissions_wrapper(str(syftobject_file_path), self.syftobject_permissions)
        
        # Create permissions for mock and private files
        set_file_permissions_wrapper(self.mock_url, self.mock_permissions, self.mock_write_permissions)
        set_file_permissions_wrapper(self.private_url, self.private_permissions, self.private_write_permissions)

    def set_permissions(self, file_type: str, read: list[str] = None, write: list[str] = None, syftobject_file_path: str | Path = None) -> None:
        """
        Update permissions for a file in this object (mock, private, or syftobject).
        Uses the minimal permission utilities from permissions.py.
        """
        if file_type == "mock":
            if read is not None:
                self.mock_permissions = read
            if write is not None:
                self.mock_write_permissions = write
            # Update syft.pub.yaml if possible
            set_file_permissions_wrapper(self.mock_url, self.mock_permissions, self.mock_write_permissions)
        elif file_type == "private":
            if read is not None:
                self.private_permissions = read
            if write is not None:
                self.private_write_permissions = write
            # Update syft.pub.yaml if possible
            set_file_permissions_wrapper(self.private_url, self.private_permissions, self.private_write_permissions)
        elif file_type == "syftobject":
            if read is not None:
                self.syftobject_permissions = read
            # Discovery files are read-only, so use syftobject_path or provided path
            if syftobject_file_path:
                set_file_permissions_wrapper(str(syftobject_file_path), self.syftobject_permissions)
            elif self.syftobject:
                set_file_permissions_wrapper(self.syftobject, self.syftobject_permissions)
        else:
            raise ValueError(f"Invalid file_type: {file_type}. Must be 'mock', 'private', or 'syftobject'.")
    
    def delete(self) -> bool:
        """
        Delete this syft-object and all its associated files.
        
        For folder objects, this will delete the entire directory structure.
        For file objects, this will delete the individual files.
        
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            if self.is_folder:
                return self._delete_folder_object()
            else:
                return self._delete_file_object()
        except Exception as e:
            return False
    
    def _delete_folder_object(self) -> bool:
        """Delete a folder-type syft-object by removing its directory structure."""
        try:
            from pathlib import Path
            import shutil
            
            # Try multiple strategies to find the folder path
            folder_path = None
            
            # Strategy 1: Use syftobject_path parent directory (most reliable for syft-queue jobs)
            if self.syftobject_path:
                syftobject_path = Path(self.syftobject_path)
                if syftobject_path.exists():
                    folder_path = syftobject_path.parent
                    pass  # Found folder path via syftobject_path
            
            # Strategy 2: For syft-queue jobs, search across all status directories
            if not folder_path and hasattr(self, 'metadata') and self.metadata and self.metadata.get('type') == 'SyftBox Job':
                # Search in syft-queues directories for this job UID
                job_uid = str(self.uid)
                
                # Common syft-queue base paths
                potential_bases = [
                    Path.home() / "SyftBox" / "datasites",
                    Path("/tmp"),  # fallback
                ]
                
                for base in potential_bases:
                    if base.exists():
                        # Search for job directories with this UID across all status folders
                        for queue_dir in base.rglob("**/syft-queues"):
                            for status_dir in ["inbox", "running", "completed", "failed"]:
                                status_path = queue_dir / f"*_queue" / "jobs" / status_dir
                                for job_dir in status_path.parent.glob(f"jobs/{status_dir}/*"):
                                    if job_dir.is_dir() and job_uid in job_dir.name:
                                        folder_path = job_dir
                                        pass  # Found syft-queue job folder
                                        break
                                if folder_path:
                                    break
                            if folder_path:
                                break
                    if folder_path:
                        break
            
            # Strategy 3: Check if private_path is a directory
            if not folder_path and self.private_path:
                private_path = Path(self.private_path)
                if private_path.exists() and private_path.is_dir():
                    folder_path = private_path
                    pass  # Found folder path via private_path (is_dir)
                elif private_path.exists() and private_path.is_file():
                    # If private_path is a file, use its parent directory
                    folder_path = private_path.parent
                    pass  # Found folder path via private_path parent
            
            # Strategy 4: Check folder paths in metadata
            if not folder_path and hasattr(self, 'metadata') and self.metadata:
                folder_paths = self.metadata.get('_folder_paths', {})
                if 'private' in folder_paths:
                    metadata_path = Path(folder_paths['private'])
                    pass  # Found folder path via metadata
                    
                    # Check if the metadata path actually exists
                    if metadata_path.exists() and metadata_path.is_dir():
                        folder_path = metadata_path
                        pass  # Metadata path exists and is valid
                    else:
                        pass  # Metadata path doesn't exist, checking if job moved
                        
                        # The metadata path is stale - search for the job in current location
                        job_uid = str(self.uid)
                        potential_bases = [
                            Path.home() / "SyftBox" / "datasites",
                            Path("/tmp"),  # fallback
                        ]
                        
                        for base in potential_bases:
                            if base.exists():
                                # Search for job directories with this UID across all status folders
                                for queue_dir in base.rglob("**/syft-queues"):
                                    for status_dir in ["running", "completed", "failed", "inbox"]:  # prioritize current status
                                        for job_dir in queue_dir.rglob(f"*/jobs/{status_dir}/*{job_uid}*"):
                                            if job_dir.is_dir():
                                                folder_path = job_dir
                                                pass  # Found job in status folder
                                                break
                                        if folder_path:
                                            break
                                    if folder_path:
                                        break
                            if folder_path:
                                break
            
            if folder_path and folder_path.exists() and folder_path.is_dir():
                shutil.rmtree(str(folder_path))
                
                # Refresh the objects collection
                try:
                    from .collections import objects
                    if objects:
                        objects.refresh()
                except ImportError:
                    pass
                return True
            else:
                return False
                
        except Exception as e:
            return False
    
    def _delete_file_object(self) -> bool:
        """Delete a file-type syft-object by removing its individual files."""
        try:
            from pathlib import Path
            import shutil
            deleted_files = []
            
            # Delete private file/directory if it exists
            if self.private_path:
                private_path = Path(self.private_path)
                if private_path.exists():
                    if private_path.is_file():
                        private_path.unlink()
                        deleted_files.append("private")
                    elif private_path.is_dir():
                        shutil.rmtree(str(private_path))
                        deleted_files.append("private_directory")
            
            # Delete mock file/directory if it exists
            if self.mock_path:
                mock_path = Path(self.mock_path)
                if mock_path.exists():
                    if mock_path.is_file():
                        mock_path.unlink()
                        deleted_files.append("mock")
                    elif mock_path.is_dir():
                        shutil.rmtree(str(mock_path))
                        deleted_files.append("mock_directory")
            
            # Delete syftobject file if it exists
            if self.syftobject_path:
                syftobject_path = Path(self.syftobject_path)
                if syftobject_path.exists():
                    syftobject_path.unlink()
                    deleted_files.append("syftobject")
            
            if deleted_files:
                # Refresh the objects collection
                try:
                    from .collections import objects
                    if objects:
                        objects.refresh()
                except ImportError:
                    pass
                return True
            else:
                return False
                
        except Exception as e:
            return False
    
 