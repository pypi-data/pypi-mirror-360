"""
Comprehensive test file targeting 95% code coverage
"""

import pytest
import os
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime, timedelta
from uuid import uuid4
import subprocess
import sys


def test_queue_module_comprehensive():
    """Test comprehensive queue module functionality"""
    from syft_queue import q, JobStatus, DataQueue, CodeQueue, BaseQueue
    
    # Test different queue types
    code_queue = q("comprehensive_code", queue_type="code", force=True)
    data_queue = q("comprehensive_data", queue_type="data", force=True)
    
    # Test queue type verification
    assert isinstance(code_queue, CodeQueue)
    assert isinstance(data_queue, DataQueue)
    assert isinstance(code_queue, BaseQueue)
    assert isinstance(data_queue, BaseQueue)
    
    # Test queue creation with all parameters
    job = code_queue.create_job(
        "comprehensive_job",
        "user@test.com",
        "target@test.com",
        description="Comprehensive test job",
        data={"input": [1, 2, 3], "config": {"param": "value"}},
        metadata={"priority": "high", "environment": "test"},
        mock_data=False
    )
    
    # Test job properties
    assert job.name.startswith("test_J:")
    assert job.requester_email == "user@test.com"
    assert job.target_email == "target@test.com"
    assert job.description == "Comprehensive test job"
    assert job.data["input"] == [1, 2, 3]
    assert job.metadata["priority"] == "high"
    
    # Test job status progression
    assert job.status == JobStatus.inbox
    assert not job.is_terminal
    
    job.update_status(JobStatus.approved)
    assert job.is_approved
    assert not job.is_terminal
    
    job.update_status(JobStatus.running)
    assert job.is_running
    assert not job.is_terminal
    
    job.update_status(JobStatus.completed)
    assert job.is_completed
    assert job.is_terminal
    
    # Test queue operations
    all_jobs = code_queue.list_jobs()
    assert len(all_jobs) >= 1
    
    found_job = code_queue.get_job(job.uid)
    assert found_job.uid == job.uid
    
    # Test queue statistics
    stats = code_queue.get_stats()
    assert "total_jobs" in stats
    assert "inbox" in stats
    assert "approved" in stats
    assert "running" in stats
    assert "completed" in stats
    assert "failed" in stats
    assert "rejected" in stats
    
    # Test queue refresh
    code_queue.refresh_stats()
    new_stats = code_queue.get_stats()
    assert new_stats["total_jobs"] == stats["total_jobs"]


def test_job_path_operations():
    """Test job path operations comprehensively"""
    from syft_queue import q
    
    queue = q("path_operations", force=True)
    job = queue.create_job("path_job", "user@test.com", "owner@test.com")
    
    # Test code folder resolution
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Test with absolute path
        code_dir = temp_path / "code"
        code_dir.mkdir()
        job.code_folder = str(code_dir)
        assert job.resolved_code_folder == code_dir
        
        # Test with relative path
        job.code_folder = None
        job.code_folder_relative = "rel_code"
        rel_code_dir = job.object_path / "rel_code"
        rel_code_dir.mkdir(parents=True, exist_ok=True)
        assert job.resolved_code_folder == rel_code_dir
        
        # Test with fallback
        job.code_folder_relative = None
        job.code_folder_absolute_fallback = str(code_dir)
        assert job.resolved_code_folder == code_dir
    
    # Test update_relative_paths
    job.update_relative_paths()
    
    # Test code_files property
    with tempfile.TemporaryDirectory() as temp_dir:
        code_dir = Path(temp_dir) / "test_code"
        code_dir.mkdir()
        
        # Create test files
        (code_dir / "main.py").write_text("print('main')")
        (code_dir / "utils.py").write_text("def helper(): pass")
        (code_dir / "config.json").write_text("{}")
        
        job.code_folder = str(code_dir)
        files = job.code_files
        assert len(files) >= 3
        
        file_names = [Path(f).name for f in files]
        assert "main.py" in file_names
        assert "utils.py" in file_names
        assert "config.json" in file_names
    
    # Test with no code folder
    job.code_folder = None
    assert job.code_files == []


def test_progression_api_comprehensive():
    """Test progression API comprehensively"""
    from syft_queue import q, approve, reject, start, complete, fail, timeout, advance, JobStatus
    
    queue = q("progression_comprehensive", force=True)
    
    # Create multiple jobs
    jobs = []
    for i in range(6):
        job = queue.create_job(f"prog_job_{i}", f"user{i}@test.com", "owner@test.com")
        jobs.append(job)
    
    # Test approve with parameters
    approved_job = approve(jobs[0], approver="admin@test.com", notes="Test approval")
    assert approved_job.status == JobStatus.approved
    
    # Test reject with parameters
    rejected_job = reject(jobs[1], reason="Invalid input", reviewer="admin@test.com")
    assert rejected_job.status == JobStatus.rejected
    
    # Test start with parameters
    started_job = start(approved_job, runner="worker_1", notes="Starting job")
    assert started_job.status == JobStatus.running
    
    # Test complete with parameters
    completed_job = complete(started_job, output="Job completed", duration_seconds=30)
    assert completed_job.status == JobStatus.completed
    
    # Test fail with parameters
    job_to_fail = approve(jobs[2])
    job_to_fail = start(job_to_fail)
    failed_job = fail(job_to_fail, error="Process failed", exit_code=1)
    assert failed_job.status == JobStatus.failed
    
    # Test timeout
    job_to_timeout = approve(jobs[3])
    job_to_timeout = start(job_to_timeout)
    timed_out_job = timeout(job_to_timeout)
    assert timed_out_job.status == JobStatus.failed
    
    # Test advance
    advanced_job = advance(jobs[4])
    assert advanced_job.status == JobStatus.approved
    
    # Test approve_all
    inbox_jobs = [jobs[5]]
    approved_jobs = # approve_all(inbox_jobs, approver="batch_admin@test.com")
    assert len(approved_jobs) == 1
    assert approved_jobs[0].status == JobStatus.approved


def test_server_utils_comprehensive():
    """Test server utils module comprehensively"""
    from syft_queue import server_utils
    
    # Test configuration functions
    config_path = server_utils.get_config_path()
    assert isinstance(config_path, Path)
    
    # Test server status functions
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        assert server_utils.is_server_running()
        
        mock_get.return_value.status_code = 404
        assert not server_utils.is_server_running()
        
        mock_get.side_effect = Exception("Connection error")
        assert not server_utils.is_server_running()
    
    # Test server health check
    with patch('syft_queue.server_utils.is_server_running', return_value=True):
        assert server_utils.ensure_server_healthy(max_retries=1)
    
    with patch('syft_queue.server_utils.is_server_running', return_value=False):
        with patch('time.sleep'):
            assert not server_utils.ensure_server_healthy(max_retries=1)
    
    # Test URL generation
    url = server_utils.get_syft_queue_url("test_endpoint")
    assert isinstance(url, str)
    assert "test_endpoint" in url
    
    # Test mode detection
    mode = server_utils.is_syftbox_mode()
    assert isinstance(mode, bool)
    
    # Test server management
    with patch('subprocess.Popen') as mock_popen:
        mock_popen.return_value.poll.return_value = None
        result = server_utils.start_server()
        assert isinstance(result, bool)
    
    # Test server stopping
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        server_utils.stop_server()


def test_auto_install_comprehensive():
    """Test auto_install module comprehensively"""
    from syft_queue import auto_install
    
    # Test installation checks
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "syftbox"
        assert auto_install.is_syftbox_installed()
        
        mock_run.return_value.returncode = 1
        assert not auto_install.is_syftbox_installed()
    
    # Test app installation check
    with patch('pathlib.Path.exists', return_value=True):
        result = auto_install.is_app_installed()
        assert isinstance(result, bool)
    
    # Test startup banner
    with patch('builtins.print') as mock_print:
        auto_install.show_startup_banner()
        mock_print.assert_called()
    
    # Test auto install function
    with patch('syft_queue.auto_install.is_syftbox_installed', return_value=True):
        with patch('syft_queue.auto_install.is_app_installed', return_value=False):
            with patch('syft_queue.auto_install.install_app') as mock_install:
                auto_install.auto_install()
                mock_install.assert_called()


def test_global_utility_functions():
    """Test global utility functions comprehensively"""
    from syft_queue import (
        list_queues, get_queue, cleanup_orphaned_queues,
        recreate_missing_queue_directories, get_queues_path, help,
        q, _queue_exists, _cleanup_empty_queue_directory,
        _cleanup_ghost_job_folders, _cleanup_all_ghost_job_folders,
        _cleanup_orphaned_queue_directories, _cleanup_all_orphaned_queue_directories,
        _is_ghost_job_folder, _queue_has_valid_syftobject, _get_queues_table
    )
    
    # Create test queue
    test_queue = q("utility_test", force=True)
    
    # Test list_queues
    queues_list = list_queues()
    assert isinstance(queues_list, list)
    assert len(queues_list) > 0
    
    # Test get_queue
    found_queue = get_queue("utility_test")
    assert found_queue is not None
    assert found_queue.name == test_queue.name
    
    not_found = get_queue("nonexistent_queue_xyz")
    assert not_found is None
    
    # Test get_queues_path
    path = get_queues_path()
    assert isinstance(path, Path)
    
    # Test help function
    with patch('builtins.print') as mock_print:
        help()
        mock_print.assert_called()
    
    # Test internal utilities
    assert _is_ghost_job_folder(Path("/tmp/J:ghost_job"))
    assert not _is_ghost_job_folder(Path("/tmp/Q:real_queue"))
    
    with patch('syft_objects.objects.get_object', return_value={"name": "Q:test"}):
        assert _queue_exists("test")
        assert _queue_has_valid_syftobject("test")
    
    with patch('syft_objects.objects.get_object', return_value=None):
        assert not _queue_exists("test")
        assert not _queue_has_valid_syftobject("test")
    
    # Test cleanup functions
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test structure
        empty_queue = temp_path / "Q:empty"
        empty_queue.mkdir()
        
        queue_with_ghosts = temp_path / "Q:with_ghosts"
        queue_with_ghosts.mkdir()
        (queue_with_ghosts / "J:ghost1").mkdir()
        (queue_with_ghosts / "J:ghost2").mkdir()
        
        # Test cleanup functions
        _cleanup_empty_queue_directory(empty_queue)
        count = _cleanup_ghost_job_folders(queue_with_ghosts)
        assert isinstance(count, int)
    
    # Test global cleanup functions
    total_ghosts = _cleanup_all_ghost_job_folders()
    assert isinstance(total_ghosts, int)
    
    total_orphaned = _cleanup_all_orphaned_queue_directories()
    assert isinstance(total_orphaned, int)
    
    # Test utility functions
    cleanup_orphaned_queues()
    recreate_missing_queue_directories()
    
    # Test queues table
    table = _get_queues_table()
    assert isinstance(table, str)


def test_job_execution_utilities():
    """Test job execution utilities comprehensively"""
    from syft_queue import q, process_queue, JobStatus
    from syft_queue.queue import prepare_job_for_execution, execute_job_with_context
    
    queue = q("execution_test", force=True)
    
    # Create jobs with code
    jobs = []
    for i in range(3):
        job = queue.create_job(f"exec_job_{i}", "user@test.com", "owner@test.com")
        job.update_status(JobStatus.approved)
        
        # Add code folder
        code_dir = job.object_path / "code"
        code_dir.mkdir(exist_ok=True)
        (code_dir / "run.py").write_text("print('test')")
        job.code_folder = str(code_dir)
        job.save()
        jobs.append(job)
    
    # Test prepare_job_for_execution
    context = prepare_job_for_execution(jobs[0])
    assert isinstance(context, dict)
    assert "job_uid" in context
    assert "job_name" in context
    assert context["job_uid"] == jobs[0].uid
    
    # Test execute_job_with_context
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")
        success, output = execute_job_with_context(jobs[0])
        assert isinstance(success, bool)
        assert isinstance(output, str)
    
    # Test process_queue
    results = process_queue(queue, max_jobs=2)
    assert isinstance(results, list)
    assert len(results) <= 2


def test_job_lifecycle_comprehensive():
    """Test comprehensive job lifecycle scenarios"""
    from syft_queue import q, JobStatus
    
    queue = q("lifecycle_comprehensive", force=True)
    
    # Test job creation with all parameters
    job = queue.create_job(
        "lifecycle_job",
        "user@test.com",
        "owner@test.com",
        description="Lifecycle test job",
        data={"test": "data"},
        metadata={"version": "1.0"},
        mock_data=False
    )
    
    # Test initial state
    assert job.status == JobStatus.inbox
    assert not job.is_terminal
    assert not job.is_approved
    assert not job.is_running
    assert not job.is_completed
    assert not job.is_failed
    assert not job.is_rejected
    
    # Test expiration
    job.updated_at = datetime.now() - timedelta(days=31)
    assert job.is_expired
    
    job.updated_at = datetime.now() - timedelta(days=29)
    assert not job.is_expired
    
    job.updated_at = None
    assert not job.is_expired
    
    # Test save and load
    job.save()
    from syft_queue import Job
    loaded_job = Job(job.object_path, owner_email="owner@test.com")
    assert loaded_job.uid == job.uid
    assert loaded_job.name == job.name
    assert loaded_job.description == job.description
    
    # Test string representations
    str_result = str(job)
    assert job.name in str_result
    assert job.description in str_result
    
    repr_result = repr(job)
    assert "Job" in repr_result
    assert job.uid in repr_result
    
    # Test status transitions
    job.update_status(JobStatus.approved)
    assert job.is_approved
    
    job.update_status(JobStatus.running)
    assert job.is_running
    
    job.update_status(JobStatus.completed)
    assert job.is_completed
    assert job.is_terminal
    
    # Test terminal to terminal transition
    job.update_status(JobStatus.failed)
    assert job.is_failed
    assert job.is_terminal


def test_error_handling_comprehensive():
    """Test comprehensive error handling scenarios"""
    from syft_queue import q, JobStatus, queue as queue_factory
    
    # Test invalid queue type
    with pytest.raises(ValueError):
        queue_factory("test", queue_type="invalid_type")
    
    # Test job operations with errors
    queue = q("error_handling", force=True)
    job = queue.create_job("error_job", "user@test.com", "owner@test.com")
    
    # Test deletion with permission error
    with patch('shutil.rmtree', side_effect=OSError("Permission denied")):
        try:
            job.delete()
        except OSError:
            pass  # Expected
    
    # Test validation errors in progression API
    from syft_queue import approve, start, complete
    
    # Try to approve already approved job
    job.update_status(JobStatus.approved)
    try:
        approve(job)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    # Try to start non-approved job
    inbox_job = queue.create_job("inbox_job", "user@test.com", "owner@test.com")
    try:
        start(inbox_job)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    # Try to complete non-running job
    try:
        complete(inbox_job)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_data_queue_specific():
    """Test DataQueue specific functionality"""
    from syft_queue import q, DataQueue
    
    data_queue = q("data_specific", queue_type="data", force=True)
    assert isinstance(data_queue, DataQueue)
    
    # Create data job
    data_job = data_queue.create_job(
        "data_job",
        "data_user@test.com",
        "data_owner@test.com",
        data={"dataset": "test_data.csv", "size": 1000}
    )
    
    # Test data job properties
    assert data_job.data["dataset"] == "test_data.csv"
    assert data_job.data["size"] == 1000
    
    # Test data queue operations
    jobs = data_queue.list_jobs()
    assert len(jobs) >= 1
    
    stats = data_queue.get_stats()
    assert stats["total_jobs"] >= 1
    
    # Test queue string representations
    str_result = str(data_queue)
    assert "data_specific" in str_result
    
    repr_result = repr(data_queue)
    assert "Queue" in repr_result or "data_specific" in repr_result


def test_pipeline_coverage():
    """Test pipeline module coverage"""
    try:
        from syft_queue import Pipeline, PipelineBuilder, PipelineStage
        
        # Test pipeline creation
        builder = PipelineBuilder()
        assert builder is not None
        
        # Test pipeline stage
        stage = PipelineStage("test_stage", lambda x: x)
        assert stage.name == "test_stage"
        
        # Test pipeline building
        pipeline = builder.build()
        assert isinstance(pipeline, Pipeline)
        
    except ImportError:
        # Pipeline features are optional
        pass


def test_test_utils_coverage():
    """Test test_utils module coverage"""
    try:
        from syft_queue import cleanup_all_test_artifacts, cleanup_test_objects, cleanup_test_queues
        
        # Test cleanup functions
        cleanup_all_test_artifacts()
        cleanup_test_objects()
        cleanup_test_queues()
        
    except ImportError:
        # Test utilities are optional
        pass


def test_init_module_coverage():
    """Test __init__.py module coverage"""
    from syft_queue import queues, __version__
    
    # Test version
    assert isinstance(__version__, str)
    assert len(__version__) > 0
    
    # Test queues collection
    with patch('syft_queue.server_utils.start_server', return_value=True):
        with patch('syft_queue.server_utils.get_syft_queue_url', return_value='http://test.com'):
            # Test widget
            widget = queues.widget()
            assert '<iframe' in widget
            
            # Test _repr_html_
            html = queues._repr_html_()
            assert '<iframe' in html
    
    # Test string representations
    with patch('syft_queue.queue._get_queues_table', return_value='Test table'):
        assert str(queues) == 'Test table'


def test_edge_cases_comprehensive():
    """Test comprehensive edge cases"""
    from syft_queue import q, get_queue, JobStatus
    
    # Test queue creation with same name
    queue1 = q("edge_case", force=True)
    queue2 = q("edge_case", force=True)  # Should work with force=True
    
    # Test empty queue operations
    empty_queue = q("empty_edge", force=True)
    empty_jobs = empty_queue.list_jobs()
    assert len(empty_jobs) == 0
    
    empty_stats = empty_queue.get_stats()
    assert empty_stats["total_jobs"] == 0
    
    # Test job with minimal data
    minimal_job = empty_queue.create_job("minimal", "user@test.com", "owner@test.com")
    assert minimal_job.name.startswith("test_J:")
    assert minimal_job.status == JobStatus.inbox
    
    # Test job listing with filters
    jobs = []
    for i in range(3):
        job = empty_queue.create_job(f"filter_job_{i}", "user@test.com", "owner@test.com")
        jobs.append(job)
    
    jobs[0].update_status(JobStatus.approved)
    jobs[1].update_status(JobStatus.rejected)
    
    inbox_jobs = empty_queue.list_jobs(status=JobStatus.inbox)
    approved_jobs = empty_queue.list_jobs(status=JobStatus.approved)
    rejected_jobs = empty_queue.list_jobs(status=JobStatus.rejected)
    
    assert len(inbox_jobs) >= 1
    assert len(approved_jobs) >= 1
    assert len(rejected_jobs) >= 1
    
    # Test get_job with non-existent uid
    fake_uid = str(uuid4())
    not_found = empty_queue.get_job(fake_uid)
    assert not_found is None