# syft-objects display - HTML rendering and rich display functionality

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import SyftObject


def create_html_display(syft_obj: 'SyftObject') -> str:
    """Create a beautiful HTML display for the SyftObject"""
    # Get file operations info from metadata if available
    file_ops = syft_obj.metadata.get("_file_operations", {})
    files_moved = file_ops.get("files_moved_to_syftbox", [])
    created_files = file_ops.get("created_files", [])
    syftbox_available = file_ops.get("syftbox_available", False)
    syftobject_yaml_path = file_ops.get("syftobject_yaml_path")
    
    # Check if files exist locally
    mock_file_exists = syft_obj._check_file_exists(syft_obj.mock_url)
    private_file_exists = syft_obj._check_file_exists(syft_obj.private_url)
    
    # Permission badge colors
    def permission_badge(users, perm_type="read"):
        if not users:
            return '<span class="syft-badge syft-badge-none">None</span>'
        elif "public" in users or "*" in users:
            return '<span class="syft-badge syft-badge-public">Public</span>'
        elif len(users) == 1:
            return f'<span class="syft-badge syft-badge-user">{users[0]}</span>'
        else:
            return f'<span class="syft-badge syft-badge-multiple">{len(users)} users</span>'
    
    # File status badges
    def file_badge(exists, url, file_type="file"):
        if exists:
            return '<span class="syft-badge syft-badge-available">✓ Available</span>'
        else:
            return '<span class="syft-badge syft-badge-unavailable">⚠ Not accessible</span>'
    
    # Generate metadata rows
    updated_row = ""
    if syft_obj.updated_at:
        updated_row = f'<div class="syft-meta-row"><span class="syft-meta-key">Updated</span><span class="syft-meta-value">{syft_obj.updated_at.strftime("%Y-%m-%d %H:%M UTC")}</span></div>'
    
    description_row = ""
    if syft_obj.description:
        description_row = f'<div class="syft-meta-row"><span class="syft-meta-key">Description</span><span class="syft-meta-value">{str(syft_obj.description)}</span></div>'
    
    # Show basic file information without buttons
    mock_info = ""
    if mock_file_exists:
        mock_path = syft_obj._get_local_file_path(syft_obj.mock)
        if mock_path:
            mock_info = f'<div class="syft-file-info">Path: {mock_path}</div>'
    
    private_info = ""
    if private_file_exists:
        private_path = syft_obj._get_local_file_path(syft_obj.private_url)
        if private_path:
            private_info = f'<div class="syft-file-info">Path: {private_path}</div>'
    
    # Create the complete HTML
    html = create_html_template(
        syft_obj=syft_obj,
        mock_file_exists=mock_file_exists,
        private_file_exists=private_file_exists,
        mock_info=mock_info,
        private_info=private_info,
        syftobject_yaml_path=syftobject_yaml_path,
        permission_badge=permission_badge,
        file_badge=file_badge,
        updated_row=updated_row,
        description_row=description_row,
        files_moved=files_moved,
        created_files=created_files,
        syftbox_available=syftbox_available
    )
    
    return html


def create_html_template(syft_obj, mock_file_exists, private_file_exists, mock_info, private_info, 
                        syftobject_yaml_path, permission_badge, file_badge, updated_row, 
                        description_row, files_moved, created_files, syftbox_available) -> str:
    """Create the HTML template with all the styling"""
    return f'''
    <style>
    .syft-object {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        border: 2px solid #e0e7ff;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }}
    .syft-header {{
        display: flex;
        align-items: center;
        margin-bottom: 20px;
        padding-bottom: 15px;
        border-bottom: 2px solid #e2e8f0;
    }}
    .syft-title {{
        font-size: 24px;
        font-weight: 700;
        color: #1e293b;
        margin: 0;
        flex-grow: 1;
    }}
    .syft-uid {{
        font-family: 'Monaco', 'Menlo', monospace;
        font-size: 12px;
        color: #64748b;
        background: #f1f5f9;
        padding: 4px 8px;
        border-radius: 6px;
    }}
    .syft-section {{
        margin-bottom: 20px;
    }}
    .syft-section-title {{
        font-size: 16px;
        font-weight: 600;
        color: #374151;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
    }}
    .syft-section-title::before {{
        content: '';
        width: 4px;
        height: 20px;
        background: #3b82f6;
        margin-right: 10px;
        border-radius: 2px;
    }}
    .syft-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
    }}
    .syft-files {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 15px;
    }}
    .syft-file-card {{
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }}
    .syft-file-header {{
        display: flex;
        justify-content: between;
        align-items: center;
        margin-bottom: 10px;
    }}
    .syft-file-type {{
        font-weight: 600;
        color: #374151;
    }}
    .syft-file-url {{
        font-family: 'Monaco', 'Menlo', monospace;
        font-size: 11px;
        color: #6b7280;
        word-break: break-all;
        margin: 8px 0;
        background: #f9fafb;
        padding: 6px 8px;
        border-radius: 4px;
    }}
    .syft-permissions {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 10px;
        margin-top: 10px;
    }}
    .syft-perm-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 12px;
        background: white;
        border-radius: 6px;
        border: 1px solid #e5e7eb;
    }}
    .syft-perm-label {{
        font-weight: 500;
        font-size: 13px;
        color: #374151;
    }}
    .syft-badge {{
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 500;
        text-transform: uppercase;
    }}
    .syft-badge-public {{
        background: #dcfce7;
        color: #166534;
    }}
    .syft-badge-user {{
        background: #dbeafe;
        color: #1d4ed8;
    }}
    .syft-badge-multiple {{
        background: #fef3c7;
        color: #92400e;
    }}
    .syft-badge-none {{
        background: #fee2e2;
        color: #dc2626;
    }}
    .syft-badge-available {{
        background: #dcfce7;
        color: #166534;
    }}
    .syft-badge-unavailable {{
        background: #fef3c7;
        color: #92400e;
    }}
    .syft-file-info {{
        font-family: 'Monaco', 'Menlo', monospace;
        font-size: 11px;
        color: #6b7280;
        margin-top: 8px;
        padding: 6px 8px;
        background: #f9fafb;
        border-radius: 4px;
        word-break: break-all;
    }}
    .syft-metadata-file {{
        border-left: 3px solid #8b5cf6;
    }}
    .syft-metadata-file .syft-file-type {{
        color: #8b5cf6;
    }}
    .syft-metadata {{
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 15px;
    }}
    .syft-meta-row {{
        display: flex;
        justify-content: space-between;
        padding: 6px 0;
        border-bottom: 1px solid #f3f4f6;
    }}
    .syft-meta-row:last-child {{
        border-bottom: none;
    }}
    .syft-meta-key {{
        font-weight: 500;
        color: #374151;
    }}
    .syft-meta-value {{
        color: #6b7280;
        font-family: 'Monaco', 'Menlo', monospace;
        font-size: 12px;
    }}
    .syft-file-ops {{
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 12px;
        margin-top: 10px;
    }}
    .syft-file-ops-title {{
        font-weight: 600;
        color: #374151;
        font-size: 13px;
        margin-bottom: 8px;
    }}
    .syft-file-ops-list {{
        font-size: 11px;
        color: #6b7280;
        font-family: 'Monaco', 'Menlo', monospace;
    }}
    </style>
    
    <div class="syft-object">
        <div class="syft-header">
            <h3 class="syft-title">🔐 {syft_obj.name or 'Syft Object'}</h3>
            <span class="syft-uid">{str(syft_obj.uid)[:8]}...</span>
        </div>
        
        <div class="syft-grid">
            <div class="syft-section">
                <div class="syft-section-title">📁 Files</div>
                <div class="syft-files">
                    <div class="syft-file-card">
                        <div class="syft-file-header">
                            <span class="syft-file-type">🔍 Mock (Demo)</span>
                            {file_badge(mock_file_exists, syft_obj.mock_url)}
                        </div>
                        <div class="syft-file-url">{syft_obj.mock_url}</div>
                        {mock_info}
                    </div>
                    
                    <div class="syft-file-card">
                        <div class="syft-file-header">
                            <span class="syft-file-type">🔐 Private (Real)</span>
                            {file_badge(private_file_exists, syft_obj.private_url)}
                        </div>
                        <div class="syft-file-url">{syft_obj.private_url}</div>
                        {private_info}
                    </div>
                    
                    <div class="syft-file-card syft-metadata-file">
                        <div class="syft-file-header">
                            <span class="syft-file-type">📋 Metadata (.syftobject.yaml)</span>
                            <span class="syft-badge syft-badge-available">✓ Saved</span>
                        </div>
                        <div class="syft-file-url">Object metadata and permissions</div>
                        {f'<div class="syft-file-info">Path: {syftobject_yaml_path}</div>' if syftobject_yaml_path else ''}
                    </div>
                </div>
            </div>
            
            <div class="syft-section">
                <div class="syft-section-title">🎯 Permissions</div>
                <div class="syft-permissions">
                    <div class="syft-perm-row">
                        <span class="syft-perm-label">Discovery</span>
                        {permission_badge(syft_obj.syftobject_permissions)}
                    </div>
                    <div class="syft-perm-row">
                        <span class="syft-perm-label">Mock Read</span>
                        {permission_badge(syft_obj.mock_permissions)}
                    </div>
                    <div class="syft-perm-row">
                        <span class="syft-perm-label">Mock Write</span>
                        {permission_badge(syft_obj.mock_write_permissions)}
                    </div>
                    <div class="syft-perm-row">
                        <span class="syft-perm-label">Private Read</span>
                        {permission_badge(syft_obj.private_permissions)}
                    </div>
                    <div class="syft-perm-row">
                        <span class="syft-perm-label">Private Write</span>
                        {permission_badge(syft_obj.private_write_permissions)}
                    </div>
                </div>
            </div>
        </div>
        
        <div class="syft-section">
            <div class="syft-section-title">📋 Metadata</div>
            <div class="syft-metadata">
                <div class="syft-meta-row">
                    <span class="syft-meta-key">Created</span>
                    <span class="syft-meta-value">{syft_obj.created_at.strftime('%Y-%m-%d %H:%M UTC') if syft_obj.created_at else 'Unknown'}</span>
                </div>
                {updated_row}
                {description_row}
                {render_custom_metadata(syft_obj)}
            </div>
            
            {render_file_operations(files_moved, created_files, syftbox_available)}
        </div>
    </div>
    '''


def render_custom_metadata(syft_obj: 'SyftObject') -> str:
    """Render custom metadata fields (excluding system fields)"""
    system_fields = {"_file_operations"}
    custom_metadata = {k: v for k, v in syft_obj.metadata.items() if k not in system_fields}
    
    if not custom_metadata:
        return ""
    
    html = ""
    for key, value in custom_metadata.items():
        html += f'''
        <div class="syft-meta-row">
            <span class="syft-meta-key">{key}</span>
            <span class="syft-meta-value">{str(value)}</span>
        </div>
        '''
    return html


def render_file_operations(files_moved, created_files, syftbox_available) -> str:
    """Render file operations section"""
    if not files_moved and not created_files:
        return ""
    
    status_icon = "✅" if syftbox_available else "⚠️"
    status_text = "SyftBox Integration Active" if syftbox_available else "SyftBox Not Available"
    
    ops_html = f'''
    <div class="syft-file-ops">
        <div class="syft-file-ops-title">{status_icon} File Operations - {status_text}</div>
        <div class="syft-file-ops-list">
    '''
    
    if files_moved:
        ops_html += "Moved to SyftBox locations:<br>"
        for move_info in files_moved:
            ops_html += f"  • {move_info}<br>"
    
    if created_files and not files_moved:
        ops_html += "Created in tmp/ directory:<br>"
        for file_path in created_files:
            ops_html += f"  • {file_path}<br>"
        if not syftbox_available:
            ops_html += "  (Install syft-core for SyftBox integration)<br>"
    
    ops_html += "</div></div>"
    return ops_html 