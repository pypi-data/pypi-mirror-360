"""
Additional coverage push tests - targeting higher coverage
"""

import pytest
import os
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime, timedelta
from uuid import uuid4


def test_queue_additional_operations():
    """Test additional queue operations for coverage"""
    from syft_queue import q, JobStatus, DataQueue
    
    # Create different queue types
    code_queue = q("additional_code", queue_type="code", force=True)
    data_queue = q("additional_data", queue_type="data", force=True)
    
    # Verify types
    assert not isinstance(code_queue, DataQueue)
    assert isinstance(data_queue, DataQueue)
    
    # Test queue with more complex job creation
    job = code_queue.create_job(
        "complex_job",
        "complex@test.com",
        "target@test.com",
        description="A complex test job",
        data={"input": [1, 2, 3], "config": {"param": "value"}},
        mock_data=False,
        metadata={"priority": "high", "tags": ["test", "complex"]}
    )
    
    # Test job properties
    assert job.description == "A complex test job"
    assert job.data["input"] == [1, 2, 3]
    assert job.metadata["priority"] == "high"
    
    # Test queue operations
    all_jobs = code_queue.list_jobs()
    assert len(all_jobs) >= 1
    
    found_job = code_queue.get_job(job.uid)
    assert found_job.uid == job.uid
    
    # Test queue statistics
    stats = code_queue.get_stats()
    assert stats["total_jobs"] >= 1
    assert stats["inbox"] >= 1


def test_job_path_operations_extended():
    """Test extended job path operations"""
    from syft_queue import q
    
    queue = q("path_extended", force=True)
    job = queue.create_job("path_job", "user@test.com", "owner@test.com")
    
    # Test update_relative_paths with various scenarios
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Set up code and output folders
        code_dir = temp_path / "code"
        code_dir.mkdir()
        output_dir = temp_path / "output"
        output_dir.mkdir()
        
        job.code_folder = str(code_dir)
        job.output_folder = str(output_dir)
        
        # Call update_relative_paths
        job.update_relative_paths()
        
        # Verify relative paths were set (if the method exists)
        if hasattr(job, 'code_folder_relative'):
            assert job.code_folder_relative is not None
        if hasattr(job, 'output_folder_relative'):
            assert job.output_folder_relative is not None


def test_progression_api_extended():
    """Test extended progression API functionality"""
    from syft_queue import q, approve, reject, start, complete, fail, timeout, advance, JobStatus
    
    queue = q("progression_extended", force=True)
    
    # Create multiple jobs for testing
    jobs = []
    for i in range(5):
        job = queue.create_job(f"prog_job_{i}", f"user{i}@test.com", "owner@test.com")
        jobs.append(job)
    
    # Test progression with additional parameters
    approved_job = approve(jobs[0], approver="admin@test.com", notes="Approved for testing")
    assert approved_job.status == JobStatus.approved
    
    rejected_job = reject(jobs[1], reason="Invalid input", reviewer="admin@test.com")
    assert rejected_job.status == JobStatus.rejected
    
    # Test start with runner information
    started_job = start(approved_job, runner="worker_1", notes="Starting on worker 1")
    assert started_job.status == JobStatus.running
    
    # Test complete with output
    completed_job = complete(started_job, output="Job completed successfully", duration_seconds=30)
    assert completed_job.status == JobStatus.completed
    
    # Test fail with error details
    job_to_fail = queue.create_job("fail_job", "user@test.com", "owner@test.com")
    job_to_fail.update_status(JobStatus.running)
    failed_job = fail(job_to_fail, error="Process failed with error code 1", exit_code=1)
    assert failed_job.status == JobStatus.failed
    
    # Test timeout
    job_to_timeout = queue.create_job("timeout_job", "user@test.com", "owner@test.com")
    job_to_timeout.update_status(JobStatus.running)
    timed_out_job = timeout(job_to_timeout)
    assert timed_out_job.status == JobStatus.failed
    
    # Test advance
    advanced_job = advance(jobs[2])
    assert advanced_job.status == JobStatus.approved


def test_global_utility_functions():
    """Test global utility functions"""
    from syft_queue import (
        list_queues, get_queue, cleanup_orphaned_queues,
        recreate_missing_queue_directories, get_queues_path, help
    )
    
    # Test list_queues
    queues_list = list_queues()
    assert isinstance(queues_list, list)
    
    # Test get_queues_path
    path = get_queues_path()
    assert isinstance(path, Path)
    
    # Test utility functions (these should run without error)
    cleanup_orphaned_queues()
    recreate_missing_queue_directories()
    
    # Test help function
    with patch('builtins.print') as mock_print:
        help()
        mock_print.assert_called()
    
    # Test get_queue with existing and non-existing queues
    from syft_queue import q
    test_queue = q("utility_test", force=True)
    
    found = get_queue("utility_test")
    assert found is not None
    
    not_found = get_queue("nonexistent_queue_xyz")
    assert not_found is None


def test_job_lifecycle_comprehensive():
    """Test comprehensive job lifecycle"""
    from syft_queue import q, JobStatus
    
    queue = q("lifecycle_comprehensive", force=True)
    
    # Create job and test full lifecycle
    job = queue.create_job("lifecycle_job", "user@test.com", "owner@test.com")
    
    # Test initial state
    assert job.status == JobStatus.inbox
    assert not job.is_terminal
    assert not job.is_approved
    assert not job.is_running
    assert not job.is_completed
    assert not job.is_failed
    assert not job.is_rejected
    
    # Test progression through states
    job.update_status(JobStatus.approved)
    assert job.is_approved
    assert not job.is_terminal
    
    job.update_status(JobStatus.running)
    assert job.is_running
    assert not job.is_terminal
    
    job.update_status(JobStatus.completed)
    assert job.is_completed
    assert job.is_terminal
    
    # Test another job with failure path
    job2 = queue.create_job("failure_job", "user@test.com", "owner@test.com")
    job2.update_status(JobStatus.approved)
    job2.update_status(JobStatus.running)
    job2.update_status(JobStatus.failed)
    assert job2.is_failed
    assert job2.is_terminal
    
    # Test rejection path
    job3 = queue.create_job("rejected_job", "user@test.com", "owner@test.com")
    job3.update_status(JobStatus.rejected)
    assert job3.is_rejected
    assert job3.is_terminal


def test_job_serialization():
    """Test job serialization and deserialization"""
    from syft_queue import q, Job
    
    queue = q("serialization_test", force=True)
    job = queue.create_job(
        "serial_job",
        "user@test.com",
        "owner@test.com",
        description="Serialization test",
        data={"test": "data"},
        metadata={"version": "1.0"}
    )
    
    # Save job
    job.save()
    
    # Load job from disk
    loaded_job = Job(job.object_path, owner_email="owner@test.com")
    
    # Verify loaded job matches original
    assert loaded_job.uid == job.uid
    assert loaded_job.name == job.name
    assert loaded_job.description == job.description
    assert loaded_job.requester_email == job.requester_email
    assert loaded_job.target_email == job.target_email


def test_queue_string_representations():
    """Test queue string representations"""
    from syft_queue import q
    
    queue = q("string_repr_test", force=True)
    
    # Add some jobs
    for i in range(3):
        queue.create_job(f"repr_job_{i}", "user@test.com", "owner@test.com")
    
    # Test __str__
    str_result = str(queue)
    assert "string_repr_test" in str_result
    
    # Test __repr__
    repr_result = repr(queue)
    assert "Queue" in repr_result or "string_repr_test" in repr_result


def test_server_utils_remaining_coverage():
    """Test remaining server_utils functionality"""
    from syft_queue import server_utils
    
    # Test is_syftbox_mode with different scenarios
    result = server_utils.is_syftbox_mode()
    assert isinstance(result, bool)
    
    # Test ensure_server_healthy with different retry counts
    with patch('syft_queue.server_utils.is_server_running', return_value=True):
        assert server_utils.ensure_server_healthy(max_retries=1) is True
    
    with patch('syft_queue.server_utils.is_server_running', return_value=False):
        with patch('time.sleep'):
            assert server_utils.ensure_server_healthy(max_retries=1) is False


def test_data_queue_specific():
    """Test DataQueue specific functionality"""
    from syft_queue import q, DataQueue
    
    # Create data queue
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


def test_job_expiration_scenarios():
    """Test various job expiration scenarios"""
    from syft_queue import q
    
    queue = q("expiration_scenarios", force=True)
    
    # Test job with no updated_at (should not be expired)
    job1 = queue.create_job("no_update", "user@test.com", "owner@test.com")
    job1.updated_at = None
    assert not job1.is_expired
    
    # Test job with recent update (should not be expired)
    job2 = queue.create_job("recent_update", "user@test.com", "owner@test.com")
    job2.updated_at = datetime.now() - timedelta(days=1)
    assert not job2.is_expired
    
    # Test job with old update (should be expired)
    job3 = queue.create_job("old_update", "user@test.com", "owner@test.com")
    job3.updated_at = datetime.now() - timedelta(days=31)
    assert job3.is_expired
    
    # Test boundary case
    job4 = queue.create_job("boundary", "user@test.com", "owner@test.com")
    job4.updated_at = datetime.now() - timedelta(days=30, hours=1)
    assert not job4.is_expired


def test_approve_all_functionality():
    """Test approve_all function comprehensively"""
    from syft_queue import q, approve_all, JobStatus
    
    queue = q("approve_all_test", force=True)
    
    # Create multiple jobs
    jobs = []
    for i in range(5):
        job = queue.create_job(f"batch_job_{i}", "user@test.com", "owner@test.com")
        jobs.append(job)
    
    # Test approve_all
    approved_jobs = approve_all(jobs, approver="batch_admin@test.com")
    
    # Verify all jobs were approved
    assert len(approved_jobs) == 5
    for job in approved_jobs:
        assert job.status == JobStatus.approved
    
    # Test approve_all with mixed statuses
    mixed_jobs = []
    for i in range(3):
        job = queue.create_job(f"mixed_job_{i}", "user@test.com", "owner@test.com")
        mixed_jobs.append(job)
    
    # Approve one manually first
    mixed_jobs[0].update_status(JobStatus.approved)
    
    # Run approve_all
    approved_mixed = approve_all(mixed_jobs)
    
    # Should handle already approved jobs gracefully
    assert len(approved_mixed) >= 2