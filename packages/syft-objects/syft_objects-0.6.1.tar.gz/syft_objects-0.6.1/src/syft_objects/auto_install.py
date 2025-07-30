"""Auto-installation utilities for SyftBox integration."""

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None  # pragma: no cover


def get_syftbox_apps_path() -> Optional[Path]:
    """Get the SyftBox apps directory path.
    
    Returns:
        Path to SyftBox/apps directory or None if SyftBox not found
    """
    home = Path.home()
    syftbox_path = home / "SyftBox"
    
    if not syftbox_path.exists():
        return None
        
    apps_path = syftbox_path / "apps"
    return apps_path


def is_syftbox_app_installed() -> bool:
    """Check if syft-objects app is installed in SyftBox.
    
    Returns:
        True if syft-objects app directory exists in SyftBox/apps
    """
    apps_path = get_syftbox_apps_path()
    if not apps_path:
        return False
        
    syft_objects_app_path = apps_path / "syft-objects"
    return syft_objects_app_path.exists() and syft_objects_app_path.is_dir()


def clone_syftbox_app() -> bool:
    """Clone the syft-objects repository into SyftBox/apps.
    
    Returns:
        True if successful, False otherwise
    """
    apps_path = get_syftbox_apps_path()
    if not apps_path:
        print("Warning: SyftBox directory not found. Cannot auto-install syft-objects app.", file=sys.stderr)
        return False
    
    # Ensure apps directory exists
    apps_path.mkdir(parents=True, exist_ok=True)
    
    # Repository URL
    repo_url = "https://github.com/OpenMined/syft-objects.git"
    target_path = apps_path / "syft-objects"
    
    try:
        # Check if git is available
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        
        # Clone the repository
        result = subprocess.run(
            ["git", "clone", repo_url, str(target_path)],
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )
        
        if result.returncode == 0:
            return True
        else:
            print(f"❌ Failed to clone repository:", file=sys.stderr)
            print(f"Git error: {result.stderr}", file=sys.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Git clone timed out after 60 seconds", file=sys.stderr)
        return False
    except subprocess.CalledProcessError:
        print("❌ Git is not available. Cannot auto-install syft-objects app.", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("❌ Git is not installed. Cannot auto-install syft-objects app.", file=sys.stderr)
        return False
    except Exception as e:
        print(f"❌ Unexpected error during installation: {e}", file=sys.stderr)
        return False


def ensure_server_healthy(timeout_minutes: int = 5) -> bool:
    """Ensure syft-objects server is healthy by checking /health endpoint.
    
    This is the main function that implements the robust startup flow:
    1. Always check /health endpoint first
    2. If /health fails, check if syft-objects is installed in SyftBox
    3. If not installed, automatically reinstall it
    4. Wait until /health endpoint is available
    5. Then render the widget
    
    Args:
        timeout_minutes: Maximum time to wait in minutes
        
    Returns:
        True if server becomes healthy, False if timeout or critical failure
    """
    if not requests:
        print("❌ Cannot check server health - requests library not available")
        return False
    
    # Step 1: Always check /health endpoint first
    if _check_health_endpoint():
        return True
    
    # Step 2: /health failed - check if SyftBox app is installed
    if not get_syftbox_apps_path():
        print("❌ SyftBox not found - syft-objects requires SyftBox to run")
        return False
    
    if not is_syftbox_running():
        print("❌ SyftBox is not running - please start SyftBox first")
        return False
    
    # Step 3: If app not installed, automatically reinstall
    if not is_syftbox_app_installed():
        
        if not reinstall_syftbox_app(silent=True):
            print("❌ Failed to install syft-objects app")
            return False
        print("✅ Syft-objects app installed")
    
    # Step 4: Wait until /health endpoint is available
    
    return _wait_for_health_endpoint(timeout_minutes)


def _check_health_endpoint() -> bool:
    """Quick check of the /health endpoint"""
    try:
        port = _get_server_port()
        if port:
            response = requests.get(f"http://localhost:{port}/health", timeout=1)
            return response.status_code == 200
    except Exception:
        pass
    return False


def _get_server_port() -> Optional[int]:
    """Get the server port from config file"""
    try:
        config_file = Path.home() / ".syftbox" / "syft_objects.config"
        if config_file.exists():
            port_str = config_file.read_text().strip()
            if port_str.isdigit():
                return int(port_str)
    except Exception:
        pass
    return None


def _wait_for_health_endpoint(timeout_minutes: int) -> bool:
    """Wait for the /health endpoint to become available"""
    timeout_seconds = timeout_minutes * 60
    start_time = time.time()
    
    while time.time() - start_time < timeout_seconds:
        if _check_health_endpoint():
            port = _get_server_port() or 8004
            return True
        
        # Wait before checking again
        time.sleep(0.5)
    
    print(f"⏰ Server health check timeout after {timeout_minutes} minutes")
    return False


def wait_for_syft_objects_server(timeout_minutes: int = 5) -> bool:
    """Wait for syft-objects server to be available.
    
    DEPRECATED: Use ensure_server_healthy() instead.
    This function is kept for backward compatibility.
    
    Args:
        timeout_minutes: Maximum time to wait in minutes
        
    Returns:
        True if server becomes available, False if timeout
    """
    return ensure_server_healthy(timeout_minutes)


def start_syftbox_app(app_path: Path) -> bool:
    """Start the syft-objects app in SyftBox.
    
    Args:
        app_path: Path to the syft-objects app directory
        
    Returns:
        True if app started successfully
    """
    run_script = app_path / "run.sh"
    if not run_script.exists():
        print(f"❌ run.sh not found in {app_path}")
        return False
    
    try:
        print("🚀 Starting syft-objects server...")
        # Start the server in the background
        subprocess.Popen(
            ["bash", str(run_script)],
            cwd=str(app_path),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except Exception as e:
        print(f"❌ Failed to start syft-objects app: {e}")
        return False


def is_syftbox_running() -> bool:
    """Check if SyftBox daemon/app is running.
    
    Returns:
        True if SyftBox is running and accessible
    """
    try:
        # Import here to avoid circular imports
        from .client import get_syftbox_client
        
        syftbox_client = get_syftbox_client()
        if not syftbox_client:
            return False
        
        # Check if SyftBox app is running by trying to access it
        try:
            response = requests.get(str(syftbox_client.config.client_url), timeout=2)
            return response.status_code == 200 and "go1." in response.text
        except Exception:
            return False
            
    except Exception:
        return False


def reinstall_syftbox_app(silent=False) -> bool:
    """Reinstall syft-objects app in SyftBox by removing and re-cloning.
    
    Args:
        silent: If True, suppress non-error messages
        
    Returns:
        True if reinstallation was successful, False otherwise
    """
    # Check if SyftBox exists
    apps_path = get_syftbox_apps_path()
    if not apps_path:
        if not silent:
            print("❌ SyftBox directory not found. Cannot reinstall syft-objects app.")
        return False
    
    # Check if SyftBox is running
    if not is_syftbox_running():
        if not silent:
            print("❌ SyftBox is not running. Please start SyftBox before reinstalling.")
        return False
    
    syft_objects_app_path = apps_path / "syft-objects"
    
    try:
        # Remove existing app directory if it exists
        if syft_objects_app_path.exists():
            if not silent:
                print(f"🗑️  Removing existing syft-objects app from {syft_objects_app_path}")
            shutil.rmtree(syft_objects_app_path)
        
        # Clone fresh copy
        if not silent:
            print("🔄 Reinstalling syft-objects app...")
        
        success = clone_syftbox_app()
        
        if success and not silent:
            print("✅ Syft-objects app reinstalled successfully")
            print("📝 The app will automatically restart with the updated version")
        
        return success
        
    except Exception as e:
        if not silent:
            print(f"❌ Error during reinstallation: {e}")
        return False


def ensure_syftbox_app_installed(silent=True) -> bool:
    """Ensure syft-objects app is installed in SyftBox (but don't auto-start server).
    
    This function only ensures the app is INSTALLED, not running.
    The server should be started manually by running './run.sh' to avoid recursive loops.
    This prevents the import->start server->import->start server cycle.
    
    Args:
        silent: If True, only print messages for installation actions
        
    Returns:
        True if app is installed and available
    """
    # Check if SyftBox exists
    apps_path = get_syftbox_apps_path()
    if not apps_path:
        # SyftBox not found - this is normal for users not using SyftBox
        return False
    
    # Require SyftBox to be running
    if not is_syftbox_running():
        if not silent:
            print("❌ SyftBox is not running. Please start SyftBox before using syft-objects.")
            print("    Make sure SyftBox is installed and running, then try again.")
        return False
    
    app_installed = is_syftbox_app_installed()
    
    # If app is not installed, clone it (but don't start it)
    if not app_installed:
        if not silent:
            print("SyftBox detected but syft-objects app not found. Attempting auto-installation...")
        if not clone_syftbox_app():
            return False
        
        if not silent:
            print("✅ Syft-objects app installed successfully")
            print("📝 To start the server, run './run.sh' from the app directory")
        return True
    
    else:
        # App is already installed - that's all we need for import
        return True


if __name__ == "__main__":  # pragma: no cover
    # Allow running this module directly for testing
    if ensure_syftbox_app_installed():  # pragma: no cover
        print("syft-objects app is available in SyftBox")  # pragma: no cover
    else:  # pragma: no cover
        print("syft-objects app is not available")  # pragma: no cover 