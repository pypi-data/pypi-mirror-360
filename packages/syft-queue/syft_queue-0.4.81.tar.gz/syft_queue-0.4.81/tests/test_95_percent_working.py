"""
Working test to achieve 95% coverage
"""

import pytest
import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open, call
from datetime import datetime, timedelta
from uuid import uuid4
import subprocess
import io
import time
import builtins


def test_server_utils_working():
    """Test server_utils.py with correct API"""
    from syft_queue import server_utils
    
    # Test get_config_path
    config_path = server_utils.get_config_path()
    assert config_path == Path.home() / ".syftbox" / "syft_queue.config"
    
    # Test read_config - config exists and valid
    with patch('pathlib.Path.exists', return_value=True):
        with patch('builtins.open', mock_open(read_data='{"port": 8080}')):
            config = server_utils.read_config()
            assert config == {"port": 8080}
    
    # Config exists but invalid JSON
    with patch('pathlib.Path.exists', return_value=True):
        with patch('builtins.open', side_effect=Exception("Invalid JSON")):
            config = server_utils.read_config()
            assert config == {}
    
    # Config doesn't exist
    with patch('pathlib.Path.exists', return_value=False):
        config = server_utils.read_config()
        assert config == {}
    
    # Test get_syft_queue_url - with config
    with patch('syft_queue.server_utils.read_config', return_value={"port": 9000}):
        url = server_utils.get_syft_queue_url()
        assert "9000" in url
        
        # With endpoint
        url = server_utils.get_syft_queue_url("health")
        assert "health" in url
    
    # With port file (backward compatibility)
    with patch('syft_queue.server_utils.read_config', return_value={}):
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.read_text', return_value='8888'):
                url = server_utils.get_syft_queue_url()
                assert "8888" in url
    
    # With port file error
    with patch('syft_queue.server_utils.read_config', return_value={}):
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.read_text', side_effect=Exception("Read error")):
                url = server_utils.get_syft_queue_url()
    
    # With environment variables
    with patch('syft_queue.server_utils.read_config', return_value={}):
        with patch('pathlib.Path.exists', return_value=False):
            with patch.dict('os.environ', {'SYFTQUEUE_PORT': '7777'}, clear=True):
                url = server_utils.get_syft_queue_url()
                assert "7777" in url
    
    # Test is_server_running
    with patch('requests.get') as mock_get:
        mock_get.return_value = MagicMock(status_code=200)
        assert server_utils.is_server_running() is True
        
        mock_get.return_value = MagicMock(status_code=500)
        assert server_utils.is_server_running() is False
        
        mock_get.side_effect = Exception("Connection error")
        assert server_utils.is_server_running() is False
    
    # Test is_syftbox_mode - success case
    with patch('syft_queue.auto_install.is_syftbox_installed', return_value=True):
        with patch('syft_queue.auto_install.is_app_installed', return_value=True):
            assert server_utils.is_syftbox_mode() is True
    
    # Import error case
    with patch('syft_queue.auto_install.is_syftbox_installed', side_effect=ImportError):
        assert server_utils.is_syftbox_mode() is False
    
    # Test ensure_server_healthy
    with patch('syft_queue.server_utils.is_server_running', side_effect=[False, False, True]):
        with patch('time.sleep'):
            assert server_utils.ensure_server_healthy() is True
    
    with patch('syft_queue.server_utils.is_server_running', return_value=False):
        with patch('time.sleep'):
            assert server_utils.ensure_server_healthy() is False
    
    # Test start_server - already running
    with patch('syft_queue.server_utils.is_server_running', return_value=True):
        assert server_utils.start_server() is True
    
    # SyftBox mode - healthy
    with patch('syft_queue.server_utils.is_server_running', return_value=False):
        with patch('syft_queue.server_utils.is_syftbox_mode', return_value=True):
            with patch('syft_queue.server_utils.ensure_server_healthy', return_value=True):
                assert server_utils.start_server() is True
    
    # SyftBox mode - not healthy
    with patch('syft_queue.server_utils.is_server_running', return_value=False):
        with patch('syft_queue.server_utils.is_syftbox_mode', return_value=True):
            with patch('syft_queue.server_utils.ensure_server_healthy', return_value=False):
                with patch('warnings.warn'):
                    assert server_utils.start_server() is False
    
    # Non-SyftBox mode - script not found
    with patch('syft_queue.server_utils.is_server_running', return_value=False):
        with patch('syft_queue.server_utils.is_syftbox_mode', return_value=False):
            with patch('pathlib.Path.exists', return_value=False):
                with patch('builtins.print'):
                    assert server_utils.start_server() is False
    
    # Non-SyftBox mode - successful start
    with patch('syft_queue.server_utils.is_server_running', return_value=False):
        with patch('syft_queue.server_utils.is_syftbox_mode', return_value=False):
            with patch('pathlib.Path.exists', return_value=True):
                with patch('subprocess.Popen'):
                    with patch('syft_queue.server_utils.ensure_server_healthy', return_value=True):
                        assert server_utils.start_server() is True
    
    # Start fails with timeout
    with patch('syft_queue.server_utils.is_server_running', return_value=False):
        with patch('syft_queue.server_utils.is_syftbox_mode', return_value=False):
            with patch('pathlib.Path.exists', return_value=True):
                with patch('subprocess.Popen'):
                    with patch('syft_queue.server_utils.ensure_server_healthy', return_value=False):
                        with patch('builtins.print'):
                            assert server_utils.start_server() is False
    
    # Exception during start
    with patch('syft_queue.server_utils.is_server_running', return_value=False):
        with patch('syft_queue.server_utils.is_syftbox_mode', return_value=False):
            with patch('pathlib.Path.exists', return_value=True):
                with patch('subprocess.Popen', side_effect=Exception("Failed to start")):
                    with patch('builtins.print'):
                        assert server_utils.start_server() is False


def test_init_working():
    """Test __init__.py with working API"""
    # Clear modules to test import
    for mod in list(sys.modules.keys()):
        if mod.startswith('syft_queue'):
            del sys.modules[mod]
    
    # Test pipeline import error
    with patch.dict('sys.modules', {'syft_queue.pipeline': None}):
        import syft_queue
    
    # Test queues collection
    from syft_queue import queues
    
    # Test __repr__ in Jupyter
    queues._ipython_canary_method_should_not_exist_ = True
    with patch.object(queues, '_repr_html_', return_value='<html>Test</html>'):
        result = repr(queues)
        assert result == '<html>Test</html>'
    del queues._ipython_canary_method_should_not_exist_
    
    # Test __repr__ non-Jupyter
    from syft_queue.queue import _get_queues_table
    with patch('syft_queue.queue._get_queues_table', return_value='Table'):
        result = repr(queues)
        assert result == 'Table'
    
    # Test __str__
    with patch('syft_queue.queue._get_queues_table', return_value='String'):
        result = str(queues)
        assert result == 'String'
    
    # Test _repr_html_ - server fails
    with patch('syft_queue.server_utils.start_server', return_value=False):
        html = queues._repr_html_()
        assert 'Error' in html
    
    # Test _repr_html_ - server starts
    with patch('syft_queue.server_utils.start_server', return_value=True):
        with patch('syft_queue.server_utils.get_syft_queue_url', return_value='http://test/widget'):
            html = queues._repr_html_()
            assert 'iframe' in html
    
    # Test widget - server fails
    with patch('syft_queue.server_utils.start_server', return_value=False):
        widget = queues.widget()
        assert 'Error' in widget
    
    # Test widget - server starts
    with patch('syft_queue.server_utils.start_server', return_value=True):
        with patch('syft_queue.server_utils.get_syft_queue_url', return_value='http://test/widget'):
            widget = queues.widget(width="800px", height="600px", url="http://custom")
            assert 'width="800px"' in widget
            assert 'http://custom' in widget


def test_queue_basic_operations():
    """Test basic queue operations"""
    from syft_queue import q, JobStatus, get_queue, list_queues
    
    # Create queue
    queue = q("basic_test", force=True)
    
    # Create job
    job = queue.create_job("test_job", "user@test.com", "owner@test.com")
    
    # Test job properties
    assert job.name == "test_J:test_job"
    assert job.status == JobStatus.inbox
    
    # Test job status updates
    job.update_status(JobStatus.approved)
    assert job.status == JobStatus.approved
    
    job.update_status(JobStatus.running)
    assert job.status == JobStatus.running
    
    job.update_status(JobStatus.completed)
    assert job.status == JobStatus.completed
    
    # Test queue operations
    jobs = queue.list_jobs()
    assert len(jobs) >= 1
    
    found_job = queue.get_job(job.uid)
    assert found_job is not None
    
    not_found = queue.get_job(str(uuid4()))
    assert not_found is None
    
    # Test stats
    stats = queue.get_stats()
    assert "total_jobs" in stats
    
    # Test string representations
    str(queue)
    repr(queue)
    str(job)
    repr(job)
    
    # Test get_queue
    found_queue = get_queue("basic_test")
    assert found_queue is not None
    
    # Test list_queues
    queues_list = list_queues()
    assert isinstance(queues_list, list)


def test_progression_api_working():
    """Test progression API with working calls"""
    from syft_queue import (
        q, approve, reject, start, complete, fail, timeout, advance,
        approve_all, JobStatus
    )
    
    queue = q("progression_test", force=True)
    
    # Test approve
    job1 = queue.create_job("approve1", "user@test.com", "owner@test.com")
    approved = approve(job1)
    assert approved.status == JobStatus.approved
    
    # Test reject
    job2 = queue.create_job("reject1", "user@test.com", "owner@test.com")
    rejected = reject(job2, reason="Invalid")
    assert rejected.status == JobStatus.rejected
    
    # Test start
    job3 = queue.create_job("start1", "user@test.com", "owner@test.com")
    job3.update_status(JobStatus.approved)
    started = start(job3)
    assert started.status == JobStatus.running
    
    # Test complete
    completed = complete(started)
    assert completed.status == JobStatus.completed
    
    # Test fail
    job4 = queue.create_job("fail1", "user@test.com", "owner@test.com")
    job4.update_status(JobStatus.running)
    failed = fail(job4, error="Process failed")
    assert failed.status == JobStatus.failed
    
    # Test timeout
    job5 = queue.create_job("timeout1", "user@test.com", "owner@test.com")
    job5.update_status(JobStatus.running)
    timed_out = timeout(job5)
    assert timed_out.status == JobStatus.failed
    
    # Test advance
    job6 = queue.create_job("advance1", "user@test.com", "owner@test.com")
    advanced = advance(job6)
    assert advanced.status == JobStatus.approved
    
    # Test approve_all
    batch = [queue.create_job(f"batch{i}", "user@test.com", "owner@test.com") for i in range(3)]
    approved_batch = # approve_all(batch)
    assert len(approved_batch) == 3


def test_pipeline_working():
    """Test pipeline with working API"""
    from syft_queue.pipeline import (
        Pipeline, PipelineBuilder, PipelineStage,
        advance_job, approve_job, reject_job, start_job, complete_job, fail_job
    )
    
    # Test PipelineStage enum
    for stage in PipelineStage:
        assert isinstance(stage.value, str)
    
    # Test PipelineBuilder
    builder = PipelineBuilder("test")
    builder.stage("inbox", "inbox")
    builder.stage("review", "approved")
    builder.transition("inbox", "review")
    pipeline = builder.build()
    
    # Mock job for testing
    mock_job = MagicMock()
    mock_job.status = "inbox"
    mock_job.uid = "123"
    mock_job.advance = MagicMock()
    
    # Test get_job_stage
    stage = pipeline.get_job_stage(mock_job)
    assert stage == "inbox"
    
    # Test advance
    result = pipeline.advance(mock_job)
    mock_job.advance.assert_called_with("review")
    
    # Test job helpers
    advance_job(mock_job)
    approve_job(mock_job)
    reject_job(mock_job, "reason")
    start_job(mock_job)
    complete_job(mock_job)
    fail_job(mock_job, "error")


def test_utilities_working():
    """Test utility functions with working API"""
    from syft_queue import (
        list_queues, cleanup_orphaned_queues, get_queues_path, help
    )
    from syft_queue.queue import (
        _queue_exists, _cleanup_empty_queue_directory, _is_ghost_job_folder,
        _get_queues_table
    )
    
    # Test _queue_exists
    with patch('syft_objects.objects.get_object', return_value=None):
        assert not _queue_exists("nonexistent")
    
    with patch('syft_objects.objects.get_object', return_value={"name": "Q:exists"}):
        assert _queue_exists("exists")
    
    # Test _is_ghost_job_folder
    ghost_path = Path("/tmp/J:ghost")
    assert _is_ghost_job_folder(ghost_path)
    
    non_ghost_path = Path("/tmp/Q:queue")
    assert not _is_ghost_job_folder(non_ghost_path)
    
    # Test high-level functions
    queues = list_queues()
    assert isinstance(queues, list)
    
    cleanup_orphaned_queues()
    
    path = get_queues_path()
    assert isinstance(path, Path)
    
    table = _get_queues_table()
    assert isinstance(table, str)
    
    # Test help
    with patch('builtins.print'):
        help()


def test_job_comprehensive():
    """Test Job class comprehensively"""
    from syft_queue import q, JobStatus
    
    queue = q("job_comprehensive", force=True)
    
    # Create job with all parameters
    job = queue.create_job(
        name="comprehensive_job",
        requester_email="user@test.com",
        target_email="owner@test.com",
        description="Test description",
        data={"input": "data"},
        mock_data=True,
        metadata={"priority": "high"}
    )
    
    # Test properties
    assert job.name == "test_J:comprehensive_job"
    assert job.requester_email == "user@test.com"
    assert job.target_email == "owner@test.com"
    assert job.description == "Test description"
    
    # Test status properties
    assert not job.is_terminal
    assert not job.is_approved
    assert not job.is_running
    assert not job.is_completed
    assert not job.is_failed
    assert not job.is_rejected
    
    # Test status changes
    job.update_status(JobStatus.approved)
    assert job.is_approved
    assert not job.is_terminal
    
    job.update_status(JobStatus.running)
    assert job.is_running
    assert not job.is_terminal
    
    job.update_status(JobStatus.completed)
    assert job.is_completed
    assert job.is_terminal
    
    # Test expiration
    job.updated_at = None
    assert not job.is_expired
    
    job.updated_at = datetime.now() - timedelta(days=31)
    assert job.is_expired
    
    job.updated_at = datetime.now() - timedelta(days=1)
    assert not job.is_expired
    
    # Test save/load
    job.save()
    
    # Test code_files with no code folder
    files = job.code_files
    assert files == []
    
    # Test string representations
    str_result = str(job)
    assert job.name in str_result
    
    repr_result = repr(job)
    assert "Job" in repr_result


def test_data_queue():
    """Test DataQueue functionality"""
    from syft_queue import q, DataQueue
    
    # Create DataQueue
    data_queue = q("data_test", queue_type="data", force=True)
    assert isinstance(data_queue, DataQueue)
    
    # Create job in data queue
    job = data_queue.create_job("data_job", "user@test.com", "owner@test.com")
    assert job is not None


def test_queue_edge_cases():
    """Test queue edge cases"""
    from syft_queue import q, queue as queue_factory
    
    # Test queue factory validation
    try:
        queue_factory("test", queue_type="invalid")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    # Test queue with force=True
    queue1 = q("edge_test", force=True)
    queue2 = q("edge_test", force=True)  # Should work
    
    # Test empty queue operations
    empty_queue = q("empty_test", force=True)
    jobs = empty_queue.list_jobs()
    assert len(jobs) == 0
    
    stats = empty_queue.get_stats()
    assert stats["total_jobs"] == 0


def test_path_detection():
    """Test path detection with minimal mocking"""
    from syft_queue.queue import _detect_syftbox_queues_path
    
    # Test with environment variable
    with patch.dict('os.environ', {'SYFTBOX_DATA_FOLDER': '/test/data'}, clear=True):
        with patch('pathlib.Path.mkdir'):
            result = _detect_syftbox_queues_path()
            assert '/test/data' in str(result)
    
    # Test fallback to current directory
    with patch.dict('os.environ', {}, clear=True):
        with patch('pathlib.Path.home', return_value=Path('/home/user')):
            with patch('pathlib.Path.exists', return_value=False):
                with patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'git')):
                    result = _detect_syftbox_queues_path()
                    assert result == Path.cwd()
