"""Tests for job deletion functionality"""

import pytest
from pathlib import Path
from uuid import uuid4

from syft_queue import CodeQueue, DataQueue, JobStatus
from syft_queue.test_utils import cleanup_all_test_artifacts


@pytest.fixture(autouse=True)
def cleanup():
    """Clean up test artifacts before and after tests."""
    cleanup_all_test_artifacts()
    yield
    cleanup_all_test_artifacts()


def test_job_delete_method():
    """Test the delete() method on Job objects."""
    # Create a queue and job
    queue = CodeQueue("test_delete_method")
    # Refresh stats to ensure we start from filesystem state
    queue.refresh_stats()
    
    job = queue.create_job(
        name="test_job_delete",
        requester_email="test@example.com",
        target_email="owner@example.com",
        description="Test job for deletion"
    )
    
    # Store job info
    job_uid = job.uid
    job_path = job.object_path
    
    # Verify job exists
    assert job_path.exists()
    assert queue.get_job(job_uid) is not None
    
    # Delete the job
    success = job.delete()
    assert success is True
    
    # Verify job is deleted
    assert not job_path.exists()
    assert queue.get_job(job_uid) is None
    
    # Verify statistics are updated
    stats = queue.get_stats()
    assert stats['total_jobs'] == 0
    assert stats['inbox_jobs'] == 0


def test_queue_delete_job_method():
    """Test the delete_job() method on Queue objects."""
    # Create a queue with multiple jobs
    queue = DataQueue("test_queue_delete")
    # Refresh stats to ensure we start from filesystem state
    queue.refresh_stats()
    
    job_uids = []
    
    for i in range(3):
        job = queue.create_job(
            name=f"test_job_{i}",
            requester_email="test@example.com",
            target_email="owner@example.com"
        )
        job_uids.append(job.uid)
    
    # Verify initial state
    stats = queue.get_stats()
    assert stats['total_jobs'] == 3
    assert stats['inbox_jobs'] == 3
    
    # Delete a job using queue method
    success = queue.delete_job(job_uids[0])
    assert success is True
    
    # Verify job is deleted
    assert queue.get_job(job_uids[0]) is None
    assert queue.get_job(job_uids[1]) is not None
    assert queue.get_job(job_uids[2]) is not None
    
    # Verify statistics
    queue.refresh_stats()
    stats = queue.get_stats()
    assert stats['total_jobs'] == 2
    assert stats['inbox_jobs'] == 2


def test_delete_nonexistent_job():
    """Test deleting a job that doesn't exist."""
    queue = CodeQueue("test_delete_nonexistent")
    
    # Try to delete a job that doesn't exist
    fake_uid = uuid4()
    success = queue.delete_job(fake_uid)
    assert success is False


def test_delete_job_in_different_status():
    """Test deleting jobs in different statuses."""
    queue = CodeQueue("test_delete_status")
    
    # Create jobs and move them to different statuses
    job1 = queue.create_job("job1", "test@example.com", "owner@example.com")
    job2 = queue.create_job("job2", "test@example.com", "owner@example.com")
    job3 = queue.create_job("job3", "test@example.com", "owner@example.com")
    
    # Move jobs to different statuses
    job1.update_status(JobStatus.approved)
    job2.update_status(JobStatus.running)
    job3.update_status(JobStatus.completed)
    
    # Verify jobs are in different directories
    assert not (queue.object_path / "jobs" / "inbox" / str(job1.uid)).exists()
    assert (queue.object_path / "jobs" / "approved" / str(job1.uid)).exists()
    
    # Delete jobs in different statuses
    assert job1.delete() is True
    assert job2.delete() is True
    assert job3.delete() is True
    
    # Verify all jobs are deleted
    assert queue.get_job(job1.uid) is None
    assert queue.get_job(job2.uid) is None
    assert queue.get_job(job3.uid) is None
    
    # Verify statistics
    queue.refresh_stats()
    stats = queue.get_stats()
    assert stats['total_jobs'] == 0
    assert stats['approved_jobs'] == 0
    assert stats['running_jobs'] == 0
    assert stats['completed_jobs'] == 0


def test_delete_job_updates_queue_stats():
    """Test that deleting jobs properly updates queue statistics."""
    queue = DataQueue("test_stats_update")
    # Refresh stats to ensure we start from filesystem state
    queue.refresh_stats()
    
    # Create jobs in different statuses
    jobs = []
    for i in range(5):
        job = queue.create_job(f"job_{i}", "test@example.com", "owner@example.com")
        jobs.append(job)
    
    # Move some jobs to different statuses
    jobs[1].update_status(JobStatus.approved)
    jobs[2].update_status(JobStatus.running)
    jobs[3].update_status(JobStatus.completed)
    jobs[4].update_status(JobStatus.failed)
    
    # Initial statistics
    queue.refresh_stats()
    initial_stats = queue.get_stats()
    assert initial_stats['total_jobs'] == 5
    assert initial_stats['inbox_jobs'] == 1
    assert initial_stats['approved_jobs'] == 1
    assert initial_stats['running_jobs'] == 1
    assert initial_stats['completed_jobs'] == 1
    assert initial_stats['failed_jobs'] == 1
    
    # Delete jobs from different statuses
    jobs[0].delete()  # inbox
    jobs[2].delete()  # running
    jobs[4].delete()  # failed
    
    # Check updated statistics
    queue.refresh_stats()
    updated_stats = queue.get_stats()
    assert updated_stats['total_jobs'] == 2
    assert updated_stats['inbox_jobs'] == 0
    assert updated_stats['approved_jobs'] == 1
    assert updated_stats['running_jobs'] == 0
    assert updated_stats['completed_jobs'] == 1
    assert updated_stats['failed_jobs'] == 0


def test_delete_job_with_files():
    """Test deleting a job that contains additional files."""
    queue = CodeQueue("test_delete_with_files")
    
    # Create a job
    job = queue.create_job(
        name="job_with_files",
        requester_email="test@example.com",
        target_email="owner@example.com"
    )
    
    # Add some extra files to the job directory
    (job.object_path / "extra_file.txt").write_text("test content")
    (job.object_path / "extra_dir").mkdir()
    (job.object_path / "extra_dir" / "nested_file.txt").write_text("nested content")
    
    # Verify files exist
    assert (job.object_path / "extra_file.txt").exists()
    assert (job.object_path / "extra_dir" / "nested_file.txt").exists()
    
    # Delete the job
    success = job.delete()
    assert success is True
    
    # Verify entire directory is gone
    assert not job.object_path.exists()
    assert not (job.object_path / "extra_file.txt").exists()
    assert not (job.object_path / "extra_dir").exists()