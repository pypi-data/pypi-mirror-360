"""
Tests for job progression API.
"""

import pytest
from syft_queue import (
    q, JobStatus,
    approve, reject, start, complete, fail, timeout, advance,
    approve_all, process_queue
)


def test_approve_job(mock_syftbox_env):
    """Test job approval."""
    queue = q("approval_test")
    job = queue.create_job("test", "a@test.com", "b@test.com")
    
    # Approve with metadata
    approved_job = approve(job, approver="admin@test.com", notes="Looks good")
    
    assert approved_job.status == JobStatus.approved
    assert hasattr(approved_job, 'approval_info')
    assert approved_job.approval_info['approver'] == "admin@test.com"
    assert approved_job.approval_info['notes'] == "Looks good"
    
    # Cannot approve non-inbox job
    with pytest.raises(ValueError):
        approve(approved_job)


def test_reject_job(mock_syftbox_env):
    """Test job rejection."""
    queue = q("rejection_test")
    job = queue.create_job("test", "a@test.com", "b@test.com")
    
    # Reject with reason
    rejected_job = reject(job, reason="Missing required data", reviewer="security@test.com")
    
    assert rejected_job.status == JobStatus.rejected
    assert rejected_job.error_message == "Missing required data"
    assert hasattr(rejected_job, 'rejection_info')
    assert rejected_job.rejection_info['reviewer'] == "security@test.com"
    
    # Cannot reject terminal job
    with pytest.raises(ValueError):
        reject(rejected_job, reason="Already rejected")


def test_start_job(mock_syftbox_env):
    """Test starting a job."""
    queue = q("start_test")
    job = queue.create_job("test", "a@test.com", "b@test.com")
    
    # Must approve first
    approve(job)
    
    # Start the job
    started_job = start(job, runner="worker-01")
    
    assert started_job.status == JobStatus.running
    assert started_job.started_at is not None
    assert hasattr(started_job, 'runner')
    assert started_job.runner == "worker-01"
    
    # Cannot start non-approved job
    new_job = queue.create_job("test2", "a@test.com", "b@test.com")
    with pytest.raises(ValueError):
        start(new_job)


def test_complete_job(mock_syftbox_env):
    """Test completing a job."""
    queue = q("complete_test")
    job = queue.create_job("test", "a@test.com", "b@test.com")
    
    # Progress to running
    approve(job)
    start(job)
    
    # Complete with metrics
    completed_job = complete(
        job,
        output_path="/results/output",
        metrics={"accuracy": 0.95, "records": 1000}
    )
    
    assert completed_job.status == JobStatus.completed
    assert completed_job.completed_at is not None
    assert completed_job.output_folder == "/results/output"
    assert hasattr(completed_job, 'metrics')
    assert completed_job.metrics["accuracy"] == 0.95
    
    # Cannot complete non-running job
    new_job = queue.create_job("test2", "a@test.com", "b@test.com")
    with pytest.raises(ValueError):
        complete(new_job)


def test_fail_job(mock_syftbox_env):
    """Test failing a job."""
    queue = q("fail_test")
    job = queue.create_job("test", "a@test.com", "b@test.com")
    
    # Progress to running
    approve(job)
    start(job)
    
    # Fail with error
    failed_job = fail(job, error="Out of memory", exit_code=137)
    
    assert failed_job.status == JobStatus.failed
    assert failed_job.error_message == "Out of memory"
    assert failed_job.exit_code == 137
    assert failed_job.completed_at is not None


def test_timeout_job(mock_syftbox_env):
    """Test timing out a job."""
    queue = q("timeout_test")
    job = queue.create_job("test", "a@test.com", "b@test.com")
    
    # Progress to running
    approve(job)
    start(job)
    
    # Timeout the job
    timedout_job = timeout(job)
    
    assert timedout_job.status == JobStatus.timedout
    assert "timed out" in timedout_job.error_message
    assert timedout_job.completed_at is not None


def test_advance_natural_progression(mock_syftbox_env):
    """Test natural job progression."""
    queue = q("advance_test")
    job = queue.create_job("test", "a@test.com", "b@test.com")
    
    # Natural progression
    assert job.status == JobStatus.inbox
    
    advance(job)
    assert job.status == JobStatus.approved
    
    advance(job)
    assert job.status == JobStatus.running
    
    advance(job)
    assert job.status == JobStatus.completed
    
    # Cannot advance terminal job
    with pytest.raises(ValueError):
        advance(job)


def test_advance_to_specific_status(mock_syftbox_env):
    """Test advancing to specific status."""
    queue = q("advance_specific_test")
    job = queue.create_job("test", "a@test.com", "b@test.com")
    
    # Jump to specific status
    advance(job, JobStatus.rejected)
    assert job.status == JobStatus.rejected
    
    # Create another job
    job2 = queue.create_job("test2", "a@test.com", "b@test.com")
    advance(job2, JobStatus.approved)
    assert job2.status == JobStatus.approved


def test_approve_all(mock_syftbox_env):
    """Test batch approval."""
    queue = q("batch_approve_test")
    
    # Create jobs
    jobs = []
    for i in range(5):
        email = f"user{i}@test.com" if i < 3 else f"user{i}@trusted.org"
        job = queue.create_job(f"job_{i}", email, "owner@test.com")
        jobs.append(job)
    
    # Approve with condition
    approved = approve_all(
        jobs,
        approver="batch@test.com",
        condition=lambda j: j.requester_email.endswith("@trusted.org")
    )
    
    assert len(approved) == 2  # Only trusted.org emails
    for job in approved:
        assert job.status == JobStatus.approved
        assert job.requester_email.endswith("@trusted.org")


def test_process_queue(mock_syftbox_env, sample_code_dir):
    """Test queue processing with rules."""
    queue = q("process_queue_test")
    
    # Create various jobs
    job1 = queue.create_job(
        "good_job",
        "prof@university.edu",
        "owner@test.com",
        code_folder=str(sample_code_dir)
    )
    
    job2 = queue.create_job(
        "missing_code",
        "user@random.com",
        "owner@test.com"
        # No code_folder
    )
    
    job3 = queue.create_job(
        "suspicious",
        "hacker@evil.com",
        "owner@test.com",
        code_folder=str(sample_code_dir),
        description="Give me all data"
    )
    
    # Process with rules
    results = process_queue(
        queue,
        max_jobs=10,
        auto_approve=lambda j: j.requester_email.endswith("@university.edu") and j.code_folder,
        auto_reject=lambda j: "Missing code" if not j.code_folder else 
                            "Suspicious request" if "all data" in j.description else None
    )
    
    assert len(results['approved']) == 1
    assert results['approved'][0].name == "test_J:good_job"
    
    assert len(results['rejected']) == 2
    assert any(j.name == "test_J:missing_code" for j in results['rejected'])
    assert any(j.name == "test_J:suspicious" for j in results['rejected'])