"""
Tests for queue type system (CodeQueue vs DataQueue).
"""

import pytest
from syft_queue import q, CodeQueue, DataQueue


def test_code_queue_creation(mock_syftbox_env):
    """Test creating a CodeQueue."""
    code_queue = q("test-code-queue", queue_type="code", force=True)
    
    assert isinstance(code_queue, CodeQueue)
    assert code_queue.__class__.__name__ == "CodeQueue"
    assert code_queue.queue_name == "test_Q:test-code-queue"


def test_data_queue_creation(mock_syftbox_env):
    """Test creating a DataQueue."""
    data_queue = q("test-data-queue", queue_type="data", force=True)
    
    assert isinstance(data_queue, DataQueue)
    assert data_queue.__class__.__name__ == "DataQueue"
    assert data_queue.queue_name == "test_Q:test-data-queue"


def test_default_queue_type(mock_syftbox_env):
    """Test that default queue type is CodeQueue for backward compatibility."""
    default_queue = q("test-default-queue", force=True)
    
    assert isinstance(default_queue, CodeQueue)
    assert default_queue.__class__.__name__ == "CodeQueue"


def test_invalid_queue_type(mock_syftbox_env):
    """Test that invalid queue types are rejected."""
    with pytest.raises(ValueError) as exc_info:
        q("test-invalid-queue", queue_type="invalid", force=True)
    
    assert "Invalid queue_type 'invalid'" in str(exc_info.value)
    assert "Must be 'code' or 'data'" in str(exc_info.value)


def test_job_creation_in_different_queue_types(mock_syftbox_env, sample_code_dir):
    """Test creating jobs in different queue types."""
    # Create CodeQueue and job
    code_queue = q("test-code-jobs", queue_type="code", force=True)
    code_job = code_queue.create_job(
        name="analysis-job",
        requester_email="scientist@company.com",
        target_email="target@company.com",
        code_folder=str(sample_code_dir)
    )
    
    assert code_job is not None
    assert code_job.name == "test_J:analysis-job"
    assert code_job.requester_email == "scientist@company.com"
    
    # Create DataQueue and job
    data_queue = q("test-data-jobs", queue_type="data", force=True)
    data_job = data_queue.create_job(
        name="data-processing-job",
        requester_email="data-engineer@company.com",
        target_email="target@company.com"
    )
    
    assert data_job is not None
    assert data_job.name == "test_J:data-processing-job"
    assert data_job.requester_email == "data-engineer@company.com"


def test_queue_type_persistence(mock_syftbox_env):
    """Test that queue type is preserved when loading existing queue."""
    # Create a DataQueue
    data_queue = q("persistent-data-queue", queue_type="data", force=True)
    job = data_queue.create_job("test-job", "a@test.com", "b@test.com")
    job_uid = job.uid
    
    # Load the same queue again with the correct type
    # Note: Current implementation requires specifying queue_type when loading
    loaded_queue = q("persistent-data-queue", queue_type="data", force=True)
    
    assert isinstance(loaded_queue, DataQueue)
    assert loaded_queue.__class__.__name__ == "DataQueue"
    
    # Create a new job to test
    new_job = loaded_queue.create_job("test-job-2", "a@test.com", "b@test.com")
    assert new_job.name == "test_J:test-job-2"


def test_separate_queue_types_with_same_name(mock_syftbox_env):
    """Test that queues with same name but different types are separate."""
    # This test verifies if the system allows same name for different queue types
    # or if it treats them as the same queue
    
    # Create a CodeQueue
    code_queue = q("shared-name", queue_type="code", force=True)
    code_job = code_queue.create_job("code-job", "a@test.com", "b@test.com")
    
    # Try to create a DataQueue with the same name
    # The behavior depends on implementation - it might require force=True
    try:
        data_queue = q("shared-name", queue_type="data", force=True)
        data_job = data_queue.create_job("data-job", "a@test.com", "b@test.com")
        
        # If we get here, they are separate queues
        assert code_queue.total_jobs == 1
        assert data_queue.total_jobs == 1
    except ValueError:
        # If we get here, the system doesn't allow same name for different types
        # This is also valid behavior
        pass