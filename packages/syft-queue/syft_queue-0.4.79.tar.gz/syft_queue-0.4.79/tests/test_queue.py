"""
Tests for core queue functionality.
"""

import pytest
from syft_queue import q, Queue, Job, JobStatus, get_queue, list_queues


def test_create_queue(mock_syftbox_env):
    """Test queue creation."""
    queue = q("test_queue")
    
    assert isinstance(queue, Queue)
    assert queue.queue_name == "test_Q:test_queue"  # In test mode, all queues get test_Q: prefix
    assert queue.total_jobs == 0
    assert queue.object_path.exists()


def test_queue_persistence(mock_syftbox_env):
    """Test that queues persist."""
    # Create queue
    queue1 = q("persistent_queue")
    queue1.create_job("test_job", "user@example.com", "owner@example.com")
    
    # Get same queue again
    queue2 = get_queue("persistent_queue")
    
    assert queue2 is not None
    assert queue2.total_jobs == 1
    assert queue2.queue_name == queue1.queue_name


def test_list_queues(mock_syftbox_env):
    """Test listing queues."""
    # Create multiple queues
    q("queue1")
    q("queue2")
    q("queue3")
    
    queues = list_queues()
    
    assert len(queues) == 3
    assert "queue1" in queues
    assert "queue2" in queues
    assert "queue3" in queues


def test_create_job(mock_syftbox_env, sample_code_dir):
    """Test job creation."""
    queue = q("job_test_queue")
    
    job = queue.create_job(
        name="test_analysis",
        requester_email="researcher@uni.edu",
        target_email="data_owner@company.com",
        code_folder=str(sample_code_dir),
        description="Test job creation"
    )
    
    assert isinstance(job, Job)
    assert job.name == "test_J:test_analysis"  # In test mode, jobs get test_ prefix
    assert job.status == JobStatus.inbox
    assert job.code_folder is not None
    assert job.code_folder_relative == "code"  # Should be relative


def test_job_status_tracking(mock_syftbox_env):
    """Test job status tracking in queue."""
    queue = q("status_test_queue")
    
    # Create jobs in different statuses
    job1 = queue.create_job("job1", "a@test.com", "b@test.com")
    job2 = queue.create_job("job2", "a@test.com", "b@test.com")
    job3 = queue.create_job("job3", "a@test.com", "b@test.com")
    
    # Check initial state
    assert queue.inbox_jobs == 3
    
    # Update statuses
    job1.update_status(JobStatus.approved)
    job2.update_status(JobStatus.running)
    job3.update_status(JobStatus.completed)
    
    # Refresh stats
    queue.refresh_stats()
    
    # Check counts
    assert queue.inbox_jobs == 0
    assert queue.approved_jobs == 1
    assert queue.running_jobs == 1
    assert queue.completed_jobs == 1


def test_list_jobs_by_status(mock_syftbox_env):
    """Test listing jobs by status."""
    queue = q("list_test_queue")
    
    # Create jobs
    for i in range(5):
        job = queue.create_job(f"job_{i}", "a@test.com", "b@test.com")
        if i < 2:
            job.update_status(JobStatus.approved)
        elif i < 4:
            job.update_status(JobStatus.running)
    
    # List by status
    inbox_jobs = queue.list_jobs(JobStatus.inbox)
    approved_jobs = queue.list_jobs(JobStatus.approved)
    running_jobs = queue.list_jobs(JobStatus.running)
    
    assert len(inbox_jobs) == 1
    assert len(approved_jobs) == 2
    assert len(running_jobs) == 2


def test_get_job_by_uid(mock_syftbox_env):
    """Test retrieving job by UID."""
    queue = q("uid_test_queue")
    
    # Create job
    original_job = queue.create_job("find_me", "a@test.com", "b@test.com")
    job_uid = original_job.uid
    
    # Get job by UID
    found_job = queue.get_job(job_uid)
    
    assert found_job is not None
    assert found_job.uid == job_uid
    assert found_job.name == "test_J:find_me"  # In test mode, jobs get test_ prefix


def test_job_expiration(mock_syftbox_env):
    """Test job expiration checking."""
    queue = q("expiration_test_queue")
    
    # Create job with short timeout
    job = queue.create_job(
        "quick_job",
        "a@test.com",
        "b@test.com",
        timeout_seconds=1
    )
    
    # Initially not expired
    assert not job.is_expired
    
    # Wait and check again
    import time
    time.sleep(2)
    
    assert job.is_expired


def test_job_terminal_states(mock_syftbox_env):
    """Test terminal state checking."""
    queue = q("terminal_test_queue")
    
    job = queue.create_job("test_job", "a@test.com", "b@test.com")
    
    # Non-terminal states
    for status in [JobStatus.inbox, JobStatus.approved, JobStatus.running]:
        job.status = status
        assert not job.is_terminal
    
    # Terminal states
    for status in [JobStatus.completed, JobStatus.failed, JobStatus.rejected, JobStatus.timedout]:
        job.status = status
        assert job.is_terminal