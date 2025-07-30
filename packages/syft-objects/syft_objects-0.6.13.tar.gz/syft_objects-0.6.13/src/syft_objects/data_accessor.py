"""
Data accessor for syft objects - provides multiple ways to access the same data
"""

from pathlib import Path
from typing import Any, Union, BinaryIO, TextIO, List


class FolderAccessor:
    """Accessor for folder objects."""
    
    def __init__(self, folder_path: Path):
        self.path = folder_path if isinstance(folder_path, Path) else Path(folder_path)
    
    def list_files(self, pattern: str = "*") -> List[Path]:
        """List files in the folder matching pattern."""
        return [f for f in self.path.glob(pattern) if f.is_file()]
    
    def list_all_files(self) -> List[Path]:
        """Recursively list all files."""
        return [f for f in self.path.rglob("*") if f.is_file()]
    
    def get_file(self, relative_path: str) -> Path:
        """Get a specific file by relative path."""
        file_path = self.path / relative_path
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {relative_path}")
        return file_path
    
    def read_file(self, relative_path: str) -> str:
        """Read a text file's contents."""
        return self.get_file(relative_path).read_text()
    
    def exists(self) -> bool:
        """Check if folder exists."""
        return self.path.exists() and self.path.is_dir()
    
    def size(self) -> int:
        """Get total size of all files in folder."""
        total = 0
        for file in self.path.rglob("*"):
            if file.is_file():
                total += file.stat().st_size
        return total
    
    def __repr__(self):
        file_count = len(list(self.path.rglob("*")))
        return f"FolderAccessor(path={self.path}, files={file_count})"


class DataAccessor:
    """
    Provides multiple access patterns for syft object data:
    - .obj: Loaded object (DataFrame, dict, etc.)
    - .file: Open file handle
    - .path: Local file path
    - .url: Syft URL
    - ._repr_html_: HTML representation for widgets
    """
    
    def __init__(self, syft_url: str, syft_object: 'SyftObject'):
        self._syft_url = syft_url
        self._syft_object = syft_object
        self._cached_obj = None
        self._cached_path = None
    
    @property
    def url(self) -> str:
        """Get the syft:// URL for this data"""
        return self._syft_url
    
    @property
    def path(self) -> str:
        """Get the local file path for this data"""
        if self._cached_path is None:
            self._cached_path = self._syft_object._get_local_file_path(self._syft_url)
            # For folders, ensure path doesn't have trailing /
            if (hasattr(self._syft_object, 'is_folder') and 
                getattr(self._syft_object, 'is_folder', False) is True and 
                self._cached_path.endswith('/')):
                self._cached_path = self._cached_path.rstrip('/')
        return self._cached_path
    
    @property
    def file(self) -> Union[TextIO, BinaryIO]:
        """Get an open file handle for this data"""
        file_path = self.path
        if not file_path:
            raise FileNotFoundError(f"File not found: {self._syft_url}")
        
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check if file is binary by trying to read a small portion
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read(512)  # Try reading first 512 bytes
            return open(file_path, 'r', encoding='utf-8')
        except UnicodeDecodeError:
            return open(file_path, 'rb')
    
    @property
    def obj(self) -> Any:
        """Get the loaded object - returns FolderAccessor for folders"""
        # Only create FolderAccessor for actual folder objects, not Mock objects
        if (hasattr(self._syft_object, 'is_folder') and 
            getattr(self._syft_object, 'is_folder', False) is True):
            return FolderAccessor(Path(self.path))
        
        if self._cached_obj is None:
            self._cached_obj = self._load_file_content()
        return self._cached_obj
    
    def _load_file_content(self) -> Any:
        """Load and return file content based on file type"""
        try:
            file_path = self.path
            if not file_path:
                return f"File not found: {self._syft_url}"
            
            path = Path(file_path)
            if not path.exists():
                return f"File not found: {file_path}"
            
            # Get file extension to determine how to load it
            file_ext = path.suffix.lower()
            
            if file_ext == '.txt':
                # Return text content
                return path.read_text(encoding='utf-8')
            
            elif file_ext == '.csv':
                # Return pandas DataFrame
                try:
                    import pandas as pd
                    return pd.read_csv(file_path)
                except ImportError:
                    # If pandas not available, return text content with a warning
                    content = path.read_text(encoding='utf-8')
                    return f"Warning: pandas not available. Returning raw CSV content:\n\n{content}"
            
            elif file_ext in ['.json']:
                # Return parsed JSON
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            elif file_ext in ['.sqlite', '.db', '.sqlite3']:
                # Return sqlite3 connection
                import sqlite3
                return sqlite3.connect(file_path)
            
            elif file_ext in ['.xlsx', '.xls']:
                # Return pandas DataFrame for Excel files
                try:
                    import pandas as pd
                    return pd.read_excel(file_path)
                except ImportError:
                    return f"Warning: pandas not available. Cannot load Excel file: {file_path}"
                except Exception as e:
                    return f"Error loading Excel file: {str(e)}"
            
            elif file_ext == '.parquet':
                # Return pandas DataFrame for Parquet files
                try:
                    import pandas as pd
                    return pd.read_parquet(file_path)
                except ImportError:
                    return f"Warning: pandas and pyarrow not available. Cannot load Parquet file: {file_path}"
                except Exception as e:
                    return f"Error loading Parquet file: {str(e)}"
            
            elif file_ext in ['.pkl', '.pickle']:
                # Return unpickled Python object
                import pickle
                with open(file_path, 'rb') as f:
                    return pickle.load(f)
            
            elif file_ext in ['.yaml', '.yml']:
                # Return parsed YAML
                try:
                    import yaml
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return yaml.safe_load(f)
                except ImportError:
                    return f"Warning: PyYAML not available. Cannot load YAML file: {file_path}"
                except Exception as e:
                    return f"Error loading YAML file: {str(e)}"
            
            elif file_ext in ['.npy']:
                # Return numpy array
                try:
                    import numpy as np
                    return np.load(file_path)
                except ImportError:
                    return f"Warning: numpy not available. Cannot load .npy file: {file_path}"
                except Exception as e:
                    return f"Error loading numpy file: {str(e)}"
            
            elif file_ext in ['.npz']:
                # Return numpy archive
                try:
                    import numpy as np
                    return np.load(file_path)
                except ImportError:
                    return f"Warning: numpy not available. Cannot load .npz file: {file_path}"
                except Exception as e:
                    return f"Error loading numpy archive: {str(e)}"
            
            else:
                # For unknown file types, return text content
                try:
                    return path.read_text(encoding='utf-8')
                except UnicodeDecodeError:
                    # If it's a binary file, return file info
                    size = path.stat().st_size
                    return f"Binary file: {path.name}\nSize: {size} bytes\nPath: {file_path}\n\n(Use .file to get file handle for manual loading)"
                    
        except Exception as e:
            return f"Error loading file: {str(e)}"
    
    def _repr_html_(self) -> str:
        """HTML representation for Jupyter widgets"""
        try:
            obj = self.obj
            
            # Handle FolderAccessor objects
            if isinstance(obj, FolderAccessor):
                files = obj.list_files()
                file_list = "<br/>".join([f"📄 {f.name}" for f in files[:10]])
                if len(files) > 10:
                    file_list += f"<br/>... and {len(files) - 10} more files"
                return f"<div><strong>📁 Folder:</strong> {obj.path}<br/><strong>Files ({len(files)}):</strong><br/>{file_list}</div>"
            
            # If the object has its own _repr_html_, use that
            if hasattr(obj, '_repr_html_') and callable(getattr(obj, '_repr_html_')):
                return obj._repr_html_()
            
            # For pandas DataFrames, use their HTML representation
            if hasattr(obj, 'to_html'):
                return obj.to_html()
            
            # For strings, wrap in <pre> tags
            if isinstance(obj, str):
                # Truncate long strings
                display_str = obj[:1000] + "..." if len(obj) > 1000 else obj
                return f"<pre>{display_str}</pre>"
            
            # For dicts, format as JSON
            if isinstance(obj, dict):
                import json
                json_str = json.dumps(obj, indent=2)
                display_str = json_str[:1000] + "..." if len(json_str) > 1000 else json_str
                return f"<pre>{display_str}</pre>"
            
            # For sqlite connections, show table info
            if str(type(obj)) == "<class 'sqlite3.Connection'>":
                try:
                    cursor = obj.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cursor.fetchall()
                    table_names = [table[0] for table in tables]
                    return f"<div><strong>SQLite Database</strong><br/>Tables: {', '.join(table_names)}</div>"
                except:
                    return f"<div><strong>SQLite Database</strong><br/>Connection: {self.path}</div>"
            
            # Default: show string representation
            str_repr = str(obj)
            display_str = str_repr[:500] + "..." if len(str_repr) > 500 else str_repr
            return f"<pre>{display_str}</pre>"
            
        except Exception as e:
            return f"<div><strong>Error generating HTML representation:</strong> {str(e)}</div>"
    
    def __repr__(self) -> str:
        """String representation"""
        return f"DataAccessor(url='{self.url}', path='{self.path}')"
    
    def __str__(self) -> str:
        """String representation"""
        return self.__repr__() 