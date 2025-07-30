"""Tests to verify load_queue doesn't create new config files when loading existing queues."""

import os
import time
import json
import tempfile
from pathlib import Path
import syft_queue as sq
import pytest


def test_load_queue_does_not_create_new_config(mock_syftbox_env, capsys):
    """Test that load_queue doesn't create a new config file when loading an existing queue."""
    # Create a new queue
    queue_name = "test_analytics"
    queue1 = sq.q(queue_name)
    
    # Verify config file was created
    config_path = queue1.object_path / "queue_config.json"
    assert config_path.exists()
    
    # Get the original modification time
    original_mtime = config_path.stat().st_mtime
    
    # Sleep briefly to ensure timestamp would be different if modified
    time.sleep(0.1)
    
    # Clear captured output
    capsys.readouterr()
    
    # Load the existing queue
    queue2 = sq.load_queue(queue_name)
    
    # Verify queue was loaded successfully
    assert queue2 is not None
    assert queue2.queue_name == queue1.queue_name
    
    # Check that no "Created queue config" message was printed
    captured = capsys.readouterr()
    assert "Created queue config" not in captured.out
    
    # Verify the config file wasn't modified
    new_mtime = config_path.stat().st_mtime
    assert new_mtime == original_mtime, "Config file was modified during load_queue"
    
    # Verify loaded queue has same configuration
    assert queue2.max_concurrent_jobs == queue1.max_concurrent_jobs
    assert queue2.job_timeout == queue1.job_timeout
    assert queue2.cleanup_completed_after == queue1.cleanup_completed_after
    assert queue2.description == queue1.description


def test_load_queue_with_existing_jobs(mock_syftbox_env, sample_code_dir):
    """Test that load_queue preserves existing jobs."""
    # Create a queue with some jobs
    queue_name = "test_job_queue"
    queue1 = sq.q(queue_name)
    
    # Create a job
    job = queue1.create_job(
        name="test_job",
        requester_email="alice@example.com",
        target_email="bob@example.com",
        code_folder=str(sample_code_dir)
    )
    
    # Update queue activity
    queue1.update_last_activity()
    
    # Load the queue
    queue2 = sq.load_queue(queue_name)
    
    # Verify job still exists
    loaded_job = queue2.get_job(job.uid)
    assert loaded_job is not None
    assert loaded_job.name == job.name


def test_load_queue_multiple_times(mock_syftbox_env, capsys):
    """Test that loading a queue multiple times doesn't create new config files."""
    queue_name = "test_multiple_loads"
    
    # Create initial queue
    original_queue = sq.q(queue_name)
    config_path = original_queue.object_path / "queue_config.json"
    
    # Get original timestamp
    original_mtime = config_path.stat().st_mtime
    
    # Load queue multiple times
    for i in range(5):
        time.sleep(0.05)  # Brief sleep to ensure different timestamp
        capsys.readouterr()  # Clear output
        
        loaded = sq.load_queue(queue_name)
        assert loaded is not None
        
        # Check no creation message
        captured = capsys.readouterr()
        assert "Created queue config" not in captured.out
        
        # Check timestamp hasn't changed
        assert config_path.stat().st_mtime == original_mtime


def test_load_queue_nonexistent_raises_error(mock_syftbox_env, capsys):
    """Test that loading a non-existent queue raises FileNotFoundError."""
    # Try to load a queue that doesn't exist
    with pytest.raises(FileNotFoundError, match="Queue 'nonexistent_queue' not found"):
        sq.load_queue("nonexistent_queue")
    
    # Verify no creation message
    captured = capsys.readouterr()
    assert "Created queue config" not in captured.out
    
    # Verify no directory was created
    queues_path = sq.get_queues_path()
    nonexistent_path = queues_path / "nonexistent_queue_queue"
    assert not nonexistent_path.exists()


def test_load_queue_with_corrupted_config(mock_syftbox_env):
    """Test that load_queue handles corrupted config files gracefully."""
    queue_name = "test_corrupted"
    
    # Create a queue
    queue = sq.q(queue_name)
    config_path = queue.object_path / "queue_config.json"
    
    # Corrupt the config file
    config_path.write_text("{ invalid json }")
    
    # Try to load the queue - should raise ValueError
    with pytest.raises(ValueError, match="Invalid queue config"):
        sq.load_queue(queue_name)


def test_load_queue_preserves_custom_configuration(mock_syftbox_env):
    """Test that custom queue configuration is preserved when loading."""
    queue_name = "test_custom_config"
    
    # Create queue with custom configuration
    custom_config = {
        "max_concurrent_jobs": 10,
        "job_timeout": 600,
        "cleanup_completed_after": 172800,
        "description": "Custom test queue"
    }
    
    queue1 = sq.q(queue_name, **custom_config)
    
    # Load the queue
    queue2 = sq.load_queue(queue_name)
    
    # Verify custom configuration was preserved
    assert queue2.max_concurrent_jobs == 10
    assert queue2.job_timeout == 600
    assert queue2.cleanup_completed_after == 172800
    assert queue2.description == "Custom test queue"


def test_load_queue_directory_without_config(mock_syftbox_env):
    """Test load_queue behavior when directory exists but config is missing."""
    queue_name = "test_no_config"
    queues_path = sq.get_queues_path()
    queue_dir = queues_path / f"{queue_name}_queue"
    
    # Create directory without config file
    queue_dir.mkdir(parents=True, exist_ok=True)
    
    # Try to load - should raise FileNotFoundError
    with pytest.raises(FileNotFoundError, match="Queue config file not found"):
        sq.load_queue(queue_name)