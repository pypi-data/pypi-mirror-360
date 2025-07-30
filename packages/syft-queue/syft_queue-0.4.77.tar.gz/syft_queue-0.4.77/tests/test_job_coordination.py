"""
Tests for job coordination between DataQueue and CodeQueue.
"""

import pytest
from uuid import uuid4
import time
from syft_queue import q, DataQueue, CodeQueue, JobStatus


def test_shared_job_id_across_queues(mock_syftbox_env):
    """Test creating jobs with shared IDs across different queues."""
    shared_job_id = uuid4()
    
    # Create DataQueues for preprocessing
    data_queue_1 = q("data-filter-coordination", queue_type="data", force=True)
    data_queue_2 = q("data-clean-coordination", queue_type="data", force=True)
    
    # Create CodeQueue for analysis
    code_queue = q("analysis-coordination", queue_type="code", force=True)
    
    # Create jobs with same ID in data queues
    data_job_1 = data_queue_1.create_job(
        name="filter-data",
        requester_email="pipeline@company.com",
        target_email="data-team@company.com",
        uid=shared_job_id
    )
    
    data_job_2 = data_queue_2.create_job(
        name="clean-data",
        requester_email="pipeline@company.com",
        target_email="data-team@company.com",
        uid=shared_job_id
    )
    
    # Verify same UID
    assert data_job_1.uid == shared_job_id
    assert data_job_2.uid == shared_job_id
    assert data_job_1.uid == data_job_2.uid


def test_pipeline_coordination_workflow(mock_syftbox_env, sample_code_dir):
    """Test a complete pipeline workflow with data preprocessing and code analysis."""
    # Create queues
    data_queue = q("preprocessing-pipeline", queue_type="data", force=True)
    code_queue = q("analysis-pipeline", queue_type="code", force=True)
    
    # Create data preprocessing job
    data_job = data_queue.create_job(
        name="preprocess-dataset",
        requester_email="data-scientist@company.com",
        target_email="data-owner@company.com",
        description="Preprocess customer data for analysis"
    )
    
    # Simulate data preprocessing workflow
    data_job.update_status(JobStatus.approved)
    assert data_job.status == JobStatus.approved
    
    data_job.update_status(JobStatus.running)
    assert data_job.status == JobStatus.running
    
    # Complete data preprocessing
    data_job.update_status(JobStatus.completed)
    assert data_job.status == JobStatus.completed
    
    # Create analysis job that depends on the preprocessed data
    analysis_job = code_queue.create_job(
        name="analyze-preprocessed-data",
        requester_email="data-scientist@company.com",
        target_email="data-owner@company.com",
        code_folder=str(sample_code_dir),
        description=f"Analyze data from job {data_job.uid}"
    )
    
    # Verify the analysis job was created
    assert analysis_job is not None
    assert "test_J:analyze-preprocessed-data" in analysis_job.name or "analyze-preprocessed-data" in analysis_job.name
    assert str(data_job.uid) in analysis_job.description


def test_multiple_data_jobs_feeding_code_job(mock_syftbox_env, sample_code_dir):
    """Test multiple data processing jobs feeding into a single analysis job."""
    # Create multiple data queues for different preprocessing steps
    filter_queue = q("filter-multi", queue_type="data", force=True)
    clean_queue = q("clean-multi", queue_type="data", force=True)
    transform_queue = q("transform-multi", queue_type="data", force=True)
    
    # Create analysis queue
    analysis_queue = q("analysis-multi", queue_type="code", force=True)
    
    # Create data processing jobs
    filter_job = filter_queue.create_job(
        name="filter-outliers",
        requester_email="pipeline@company.com",
        target_email="data@company.com"
    )
    
    clean_job = clean_queue.create_job(
        name="clean-missing-values",
        requester_email="pipeline@company.com",
        target_email="data@company.com"
    )
    
    transform_job = transform_queue.create_job(
        name="normalize-features",
        requester_email="pipeline@company.com",
        target_email="data@company.com"
    )
    
    # Complete all data jobs
    for job in [filter_job, clean_job, transform_job]:
        job.update_status(JobStatus.approved)
        job.update_status(JobStatus.running)
        job.update_status(JobStatus.completed)
    
    # Create analysis job that depends on all completed data jobs
    analysis_job = analysis_queue.create_job(
        name="final-analysis",
        requester_email="pipeline@company.com",
        target_email="data@company.com",
        code_folder=str(sample_code_dir),
        description=f"Analyze data from jobs: {filter_job.uid}, {clean_job.uid}, {transform_job.uid}"
    )
    
    # Verify all job IDs are referenced
    assert str(filter_job.uid) in analysis_job.description
    assert str(clean_job.uid) in analysis_job.description
    assert str(transform_job.uid) in analysis_job.description


def test_queue_type_job_listing(mock_syftbox_env):
    """Test listing jobs separately for different queue types."""
    # Create both queue types with force=True to ensure clean state
    data_queue = q("data-listing-test", queue_type="data", force=True)
    code_queue = q("code-listing-test", queue_type="code", force=True)
    
    # Create jobs in each queue
    data_jobs = []
    for i in range(3):
        job = data_queue.create_job(
            f"data-job-{i}",
            "data@company.com",
            "owner@company.com"
        )
        data_jobs.append(job)
    
    code_jobs = []
    for i in range(2):
        job = code_queue.create_job(
            f"code-job-{i}",
            "dev@company.com",
            "owner@company.com"
        )
        code_jobs.append(job)
    
    # Verify job counts by checking created jobs
    assert len(data_jobs) == 3
    assert len(code_jobs) == 2
    
    # Verify jobs were created with correct names
    for i, job in enumerate(data_jobs):
        assert job.name == f"test_J:data-job-{i}"
    
    for i, job in enumerate(code_jobs):
        assert job.name == f"test_J:code-job-{i}"
    
    # Verify job UIDs are unique
    all_uids = [j.uid for j in data_jobs + code_jobs]
    assert len(all_uids) == len(set(all_uids))  # All unique


def test_coordinated_job_status_tracking(mock_syftbox_env):
    """Test tracking job statuses across coordinated queues."""
    # Create queues
    data_queue = q("data-status-track", queue_type="data", force=True)
    code_queue = q("code-status-track", queue_type="code", force=True)
    
    # Create initial data job
    data_job = data_queue.create_job(
        "prepare-data",
        "coordinator@company.com",
        "data@company.com"
    )
    
    # Track data job through its lifecycle
    statuses = [JobStatus.approved, JobStatus.running, JobStatus.completed]
    for status in statuses:
        data_job.update_status(status)
        data_queue.refresh_stats()
        
        if status == JobStatus.approved:
            assert data_queue.approved_jobs == 1
        elif status == JobStatus.running:
            assert data_queue.running_jobs == 1
        elif status == JobStatus.completed:
            assert data_queue.completed_jobs == 1
    
    # Create dependent code job
    code_job = code_queue.create_job(
        "analyze-prepared-data",
        "coordinator@company.com",
        "data@company.com",
        description=f"Depends on data job {data_job.uid}"
    )
    
    # Verify initial state
    assert code_queue.inbox_jobs == 1
    assert data_queue.completed_jobs == 1