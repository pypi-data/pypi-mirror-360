"""
Auto-installation module for syft-queue SyftBox app.

This module handles automatic installation of the syft-queue server
as a SyftBox app when syft-queue is imported.
"""

import os
import shutil
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
import warnings


def get_syftbox_path() -> Optional[Path]:
    """Get the SyftBox installation path."""
    syftbox_path = Path.home() / "SyftBox"
    if syftbox_path.exists() and syftbox_path.is_dir():
        return syftbox_path
    return None


def get_syftbox_apps_path() -> Optional[Path]:
    """Get the SyftBox apps directory path."""
    syftbox_path = get_syftbox_path()
    if syftbox_path:
        apps_path = syftbox_path / "apps"
        if apps_path.exists():
            return apps_path
    return None


def get_package_app_path() -> Path:
    """Get the path to the syftbox_app directory in the package."""
    return Path(__file__).parent.parent.parent / "syftbox_app"


def get_config_path() -> Path:
    """Get the path to the syft-queue config file."""
    config_dir = Path.home() / ".syftbox"
    config_dir.mkdir(exist_ok=True)
    return config_dir / "syft_queue.config"


def read_config() -> Dict[str, Any]:
    """Read the syft-queue configuration."""
    config_path = get_config_path()
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}


def get_server_port() -> int:
    """Get the configured server port."""
    config = read_config()
    return config.get('port', int(os.environ.get('SYFTQUEUE_PORT', 8005)))


def is_syftbox_installed() -> bool:
    """Check if SyftBox is installed."""
    return get_syftbox_path() is not None


def is_app_installed() -> bool:
    """Check if syft-queue is installed as a SyftBox app."""
    apps_path = get_syftbox_apps_path()
    if apps_path:
        app_path = apps_path / "syft-queue"
        return app_path.exists() and (app_path / "run.sh").exists()
    return False


def copy_app_to_syftbox(force: bool = False, update: bool = True) -> bool:
    """Copy the syft-queue app to SyftBox apps directory."""
    apps_path = get_syftbox_apps_path()
    if not apps_path:
        return False
    
    source_path = get_package_app_path()
    if not source_path.exists():
        warnings.warn(f"SyftBox app source not found at {source_path}")
        return False
    
    dest_path = apps_path / "syft-queue"
    
    # Check if already installed and not forcing or updating
    if dest_path.exists() and not force and not update:
        return True
    
    try:
        # Remove existing if forcing, or update key files if updating
        if dest_path.exists() and force:
            shutil.rmtree(dest_path)
        elif dest_path.exists() and update:
            # Update key files only
            key_files = ["run.sh", "requirements.txt", "backend/server.py"]
            for file_path in key_files:
                src_file = source_path / file_path
                dest_file = dest_path / file_path
                if src_file.exists():
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_file, dest_file)
        
        # Copy the app
        shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
        
        # Make run.sh executable
        run_script = dest_path / "run.sh"
        if run_script.exists():
            run_script.chmod(0o755)
        
        return True
    except Exception as e:
        warnings.warn(f"Failed to install syft-queue as SyftBox app: {e}")
        return False


def ensure_syftbox_app_installed() -> bool:
    """Ensure syft-queue is installed as a SyftBox app if SyftBox is available."""
    if not is_syftbox_installed():
        return False
    
    if is_app_installed():
        # Always update existing installations
        return copy_app_to_syftbox(update=True)
    
    return copy_app_to_syftbox()


def show_startup_banner():
    """Show startup banner with SyftBox integration status."""
    if is_syftbox_installed():
        if is_app_installed():
            config = read_config()
            if config.get('syftbox_mode'):
                print("✓ SyftQueue server running as SyftBox app")
            else:
                print("✓ SyftQueue ready (SyftBox app available)")
        else:
            print("⚠️  SyftBox detected but syft-queue app not installed")
            print("   Run: syft_queue.auto_install.copy_app_to_syftbox()")
    else:
        # Silent when not in SyftBox mode
        pass


# Auto-install on import
def auto_install():
    """Perform auto-installation tasks."""
    try:
        ensure_syftbox_app_installed()
    except Exception:
        # Silently fail - don't break imports
        pass