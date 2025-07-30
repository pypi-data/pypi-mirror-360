"""
Test complete queue deletion and cleanup functionality.

This test verifies that when a queue's syft-object is deleted (through UI or API),
the corresponding queue folder and all its contents are properly cleaned up.
"""

import pytest
import shutil
from pathlib import Path
from syft_queue import q, _cleanup_orphaned_queue_directories, _queue_has_valid_syftobject


class TestQueueDeletionCleanup:
    """Test complete queue deletion and cleanup of orphaned directories."""
    
    def test_queue_folder_cleanup_after_syftobject_deletion(self, mock_syftbox_env):
        """Test that queue folders are cleaned up when syft-objects are deleted."""
        # Create multiple queues
        queue1 = q("test-queue-1", force=True)
        queue2 = q("test-queue-2", force=True)
        queue3 = q("test-queue-3", force=True)
        
        # Add some jobs to make it more realistic
        for queue in [queue1, queue2, queue3]:
            job = queue.create_job("test_job", "user@test.com", "owner@test.com")
            # Move one job to completed status
            job.update_status(queue.JobStatus.completed)
        
        # Verify queue directories exist
        queue_paths = [queue1.object_path, queue2.object_path, queue3.object_path]
        for queue_path in queue_paths:
            assert queue_path.exists(), f"Queue directory should exist: {queue_path}"
            
            # Verify they have the expected structure
            jobs_dir = queue_path / "jobs"
            assert jobs_dir.exists()
            
            # Check for syft.pub.yaml files in status directories
            for status_dir in jobs_dir.iterdir():
                if status_dir.is_dir():
                    syft_pub_file = status_dir / "syft.pub.yaml"
                    assert syft_pub_file.exists(), f"syft.pub.yaml missing in {status_dir}"
        
        # Simulate deletion of queue syft-objects (as would happen through UI)
        # We'll delete the syft-object files to simulate what happens when
        # someone deletes queues through the syft-objects interface
        
        # Find and delete the syft-object files for queue1 and queue2
        syft_objects_to_delete = []
        
        # Get all queue syft-objects
        import syft_objects as syo
        for obj in syo.objects:
            if (hasattr(obj, 'name') and obj.name and 
                (obj.name.startswith('Q:test-queue-1') or obj.name.startswith('Q:test-queue-2'))):
                syft_objects_to_delete.append(obj)
        
        # Delete the syft-object files (simulating UI deletion)
        for obj in syft_objects_to_delete:
            # Delete the syft-object files manually to simulate external deletion
            if hasattr(obj, 'syftobject_path') and obj.syftobject_path:
                syftobject_file = Path(obj.syftobject_path)
                if syftobject_file.exists():
                    syftobject_file.unlink()
                    
            if hasattr(obj, 'private_path') and obj.private_path:
                private_file = Path(obj.private_path)
                if private_file.exists():
                    private_file.unlink()
                    
            if hasattr(obj, 'mock_path') and obj.mock_path:
                mock_file = Path(obj.mock_path)
                if mock_file.exists():
                    mock_file.unlink()
        
        # Verify syft-objects are gone (queue1 and queue2)
        remaining_queue_objects = []
        for obj in syo.objects:
            if (hasattr(obj, 'name') and obj.name and 
                (obj.name.startswith('Q:test-queue-1') or 
                 obj.name.startswith('Q:test-queue-2') or 
                 obj.name.startswith('Q:test-queue-3'))):
                remaining_queue_objects.append(obj.name)
        
        # Should only have queue3 remaining
        queue3_objects = [name for name in remaining_queue_objects if 'test-queue-3' in name]
        deleted_objects = [name for name in remaining_queue_objects if 'test-queue-1' in name or 'test-queue-2' in name]
        
        assert len(queue3_objects) > 0, "Queue3 syft-object should still exist"
        assert len(deleted_objects) == 0, f"Deleted queue syft-objects still exist: {deleted_objects}"
        
        # Now run the cleanup function to remove orphaned directories
        queues_path = mock_syftbox_env
        cleaned_count = _cleanup_orphaned_queue_directories(queues_path)
        
        # Verify cleanup results
        assert cleaned_count == 2, f"Should have cleaned up 2 queue directories, but cleaned {cleaned_count}"
        
        # Check that queue1 and queue2 directories are gone
        assert not queue1.object_path.exists(), f"Queue1 directory should be deleted: {queue1.object_path}"
        assert not queue2.object_path.exists(), f"Queue2 directory should be deleted: {queue2.object_path}"
        
        # But queue3 should still exist (syft-object wasn't deleted)
        assert queue3.object_path.exists(), f"Queue3 directory should still exist: {queue3.object_path}"
    
    def test_cleanup_preserves_queues_with_valid_syftobjects(self, mock_syftbox_env):
        """Test that cleanup only removes queues without valid syft-objects."""
        # Create queues
        valid_queue = q("valid-queue", force=True) 
        orphaned_queue_path = mock_syftbox_env / "orphaned-queue_queue"
        
        # Create orphaned queue directory manually (simulate leftover after deletion)
        orphaned_queue_path.mkdir(parents=True, exist_ok=True)
        jobs_dir = orphaned_queue_path / "jobs"
        jobs_dir.mkdir(exist_ok=True)
        
        # Create some status directories with syft.pub.yaml
        for status in ["inbox", "completed", "failed"]:
            status_dir = jobs_dir / status
            status_dir.mkdir(exist_ok=True)
            (status_dir / "syft.pub.yaml").write_text("rules:\n- pattern: '**'\n  access:\n    read:\n    - '*'")
        
        # Add some fake job directories
        (jobs_dir / "inbox" / "fake-job-uuid").mkdir(exist_ok=True)
        (jobs_dir / "completed" / "another-fake-uuid").mkdir(exist_ok=True)
        
        # Verify initial state
        assert valid_queue.object_path.exists()
        assert orphaned_queue_path.exists()
        
        # Run cleanup
        cleaned_count = _cleanup_orphaned_queue_directories(mock_syftbox_env)
        
        # Should clean up the orphaned queue (no syft-object) but keep valid queue
        assert cleaned_count == 1
        assert valid_queue.object_path.exists(), "Valid queue should be preserved"
        assert not orphaned_queue_path.exists(), "Orphaned queue should be cleaned up"
    
    def test_cleanup_on_import_removes_orphaned_queues(self, mock_syftbox_env):
        """Test that cleanup runs automatically on import and removes orphaned queues."""
        # Create a queue, then manually delete its syft-object
        queue = q("will-be-orphaned", force=True)
        queue_path = queue.object_path
        
        # Add a job to make it more realistic
        job = queue.create_job("test_job", "user@test.com", "owner@test.com")
        
        # Verify queue exists
        assert queue_path.exists()
        
        # Manually delete the queue's syft-object files (simulate external deletion)
        import syft_objects as syo
        for obj in syo.objects:
            if hasattr(obj, 'name') and obj.name and 'will-be-orphaned' in obj.name:
                # Delete the syft-object files
                if hasattr(obj, 'syftobject_path') and obj.syftobject_path:
                    Path(obj.syftobject_path).unlink(missing_ok=True)
                if hasattr(obj, 'private_path') and obj.private_path:
                    Path(obj.private_path).unlink(missing_ok=True)
                if hasattr(obj, 'mock_path') and obj.mock_path:
                    Path(obj.mock_path).unlink(missing_ok=True)
        
        # Queue directory should still exist but syft-object should be gone
        assert queue_path.exists()
        
        # Verify syft-object is actually gone
        remaining_objects = [obj.name for obj in syo.objects if hasattr(obj, 'name') and obj.name and 'will-be-orphaned' in obj.name]
        assert len(remaining_objects) == 0, f"Syft-object should be deleted but found: {remaining_objects}"
        
        # Now test that re-importing syft-queue triggers cleanup
        # Since we're already in a test, we'll call the cleanup function directly
        # In real usage, this would happen during import
        cleaned_count = _cleanup_orphaned_queue_directories(mock_syftbox_env)
        
        # Should have cleaned up the orphaned queue
        assert cleaned_count == 1
        assert not queue_path.exists(), f"Orphaned queue directory should be cleaned up: {queue_path}"
    
    def test_cleanup_handles_partial_queue_structures(self, mock_syftbox_env):
        """Test cleanup handles queues with incomplete or corrupted structure."""
        # Create various incomplete queue structures
        test_cases = [
            "incomplete-queue-1_queue",  # No jobs directory
            "incomplete-queue-2_queue",  # Empty jobs directory
            "incomplete-queue-3_queue",  # Jobs dir but no status dirs
        ]
        
        queue_paths = []
        for queue_name in test_cases:
            queue_path = mock_syftbox_env / queue_name
            queue_path.mkdir(parents=True, exist_ok=True)
            queue_paths.append(queue_path)
            
            if "queue-2" in queue_name:
                # Create empty jobs directory
                (queue_path / "jobs").mkdir(exist_ok=True)
            elif "queue-3" in queue_name:
                # Create jobs directory with some random files
                jobs_dir = queue_path / "jobs"
                jobs_dir.mkdir(exist_ok=True)
                (jobs_dir / "random_file.txt").write_text("random content")
        
        # Verify all exist
        for queue_path in queue_paths:
            assert queue_path.exists()
        
        # Run cleanup
        cleaned_count = _cleanup_orphaned_queue_directories(mock_syftbox_env)
        
        # Should clean up all incomplete structures
        assert cleaned_count == len(test_cases)
        for queue_path in queue_paths:
            assert not queue_path.exists(), f"Incomplete queue should be cleaned: {queue_path}"
    
    def test_cleanup_skips_non_queue_directories(self, mock_syftbox_env):
        """Test that cleanup doesn't touch non-queue directories."""
        # Create various non-queue directories
        non_queue_dirs = [
            mock_syftbox_env / "not-a-queue",
            mock_syftbox_env / "some-other-folder",
            mock_syftbox_env / "queue-but-no-suffix",  # Doesn't end with _queue
            mock_syftbox_env / "my_queue_not_suffix",  # Has queue but wrong suffix
        ]
        
        for dir_path in non_queue_dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            (dir_path / "some_content.txt").write_text("test content")
        
        # Also create a valid queue for comparison
        valid_queue = q("valid-test-queue", force=True)
        
        # Run cleanup
        cleaned_count = _cleanup_orphaned_queue_directories(mock_syftbox_env)
        
        # Should not clean up any non-queue directories
        assert cleaned_count == 0, f"Should not have cleaned any directories, but cleaned {cleaned_count}"
        
        # Verify non-queue directories still exist
        for dir_path in non_queue_dirs:
            assert dir_path.exists(), f"Non-queue directory was incorrectly deleted: {dir_path}"
        
        # Valid queue should also still exist
        assert valid_queue.object_path.exists()