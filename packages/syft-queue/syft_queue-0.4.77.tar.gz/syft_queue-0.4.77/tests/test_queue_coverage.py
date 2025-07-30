"""
Additional tests to improve coverage for queue.py
"""

import pytest
import tempfile
import json
import shutil
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime
import subprocess

from syft_queue import (
    q, Queue, Job, JobStatus, DataQueue,
    _generate_mock_data, _queue_exists, _cleanup_empty_queue_directory,
    _is_ghost_job_folder, _cleanup_ghost_job_folders, _cleanup_all_ghost_job_folders,
    _cleanup_orphaned_queue_directories, _cleanup_all_orphaned_queue_directories,
    _queue_has_valid_syftobject, get_queues_path, list_queues, queues,
    prepare_job_for_execution, execute_job_with_context,
    approve, reject, start, complete, fail, timeout, advance,
    approve_all, process_queue, help
)


def test_generate_mock_data():
    """Test mock data generation for privacy protection."""
    real_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30,
        "nested": {
            "address": "123 Main St",
            "city": "Somewhere"
        }
    }
    
    mock_data = _generate_mock_data(real_data)
    
    # Check that values are mocked
    assert mock_data["name"] != "John Doe"
    assert mock_data["email"] != "john@example.com"
    assert mock_data["age"] != 30
    assert mock_data["nested"]["address"] != "123 Main St"
    assert mock_data["nested"]["city"] != "Somewhere"
    
    # Check structure is preserved
    assert set(mock_data.keys()) == set(real_data.keys())
    assert set(mock_data["nested"].keys()) == set(real_data["nested"].keys())


def test_job_properties(mock_syftbox_env, sample_code_dir):
    """Test various Job properties and methods."""
    queue = q("test_job_props")
    job = queue.create_job(
        "test_job",
        "user@test.com",
        "owner@test.com",
        code_folder=str(sample_code_dir)
    )
    
    # Test job_id property
    assert job.job_id == job.id
    
    # Test job_dir property
    assert job.job_dir == job.job_folder_absolute
    
    # Test has_code property
    assert job.has_code is True
    
    # Test description setter
    job.description = "New description"
    assert job.description == "New description"
    
    # Test notes setter
    job.notes = ["Note 1", "Note 2"]
    assert job.notes == ["Note 1", "Note 2"]
    
    # Test get method
    assert job.get("status") == JobStatus.inbox
    assert job.get("nonexistent", "default") == "default"
    
    # Test update method
    job.update({"custom_field": "value"})
    assert job.custom_field == "value"
    
    # Test dict conversion
    job_dict = job.to_dict()
    assert isinstance(job_dict, dict)
    assert job_dict["name"] == "test_J:test_job"
    
    # Test string representation
    str_repr = str(job)
    assert "test_J:test_job" in str_repr
    assert "inbox" in str_repr
    
    # Test repr
    repr_str = repr(job)
    assert "Job" in repr_str


def test_job_with_mock_data(mock_syftbox_env):
    """Test job creation with mock_data parameter."""
    queue = q("test_mock_data")
    
    # Create job with mock data enabled
    job = queue.create_job(
        "test_job",
        "user@test.com",
        "owner@test.com",
        data={"sensitive": "info"},
        mock_data=True
    )
    
    # Data should be mocked
    assert job.data["sensitive"] != "info"


def test_job_error_handling(mock_syftbox_env):
    """Test job error conditions."""
    queue = q("test_errors")
    job = queue.create_job("test_job", "user@test.com", "owner@test.com")
    
    # Test invalid status updates
    with pytest.raises(ValueError):
        job.update_status("invalid_status")
    
    # Test job deletion
    job.delete()
    assert not job.object_path.exists()


def test_queue_exists():
    """Test _queue_exists function."""
    with patch('syft_queue.queue.get_syft_object') as mock_get:
        # Queue exists
        mock_get.return_value = {"name": "Q:test"}
        assert _queue_exists("test") is True
        
        # Queue doesn't exist
        mock_get.return_value = None
        assert _queue_exists("nonexistent") is False


def test_cleanup_empty_queue_directory(tmp_path):
    """Test _cleanup_empty_queue_directory function."""
    # Create empty queue directory
    queue_dir = tmp_path / "Q:empty_queue"
    queue_dir.mkdir()
    
    # Should be removed
    _cleanup_empty_queue_directory(queue_dir)
    assert not queue_dir.exists()
    
    # Create non-empty queue directory
    queue_dir.mkdir()
    (queue_dir / "somefile.txt").write_text("content")
    
    # Should not be removed
    _cleanup_empty_queue_directory(queue_dir)
    assert queue_dir.exists()


def test_is_ghost_job_folder(tmp_path):
    """Test _is_ghost_job_folder function."""
    # Create valid job folder with syftobject
    job_dir = tmp_path / "J:valid_job"
    job_dir.mkdir()
    (job_dir / ".syftobject").write_text("{}")
    
    assert _is_ghost_job_folder(job_dir) is False
    
    # Create ghost job folder (no syftobject)
    ghost_dir = tmp_path / "J:ghost_job"
    ghost_dir.mkdir()
    
    assert _is_ghost_job_folder(ghost_dir) is True
    
    # Non-job folder
    other_dir = tmp_path / "not_a_job"
    other_dir.mkdir()
    
    assert _is_ghost_job_folder(other_dir) is False


def test_cleanup_ghost_job_folders(tmp_path):
    """Test _cleanup_ghost_job_folders function."""
    queue_path = tmp_path / "Q:test_queue"
    queue_path.mkdir()
    
    # Create ghost job folders
    for i in range(3):
        ghost_dir = queue_path / f"J:ghost_{i}"
        ghost_dir.mkdir()
    
    # Create valid job folder
    valid_dir = queue_path / "J:valid"
    valid_dir.mkdir()
    (valid_dir / ".syftobject").write_text("{}")
    
    # Cleanup
    cleaned = _cleanup_ghost_job_folders(queue_path)
    
    assert cleaned == 3
    assert not (queue_path / "J:ghost_0").exists()
    assert not (queue_path / "J:ghost_1").exists()
    assert not (queue_path / "J:ghost_2").exists()
    assert (queue_path / "J:valid").exists()


def test_cleanup_all_ghost_job_folders(mock_syftbox_env):
    """Test _cleanup_all_ghost_job_folders function."""
    with patch('syft_queue.queue._cleanup_ghost_job_folders') as mock_cleanup:
        mock_cleanup.return_value = 2
        
        total = _cleanup_all_ghost_job_folders()
        
        # Should be called for each queue directory
        assert mock_cleanup.called
        assert total >= 0


def test_queue_has_valid_syftobject():
    """Test _queue_has_valid_syftobject function."""
    with patch('syft_queue.queue.get_syft_object') as mock_get:
        # Valid syftobject
        mock_get.return_value = {"name": "Q:test"}
        assert _queue_has_valid_syftobject("test") is True
        
        # No syftobject
        mock_get.return_value = None
        assert _queue_has_valid_syftobject("test") is False


def test_cleanup_orphaned_queue_directories(tmp_path):
    """Test _cleanup_orphaned_queue_directories function."""
    # Create orphaned queue directory
    orphan_dir = tmp_path / "Q:orphan"
    orphan_dir.mkdir()
    
    # Create valid queue directory
    valid_dir = tmp_path / "Q:valid"
    valid_dir.mkdir()
    
    with patch('syft_queue.queue._queue_has_valid_syftobject') as mock_has:
        mock_has.side_effect = lambda name: name == "valid"
        
        cleaned = _cleanup_orphaned_queue_directories(tmp_path)
        
        assert cleaned == 1
        assert not orphan_dir.exists()
        assert valid_dir.exists()


def test_cleanup_all_orphaned_queue_directories(mock_syftbox_env):
    """Test _cleanup_all_orphaned_queue_directories function."""
    with patch('syft_queue.queue._cleanup_orphaned_queue_directories') as mock_cleanup:
        mock_cleanup.return_value = 3
        
        total = _cleanup_all_orphaned_queue_directories()
        
        assert mock_cleanup.called
        assert total == 3


def test_get_queues_path(mock_syftbox_env):
    """Test get_queues_path function."""
    path = get_queues_path()
    assert isinstance(path, Path)
    assert path.name == "queues"


def test_list_queues_empty(mock_syftbox_env):
    """Test list_queues with no queues."""
    queues = list_queues()
    assert queues == []


def test_prepare_job_for_execution(mock_syftbox_env, sample_code_dir):
    """Test prepare_job_for_execution function."""
    queue = q("test_prepare")
    job = queue.create_job(
        "test_job",
        "user@test.com",
        "owner@test.com",
        code_folder=str(sample_code_dir),
        data={"key": "value"}
    )
    
    context = prepare_job_for_execution(job)
    
    assert "job_id" in context
    assert "queue_name" in context
    assert "data" in context
    assert context["data"]["key"] == "value"
    
    # Test with no data
    job2 = queue.create_job("test_job2", "user@test.com", "owner@test.com")
    context2 = prepare_job_for_execution(job2)
    assert context2["data"] == {}


def test_execute_job_with_context(mock_syftbox_env, sample_code_dir):
    """Test execute_job_with_context function."""
    queue = q("test_execute")
    job = queue.create_job(
        "test_job",
        "user@test.com",
        "owner@test.com",
        code_folder=str(sample_code_dir)
    )
    
    # Test successful execution
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")
        
        success, output = execute_job_with_context(job)
        
        assert success is True
        assert "Success" in output
    
    # Test failed execution
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="Error")
        
        success, output = execute_job_with_context(job, runner_command="python")
        
        assert success is False
        assert "Error" in output
    
    # Test execution without code
    job2 = queue.create_job("test_job2", "user@test.com", "owner@test.com")
    
    with pytest.raises(ValueError, match="no code folder"):
        execute_job_with_context(job2)


def test_help_function(capsys):
    """Test help function."""
    help()
    captured = capsys.readouterr()
    assert "SyftQueue Help" in captured.out
    assert "Creating Queues" in captured.out


def test_job_progression_functions(mock_syftbox_env):
    """Test job progression functions: approve, reject, start, complete, fail, timeout."""
    queue = q("test_progression")
    job = queue.create_job("test_job", "user@test.com", "owner@test.com")
    
    # Test approve
    approved_job = approve(job, approver="admin@test.com", notes="Looks good")
    assert approved_job.status == JobStatus.approved
    assert "admin@test.com" in str(approved_job.notes)
    
    # Test start
    started_job = start(approved_job, runner="worker1")
    assert started_job.status == JobStatus.running
    
    # Test complete
    completed_job = complete(started_job, output_data={"result": "success"})
    assert completed_job.status == JobStatus.completed
    assert completed_job.output_data == {"result": "success"}
    
    # Test reject
    job2 = queue.create_job("test_job2", "user@test.com", "owner@test.com")
    rejected_job = reject(job2, reason="Invalid request", reviewer="admin@test.com")
    assert rejected_job.status == JobStatus.rejected
    assert "Invalid request" in str(rejected_job.notes)
    
    # Test fail
    job3 = queue.create_job("test_job3", "user@test.com", "owner@test.com")
    job3.update_status(JobStatus.running)
    failed_job = fail(job3, error="Process crashed", exit_code=1)
    assert failed_job.status == JobStatus.failed
    assert failed_job.exit_code == 1
    
    # Test timeout
    job4 = queue.create_job("test_job4", "user@test.com", "owner@test.com")
    job4.update_status(JobStatus.running)
    timeout_job = timeout(job4)
    assert timeout_job.status == JobStatus.failed
    assert "timed out" in str(timeout_job.notes)


def test_advance_function(mock_syftbox_env):
    """Test advance function for automatic progression."""
    queue = q("test_advance")
    job = queue.create_job("test_job", "user@test.com", "owner@test.com")
    
    # Advance from inbox to approved
    job = advance(job)
    assert job.status == JobStatus.approved
    
    # Advance from approved to running
    job = advance(job)
    assert job.status == JobStatus.running
    
    # Advance to specific status
    job2 = queue.create_job("test_job2", "user@test.com", "owner@test.com")
    job2 = advance(job2, to_status=JobStatus.completed)
    assert job2.status == JobStatus.completed
    
    # Test invalid progression
    job3 = queue.create_job("test_job3", "user@test.com", "owner@test.com")
    job3.update_status(JobStatus.completed)
    
    with pytest.raises(ValueError):
        advance(job3)


def test_approve_all_function(mock_syftbox_env):
    """Test approve_all batch function."""
    queue = q("test_approve_all")
    
    # Create multiple jobs
    jobs = []
    for i in range(3):
        job = queue.create_job(f"job_{i}", "user@test.com", "owner@test.com")
        jobs.append(job)
    
    # Approve all
    approved = approve_all(jobs, approver="admin@test.com")
    
    assert len(approved) == 3
    for job in approved:
        assert job.status == JobStatus.approved
    
    # Test with filter
    job4 = queue.create_job("special_job", "vip@test.com", "owner@test.com")
    jobs.append(job4)
    
    filtered = approve_all(
        jobs,
        approver="admin@test.com",
        filter_fn=lambda j: "vip" in j.requester_email
    )
    
    assert len(filtered) == 1
    assert filtered[0].name == "test_J:special_job"


def test_process_queue_function(mock_syftbox_env, sample_code_dir):
    """Test process_queue batch function."""
    queue = q("test_process")
    
    # Create jobs
    job1 = queue.create_job("job1", "user@test.com", "owner@test.com", code_folder=str(sample_code_dir))
    job2 = queue.create_job("job2", "user@test.com", "owner@test.com", code_folder=str(sample_code_dir))
    
    # Approve them
    job1.update_status(JobStatus.approved)
    job2.update_status(JobStatus.approved)
    
    # Mock execution
    def mock_processor(job):
        job.update_status(JobStatus.completed)
        return True
    
    # Process queue
    results = process_queue(
        queue,
        processor=mock_processor,
        status_filter=JobStatus.approved
    )
    
    assert len(results) == 2
    assert all(success for success, _ in results)
    
    # Refresh and check
    queue.refresh_stats()
    assert queue.completed_jobs == 2


def test_data_queue(mock_syftbox_env):
    """Test DataQueue functionality."""
    data_queue = q("test_data", queue_type="data")
    
    assert isinstance(data_queue, DataQueue)
    
    # Create job without code (allowed for data queues)
    job = data_queue.create_job(
        "data_job",
        "user@test.com",
        "owner@test.com",
        data={"dataset": "important"}
    )
    
    assert job.data == {"dataset": "important"}
    assert job.code_folder is None
    
    # Process should work without code
    context = prepare_job_for_execution(job)
    assert "data" in context


def test_queue_edge_cases(mock_syftbox_env):
    """Test various edge cases in queue operations."""
    # Test queue with special characters
    queue = q("test-queue_123")
    assert queue.queue_name == "test_Q:test-queue_123"
    
    # Test empty queue stats
    assert queue.total_jobs == 0
    assert queue.pending_jobs == []
    assert queue.completed_jobs == 0
    
    # Test queue refresh with no jobs
    queue.refresh_stats()
    assert queue.total_jobs == 0
    
    # Test invalid queue type
    with pytest.raises(ValueError):
        q("invalid", queue_type="invalid_type")


def test_job_validation(mock_syftbox_env):
    """Test job validation and error handling."""
    queue = q("test_validation")
    
    # Test missing required fields
    with pytest.raises(TypeError):
        queue.create_job("test")  # Missing emails
    
    # Test invalid email format (if validation exists)
    job = queue.create_job(
        "test_job",
        "invalid-email",  # May or may not be validated
        "owner@test.com"
    )
    assert job.requester_email == "invalid-email"


def test_concurrent_queue_access(mock_syftbox_env):
    """Test concurrent access to queues."""
    queue_name = "concurrent_test"
    
    # Create queue in one instance
    queue1 = q(queue_name)
    job1 = queue1.create_job("job1", "user@test.com", "owner@test.com")
    
    # Access from another instance
    queue2 = q(queue_name)
    assert queue2.total_jobs == 1
    
    # Create job from second instance
    job2 = queue2.create_job("job2", "user@test.com", "owner@test.com")
    
    # Check both instances see updates
    queue1.refresh_stats()
    assert queue1.total_jobs == 2
    assert queue2.total_jobs == 2


def test_queues_function(mock_syftbox_env, capsys):
    """Test the queues() function that prints queue table."""
    # Create some test queues with jobs
    queue1 = q("test_queue_1")
    queue2 = q("test_queue_2", queue_type="data")
    
    # Add jobs in different states
    job1 = queue1.create_job("job1", "user@test.com", "owner@test.com")
    job2 = queue1.create_job("job2", "user@test.com", "owner@test.com")
    job3 = queue2.create_job("job3", "user@test.com", "owner@test.com")
    
    job1.update_status(JobStatus.approved)
    job2.update_status(JobStatus.completed)
    
    # Call queues function
    queues()
    
    captured = capsys.readouterr()
    output = captured.out
    
    # Check output contains expected content
    assert "Queue Name" in output
    assert "test_queue_1" in output
    assert "test_queue_2" in output
    assert "Code" in output  # queue1 type
    assert "Data" in output  # queue2 type
    
    # Test with no queues
    # Clean up existing queues
    import shutil
    queues_path = get_queues_path()
    for queue_dir in queues_path.iterdir():
        if queue_dir.is_dir():
            shutil.rmtree(queue_dir)
    
    queues()
    captured = capsys.readouterr()
    assert "No queues found" in captured.out


def test_sq_module(mock_syftbox_env, capsys):
    """Test the sq module interface."""
    import syft_queue.sq as sq
    
    # Create a test queue
    queue = q("sq_test_queue")
    queue.create_job("test_job", "user@test.com", "owner@test.com")
    
    # Test sq.queues()
    sq.queues()
    
    captured = capsys.readouterr()
    assert "sq_test_queue" in captured.out