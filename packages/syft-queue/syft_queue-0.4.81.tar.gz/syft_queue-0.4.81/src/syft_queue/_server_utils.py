"""Utilities for interacting with the SyftQueue server"""

import os
import json
from pathlib import Path
import subprocess
import time
import requests


def get_config_path():
    """Get the path to the syft-queue config file."""
    return Path.home() / ".syftbox" / "syft_queue.config"


def read_config():
    """Read the syft-queue configuration."""
    config_path = get_config_path()
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}


def get_syft_queue_url(endpoint=""):
    """Get the URL for the SyftQueue server"""
    # First check config file (updated by run.sh)
    config = read_config()
    port = config.get('port')
    
    if not port:
        # Fallback to old port file for backward compatibility
        port_file = Path.home() / ".syftbox" / "syft_queue.port"
        if port_file.exists():
            try:
                port = int(port_file.read_text().strip())
            except:
                port = None
    
    if not port:
        # Use environment variable or default
        port = int(os.environ.get("SYFTQUEUE_PORT", os.environ.get("SYFTBOX_ASSIGNED_PORT", 8005)))
    
    base_url = f"http://localhost:{port}"
    if endpoint:
        return f"{base_url}/{endpoint}"
    return base_url


def is_server_running():
    """Check if the SyftQueue server is running"""
    try:
        response = requests.get(get_syft_queue_url("health"), timeout=1)
        return response.status_code == 200
    except:
        return False


def is_syftbox_mode():
    """Check if we're running in SyftBox mode"""
    # Check if syft-queue is installed as a SyftBox app
    try:
        from .auto_install import is_syftbox_app_installed, get_syftbox_apps_path
        return get_syftbox_apps_path() is not None and is_syftbox_app_installed()
    except:
        return False


def ensure_server_healthy(max_retries=20, retry_delay=0.5):
    """Ensure the server is running and healthy."""
    for i in range(max_retries):
        if is_server_running():
            return True
        if i < max_retries - 1:
            time.sleep(retry_delay)
    return False


def start_server():
    """Start the SyftQueue server in the background"""
    if is_server_running():
        return True
    
    # Check if we're in SyftBox mode
    if is_syftbox_mode():
        # In SyftBox mode, the server should be managed by SyftBox
        # Just check if it's running without warning
        if not ensure_server_healthy(max_retries=5):
            return False
        return True
    
    # Fallback to old subprocess mode for non-SyftBox environments
    # Find the run.sh script
    queue_dir = Path(__file__).parent.parent.parent  # Go up to project root
    run_script = queue_dir / "run.sh"
    
    if not run_script.exists():
        # Try the syftbox_app location
        run_script = queue_dir / "syftbox_app" / "run.sh"
    
    if not run_script.exists():
        print(f"Error: run.sh not found at {run_script}")
        return False
    
    try:
        # Start the server in the background
        subprocess.Popen(
            ["bash", str(run_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(run_script.parent),
            env={**os.environ, "SYFTQUEUE_ENV": "standalone"}
        )
        
        # Wait for server to start
        if ensure_server_healthy():
            return True
        
        print("Warning: Server did not start within 10 seconds")
        return False
        
    except Exception as e:
        print(f"Error starting server: {e}")
        return False