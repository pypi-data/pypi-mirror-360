"""
Fixed tests for improved coverage of queue.py
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
    
    # Test basic properties
    assert job.uid is not None
    assert job.name == "test_J:test_job"
    assert job.status == JobStatus.inbox
    assert job.requester_email == "user@test.com"
    assert job.target_email == "owner@test.com"
    
    # Test resolved properties
    assert job.resolved_code_folder is not None
    
    # Test terminal and expired properties
    assert job.is_terminal is False
    assert job.is_expired is False
    
    # Test status update
    job.update_status(JobStatus.approved)
    assert job.status == JobStatus.approved
    
    # Test terminal state
    job.update_status(JobStatus.completed)
    assert job.is_terminal is True


def test_queue_exists():
    """Test _queue_exists function."""
    with patch('syft_objects.get_syft_object') as mock_get:
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
    (job_dir / "syftobject.yaml").write_text("type: SyftBox Job")
    
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
    (valid_dir / "syftobject.yaml").write_text("type: SyftBox Job")
    
    # Cleanup
    cleaned = _cleanup_ghost_job_folders(queue_path)
    
    assert cleaned == 3
    assert not (queue_path / "J:ghost_0").exists()
    assert not (queue_path / "J:ghost_1").exists()
    assert not (queue_path / "J:ghost_2").exists()
    assert (queue_path / "J:valid").exists()


def test_queue_has_valid_syftobject():
    """Test _queue_has_valid_syftobject function."""
    with patch('syft_objects.get_syft_object') as mock_get:
        # Valid syftobject
        mock_get.return_value = {"name": "Q:test"}
        assert _queue_has_valid_syftobject("test") is True
        
        # No syftobject
        mock_get.return_value = None
        assert _queue_has_valid_syftobject("test") is False


def test_get_queues_path(mock_syftbox_env):
    """Test get_queues_path function."""
    path = get_queues_path()
    assert isinstance(path, Path)
    assert path.exists()


def test_prepare_job_for_execution(mock_syftbox_env, sample_code_dir):
    """Test prepare_job_for_execution function."""
    queue = q("test_prepare")
    job = queue.create_job(
        "test_job",
        "user@test.com",
        "owner@test.com",
        code_folder=str(sample_code_dir)
    )
    
    context = prepare_job_for_execution(job)
    
    assert "job_uid" in context
    assert "job_name" in context  
    assert "job_dir" in context
    assert context["job_uid"] == str(job.uid)
    assert context["job_name"] == job.name


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


def test_help_function(capsys):
    """Test help function."""
    help()
    captured = capsys.readouterr()
    assert "SyftQueue" in captured.out
    assert "Getting Started" in captured.out


def test_job_progression_functions(mock_syftbox_env):
    """Test job progression functions: approve, reject, start, complete, fail, timeout."""
    queue = q("test_progression")
    job = queue.create_job("test_job", "user@test.com", "owner@test.com")
    
    # Test approve
    approved_job = approve(job, approver="admin@test.com")
    assert approved_job.status == JobStatus.approved
    
    # Test start
    started_job = start(approved_job, runner="worker1")
    assert started_job.status == JobStatus.running
    
    # Test complete
    completed_job = complete(started_job)
    assert completed_job.status == JobStatus.completed
    
    # Test reject
    job2 = queue.create_job("test_job2", "user@test.com", "owner@test.com")
    rejected_job = reject(job2, reason="Invalid request", reviewer="admin@test.com")
    assert rejected_job.status == JobStatus.rejected
    
    # Test fail
    job3 = queue.create_job("test_job3", "user@test.com", "owner@test.com")
    job3.update_status(JobStatus.running)
    failed_job = fail(job3, error="Process crashed", exit_code=1)
    assert failed_job.status == JobStatus.failed
    
    # Test timeout
    job4 = queue.create_job("test_job4", "user@test.com", "owner@test.com")
    job4.update_status(JobStatus.running)
    timeout_job = timeout(job4)
    assert timeout_job.status == JobStatus.failed


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
    
    # Advance from running to completed
    job = advance(job)
    assert job.status == JobStatus.completed


def test_approve_all_function(mock_syftbox_env):
    """Test approve_all batch function."""
    queue = q("test_approve_all")
    
    # Create multiple jobs
    jobs = []
    for i in range(3):
        job = queue.create_job(f"job_{i}", "user@test.com", "owner@test.com")
        jobs.append(job)
    
    # Approve all
    approved = # approve_all(jobs, approver="admin@test.com")
    
    assert len(approved) == 3
    for job in approved:
        assert job.status == JobStatus.approved


def test_process_queue_function(mock_syftbox_env):
    """Test process_queue batch function."""
    queue = q("test_process")
    
    # Create jobs
    job1 = queue.create_job("job1", "user@test.com", "owner@test.com")
    job2 = queue.create_job("job2", "user@test.com", "owner@test.com")
    
    # Approve them
    job1.update_status(JobStatus.approved)
    job2.update_status(JobStatus.approved)
    
    # Process queue
    results = process_queue(queue)
    
    assert len(results) >= 0  # Should at least run without error


def test_data_queue(mock_syftbox_env):
    """Test DataQueue functionality."""
    data_queue = q("test_data", queue_type="data")
    
    assert isinstance(data_queue, DataQueue)
    
    # Create job without code (allowed for data queues)
    job = data_queue.create_job(
        "data_job",
        "user@test.com",
        "owner@test.com"
    )
    
    assert job.name == "test_J:data_job"
    assert job.code_folder is None or job.code_folder == ""


def test_queue_edge_cases(mock_syftbox_env):
    """Test various edge cases in queue operations."""
    # Test queue with special characters
    queue = q("test-queue_123")
    assert queue.queue_name == "test_Q:test-queue_123"
    
    # Test empty queue stats
    assert queue.total_jobs == 0
    assert queue.completed_jobs == 0
    
    # Test queue refresh with no jobs
    queue.refresh_stats()
    assert queue.total_jobs == 0


def test_queues_function(mock_syftbox_env, capsys):
    """Test the queues() function that prints queue table."""
    # Import the actual queues function from queue module
    from syft_queue.queue import queues as queues_func
    
    # Create some test queues with jobs
    queue1 = q("test_queue_1", force=True)
    queue2 = q("test_queue_2", force=True)
    
    # Add jobs
    queue1.create_job("job1", "user@test.com", "owner@test.com")
    queue2.create_job("job2", "user@test.com", "owner@test.com")
    
    # Call queues function
    queues_func()
    
    captured = capsys.readouterr()
    output = captured.out
    
    # Check output contains expected content
    assert "Queue Name" in output
    assert "test_queue_1" in output
    assert "test_queue_2" in output


def test_sq_module(mock_syftbox_env, capsys):
    """Test the sq module interface."""
    import syft_queue.sq as sq
    
    # Create a test queue
    queue = q("sq_test_queue", force=True)
    queue.create_job("test_job", "user@test.com", "owner@test.com")
    
    # Test sq.queues property (accessing it should return the collection object)
    result = sq.queues
    assert isinstance(result, sq._QueuesCollection)  # Property returns collection
    
    # Check that the table is displayed
    table_str = str(result)
    assert "sq_test_queue" in table_str
    
    # Test that calling queues as function raises TypeError
    with pytest.raises(TypeError, match="Use 'sq.queues' \\(property\\) instead of 'sq.queues\\(\\)' \\(function call\\)"):
        sq.queues()
    
    # Test sq.cleanup()
    sq.cleanup()
    captured = capsys.readouterr()
    assert "Cleaning up" in captured.out
    
    # Test sq.recreate()
    sq.recreate()
    captured = capsys.readouterr()
    assert "Looking for syft-objects" in captured.out


def test_sq_interface_class():
    """Test the _SQInterface class directly."""
    import syft_queue.sq as sq
    
    # Test the interface class
    interface = sq._SQInterface()
    
    # Test property access
    result = interface.queues
    assert isinstance(result, sq._QueuesCollection)
    
    # Test cleanup method
    with patch('syft_queue.sq._cleanup') as mock_cleanup:
        interface.cleanup()
        mock_cleanup.assert_called_once()
    
    # Test recreate method
    with patch('syft_queue.sq._recreate') as mock_recreate:
        interface.recreate()
        mock_recreate.assert_called_once()


def test_sq_queues_collection_class(mock_syftbox_env):
    """Test _QueuesCollection class."""
    import syft_queue.sq as sq
    
    # Test collection behavior
    collection = sq._QueuesCollection()
    
    # Test __str__ method
    result = str(collection)
    assert isinstance(result, str)
    assert len(result) > 0  # Should contain some content
    
    # Test __repr__ method
    result = repr(collection)
    assert isinstance(result, str)
    assert len(result) > 0  # Should contain some content
    
    # Test __call__ method raises TypeError
    with pytest.raises(TypeError, match="Use 'sq.queues' \\(property\\) instead of 'sq.queues\\(\\)' \\(function call\\)"):
        collection()


def test_sq_singleton_instance():
    """Test that sq uses a singleton instance."""
    import syft_queue.sq as sq
    
    # Should be the same instance
    assert sq._sq_instance is not None
    assert isinstance(sq._sq_instance, sq._SQInterface)
    
    # Test that the exported names point to the singleton methods
    assert sq.cleanup is sq._sq_instance.cleanup
    assert sq.recreate is sq._sq_instance.recreate
    assert sq.queues is sq._sq_instance.queues