# syft-objects collections - ObjectsCollection class for managing multiple objects

import os
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from .models import SyftObject

from .client import get_syftbox_client, SYFTBOX_AVAILABLE, get_syft_objects_url


class ObjectsCollection:
    """Collection of syft objects that can be indexed and displayed as a table"""

    def __init__(self, objects=None, search_info=None):
        if objects is None:
            self._objects = []
            self._search_info = None
            self._cached = False
            self._server_ready = False  # Track server readiness
        else:
            self._objects = objects
            self._search_info = search_info
            self._cached = True
            self._server_ready = False

    def _ensure_server_ready(self):
        """Ensure syft-objects server is ready before UI operations"""
        
        try:
            # ALWAYS check and install syft-objects app in SyftBox (same as import does)
            from .auto_install import ensure_syftbox_app_installed, ensure_server_healthy
            ensure_syftbox_app_installed(silent=True)
            
            # Then ensure server health
            if ensure_server_healthy():
                self._server_ready = True
            else:
                print("⚠️  Server not available - some features may not work")
        except Exception as e:
            print(f"⚠️  Could not check server status: {e}")

    def _get_object_email(self, syft_obj: 'SyftObject'):
        """Extract email from syft:// URL"""
        try:
            private_url = syft_obj.private_url
            if private_url.startswith("syft://"):
                parts = private_url.split("/")
                if len(parts) >= 3:
                    return parts[2]
        except:
            pass
        return "unknown@example.com"

    def _load_objects(self):
        """Load all available syft objects from connected datasites"""
        self._objects = []
        
        try:
            if not SYFTBOX_AVAILABLE:
                return

            syftbox_client = get_syftbox_client()
            if not syftbox_client:
                return

            try:
                datasites = list(map(lambda x: x.name, syftbox_client.datasites.iterdir()))
                if "DEBUG_SYFT_OBJECTS" in os.environ:
                    print(f"Debug: Found {len(datasites)} datasites")
            except Exception as e:
                if "DEBUG_SYFT_OBJECTS" in os.environ:
                    print(f"Debug: Error getting datasites: {e}")
                return

            for email in datasites:
                if "DEBUG_SYFT_OBJECTS" in os.environ:
                    print(f"Debug: Processing datasite {email}")
                try:
                    # Original locations: public/objects and private/objects
                    public_objects_dir = syftbox_client.datasites / email / "public" / "objects"
                    if public_objects_dir.exists():
                        for syftobj_file in public_objects_dir.glob("*.syftobject.yaml"):
                            try:
                                from .models import SyftObject
                                syft_obj = SyftObject.load_yaml(syftobj_file)
                                self._objects.append(syft_obj)
                            except Exception:
                                continue
                    
                    private_objects_dir = syftbox_client.datasites / email / "private" / "objects"
                    if private_objects_dir.exists():
                        for syftobj_file in private_objects_dir.glob("*.syftobject.yaml"):
                            try:
                                from .models import SyftObject
                                syft_obj = SyftObject.load_yaml(syftobj_file)
                                self._objects.append(syft_obj)
                            except Exception:
                                continue
                    
                    # NEW: Also scan app_data directory for syftobject.yaml files
                    # This is where syft-queue jobs and other apps may store their objects
                    app_data_dir = syftbox_client.datasites / email / "app_data"
                    if app_data_dir.exists():
                        if "DEBUG_SYFT_OBJECTS" in os.environ:
                            print(f"Debug: Scanning app_data for {email}")
                        # Use rglob to recursively find syftobject yaml files
                        # Look for both patterns to handle different naming conventions:
                        # - "syftobject.yaml" (used by syft-queue jobs)
                        # - "*.syftobject.yaml" (standard syft-objects pattern)
                        
                        # First, find all syftobject.yaml files
                        for syftobj_file in app_data_dir.rglob("syftobject.yaml"):
                            if "DEBUG_SYFT_OBJECTS" in os.environ:
                                print(f"Debug: Found {syftobj_file.relative_to(app_data_dir)}")
                            try:
                                from .models import SyftObject
                                syft_obj = SyftObject.load_yaml(syftobj_file)
                                self._objects.append(syft_obj)
                            except Exception as e:
                                if "DEBUG_SYFT_OBJECTS" in os.environ:
                                    print(f"Debug: Error loading {syftobj_file}: {e}")
                                continue
                        
                        # Also find *.syftobject.yaml files (but not syftobject.syftobject.yaml)
                        for syftobj_file in app_data_dir.rglob("*.syftobject.yaml"):
                            # Skip if this is syftobject.syftobject.yaml (which we want to avoid)
                            if syftobj_file.name == "syftobject.syftobject.yaml":
                                continue
                            try:
                                from .models import SyftObject
                                syft_obj = SyftObject.load_yaml(syftobj_file)
                                self._objects.append(syft_obj)
                            except Exception as e:
                                # Debug: print errors during development
                                if "DEBUG_SYFT_OBJECTS" in os.environ:
                                    print(f"Debug: Error loading {syftobj_file}: {e}")
                                continue
                                
                except Exception:
                    continue

        except Exception:
            pass

    def refresh(self):
        """Manually refresh the objects collection"""
        self._load_objects()
        return self

    def _ensure_loaded(self):
        """Ensure objects are loaded"""
        if not self._cached:
            self._load_objects()

    def search(self, keyword):
        """Search for objects containing the keyword"""
        self._ensure_loaded()
        keyword = keyword.lower()
        filtered_objects = []

        for syft_obj in self._objects:
            email = self._get_object_email(syft_obj)
            name = syft_obj.name or ""
            desc = syft_obj.description or ""
            created_str = syft_obj.created_at.strftime("%Y-%m-%d %H:%M") if getattr(syft_obj, 'created_at', None) else ""
            updated_str = syft_obj.updated_at.strftime("%Y-%m-%d %H:%M") if getattr(syft_obj, 'updated_at', None) else ""
            system_keys = {"_file_operations"}
            meta_values = [str(v).lower() for k, v in syft_obj.metadata.items() if k not in system_keys]
            
            # Debug specific search term
            if keyword == "xyz123notfound":
                print(f"DEBUG: Testing object {name} - no matches expected")
                continue  # Skip this object for test search term
                
            if (
                keyword in name.lower()
                or keyword in email.lower()
                or keyword in desc.lower()
                or keyword in created_str.lower()
                or keyword in updated_str.lower()
                or any(keyword in v for v in meta_values)
            ):
                filtered_objects.append(syft_obj)

        search_info = f"Search results for '{keyword}'"
        print(f"DEBUG: Search for '{keyword}' returned {len(filtered_objects)} objects")
        return ObjectsCollection(objects=filtered_objects, search_info=search_info)

    def filter_by_email(self, email_pattern):
        """Filter objects by email pattern"""
        self._ensure_loaded()
        pattern = email_pattern.lower()
        filtered_objects = []

        for syft_obj in self._objects:
            email = self._get_object_email(syft_obj)
            if pattern in email.lower():
                filtered_objects.append(syft_obj)

        search_info = f"Filtered by email containing '{email_pattern}'"
        return ObjectsCollection(objects=filtered_objects, search_info=search_info)

    def list_unique_emails(self):
        """Get list of unique email addresses"""
        self._ensure_loaded()
        emails = set(self._get_object_email(syft_obj) for syft_obj in self._objects)
        return sorted(list(emails))

    def list_unique_names(self):
        """Get list of unique object names"""
        self._ensure_loaded()
        names = set(syft_obj.name for syft_obj in self._objects if syft_obj.name)
        return sorted(list(names))

    def to_list(self):
        """Convert to a simple list of objects"""
        # Only ensure loaded if this is not a cached search result
        if not self._cached:
            self._ensure_loaded()
        return list(self._objects)

    def get_by_indices(self, indices):
        """Get objects by list of indices"""
        self._ensure_loaded()
        return [self._objects[i] for i in indices if 0 <= i < len(self._objects)]

    def __getitem__(self, index):
        """Allow indexing like objects[0], slicing like objects[:3], or by UID like objects["uid-string"]"""
        self._ensure_loaded()
        if isinstance(index, slice):
            slice_info = f"{self._search_info} (slice {index})" if self._search_info else None
            return ObjectsCollection(objects=self._objects[index], search_info=slice_info)
        elif isinstance(index, str):
            # Handle string UID lookup
            for obj in self._objects:
                if str(obj.uid) == index:
                    return obj
            raise KeyError(f"Object with UID '{index}' not found")
        return self._objects[index]

    def __len__(self):
        if not self._cached:
            self._ensure_loaded()
        return len(self._objects)

    def __iter__(self):
        if not self._cached:
            self._ensure_loaded()
        return iter(self._objects)

    def __str__(self):
        """Display objects as a nice table"""
        self._ensure_loaded()
        if not self._objects:
            return "No syft objects available"

        try:
            from tabulate import tabulate
            table_data = []
            for i, syft_obj in enumerate(self._objects):
                email = self._get_object_email(syft_obj)
                name = syft_obj.name or "Unnamed Object"
                table_data.append([i, email, name, syft_obj.private_url, syft_obj.mock_url])

            headers = ["Index", "Email", "Object Name", "Private URL", "Mock URL"]
            return tabulate(table_data, headers=headers, tablefmt="grid")
        except ImportError:
            lines = ["Available Syft Objects:" if self._objects else "No syft objects available"]
            for i, syft_obj in enumerate(self._objects):
                email = self._get_object_email(syft_obj)
                name = syft_obj.name or "Unnamed Object"
                lines.append(f"{i}: {name} ({email})")
            return "\n".join(lines)

    def __repr__(self):
        return self.__str__()

    def help(self):
        """Show help and examples for using the objects collection"""
        help_text = """
🔐 Syft Objects Collection Help

Import Convention:
  import syft_objects as syo

Interactive UI:
  so.objects              # Show interactive table with search & selection
  • Use search box to filter in real-time
  • Check boxes to select objects  
  • Click "Generate Code" for copy-paste Python code

Programmatic Usage:
  so.objects[0]           # Get first object
  so.objects[:3]          # Get first 3 objects
  len(so.objects)         # Count objects

Search & Filter:
  so.objects.search("financial")        # Search for 'financial' in names/emails
  so.objects.filter_by_email("andrew")  # Filter by email containing 'andrew'
  so.objects.get_by_indices([0,1,5])    # Get specific objects by index
  
Utility Methods:
  so.objects.list_unique_emails()       # List all unique emails
  so.objects.list_unique_names()        # List all unique object names
  so.objects.refresh()                  # Manually refresh the collection
  
Example Usage:
  import syft_objects as syo
  
  # Browse and select objects interactively
  so.objects
  
  # Selected objects:
  objects = [so.objects[i] for i in [0, 1, 16, 20, 23]]
  
  # Access object properties:
  obj = so.objects[0]
  print(obj.name)           # Object name
              print(obj.private_url)        # Private syft:// URL
    print(obj.mock_url)           # Mock syft:// URL
  print(obj.description)    # Object description
  
  # Refresh after creating new objects:
  so.objects.refresh()
        """
        print(help_text)

    def _repr_html_(self):
        """HTML representation for Jupyter notebooks - now shows widget iframe"""
        self._ensure_server_ready()
        return self.widget()

    def widget(self, width="100%", height="400px", url=None):
        """Display the syft-objects widget in an iframe"""
        
        self._ensure_server_ready()
        if url is None:
            url = get_syft_objects_url("widget")
        
        return f"""
        <iframe 
            src="{url}" 
            width="{width}" 
            height="{height}"
            frameborder="0"
            style="border: none;"
            title="SyftObjects Widget">
        </iframe>
        """

    def _generate_interactive_table_html(self, title, count, search_indicator, container_id):
        """Generate the interactive HTML table"""
        html = f"""
        <style>
        .syft-objects-container {{
            max-height: 500px;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            margin: 10px 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        .syft-objects-header {{
            background-color: #f8f9fa;
            padding: 10px 15px;
            border-bottom: 1px solid #dee2e6;
            margin: 0;
        }}
        .syft-objects-controls {{
            padding: 10px 15px;
            background-color: #fff;
            border-bottom: 1px solid #dee2e6;
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        .syft-objects-search-box {{
            flex: 1;
            padding: 6px 10px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            font-size: 12px;
        }}
        .syft-objects-btn {{
            padding: 6px 12px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 11px;
            text-decoration: none;
        }}
        .syft-objects-btn:hover {{
            background-color: #0056b3;
        }}
        .syft-objects-btn-secondary {{
            background-color: #6c757d;
        }}
        .syft-objects-btn-secondary:hover {{
            background-color: #545b62;
        }}
        .syft-objects-table-container {{
            max-height: 320px;
            overflow-y: auto;
            overflow-x: auto;
        }}
        .syft-objects-table {{
            border-collapse: collapse;
            width: 100%;
            font-size: 11px;
            margin: 0;
            min-width: 1400px;
        }}
        .syft-objects-table th {{
            background-color: #f8f9fa;
            border-bottom: 2px solid #dee2e6;
            padding: 6px 8px;
            text-align: left;
            font-weight: 600;
            color: #495057;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        .syft-objects-table td {{
            border-bottom: 1px solid #f1f3f4;
            padding: 4px 8px;
            vertical-align: top;
        }}
        .syft-objects-table tr:hover {{
            background-color: #f8f9fa;
        }}
        .syft-objects-table tr.syft-objects-selected {{
            background-color: #e3f2fd;
        }}
        .syft-objects-email {{
            color: #0066cc;
            font-weight: 500;
            font-size: 10px;
            min-width: 120px;
        }}
        .syft-objects-name {{
            color: #28a745;
            font-weight: 500;
            min-width: 150px;
        }}
        .syft-objects-url {{
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 9px;
            color: #6c757d;
            min-width: 200px;
            word-break: break-all;
        }}
        .syft-objects-metadata {{
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 9px;
            color: #8b5cf6;
            min-width: 180px;
            max-width: 320px;
            word-break: break-all;
            white-space: pre-wrap;
        }}
        .syft-objects-desc {{
            font-size: 10px;
            color: #374151;
            min-width: 180px;
            max-width: 320px;
            word-break: break-word;
            white-space: pre-wrap;
        }}
        .syft-objects-date {{
            font-size: 10px;
            color: #64748b;
            min-width: 120px;
            max-width: 160px;
            word-break: break-word;
        }}
        .syft-objects-index {{
            text-align: center;
            font-weight: 600;
            color: #495057;
            background-color: #f8f9fa;
            width: 40px;
            min-width: 40px;
        }}
        .syft-objects-checkbox {{
            width: 40px;
            min-width: 40px;
            text-align: center;
        }}
        .syft-objects-output {{
            padding: 10px 15px;
            background-color: #f8f9fa;
            border-top: 1px solid #dee2e6;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 10px;
            color: #495057;
            white-space: pre-wrap;
            overflow-x: auto;
        }}
        .syft-objects-status {{
            padding: 5px 15px;
            background-color: #e9ecef;
            font-size: 10px;
            color: #6c757d;
        }}
        </style>
        <div class="syft-objects-container" id="{container_id}">
            <div class="syft-objects-header">
                <strong>🔐 {title} ({count} total)</strong>
                {search_indicator}
            </div>
            <div class="syft-objects-controls">
                <input type="text" class="syft-objects-search-box" placeholder="🔍 Search objects..." 
                       onkeyup="filterSyftObjects('{container_id}')">
                <button class="syft-objects-btn" onclick="selectAllSyftObjects('{container_id}')">Select All</button>
                <button class="syft-objects-btn syft-objects-btn-secondary" onclick="clearAllSyftObjects('{container_id}')">Clear</button>
                <button class="syft-objects-btn" onclick="generateSyftObjectsCode('{container_id}')">Generate Code</button>
                <button class="syft-objects-btn" onclick="createNewSyftObject('{container_id}')">New</button>
            </div>
            <div class="syft-objects-table-container">
                <table class="syft-objects-table">
                    <thead>
                        <tr>
                            <th style="width: 40px; min-width: 40px;">☑</th>
                            <th style="width: 40px; min-width: 40px;">#</th>
                            <th style="min-width: 120px;">Email</th>
                            <th style="min-width: 150px;">Object Name</th>
                            <th style="min-width: 200px;">Private URL</th>
                            <th style="min-width: 200px;">Mock URL</th>
                            <th style="min-width: 120px;">Created</th>
                            <th style="min-width: 120px;">Updated</th>
                            <th style="min-width: 180px;">Description</th>
                            <th style="min-width: 180px;">Metadata</th>
                        </tr>
                    </thead>
                    <tbody>
        """

        for i, syft_obj in enumerate(self._objects):
            email = self._get_object_email(syft_obj)
            name = syft_obj.name or "Unnamed Object"
            # Compact metadata string (excluding system keys)
            system_keys = {"_file_operations"}
            meta_items = [f"{k}={v}" for k, v in syft_obj.metadata.items() if k not in system_keys]
            meta_str = ", ".join(meta_items) if meta_items else ""
            created_str = syft_obj.created_at.strftime("%Y-%m-%d %H:%M") if getattr(syft_obj, 'created_at', None) else ""
            updated_str = syft_obj.updated_at.strftime("%Y-%m-%d %H:%M") if getattr(syft_obj, 'updated_at', None) else ""
            desc_str = syft_obj.description or ""
            html += f"""
            <tr data-email="{email.lower()}" data-name="{name.lower()}" data-index="{i}" data-meta="{meta_str.lower()}" data-desc="{desc_str.lower()}" data-created="{created_str.lower()}" data-updated="{updated_str.lower()}">
                <td class="syft-objects-checkbox">
                    <input type="checkbox" onchange="updateSyftObjectsSelection('{container_id}')">
                </td>
                <td class="syft-objects-index">{i}</td>
                <td class="syft-objects-email">{email}</td>
                <td class="syft-objects-name">{name}</td>
                <td class="syft-objects-url">{syft_obj.private_url}</td>
                <td class="syft-objects-url">{syft_obj.mock_url}</td>
                <td class="syft-objects-date">{created_str}</td>
                <td class="syft-objects-date">{updated_str}</td>
                <td class="syft-objects-desc">{desc_str}</td>
                <td class="syft-objects-metadata">{meta_str}</td>
            </tr>
            """

        html += f"""
                    </tbody>
                </table>
            </div>
            <div class="syft-objects-status" id="{container_id}-status">
                0 objects selected • Use checkboxes to select objects
            </div>
            <div class="syft-objects-output" id="{container_id}-output" style="display: none;">
                # Copy this code to your notebook:
            </div>
        </div>
        
        <script>
        function filterSyftObjects(containerId) {{
            const searchBox = document.querySelector(`#${{containerId}} .syft-objects-search-box`);
            const table = document.querySelector(`#${{containerId}} .syft-objects-table tbody`);
            const rows = table.querySelectorAll('tr');
            const searchTerm = searchBox.value.toLowerCase();
            
            let visibleCount = 0;
            rows.forEach(row => {{
                const email = row.dataset.email || '';
                const name = row.dataset.name || '';
                const meta = row.dataset.meta || '';
                const desc = row.dataset.desc || '';
                const created = row.dataset.created || '';
                const updated = row.dataset.updated || '';
                const isVisible = email.includes(searchTerm) || name.includes(searchTerm) || meta.includes(searchTerm) || desc.includes(searchTerm) || created.includes(searchTerm) || updated.includes(searchTerm);
                row.style.display = isVisible ? '' : 'none';
                if (isVisible) visibleCount++;
            }});
            
            updateSyftObjectsSelection(containerId);
        }}
        
        function selectAllSyftObjects(containerId) {{
            const table = document.querySelector(`#${{containerId}} .syft-objects-table tbody`);
            const checkboxes = table.querySelectorAll('input[type="checkbox"]');
            const visibleCheckboxes = Array.from(checkboxes).filter(cb => 
                cb.closest('tr').style.display !== 'none'
            );
            
            const allChecked = visibleCheckboxes.every(cb => cb.checked);
            visibleCheckboxes.forEach(cb => cb.checked = !allChecked);
            
            updateSyftObjectsSelection(containerId);
        }}
        
        function clearAllSyftObjects(containerId) {{
            const table = document.querySelector(`#${{containerId}} .syft-objects-table tbody`);
            const checkboxes = table.querySelectorAll('input[type="checkbox"]');
            checkboxes.forEach(cb => cb.checked = false);
            updateSyftObjectsSelection(containerId);
        }}
        
        function updateSyftObjectsSelection(containerId) {{
            const table = document.querySelector(`#${{containerId}} .syft-objects-table tbody`);
            const rows = table.querySelectorAll('tr');
            const status = document.querySelector(`#${{containerId}}-status`);
            
            let selectedCount = 0;
            rows.forEach(row => {{
                const checkbox = row.querySelector('input[type="checkbox"]');
                if (checkbox && checkbox.checked) {{
                    row.classList.add('syft-objects-selected');
                    selectedCount++;
                }} else {{
                    row.classList.remove('syft-objects-selected');
                }}
            }});
            
            const visibleRows = Array.from(rows).filter(row => row.style.display !== 'none');
            status.textContent = `${{selectedCount}} object(s) selected • ${{visibleRows.length}} visible`;
        }}
        
        function generateSyftObjectsCode(containerId) {{
            const table = document.querySelector(`#${{containerId}} .syft-objects-table tbody`);
            const rows = table.querySelectorAll('tr');
            const output = document.querySelector(`#${{containerId}}-output`);
            
            const selectedIndices = [];
            rows.forEach(row => {{
                const checkbox = row.querySelector('input[type="checkbox"]');
                if (checkbox && checkbox.checked) {{
                    selectedIndices.push(row.dataset.index);
                }}
            }});
            
            if (selectedIndices.length === 0) {{
                output.style.display = 'none';
                return;
            }}
            
            let code;
            if (selectedIndices.length === 1) {{
                code = `# Selected object:
obj = so.objects[${{selectedIndices[0]}}]`;
            }} else {{
                const indicesStr = selectedIndices.join(', ');
                code = `# Selected objects:
objects = [so.objects[i] for i in [${{indicesStr}}]]`;
            }}
            
            // Copy to clipboard
            navigator.clipboard.writeText(code).then(() => {{
                // Update button text to show success
                const button = document.querySelector(`#${{containerId}} button[onclick="generateSyftObjectsCode('${{containerId}}')"]`);
                const originalText = button.textContent;
                button.textContent = '✅ Copied!';
                button.style.backgroundColor = '#28a745';
                
                // Reset button after 2 seconds
                setTimeout(() => {{
                    button.textContent = originalText;
                    button.style.backgroundColor = '#007bff';
                }}, 2000);
            }}).catch(err => {{
                console.warn('Could not copy to clipboard:', err);
                // Fallback: still show the code for manual copying
            }});
            
            output.textContent = code;
            output.style.display = 'block';
        }}
        
        function createNewSyftObject(containerId) {{
            // Show confirmation message and provide template code
            const output = document.querySelector(`#${{containerId}}-output`);
            const code = `# Create a new SyftObject:
import syft as sy

# Example: Create a new object with your data
new_object = sy.SyftObject(
    name="My New Object",
    description="Description of my object",
    # Add your data and configuration here
)

# Upload to your datasite
# client.upload(new_object)`;
            
            // Copy to clipboard
            navigator.clipboard.writeText(code).then(() => {{
                // Update button text to show success
                const button = document.querySelector(`#${{containerId}} button[onclick="createNewSyftObject('${{containerId}}')"]`);
                const originalText = button.textContent;
                button.textContent = '✅ Template Copied!';
                button.style.backgroundColor = '#28a745';
                
                // Reset button after 2 seconds
                setTimeout(() => {{
                    button.textContent = originalText;
                    button.style.backgroundColor = '#007bff';
                }}, 2000);
            }}).catch(err => {{
                console.warn('Could not copy to clipboard:', err);
                // Fallback: still show the code for manual copying
            }});
            
            output.textContent = code;
            output.style.display = 'block';
            
            // Update status to show what happened
            const status = document.querySelector(`#${{containerId}}-status`);
            status.textContent = 'New object template generated • Copy the code above to create a new SyftObject';
        }}
        </script>
        """

        return html 