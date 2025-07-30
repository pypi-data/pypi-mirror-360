"""
Queue module coverage boost tests - targeting 95% overall coverage
"""

import pytest
import os
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime, timedelta
from uuid import uuid4


def test_queue_factory_validation():
    """Test queue factory function validation"""
    from syft_queue import queue as queue_factory
    
    # Test invalid queue type
    with pytest.raises(ValueError):
        queue_factory("test", queue_type="invalid_type")
    
    # Test valid queue types
    queue_code = queue_factory("code_test", queue_type="code", force=True)
    assert queue_code is not None
    
    queue_data = queue_factory("data_test", queue_type="data", force=True)
    assert queue_data is not None


def test_queue_utility_functions():
    """Test queue utility functions comprehensively"""
    from syft_queue.queue import (
        _queue_exists, _is_ghost_job_folder, _cleanup_empty_queue_directory,
        _cleanup_ghost_job_folders, _cleanup_all_ghost_job_folders,
        _queue_has_valid_syftobject, _cleanup_orphaned_queue_directories,
        _cleanup_all_orphaned_queue_directories, _get_queues_table
    )
    
    # Test _queue_exists
    with patch('syft_objects.objects.get_object', return_value=None):
        assert not _queue_exists("nonexistent_queue")
    
    with patch('syft_objects.objects.get_object', return_value={"name": "Q:test_queue"}):
        assert _queue_exists("test_queue")
    
    # Test _is_ghost_job_folder
    assert _is_ghost_job_folder(Path("/tmp/J:ghost_job_123"))
    assert not _is_ghost_job_folder(Path("/tmp/Q:real_queue"))
    assert not _is_ghost_job_folder(Path("/tmp/regular_folder"))
    
    # Test _queue_has_valid_syftobject
    with patch('syft_objects.objects.get_object', return_value={"name": "Q:valid_queue"}):
        assert _queue_has_valid_syftobject("valid_queue")
    
    with patch('syft_objects.objects.get_object', return_value=None):
        assert not _queue_has_valid_syftobject("invalid_queue")
    
    # Test cleanup functions with temp directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Test _cleanup_empty_queue_directory
        empty_queue = temp_path / "Q:empty_queue"
        empty_queue.mkdir()
        _cleanup_empty_queue_directory(empty_queue)
        
        # Test _cleanup_ghost_job_folders
        queue_dir = temp_path / "Q:test_queue"
        queue_dir.mkdir()
        (queue_dir / "J:ghost1").mkdir()
        (queue_dir / "J:ghost2").mkdir()
        (queue_dir / "inbox").mkdir()  # Not a ghost
        
        count = _cleanup_ghost_job_folders(queue_dir)
        assert count >= 2
        
        # Test global cleanup functions
        total_ghost = _cleanup_all_ghost_job_folders()
        assert isinstance(total_ghost, int)
        
        total_orphaned = _cleanup_all_orphaned_queue_directories()
        assert isinstance(total_orphaned, int)
    
    # Test _get_queues_table
    table = _get_queues_table()
    assert isinstance(table, str)


def test_job_path_resolution():
    """Test job path resolution comprehensively"""
    from syft_queue import q
    
    queue = q("path_resolution_test", force=True)
    job = queue.create_job("path_job", "user@test.com", "owner@test.com")
    
    # Test resolved_code_folder scenarios
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Scenario 1: code_folder exists
        code_dir = temp_path / "existing_code"
        code_dir.mkdir()
        job.code_folder = str(code_dir)
        assert job.resolved_code_folder == code_dir
        
        # Scenario 2: code_folder doesn't exist, use relative
        job.code_folder = None
        job.code_folder_relative = "relative_code"
        rel_code_dir = job.object_path / "relative_code"
        rel_code_dir.mkdir(parents=True, exist_ok=True)
        assert job.resolved_code_folder == rel_code_dir
        
        # Scenario 3: use absolute fallback
        job.code_folder_relative = None
        job.code_folder_absolute_fallback = str(code_dir)
        assert job.resolved_code_folder == code_dir
        
        # Scenario 4: search for default code directory
        job.code_folder_absolute_fallback = None
        default_code = job.object_path / "code"
        default_code.mkdir(exist_ok=True)
        resolved = job.resolved_code_folder
        assert resolved == default_code
    
    # Test resolved_output_folder scenarios
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Output folder exists
        output_dir = temp_path / "existing_output"
        output_dir.mkdir()
        job.output_folder = str(output_dir)
        assert job.resolved_output_folder == output_dir
        
        # Output folder relative
        job.output_folder = None
        job.output_folder_relative = "relative_output"
        rel_output_dir = job.object_path / "relative_output"
        rel_output_dir.mkdir(parents=True, exist_ok=True)
        resolved_output = job.resolved_output_folder
        assert resolved_output == rel_output_dir


def test_job_file_operations():
    """Test job file operations"""
    from syft_queue import q
    
    queue = q("file_ops_test", force=True)
    job = queue.create_job("file_job", "user@test.com", "owner@test.com")
    
    # Test code_files property
    with tempfile.TemporaryDirectory() as temp_dir:
        code_dir = Path(temp_dir) / "code"
        code_dir.mkdir()
        
        # Create test files
        (code_dir / "main.py").write_text("print('main')")
        (code_dir / "utils.py").write_text("def helper(): pass")
        (code_dir / "config.json").write_text("{}")
        (code_dir / "data.txt").write_text("data")
        
        job.code_folder = str(code_dir)
        files = job.code_files
        assert len(files) >= 4
        
        # Check that files are returned as relative paths
        file_names = [Path(f).name for f in files]
        assert "main.py" in file_names
        assert "utils.py" in file_names
        assert "config.json" in file_names
        assert "data.txt" in file_names
    
    # Test code_files with no code folder
    job.code_folder = None
    assert job.code_files == []
    
    # Test code_files with non-existent folder
    job.code_folder = "/path/that/does/not/exist"
    assert job.code_files == []


def test_job_expiration_edge_cases():
    """Test job expiration edge cases"""
    from syft_queue import q
    
    queue = q("expiration_edge_test", force=True)
    job = queue.create_job("expire_job", "user@test.com", "owner@test.com")
    
    # Test with None updated_at
    job.updated_at = None
    assert not job.is_expired
    
    # Test boundary cases
    job.updated_at = datetime.now() - timedelta(days=30, hours=23, minutes=59)
    assert not job.is_expired
    
    job.updated_at = datetime.now() - timedelta(days=31, hours=1)
    assert job.is_expired
    
    # Test exactly 30 days
    job.updated_at = datetime.now() - timedelta(days=30)
    assert not job.is_expired


def test_job_status_properties():
    """Test job status properties comprehensively"""
    from syft_queue import q, JobStatus
    
    queue = q("status_props_test", force=True)
    job = queue.create_job("status_job", "user@test.com", "owner@test.com")
    
    # Test initial state
    assert job.status == JobStatus.inbox
    assert not job.is_terminal
    assert not job.is_approved
    assert not job.is_running
    assert not job.is_completed
    assert not job.is_failed
    assert not job.is_rejected
    
    # Test approved state
    job.update_status(JobStatus.approved)
    assert job.is_approved
    assert not job.is_terminal
    
    # Test running state
    job.update_status(JobStatus.running)
    assert job.is_running
    assert not job.is_terminal
    
    # Test completed state
    job.update_status(JobStatus.completed)
    assert job.is_completed
    assert job.is_terminal
    
    # Test failed state
    job2 = queue.create_job("failed_job", "user@test.com", "owner@test.com")
    job2.update_status(JobStatus.running)
    job2.update_status(JobStatus.failed)
    assert job2.is_failed
    assert job2.is_terminal
    
    # Test rejected state
    job3 = queue.create_job("rejected_job", "user@test.com", "owner@test.com")
    job3.update_status(JobStatus.rejected)
    assert job3.is_rejected
    assert job3.is_terminal


def test_job_string_representations():
    """Test job string representations"""
    from syft_queue import q
    
    queue = q("string_test", force=True)
    job = queue.create_job("string_job", "user@test.com", "owner@test.com")
    
    # Test __str__ with description
    job.description = "Test job description"
    str_result = str(job)
    assert job.name in str_result
    assert "Test job description" in str_result
    
    # Test __str__ without description
    job.description = None
    str_result = str(job)
    assert job.name in str_result
    
    # Test __repr__
    repr_result = repr(job)
    assert "Job" in repr_result
    assert job.uid in repr_result


def test_job_data_handling():
    """Test job data handling"""
    from syft_queue import q
    
    queue = q("data_handling_test", force=True)
    
    # Test job with complex data
    complex_data = {
        "input": [1, 2, 3],
        "nested": {
            "config": {"param1": "value1", "param2": 42},
            "arrays": [[1, 2], [3, 4]]
        },
        "metadata": {"created_by": "test", "version": "1.0"}
    }
    
    job = queue.create_job(
        "data_job",
        "user@test.com",
        "owner@test.com",
        data=complex_data,
        metadata={"priority": "high", "tags": ["test", "complex"]}
    )
    
    # Test that data is preserved
    assert job.data == complex_data
    assert job.metadata["priority"] == "high"
    assert "test" in job.metadata["tags"]
    
    # Test job with mock data
    mock_job = queue.create_job(
        "mock_job",
        "user@test.com",
        "owner@test.com",
        mock_data=True
    )
    
    # Mock data should be generated
    assert mock_job.data is not None


def test_queue_stats_operations():
    """Test queue statistics operations"""
    from syft_queue import q, JobStatus
    
    queue = q("stats_test", force=True)
    
    # Create jobs in different states
    jobs = []
    for i in range(10):
        job = queue.create_job(f"stats_job_{i}", "user@test.com", "owner@test.com")
        jobs.append(job)
    
    # Update some job statuses
    jobs[0].update_status(JobStatus.approved)
    jobs[1].update_status(JobStatus.approved)
    jobs[2].update_status(JobStatus.approved)
    jobs[2].update_status(JobStatus.running)
    jobs[3].update_status(JobStatus.approved)
    jobs[3].update_status(JobStatus.running)
    jobs[3].update_status(JobStatus.completed)
    jobs[4].update_status(JobStatus.rejected)
    
    # Test get_stats
    stats = queue.get_stats()
    assert "total_jobs" in stats
    assert "inbox" in stats
    assert "approved" in stats
    assert "running" in stats
    assert "completed" in stats
    assert "failed" in stats
    assert "rejected" in stats
    
    assert stats["total_jobs"] == 10
    assert stats["inbox"] >= 5
    assert stats["approved"] >= 2
    assert stats["running"] >= 1
    assert stats["completed"] >= 1
    assert stats["rejected"] >= 1
    
    # Test refresh_stats
    queue.refresh_stats()
    new_stats = queue.get_stats()
    assert new_stats["total_jobs"] == stats["total_jobs"]
    
    # Test _update_stats
    original_inbox = stats["inbox"]
    queue._update_stats("inbox", 1)
    updated_stats = queue.get_stats()
    # Note: _update_stats modifies internal counters


def test_queue_job_listing():
    """Test queue job listing functionality"""
    from syft_queue import q, JobStatus
    
    queue = q("listing_test", force=True)
    
    # Create jobs
    jobs = []
    for i in range(5):
        job = queue.create_job(f"list_job_{i}", "user@test.com", "owner@test.com")
        jobs.append(job)
    
    # Update some statuses
    jobs[0].update_status(JobStatus.approved)
    jobs[1].update_status(JobStatus.approved)
    jobs[2].update_status(JobStatus.rejected)
    
    # Test list_jobs without filter
    all_jobs = queue.list_jobs()
    assert len(all_jobs) >= 5
    
    # Test list_jobs with status filter
    inbox_jobs = queue.list_jobs(status=JobStatus.inbox)
    approved_jobs = queue.list_jobs(status=JobStatus.approved)
    rejected_jobs = queue.list_jobs(status=JobStatus.rejected)
    
    assert len(inbox_jobs) >= 2
    assert len(approved_jobs) >= 2
    assert len(rejected_jobs) >= 1
    
    # Test get_job
    for job in jobs:
        found_job = queue.get_job(job.uid)
        assert found_job is not None
        assert found_job.uid == job.uid
    
    # Test get_job with non-existent uid
    fake_uid = str(uuid4())
    not_found = queue.get_job(fake_uid)
    assert not_found is None


def test_global_queue_functions():
    """Test global queue functions"""
    from syft_queue import list_queues, get_queue, cleanup_orphaned_queues, recreate_missing_queue_directories, get_queues_path, help
    
    # Test list_queues
    queues_list = list_queues()
    assert isinstance(queues_list, list)
    
    # Test get_queue with existing queue
    from syft_queue import q
    test_queue = q("global_test", force=True)
    found_queue = get_queue("global_test")
    assert found_queue is not None
    assert found_queue.name == test_queue.name
    
    # Test get_queue with non-existent queue
    not_found_queue = get_queue("nonexistent_queue_12345")
    assert not_found_queue is None
    
    # Test utility functions
    cleanup_orphaned_queues()
    recreate_missing_queue_directories()
    
    path = get_queues_path()
    assert isinstance(path, Path)
    
    # Test help function
    with patch('builtins.print') as mock_print:
        help()
        mock_print.assert_called()


def test_job_execution_context():
    """Test job execution context preparation"""
    from syft_queue import q
    from syft_queue.queue import prepare_job_for_execution, execute_job_with_context
    
    queue = q("execution_context_test", force=True)
    job = queue.create_job("exec_job", "user@test.com", "owner@test.com")
    
    # Test prepare_job_for_execution
    context = prepare_job_for_execution(job)
    assert isinstance(context, dict)
    assert "job_uid" in context
    assert "job_name" in context
    assert context["job_uid"] == job.uid
    assert context["job_name"] == job.name
    
    # Test execute_job_with_context with mocked subprocess
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")
        success, output = execute_job_with_context(job)
        assert isinstance(success, bool)
        assert isinstance(output, str)
    
    # Test execute_job_with_context with failure
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="Error occurred")
        success, output = execute_job_with_context(job)
        assert not success
        assert "error" in output.lower() or "Error occurred" in output
    
    # Test execute_job_with_context with exception
    with patch('subprocess.run', side_effect=Exception("Execution failed")):
        success, output = execute_job_with_context(job)
        assert not success
        assert "error" in output.lower() or "failed" in output.lower()