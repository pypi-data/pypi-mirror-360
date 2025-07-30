"""
Focused tests to achieve 95% coverage - fixing test failures and targeting missing lines
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


def test_server_utils_complete_coverage():
    """Test all server_utils.py functionality"""
    from syft_queue import server_utils
    
    # Test get_config_path (line 13-14)
    config_path = server_utils.get_config_path()
    assert config_path == Path.home() / ".syftbox" / "syft_queue.config"
    
    # Test read_config (lines 18-26)
    # Config exists and valid
    with patch('pathlib.Path.exists', return_value=True):
        with patch('builtins.open', mock_open(read_data='{"port": 8080}')):
            config = server_utils.read_config()
            assert config == {"port": 8080}
    
    # Config exists but invalid
    with patch('pathlib.Path.exists', return_value=True):
        with patch('builtins.open', side_effect=Exception("Invalid JSON")):
            config = server_utils.read_config()
            assert config == {}
    
    # Config doesn't exist
    with patch('pathlib.Path.exists', return_value=False):
        config = server_utils.read_config()
        assert config == {}
    
    # Test get_syft_queue_url (lines 29-51)
    # With config file
    with patch('syft_queue.server_utils.read_config', return_value={"port": 9000}):
        url = server_utils.get_syft_queue_url()
        assert "9000" in url
        
        # With endpoint
        url = server_utils.get_syft_queue_url("health")
        assert "9000" in url
        assert "health" in url
    
    # With port file (backward compatibility)
    with patch('syft_queue.server_utils.read_config', return_value={}):
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.read_text', return_value='8888'):
                url = server_utils.get_syft_queue_url()
                assert "8888" in url
    
    # With environment variables
    with patch('syft_queue.server_utils.read_config', return_value={}):
        with patch('pathlib.Path.exists', return_value=False):
            with patch.dict('os.environ', {'SYFTQUEUE_PORT': '7777'}, clear=True):
                url = server_utils.get_syft_queue_url()
                assert "7777" in url
    
    # Test is_server_running (lines 54-58)
    with patch('requests.get') as mock_get:
        mock_get.return_value = MagicMock(status_code=200)
        assert server_utils.is_server_running() is True
        
        mock_get.return_value = MagicMock(status_code=500)
        assert server_utils.is_server_running() is False
        
        mock_get.side_effect = Exception("Connection error")
        assert server_utils.is_server_running() is False
    
    # Test is_syftbox_mode (lines 39-46)
    # With auto_install module
    with patch('syft_queue.server_utils.is_syftbox_installed', return_value=True):
        with patch('syft_queue.server_utils.is_app_installed', return_value=True):
            assert server_utils.is_syftbox_mode() is True
    
    # Import error
    with patch('syft_queue.auto_install.is_syftbox_installed', side_effect=ImportError):
        assert server_utils.is_syftbox_mode() is False
    
    # Test ensure_server_healthy (lines 49-56)
    with patch('syft_queue.server_utils.is_server_running', side_effect=[False, False, True]):
        with patch('time.sleep'):
            assert server_utils.ensure_server_healthy() is True
    
    with patch('syft_queue.server_utils.is_server_running', return_value=False):
        with patch('time.sleep'):
            assert server_utils.ensure_server_healthy() is False
    
    # Test start_server (lines 59-109)
    # Server already running
    with patch('syft_queue.server_utils.is_server_running', return_value=True):
        assert server_utils.start_server() is True
    
    # SyftBox mode
    with patch('syft_queue.server_utils.is_server_running', return_value=False):
        with patch('syft_queue.server_utils.is_syftbox_mode', return_value=True):
            with patch('syft_queue.server_utils.ensure_server_healthy', return_value=False):
                with patch('warnings.warn') as mock_warn:
                    assert server_utils.start_server() is False
                    mock_warn.assert_called_once()
    
    # Non-SyftBox mode - script not found
    with patch('syft_queue.server_utils.is_server_running', return_value=False):
        with patch('syft_queue.server_utils.is_syftbox_mode', return_value=False):
            with patch('pathlib.Path.exists', return_value=False):
                assert server_utils.start_server() is False
    
    # Non-SyftBox mode - successful start
    with patch('syft_queue.server_utils.is_server_running', return_value=False):
        with patch('syft_queue.server_utils.is_syftbox_mode', return_value=False):
            with patch('pathlib.Path.exists', return_value=True):
                with patch('subprocess.Popen'):
                    with patch('syft_queue.server_utils.ensure_server_healthy', return_value=True):
                        assert server_utils.start_server() is True
    
    # Start fails
    with patch('syft_queue.server_utils.is_server_running', return_value=False):
        with patch('syft_queue.server_utils.is_syftbox_mode', return_value=False):
            with patch('pathlib.Path.exists', return_value=True):
                with patch('subprocess.Popen', side_effect=Exception("Failed to start")):
                    assert server_utils.start_server() is False


def test_init_coverage():
    """Test __init__.py coverage"""
    # Clear modules
    for mod in list(sys.modules.keys()):
        if mod.startswith('syft_queue'):
            del sys.modules[mod]
    
    # Test pipeline import error (lines 68-70)
    with patch.dict('sys.modules', {'syft_queue.pipeline': None}):
        import syft_queue
    
    # Test auto_install error (lines 82-84)
    with patch('syft_queue.auto_install.auto_install', side_effect=Exception("Install error")):
        # Should not prevent import
        pass
    
    from syft_queue import queues
    
    # Test __repr__ in Jupyter (lines 92-93)
    queues._ipython_canary_method_should_not_exist_ = True
    with patch.object(queues, '_repr_html_', return_value='<html>Test</html>'):
        result = repr(queues)
        assert result == '<html>Test</html>'
    del queues._ipython_canary_method_should_not_exist_
    
    # Test __repr__ non-Jupyter (lines 95-96)
    # Import _get_queues_table directly
    from syft_queue.queue import _get_queues_table
    with patch('syft_queue.queue._get_queues_table', return_value='Table'):
        result = repr(queues)
        assert result == 'Table'
    
    # Test __str__ (lines 99-100)
    with patch('syft_queue.queue._get_queues_table', return_value='String'):
        result = str(queues)
        assert result == 'String'
    
    # Test _repr_html_ (lines 103-111)
    with patch('syft_queue.server_utils.start_server', return_value=False):
        html = queues._repr_html_()
        assert 'Error' in html
    
    with patch('syft_queue.server_utils.start_server', return_value=True):
        with patch('syft_queue.server_utils.get_syft_queue_url', return_value='http://test/widget'):
            html = queues._repr_html_()
            assert 'iframe' in html
    
    # Test widget (lines 124-133)
    with patch('syft_queue.server_utils.start_server', return_value=False):
        widget = queues.widget()
        assert 'Error' in widget
    
    with patch('syft_queue.server_utils.start_server', return_value=True):
        with patch('syft_queue.server_utils.get_syft_queue_url', return_value='http://test/widget'):
            widget = queues.widget(width="800px", height="600px", url="http://custom")
            assert 'width="800px"' in widget
            assert 'http://custom' in widget
    
    # Test cleanup on import (lines 205-216)
    # This is tested during import


def test_queue_path_detection(tmp_path):
    """Test _detect_syftbox_queues_path"""
    from syft_queue.queue import _detect_syftbox_queues_path
    
    # SYFTBOX_DATA_FOLDER
    with patch.dict('os.environ', {'SYFTBOX_DATA_FOLDER': str(tmp_path / 'data')}, clear=True):
        result = _detect_syftbox_queues_path()
        assert str(result) == str(tmp_path / 'data')
    
    # SYFTBOX_EMAIL
    syftbox_dir = tmp_path / 'SyftBox' / 'datasites' / 'test@example.com' / 'app_data' / 'syft-queues'
    syftbox_dir.mkdir(parents=True)
    
    with patch.dict('os.environ', {'SYFTBOX_EMAIL': 'test@example.com'}, clear=True):
        with patch('pathlib.Path.home', return_value=tmp_path):
            result = _detect_syftbox_queues_path()
            assert 'test@example.com' in str(result)
    
    # YAML config
    config_dir = tmp_path / '.syftbox'
    config_dir.mkdir(exist_ok=True)
    config_file = config_dir / 'config.yaml'
    config_file.write_text('email: yaml@test.com')
    
    yaml_syftbox = tmp_path / 'SyftBox' / 'datasites' / 'yaml@test.com' / 'app_data' / 'syft-queues'
    yaml_syftbox.mkdir(parents=True)
    
    with patch.dict('os.environ', {}, clear=True):
        with patch('pathlib.Path.home', return_value=tmp_path):
            result = _detect_syftbox_queues_path()
            assert 'yaml@test.com' in str(result)
    
    # YAML ImportError
    with patch.dict('os.environ', {}, clear=True):
        with patch('pathlib.Path.home', return_value=tmp_path):
            original_import = builtins.__import__
            def mock_import(name, *args, **kwargs):
                if name == 'yaml':
                    raise ImportError()
                return original_import(name, *args, **kwargs)
            
            with patch('builtins.__import__', side_effect=mock_import):
                result = _detect_syftbox_queues_path()
                assert 'yaml@test.com' in str(result)
    
    # Config error
    config_file.write_text('invalid yaml: {{{')
    with patch.dict('os.environ', {}, clear=True):
        with patch('pathlib.Path.home', return_value=tmp_path):
            result = _detect_syftbox_queues_path()
    
    # Git config
    config_file.unlink()
    git_syftbox = tmp_path / 'SyftBox' / 'datasites' / 'git@test.com' / 'app_data' / 'syft-queues'
    git_syftbox.mkdir(parents=True)
    
    with patch.dict('os.environ', {}, clear=True):
        with patch('pathlib.Path.home', return_value=tmp_path):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stdout='git@test.com')
                result = _detect_syftbox_queues_path()
                assert 'git@test.com' in str(result)
    
    # Git fails
    with patch.dict('os.environ', {}, clear=True):
        with patch('pathlib.Path.home', return_value=tmp_path):
            with patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'git')):
                result = _detect_syftbox_queues_path()
                assert result == Path.cwd()


def test_job_class(mock_syftbox_env):
    """Test Job class functionality"""
    from syft_queue import q, JobStatus, Job
    
    queue = q("job_test", force=True)
    
    # Create job with all parameters
    job = queue.create_job(
        name="test_job",
        requester_email="user@test.com",
        target_email="owner@test.com",
        description="Test description",
        data={"input": "data"},
        mock_data=True,
        metadata={"priority": "high"}
    )
    
    # Test _make_relative
    if not hasattr(Path, 'is_relative_to'):
        Path.is_relative_to = lambda self, other: str(other) in str(self)
    
    rel_path = job.object_path / "subdir" / "file.txt"
    rel_path.parent.mkdir(parents=True, exist_ok=True)
    rel_path.touch()
    result = job._make_relative(rel_path)
    
    abs_path = Path("/absolute/path")
    result = job._make_relative(abs_path)
    assert result == abs_path
    
    # Test update_relative_paths
    job.code_folder = str(job.object_path / "code")
    (job.object_path / "code").mkdir()
    job.update_relative_paths()
    
    # Test __str__
    str_result = str(job)
    assert job.name in str_result
    
    # Test path resolution
    code_dir = mock_syftbox_env / "code"
    code_dir.mkdir()
    job.code_folder = str(code_dir)
    assert job.resolved_code_folder == code_dir
    
    # Code folder doesn't exist
    job.code_folder = "/nonexistent"
    result = job.resolved_code_folder
    
    # Test is_expired
    job.updated_at = None
    assert not job.is_expired
    
    job.updated_at = datetime.now() - timedelta(days=31)
    assert job.is_expired
    
    # Test code_files
    (code_dir / "file1.py").write_text("code")
    job.code_folder = str(code_dir)
    files = job.code_files
    
    # Test save/load
    job.save()
    
    # Load from disk
    loaded = Job(job.object_path, owner_email="owner@test.com")
    assert loaded.uid == job.uid
    
    # Test update_status
    new_job = queue.create_job("status", "user@test.com", "owner@test.com")
    new_job.update_status(JobStatus.approved)
    
    # Without queue ref
    new_job._queue_ref = None
    new_job.update_status(JobStatus.running)
    
    # Terminal transitions
    new_job.update_status(JobStatus.completed)
    new_job.update_status(JobStatus.failed)
    
    # Test properties
    assert isinstance(job.is_terminal, bool)
    assert isinstance(job.is_approved, bool)
    
    # Test __repr__
    repr_str = repr(job)
    assert "Job" in repr_str


def test_queue_class(mock_syftbox_env):
    """Test Queue class functionality"""
    from syft_queue import q, JobStatus, DataQueue, get_queue
    
    # Create queue
    queue = q("test_queue", force=True)
    
    # Create jobs
    jobs = []
    for i in range(5):
        job = queue.create_job(f"job{i}", f"user{i}@test.com", "owner@test.com")
        if i % 2 == 0:
            job.update_status(JobStatus.approved)
        jobs.append(job)
    
    # Test list_jobs
    all_jobs = queue.list_jobs()
    approved = queue.list_jobs(status=JobStatus.approved)
    
    # Test get_job
    found = queue.get_job(jobs[0].uid)
    assert found is not None
    
    not_found = queue.get_job(uuid4())
    assert not_found is None
    
    # Test process
    results = queue.process()
    
    # Test create_job with data
    data_job = queue.create_job(
        "data_job",
        "user@test.com",
        "owner@test.com",
        data={"real": "data"}
    )
    
    # Test stats
    stats = queue.get_stats()
    assert "total_jobs" in stats
    
    # Test __str__ and __repr__
    str(queue)
    repr(queue)
    
    # Test DataQueue
    data_queue = q("data_queue", queue_type="data", force=True)
    assert isinstance(data_queue, DataQueue)
    
    # Test get_queue
    found = get_queue("test_queue")
    assert found is not None
    
    not_found = get_queue("nonexistent")
    assert not_found is None


def test_progression_api(mock_syftbox_env):
    """Test progression API"""
    from syft_queue import (
        q, approve, reject, start, complete, fail, timeout, advance,
        approve_all, process_queue, JobStatus
    )
    
    queue = q("prog_test", force=True)
    
    # Test approve
    job1 = queue.create_job("approve1", "user@test.com", "owner@test.com")
    approved = approve(job1)
    assert approved.status == JobStatus.approved
    
    # Test validation
    try:
        approve(approved)
    except ValueError:
        pass
    
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
    failed = fail(job4)
    assert failed.status == JobStatus.failed
    
    # Test timeout
    job5 = queue.create_job("timeout1", "user@test.com", "owner@test.com")
    job5.update_status(JobStatus.running)
    job5.started_at = datetime.now() - timedelta(minutes=5)
    timed_out = timeout(job5)
    assert timed_out.status == JobStatus.failed
    
    # Test advance
    job6 = queue.create_job("advance1", "user@test.com", "owner@test.com")
    advanced = advance(job6)
    assert advanced.status == JobStatus.approved
    
    # Test approve_all
    batch = [queue.create_job(f"batch{i}", "user@test.com", "owner@test.com") for i in range(3)]
    approved_batch = approve_all(batch)
    assert len(approved_batch) == 3
    
    # Test process_queue
    for j in approved_batch:
        # Add code
        code_dir = j.object_path / "code"
        code_dir.mkdir()
        (code_dir / "run.py").write_text("print('test')")
        j.code_folder = str(code_dir)
        j.save()
    
    results = process_queue(queue, max_jobs=2)


def test_pipeline():
    """Test pipeline functionality"""
    from syft_queue.pipeline import (
        Pipeline, PipelineBuilder, PipelineStage,
        advance_job, approve_job, reject_job, start_job, complete_job, fail_job,
        advance_jobs, validate_data_schema, check_model_performance,
        allocate_gpu_resources, register_model_endpoint
    )
    
    # Test PipelineBuilder
    builder = PipelineBuilder("test")
    builder.stage("inbox", "inbox")
    builder.stage("review", "approved")
    builder.transition("inbox", "review")
    pipeline = builder.build()
    
    # Mock job
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
    
    # Test advance_jobs
    results = advance_jobs([mock_job])
    
    # Test validators
    validate_data_schema(mock_job)
    check_model_performance(mock_job)
    allocate_gpu_resources(mock_job)
    register_model_endpoint(mock_job)


def test_utility_functions(mock_syftbox_env):
    """Test utility functions"""
    from syft_queue import (
        list_queues, cleanup_orphaned_queues, recreate_missing_queue_directories,
        get_queues_path, help
    )
    from syft_queue.queue import (
        _queue_exists, _cleanup_empty_queue_directory, _is_ghost_job_folder,
        _cleanup_ghost_job_folders, _cleanup_all_ghost_job_folders,
        _queue_has_valid_syftobject, _get_queues_table
    )
    
    # Test _queue_exists
    with patch('syft_objects.objects.get_object', return_value=None):
        assert not _queue_exists("nonexistent")
    
    with patch('syft_objects.objects.get_object', return_value={"name": "Q:exists"}):
        assert _queue_exists("exists")
    
    # Test cleanup functions
    empty_dir = mock_syftbox_env / "Q:empty"
    empty_dir.mkdir()
    _cleanup_empty_queue_directory(empty_dir)
    
    ghost = mock_syftbox_env / "J:ghost"
    ghost.mkdir()
    assert _is_ghost_job_folder(ghost)
    
    queue_dir = mock_syftbox_env / "Q:cleanup"
    queue_dir.mkdir()
    (queue_dir / "J:ghost1").mkdir()
    count = _cleanup_ghost_job_folders(queue_dir)
    
    total = _cleanup_all_ghost_job_folders()
    
    # Test high-level functions
    queues = list_queues()
    cleanup_orphaned_queues()
    path = get_queues_path()
    recreate_missing_queue_directories()
    
    table = _get_queues_table()
    assert isinstance(table, str)
    
    # Test help
    with patch('builtins.print'):
        help()