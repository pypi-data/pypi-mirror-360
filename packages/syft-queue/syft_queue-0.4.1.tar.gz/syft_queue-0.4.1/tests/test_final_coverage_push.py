"""
Final push for 100% coverage - targeted tests for remaining lines
"""

import pytest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from uuid import uuid4


def test_basic_queue_creation(mock_syftbox_env):
    """Basic test to exercise core queue functionality."""
    from syft_queue import q, JobStatus
    
    # Test queue creation
    queue = q("basic_test", force=True)
    assert queue.queue_name == "test_Q:basic_test"
    
    # Test job creation
    job = queue.create_job("test_job", "user@test.com", "owner@test.com")
    assert job.name == "test_J:test_job"
    assert job.status == JobStatus.inbox
    
    # Test job properties
    assert job.uid is not None
    assert job.requester_email == "user@test.com"
    assert job.target_email == "owner@test.com"
    
    # Test job status transitions
    job.update_status(JobStatus.approved)
    assert job.status == JobStatus.approved
    
    job.update_status(JobStatus.running)
    assert job.status == JobStatus.running
    
    job.update_status(JobStatus.completed)
    assert job.status == JobStatus.completed
    assert job.is_terminal


def test_queue_stats_comprehensive(mock_syftbox_env):
    """Test queue statistics functionality."""
    from syft_queue import q, JobStatus
    
    queue = q("stats_test", force=True)
    
    # Create jobs in different statuses
    job1 = queue.create_job("job1", "user@test.com", "owner@test.com")
    job2 = queue.create_job("job2", "user@test.com", "owner@test.com") 
    job3 = queue.create_job("job3", "user@test.com", "owner@test.com")
    
    # Move jobs to different statuses
    job1.update_status(JobStatus.approved)
    job2.update_status(JobStatus.running)
    job3.update_status(JobStatus.completed)
    
    # Test queue stats
    stats = queue.get_stats()
    assert isinstance(stats, dict)
    assert stats["total_jobs"] >= 3
    
    # Test individual counters (refresh first)
    queue.refresh_stats()
    assert queue.total_jobs >= 3
    assert queue.approved_jobs >= 1 or queue.running_jobs >= 1 or queue.completed_jobs >= 1


def test_pipeline_basic_functionality():
    """Test basic pipeline functionality."""
    try:
        from syft_queue.pipeline import Pipeline, PipelineBuilder, PipelineStage
        
        # Test PipelineBuilder
        builder = PipelineBuilder("test_pipeline")
        builder.stage("stage1", "inbox")
        builder.stage("stage2", "approved")
        builder.transition("stage1", "stage2")
        
        pipeline = builder.build()
        assert pipeline.name == "test_pipeline"
        assert "stage1" in pipeline.stages
        assert "stage2" in pipeline.stages
    except ImportError:
        # Pipeline features are optional
        pass


def test_help_and_utility_functions():
    """Test help and utility functions."""
    from syft_queue import help
    from syft_queue.queue import _get_queues_table
    
    # Test help function
    help()  # Should not raise error
    
    # Test queues table
    table = _get_queues_table()
    assert isinstance(table, str)
    assert "Queue Name" in table


def test_job_execution_functions(mock_syftbox_env):
    """Test job execution functionality."""
    from syft_queue import q, prepare_job_for_execution, execute_job_with_context
    
    queue = q("execution_test", force=True)
    job = queue.create_job("exec_job", "user@test.com", "owner@test.com")
    
    # Test job preparation
    context = prepare_job_for_execution(job)
    assert "job_uid" in context
    assert "job_name" in context
    assert context["job_uid"] == str(job.uid)
    
    # Test job execution (will fail but we test the code path)
    success, output = execute_job_with_context(job)
    assert isinstance(success, bool)
    assert isinstance(output, str)


def test_progression_api(mock_syftbox_env):
    """Test job progression API functions."""
    from syft_queue import q, approve, reject, start, complete, fail, advance
    from syft_queue import JobStatus
    
    queue = q("progression_test", force=True)
    
    # Test approve
    job1 = queue.create_job("job1", "user@test.com", "owner@test.com")
    approved_job = approve(job1, approver="admin@test.com")
    assert approved_job.status == JobStatus.approved
    
    # Test start
    started_job = start(approved_job, runner="worker1")
    assert started_job.status == JobStatus.running
    
    # Test complete
    completed_job = complete(started_job)
    assert completed_job.status == JobStatus.completed
    
    # Test reject
    job2 = queue.create_job("job2", "user@test.com", "owner@test.com")
    rejected_job = reject(job2, reason="Invalid", reviewer="admin@test.com")
    assert rejected_job.status == JobStatus.rejected
    
    # Test fail
    job3 = queue.create_job("job3", "user@test.com", "owner@test.com")
    job3.update_status(JobStatus.running)
    failed_job = fail(job3, error="Process failed", exit_code=1)
    assert failed_job.status == JobStatus.failed
    
    # Test advance
    job4 = queue.create_job("job4", "user@test.com", "owner@test.com")
    advanced_job = advance(job4)
    assert advanced_job.status == JobStatus.approved


def test_data_queue_functionality(mock_syftbox_env):
    """Test DataQueue specific functionality."""
    from syft_queue import q, DataQueue
    
    # Create data queue
    data_queue = q("data_test", queue_type="data", force=True)
    assert isinstance(data_queue, DataQueue)
    
    # Test job creation without code
    job = data_queue.create_job("data_job", "user@test.com", "owner@test.com")
    assert job.name == "test_J:data_job"


def test_import_coverage():
    """Test import-time coverage of __init__.py."""
    # Test that we can access all the main imports
    import syft_queue
    
    # Test core classes
    assert hasattr(syft_queue, 'Job')
    assert hasattr(syft_queue, 'Queue')
    assert hasattr(syft_queue, 'JobStatus')
    assert hasattr(syft_queue, 'q')
    
    # Test queues collection
    assert hasattr(syft_queue, 'queues')
    queues_repr = repr(syft_queue.queues)
    assert isinstance(queues_repr, str)
    
    # Test pipeline imports (optional)
    try:
        assert hasattr(syft_queue, 'Pipeline')
        assert hasattr(syft_queue, 'PipelineBuilder')
    except AttributeError:
        # Pipeline imports are optional
        pass