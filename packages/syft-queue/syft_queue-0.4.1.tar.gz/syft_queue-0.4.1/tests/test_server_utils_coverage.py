"""
Focused tests for server_utils.py to achieve coverage
"""

import pytest
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open


def test_server_utils_config_functions():
    """Test config-related functions in server_utils"""
    from syft_queue import server_utils
    
    # Test get_config_path
    config_path = server_utils.get_config_path()
    expected_path = Path.home() / ".syftbox" / "syft_queue.config"
    assert config_path == expected_path
    
    # Test read_config - config exists and valid
    with patch('pathlib.Path.exists', return_value=True):
        with patch('builtins.open', mock_open(read_data='{"port": 8080, "host": "localhost"}')):
            config = server_utils.read_config()
            assert config == {"port": 8080, "host": "localhost"}
    
    # Test read_config - config exists but invalid JSON
    with patch('pathlib.Path.exists', return_value=True):
        with patch('builtins.open', side_effect=Exception("Invalid JSON")):
            config = server_utils.read_config()
            assert config == {}
    
    # Test read_config - config doesn't exist
    with patch('pathlib.Path.exists', return_value=False):
        config = server_utils.read_config()
        assert config == {}


def test_server_utils_url_generation():
    """Test URL generation functions"""
    from syft_queue import server_utils
    
    # Test with config file port
    with patch('syft_queue.server_utils.read_config', return_value={"port": 9000}):
        url = server_utils.get_syft_queue_url()
        assert "http://localhost:9000" == url
        
        # Test with endpoint
        url_with_endpoint = server_utils.get_syft_queue_url("health")
        assert url_with_endpoint == "http://localhost:9000/health"
    
    # Test with port file (backward compatibility)
    with patch('syft_queue.server_utils.read_config', return_value={}):
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.read_text', return_value='8888'):
                url = server_utils.get_syft_queue_url()
                assert "8888" in url
    
    # Test with port file read error
    with patch('syft_queue.server_utils.read_config', return_value={}):
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.read_text', side_effect=Exception("Read error")):
                url = server_utils.get_syft_queue_url()
                # Should fall back to environment or default
                assert "http://localhost:" in url
    
    # Test with environment variables
    with patch('syft_queue.server_utils.read_config', return_value={}):
        with patch('pathlib.Path.exists', return_value=False):
            with patch.dict('os.environ', {'SYFTQUEUE_PORT': '7777'}, clear=True):
                url = server_utils.get_syft_queue_url()
                assert "7777" in url
    
    # Test with SYFTBOX_ASSIGNED_PORT
    with patch('syft_queue.server_utils.read_config', return_value={}):
        with patch('pathlib.Path.exists', return_value=False):
            with patch.dict('os.environ', {'SYFTBOX_ASSIGNED_PORT': '6666'}, clear=True):
                url = server_utils.get_syft_queue_url()
                assert "6666" in url
    
    # Test default port
    with patch('syft_queue.server_utils.read_config', return_value={}):
        with patch('pathlib.Path.exists', return_value=False):
            with patch.dict('os.environ', {}, clear=True):
                url = server_utils.get_syft_queue_url()
                assert "8005" in url  # Default port


def test_server_utils_server_status():
    """Test server status checking"""
    from syft_queue import server_utils
    
    # Test server running (200 status)
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        assert server_utils.is_server_running() is True
    
    # Test server not running (non-200 status)
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        assert server_utils.is_server_running() is False
    
    # Test server check exception
    with patch('requests.get', side_effect=Exception("Connection error")):
        assert server_utils.is_server_running() is False


def test_server_utils_syftbox_mode():
    """Test SyftBox mode detection"""
    from syft_queue import server_utils
    
    # Test when both SyftBox and app are installed
    with patch('syft_queue.auto_install.is_syftbox_installed', return_value=True):
        with patch('syft_queue.auto_install.is_app_installed', return_value=True):
            assert server_utils.is_syftbox_mode() is True
    
    # Test when SyftBox is installed but app is not
    with patch('syft_queue.auto_install.is_syftbox_installed', return_value=True):
        with patch('syft_queue.auto_install.is_app_installed', return_value=False):
            assert server_utils.is_syftbox_mode() is False
    
    # Test when SyftBox is not installed
    with patch('syft_queue.auto_install.is_syftbox_installed', return_value=False):
        assert server_utils.is_syftbox_mode() is False
    
    # Test import error handling
    with patch('syft_queue.auto_install.is_syftbox_installed', side_effect=ImportError()):
        assert server_utils.is_syftbox_mode() is False


def test_server_utils_health_check():
    """Test server health checking"""
    from syft_queue import server_utils
    
    # Test server becomes healthy
    with patch('syft_queue.server_utils.is_server_running', side_effect=[False, False, True]):
        with patch('time.sleep'):
            assert server_utils.ensure_server_healthy() is True
    
    # Test server never becomes healthy
    with patch('syft_queue.server_utils.is_server_running', return_value=False):
        with patch('time.sleep'):
            assert server_utils.ensure_server_healthy() is False
    
    # Test server already healthy
    with patch('syft_queue.server_utils.is_server_running', return_value=True):
        assert server_utils.ensure_server_healthy() is True


def test_server_utils_start_server():
    """Test server starting functionality"""
    from syft_queue import server_utils
    
    # Test server already running
    with patch('syft_queue.server_utils.is_server_running', return_value=True):
        assert server_utils.start_server() is True
    
    # Test SyftBox mode - server becomes healthy
    with patch('syft_queue.server_utils.is_server_running', return_value=False):
        with patch('syft_queue.server_utils.is_syftbox_mode', return_value=True):
            with patch('syft_queue.server_utils.ensure_server_healthy', return_value=True):
                assert server_utils.start_server() is True
    
    # Test SyftBox mode - server doesn't become healthy
    with patch('syft_queue.server_utils.is_server_running', return_value=False):
        with patch('syft_queue.server_utils.is_syftbox_mode', return_value=True):
            with patch('syft_queue.server_utils.ensure_server_healthy', return_value=False):
                with patch('warnings.warn') as mock_warn:
                    assert server_utils.start_server() is False
                    mock_warn.assert_called_once()
    
    # Test non-SyftBox mode - run script not found
    with patch('syft_queue.server_utils.is_server_running', return_value=False):
        with patch('syft_queue.server_utils.is_syftbox_mode', return_value=False):
            with patch('pathlib.Path.exists', return_value=False):
                with patch('builtins.print') as mock_print:
                    assert server_utils.start_server() is False
                    mock_print.assert_called()
    
    # Test non-SyftBox mode - successful start
    with patch('syft_queue.server_utils.is_server_running', return_value=False):
        with patch('syft_queue.server_utils.is_syftbox_mode', return_value=False):
            with patch('pathlib.Path.exists', return_value=True):
                with patch('subprocess.Popen') as mock_popen:
                    with patch('syft_queue.server_utils.ensure_server_healthy', return_value=True):
                        assert server_utils.start_server() is True
                        mock_popen.assert_called_once()
    
    # Test non-SyftBox mode - server doesn't start properly
    with patch('syft_queue.server_utils.is_server_running', return_value=False):
        with patch('syft_queue.server_utils.is_syftbox_mode', return_value=False):
            with patch('pathlib.Path.exists', return_value=True):
                with patch('subprocess.Popen'):
                    with patch('syft_queue.server_utils.ensure_server_healthy', return_value=False):
                        with patch('builtins.print'):
                            assert server_utils.start_server() is False
    
    # Test non-SyftBox mode - exception during start
    with patch('syft_queue.server_utils.is_server_running', return_value=False):
        with patch('syft_queue.server_utils.is_syftbox_mode', return_value=False):
            with patch('pathlib.Path.exists', return_value=True):
                with patch('subprocess.Popen', side_effect=Exception("Failed to start")):
                    with patch('builtins.print') as mock_print:
                        assert server_utils.start_server() is False
                        mock_print.assert_called()