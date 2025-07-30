"""
Comprehensive tests to achieve 100% code coverage for all modules
"""

import pytest
import tempfile
import json
import shutil
import os
import subprocess
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime, timedelta
from uuid import UUID, uuid4

# Force clean import of syft_queue
import sys
if 'syft_queue' in sys.modules:
    del sys.modules['syft_queue']

# Use force=True for all queue creation to avoid conflicts
from syft_queue import q, Job, JobStatus


def test_detect_syftbox_queues_path():
    """Test _detect_syftbox_queues_path function."""
    from syft_queue.queue import _detect_syftbox_queues_path
    
    # Test with SYFTBOX_DATA_FOLDER environment variable
    with patch.dict('os.environ', {'SYFTBOX_DATA_FOLDER': '/tmp/test_data'}):
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            path = _detect_syftbox_queues_path()
            assert str(path) == '/tmp/test_data'
            mock_mkdir.assert_called_once()
    
    # Test with SYFTBOX_EMAIL environment variable
    with patch.dict('os.environ', {'SYFTBOX_EMAIL': 'test@example.com'}, clear=True):
        with patch('pathlib.Path.home', return_value=Path('/home/user')):
            with patch('pathlib.Path.exists', return_value=True):
                path = _detect_syftbox_queues_path()
                expected = Path('/home/user/SyftBox/datasites/test@example.com/app_data/syft-queues')
                assert path == expected
    
    # Test with config file
    mock_config = """
    email: config@example.com
    """
    with patch.dict('os.environ', {}, clear=True):
        with patch('pathlib.Path.home', return_value=Path('/home/user')):
            with patch('pathlib.Path.exists', return_value=True):
                with patch('builtins.open', mock_open(read_data=mock_config)):
                    with patch('yaml.safe_load', return_value={'email': 'config@example.com'}):
                        path = _detect_syftbox_queues_path()
                        expected = Path('/home/user/SyftBox/datasites/config@example.com/app_data/syft-queues')
                        assert path == expected
    
    # Test fallback to current directory
    with patch.dict('os.environ', {}, clear=True):
        with patch('pathlib.Path.home', return_value=Path('/home/user')):
            with patch('pathlib.Path.exists', return_value=False):
                path = _detect_syftbox_queues_path()
                assert path == Path.cwd()


def test_generate_mock_data_comprehensive():
    """Test _generate_mock_data with all data types."""
    from syft_queue.queue import _generate_mock_data
    
    # Test with various data types
    complex_data = {
        "string": "test_string",
        "integer": 42,
        "float": 3.14,
        "boolean": True,
        "none": None,
        "list": [1, 2, 3, "test"],
        "nested_dict": {
            "inner_string": "inner_value",
            "inner_int": 100,
            "deeply_nested": {
                "deep_value": "very_deep"
            }
        },
        "tuple": (1, 2, 3),
        "set": {1, 2, 3}
    }
    
    mock_data = _generate_mock_data(complex_data)
    
    # Check that structure is preserved
    assert set(mock_data.keys()) == set(complex_data.keys())
    assert set(mock_data["nested_dict"].keys()) == set(complex_data["nested_dict"].keys())
    assert set(mock_data["nested_dict"]["deeply_nested"].keys()) == set(complex_data["nested_dict"]["deeply_nested"].keys())
    
    # Check that values are different
    assert mock_data["string"] != "test_string"
    assert mock_data["integer"] != 42
    assert mock_data["float"] != 3.14
    assert mock_data["nested_dict"]["inner_string"] != "inner_value"
    
    # Check that types are preserved where possible
    assert isinstance(mock_data["integer"], int)
    assert isinstance(mock_data["float"], float)
    assert isinstance(mock_data["boolean"], bool)


def test_job_comprehensive_properties(mock_syftbox_env, sample_code_dir):
    """Test all Job properties and edge cases."""
    queue = q("comprehensive_job_test", force=True)
    
    # Test job creation with all parameters
    job = queue.create_job(
        name="comprehensive_job",
        requester_email="requester@test.com",
        target_email="target@test.com",
        code_folder=str(sample_code_dir),
        description="Comprehensive test job",
        timeout_seconds=7200,
        tags=["test", "comprehensive"],
        data={"key": "value"},
        mock_data=False
    )
    
    # Test all properties
    assert job.name.startswith("test_J:")
    assert job.requester_email == "requester@test.com"
    assert job.target_email == "target@test.com"
    assert job.description == "Comprehensive test job"
    assert job.timeout_seconds == 7200
    assert job.tags == ["test", "comprehensive"]
    assert job.status == JobStatus.inbox
    assert not job.is_terminal
    assert not job.is_expired
    
    # Test resolved paths
    assert job.resolved_code_folder is not None
    
    # Test path resolution fallback
    job.code_folder = "/nonexistent/path"
    job.code_folder_relative = None
    job.base_path = None
    resolved = job.resolved_code_folder
    # Should fall back to job directory code folder
    
    # Test with relative path
    job.base_path = str(sample_code_dir.parent)
    job.code_folder_relative = sample_code_dir.name
    resolved = job.resolved_code_folder
    assert resolved is not None
    
    # Test status update
    job.update_status(JobStatus.approved)
    assert job.status == JobStatus.approved
    
    # Test with error message
    job.update_status(JobStatus.failed, error_message="Test error")
    assert job.error_message == "Test error"
    
    # Test terminal status
    assert job.is_terminal
    
    # Test job deletion
    job_path = job.object_path
    job.delete()
    assert not job_path.exists()


def test_job_expiration(mock_syftbox_env):
    """Test job expiration logic."""
    queue = q("expiration_test", force=True)
    
    # Create job with short timeout
    job = queue.create_job(
        "expiring_job",
        "user@test.com",
        "owner@test.com",
        timeout_seconds=1
    )
    
    # Should not be expired initially
    assert not job.is_expired
    
    # Mock time to make job expired
    with patch('syft_queue.queue.datetime') as mock_datetime:
        # Set current time to 2 seconds after creation
        mock_datetime.now.return_value = job.created_at + timedelta(seconds=2)
        assert job.is_expired
    
    # Terminal jobs should never be expired
    job.update_status(JobStatus.completed)
    assert not job.is_expired


def test_job_path_resolution_comprehensive(mock_syftbox_env, tmp_path):
    """Test comprehensive path resolution scenarios."""
    queue = q("path_resolution_test", force=True)
    job = queue.create_job("path_job", "user@test.com", "owner@test.com")
    
    # Test with absolute path that exists
    test_dir = tmp_path / "test_absolute"
    test_dir.mkdir()
    job.code_folder = str(test_dir)
    resolved = job.resolved_code_folder
    assert resolved == test_dir.absolute()
    
    # Test with absolute fallback
    fallback_dir = tmp_path / "fallback"
    fallback_dir.mkdir()
    job.code_folder = "/nonexistent"
    job.code_folder_absolute_fallback = str(fallback_dir)
    resolved = job.resolved_code_folder
    assert resolved == fallback_dir.absolute()
    
    # Test with no valid paths - should find code directory in job folder
    job.code_folder = "/nonexistent"
    job.code_folder_relative = None
    job.code_folder_absolute_fallback = "/also_nonexistent"
    resolved = job.resolved_code_folder
    # Should find the job's code directory
    assert resolved is not None


def test_queue_creation_comprehensive(mock_syftbox_env):
    """Test comprehensive queue creation scenarios."""
    # Test CodeQueue creation
    code_queue = q("comprehensive_code", queue_type="code", force=True)
    assert code_queue.queue_name == "test_Q:comprehensive_code"
    assert hasattr(code_queue, 'create_job')
    
    # Test DataQueue creation
    data_queue = q("comprehensive_data", queue_type="data", force=True)
    assert data_queue.queue_name == "test_Q:comprehensive_data"
    
    # Test invalid queue type
    with pytest.raises(ValueError, match="Invalid queue_type"):
        q("invalid", queue_type="invalid", force=True)
    
    # Test queue already exists without force
    with pytest.raises(ValueError, match="already exists"):
        q("comprehensive_code", force=False)


def test_queue_job_management(mock_syftbox_env):
    """Test comprehensive job management in queues."""
    queue = q("job_management_test", force=True)
    
    # Create multiple jobs
    jobs = []
    for i in range(5):
        job = queue.create_job(f"job_{i}", "user@test.com", "owner@test.com")
        jobs.append(job)
    
    # Test job counting
    queue.refresh_stats()
    assert queue.total_jobs == 5
    assert queue.inbox_jobs == 5
    
    # Move jobs to different statuses
    jobs[0].update_status(JobStatus.approved)
    jobs[1].update_status(JobStatus.running)
    jobs[2].update_status(JobStatus.completed)
    jobs[3].update_status(JobStatus.failed)
    
    # Refresh and check counts
    queue.refresh_stats()
    assert queue.inbox_jobs == 1
    assert queue.approved_jobs == 1
    assert queue.running_jobs == 1
    assert queue.completed_jobs == 1
    assert queue.failed_jobs == 1
    
    # Test getting job by UID
    job = queue.get_job(jobs[0].uid)
    assert job is not None
    assert job.uid == jobs[0].uid
    
    # Test getting nonexistent job
    fake_uid = uuid4()
    job = queue.get_job(fake_uid)
    assert job is None
    
    # Test listing jobs by status
    inbox_jobs = queue.list_jobs(JobStatus.inbox)
    assert len(inbox_jobs) == 1
    
    completed_jobs = queue.list_jobs(JobStatus.completed)
    assert len(completed_jobs) == 1


def test_queue_directory_structure(mock_syftbox_env):
    """Test queue directory structure creation."""
    queue = q("directory_test", force=True)
    
    # Check basic structure
    assert queue.object_path.exists()
    assert (queue.object_path / "jobs").exists()
    assert (queue.object_path / "jobs" / "inbox").exists()
    assert (queue.object_path / "jobs" / "approved").exists()
    assert (queue.object_path / "jobs" / "running").exists()
    assert (queue.object_path / "jobs" / "completed").exists()
    assert (queue.object_path / "jobs" / "failed").exists()
    assert (queue.object_path / "jobs" / "rejected").exists()


def test_cleanup_functions_comprehensive(tmp_path):
    """Test all cleanup functions comprehensively."""
    from syft_queue.queue import (
        _cleanup_empty_queue_directory,
        _is_ghost_job_folder,
        _cleanup_ghost_job_folders,
        _cleanup_orphaned_queue_directories,
        _queue_has_valid_syftobject
    )
    
    # Test _cleanup_empty_queue_directory
    empty_dir = tmp_path / "empty_queue"
    empty_dir.mkdir()
    _cleanup_empty_queue_directory(empty_dir)
    assert not empty_dir.exists()
    
    # Test with non-empty directory
    non_empty_dir = tmp_path / "non_empty_queue"
    non_empty_dir.mkdir()
    (non_empty_dir / "file.txt").write_text("content")
    _cleanup_empty_queue_directory(non_empty_dir)
    assert non_empty_dir.exists()  # Should not be removed
    
    # Test _is_ghost_job_folder
    ghost_dir = tmp_path / "J:ghost_job"
    ghost_dir.mkdir()
    assert _is_ghost_job_folder(ghost_dir) is True
    
    # Create valid job folder
    valid_dir = tmp_path / "J:valid_job"
    valid_dir.mkdir()
    (valid_dir / "syftobject.yaml").write_text("type: SyftBox Job")
    assert _is_ghost_job_folder(valid_dir) is False
    
    # Test non-job folder
    other_dir = tmp_path / "not_a_job"
    other_dir.mkdir()
    assert _is_ghost_job_folder(other_dir) is False
    
    # Test _cleanup_ghost_job_folders
    queue_path = tmp_path / "test_queue"
    queue_path.mkdir()
    
    # Create ghost folders
    for i in range(3):
        ghost = queue_path / f"J:ghost_{i}"
        ghost.mkdir()
    
    # Create valid folder
    valid = queue_path / "J:valid"
    valid.mkdir()
    (valid / "syftobject.yaml").write_text("type: SyftBox Job")
    
    cleaned = _cleanup_ghost_job_folders(queue_path)
    assert cleaned == 3
    assert not (queue_path / "J:ghost_0").exists()
    assert (queue_path / "J:valid").exists()
    
    # Test _queue_has_valid_syftobject
    with patch('syft_objects.get_syft_object') as mock_get:
        mock_get.return_value = {"name": "Q:test"}
        assert _queue_has_valid_syftobject("test") is True
        
        mock_get.return_value = None
        assert _queue_has_valid_syftobject("test") is False
    
    # Test _cleanup_orphaned_queue_directories
    orphan_dir = tmp_path / "Q:orphan"
    orphan_dir.mkdir()
    
    with patch('syft_queue.queue._queue_has_valid_syftobject', return_value=False):
        cleaned = _cleanup_orphaned_queue_directories(tmp_path)
        assert cleaned >= 1
        assert not orphan_dir.exists()


def test_job_execution_context(mock_syftbox_env, sample_code_dir):
    """Test job execution context preparation."""
    from syft_queue.queue import prepare_job_for_execution, execute_job_with_context
    
    queue = q("execution_test", force=True)
    job = queue.create_job(
        "execution_job",
        "user@test.com",
        "owner@test.com",
        code_folder=str(sample_code_dir),
        data={"test": "data"}
    )
    
    # Test context preparation
    context = prepare_job_for_execution(job)
    assert "job_uid" in context
    assert "job_name" in context
    assert "job_dir" in context
    assert "code_path" in context
    assert "output_path" in context
    assert "working_dir" in context
    assert context["job_uid"] == str(job.uid)
    
    # Test execution with successful command
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Success output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        success, output = execute_job_with_context(job)
        assert success is True
        assert "Success output" in output
    
    # Test execution with failed command
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error output"
        mock_run.return_value = mock_result
        
        success, output = execute_job_with_context(job)
        assert success is False
        assert "Error output" in output
    
    # Test execution with custom runner
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Custom output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        success, output = execute_job_with_context(job, runner_command="python3")
        assert success is True
        mock_run.assert_called()
        
        # Check that python3 was used in the call
        call_args = mock_run.call_args
        assert "python3" in str(call_args)


def test_job_progression_api(mock_syftbox_env):
    """Test job progression API functions."""
    from syft_queue.queue import approve, reject, start, complete, fail, timeout, advance
    
    queue = q("progression_test", force=True)
    
    # Test approve
    job = queue.create_job("test_job", "user@test.com", "owner@test.com")
    approved_job = approve(job, approver="admin@test.com")
    assert approved_job.status == JobStatus.approved
    
    # Test start
    started_job = start(approved_job, runner="worker1")
    assert started_job.status == JobStatus.running
    assert started_job.started_at is not None
    
    # Test complete
    completed_job = complete(started_job)
    assert completed_job.status == JobStatus.completed
    assert completed_job.completed_at is not None
    
    # Test reject
    job2 = queue.create_job("test_job2", "user@test.com", "owner@test.com")
    rejected_job = reject(job2, reason="Invalid request")
    assert rejected_job.status == JobStatus.rejected
    
    # Test fail
    job3 = queue.create_job("test_job3", "user@test.com", "owner@test.com")
    job3.update_status(JobStatus.running)
    failed_job = fail(job3, error="Process failed", exit_code=1)
    assert failed_job.status == JobStatus.failed
    assert failed_job.exit_code == 1
    
    # Test timeout
    job4 = queue.create_job("test_job4", "user@test.com", "owner@test.com")
    job4.update_status(JobStatus.running)
    timeout_job = timeout(job4)
    assert timeout_job.status == JobStatus.timedout
    
    # Test advance
    job5 = queue.create_job("test_job5", "user@test.com", "owner@test.com")
    advanced_job = advance(job5)
    assert advanced_job.status == JobStatus.approved
    
    advanced_job = advance(advanced_job)
    assert advanced_job.status == JobStatus.running
    
    advanced_job = advance(advanced_job)
    assert advanced_job.status == JobStatus.completed


def test_batch_operations(mock_syftbox_env):
    """Test batch operations."""
    from syft_queue.queue import approve_all, process_queue
    
    queue = q("batch_test", force=True)
    
    # Create multiple jobs
    jobs = []
    for i in range(5):
        job = queue.create_job(f"batch_job_{i}", "user@test.com", "owner@test.com")
        jobs.append(job)
    
    # Test approve_all
    approved_jobs = approve_all(jobs, approver="admin@test.com")
    assert len(approved_jobs) == 5
    for job in approved_jobs:
        assert job.status == JobStatus.approved
    
    # Test process_queue
    def mock_processor(job_list):
        results = []
        for job in job_list:
            job.update_status(JobStatus.completed)
            results.append((True, f"Processed {job.name}"))
        return results
    
    results = process_queue(queue, max_jobs=3)
    assert len(results) <= 3


def test_data_queue_specific(mock_syftbox_env):
    """Test DataQueue specific functionality."""
    data_queue = q("data_specific_test", queue_type="data", force=True)
    
    # DataQueue should allow jobs without code
    job = data_queue.create_job(
        "data_job",
        "user@test.com",
        "owner@test.com",
        data={"dataset": "important_data"}
    )
    
    assert job.name == "test_J:data_job"
    assert job.code_folder == ""  # Should be empty for data jobs


def test_help_function(capsys):
    """Test help function."""
    from syft_queue.queue import help as syft_help
    
    syft_help()
    captured = capsys.readouterr()
    assert "SyftQueue" in captured.out
    assert "Getting Started" in captured.out


def test_queue_factory_functions(mock_syftbox_env):
    """Test queue factory functions."""
    from syft_queue.queue import queue, q as q_func, get_queue, list_queues
    
    # Test queue function
    queue1 = queue("factory_test1", force=True)
    assert queue1.queue_name == "test_Q:factory_test1"
    
    # Test q function (alias)
    queue2 = q_func("factory_test2", force=True)
    assert queue2.queue_name == "test_Q:factory_test2"
    
    # Test get_queue
    retrieved = get_queue("factory_test1")
    assert retrieved is not None
    assert retrieved.queue_name == "test_Q:factory_test1"
    
    # Test get_queue with nonexistent queue
    nonexistent = get_queue("does_not_exist")
    assert nonexistent is None
    
    # Test list_queues
    queue_names = list_queues()
    assert "factory_test1" in queue_names
    assert "factory_test2" in queue_names


def test_error_conditions_and_edge_cases(mock_syftbox_env):
    """Test various error conditions and edge cases."""
    queue = q("error_test", force=True)
    
    # Test job creation with missing parameters
    with pytest.raises(TypeError):
        queue.create_job("test")  # Missing required parameters
    
    # Test invalid status transition
    job = queue.create_job("error_job", "user@test.com", "owner@test.com")
    with pytest.raises(ValueError):
        job.update_status("invalid_status")
    
    # Test file system errors
    job2 = queue.create_job("fs_error_job", "user@test.com", "owner@test.com")
    
    # Mock file system error during job movement
    with patch('shutil.move', side_effect=OSError("File system error")):
        # Should not crash, just log error
        job2.update_status(JobStatus.approved)


def test_job_syft_object_integration(mock_syftbox_env):
    """Test Job syft-object integration."""
    queue = q("syft_object_test", force=True)
    job = queue.create_job("syft_job", "user@test.com", "owner@test.com")
    
    # Test that syft-object was created
    assert hasattr(job, '_syft_object')
    
    # Test syft-object structure
    syft_yaml = job.object_path / "syftobject.yaml"
    assert syft_yaml.exists()
    
    with open(syft_yaml) as f:
        metadata = yaml.safe_load(f)
    assert metadata["type"] == "SyftBox Job"
    
    # Test private and mock folders
    assert (job.object_path / "private").exists()
    assert (job.object_path / "mock").exists()
    assert (job.object_path / "private" / "job_data.json").exists()
    assert (job.object_path / "mock" / "job_data.json").exists()


def test_queue_with_owner_email(mock_syftbox_env):
    """Test queue creation with specific owner email."""
    queue = q("owner_test", owner_email="owner@test.com", force=True)
    
    # Create job to test owner propagation
    job = queue.create_job("owned_job", "user@test.com", "target@test.com")
    assert job is not None


def test_relative_path_updates(mock_syftbox_env, sample_code_dir):
    """Test relative path updates during job lifecycle."""
    queue = q("relative_path_test", force=True)
    job = queue.create_job(
        "path_job",
        "user@test.com",
        "owner@test.com",
        code_folder=str(sample_code_dir)
    )
    
    # Test that relative paths are set
    assert job.code_folder_relative is not None
    
    # Test path updates
    job.update_relative_paths()
    assert job.code_folder_relative == "code"