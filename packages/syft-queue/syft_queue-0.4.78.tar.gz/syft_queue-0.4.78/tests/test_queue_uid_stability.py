"""Test that queue UIDs remain stable across reloads."""

import pytest
import json
import time
from pathlib import Path
import tempfile
import os
from unittest.mock import patch

import syft_queue as sq
from syft_queue import get_queue, load_queue, q


class TestQueueUIDStability:
    """Test suite for queue UID stability."""
    
    def test_queue_uid_preserved_on_reload(self):
        """Test that queue UIDs remain stable when reloading through get_queue."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Mock the SyftBox environment to use temp directory
            with patch.dict(os.environ, {'SYFTBOX_DATA_FOLDER': tmpdir}):
                # Create a queue
                queue = q("test_uid_stability")
                initial_uid = queue.queue_uid
                initial_path = queue.object_path
                
                # Verify UID is set
                assert initial_uid is not None
                assert len(initial_uid) > 0
                
                # Check config file has the UID
                config_file = initial_path / "queue_config.json"
                assert config_file.exists()
                
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    assert config.get("queue_uid") == initial_uid
                
                # Reload the queue multiple times
                for i in range(5):
                    reloaded = get_queue("test_uid_stability")
                    assert reloaded is not None
                    assert reloaded.queue_uid == initial_uid, f"UID changed on reload {i+1}"
                    
                    # Verify config file hasn't changed
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                        assert config.get("queue_uid") == initial_uid
    
    def test_queue_uid_preserved_with_load_queue(self):
        """Test that queue UIDs remain stable when loading through load_queue."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Mock the SyftBox environment to use temp directory
            with patch.dict(os.environ, {'SYFTBOX_DATA_FOLDER': tmpdir}):
                # Create a queue
                queue = q("test_load_stability")
                initial_uid = queue.queue_uid
                queue_dir = queue.object_path
                
                # Load the queue by name
                loaded_queue = load_queue("test_load_stability")
                assert loaded_queue is not None
                assert loaded_queue.queue_uid == initial_uid
                
                # Verify the loaded queue doesn't regenerate UID on save
                loaded_queue.refresh_stats()
                
                # Check config still has same UID
                config_file = queue_dir / "queue_config.json"
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    assert config.get("queue_uid") == initial_uid
    
    
    def test_queue_uid_stability_with_job_operations(self):
        """Test that queue UIDs remain stable even when performing job operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Mock the SyftBox environment to use temp directory
            with patch.dict(os.environ, {'SYFTBOX_DATA_FOLDER': tmpdir}):
                # Create a queue
                queue = q("test_job_operations")
                initial_uid = queue.queue_uid
                
                # Create some jobs
                job1 = queue.create_job("test_job_1", "test@example.com")
                job2 = queue.create_job("test_job_2", "test@example.com")
                
                # Perform operations using the progression API
                from syft_queue import approve, start, complete, fail
                approve(job1)
                start(job1)
                
                # Reload and check UID
                reloaded = get_queue("test_job_operations")
                assert reloaded.queue_uid == initial_uid
                
                # More operations
                complete(job1)
                # Need to progress job2 to running before failing it
                approve(job2)
                start(job2)
                fail(job2, "Test failure")
                
                # Final reload and check
                final_reload = get_queue("test_job_operations")
                assert final_reload.queue_uid == initial_uid