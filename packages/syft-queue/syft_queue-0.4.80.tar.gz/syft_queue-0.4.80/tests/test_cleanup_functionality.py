"""Test cleanup functionality for test objects."""

import pytest
import syft_queue as sq
import syft_objects as syo
from syft_queue.test_utils import cleanup_all_test_artifacts


def test_cleanup_removes_test_objects(mock_syftbox_env, sample_code_dir):
    """Test that cleanup function properly removes all test objects."""
    # Create test queue and jobs
    queue = sq.q("cleanup_test")
    job1 = queue.create_job(
        name="cleanup_job_1",
        requester_email="test@example.com",
        target_email="target@example.com",
        code_folder=str(sample_code_dir)
    )
    job2 = queue.create_job(
        name="cleanup_job_2", 
        requester_email="test@example.com",
        target_email="target@example.com",
        code_folder=str(sample_code_dir)
    )
    
    # Verify objects were created with test prefix
    assert queue.queue_name.startswith("test_Q:")
    assert job1.name.startswith("test_J:")
    assert job2.name.startswith("test_J:")
    
    # Check that test objects exist in syft-objects
    test_objects_before = [obj for obj in syo.objects if obj.name.startswith(('test_Q:', 'test_J:'))]
    assert len(test_objects_before) >= 3  # At least 1 queue + 2 jobs
    
    # Run cleanup
    cleanup_all_test_artifacts()
    
    # Force reload of syft-objects
    import sys
    del sys.modules['syft_objects']
    import syft_objects as syo_refreshed
    
    # Verify all test objects are gone
    test_objects_after = [obj for obj in syo_refreshed.objects if obj.name.startswith(('test_Q:', 'test_J:'))]
    assert len(test_objects_after) == 0, f"Found remaining test objects: {[obj.name for obj in test_objects_after]}"


def test_cleanup_handles_lowercase_prefixes(mock_syftbox_env):
    """Test that cleanup handles both uppercase and lowercase file prefixes."""
    from pathlib import Path
    import tempfile
    
    # Create a fake test object file with lowercase prefix
    syftbox_path = Path.home() / "SyftBox"
    if syftbox_path.exists():
        objects_dir = syftbox_path / "datasites" / "test@example.com" / "public" / "objects"
        objects_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test files with lowercase prefixes
        test_file1 = objects_dir / "test_j:fake_job.txt"
        test_file2 = objects_dir / "test_q:fake_queue.yaml"
        test_file1.write_text("test")
        test_file2.write_text("test")
        
        # Run cleanup
        cleanup_all_test_artifacts()
        
        # Verify files were deleted
        assert not test_file1.exists()
        assert not test_file2.exists()


def test_cleanup_does_not_affect_non_test_objects(mock_syftbox_env):
    """Test that cleanup only removes test objects, not regular ones."""
    # Create a regular (non-test) queue
    import os
    old_env = os.environ.get('PYTEST_CURRENT_TEST')
    try:
        # Temporarily disable test mode
        if old_env:
            del os.environ['PYTEST_CURRENT_TEST']
        
        # This should create a regular queue without test prefix
        regular_queue = sq.q("regular_queue", force=True)
        assert not regular_queue.queue_name.startswith("test_")
        
        # Re-enable test mode
        if old_env:
            os.environ['PYTEST_CURRENT_TEST'] = old_env
        
        # Create test objects
        test_queue = sq.q("test_cleanup_queue")
        assert test_queue.queue_name.startswith("test_Q:")
        
        # Run cleanup
        cleanup_all_test_artifacts()
        
        # Force reload
        import sys
        del sys.modules['syft_objects']
        import syft_objects as syo_refreshed
        
        # Check that regular queue still exists but test queue is gone
        remaining_queues = [obj.name for obj in syo_refreshed.objects if obj.name.startswith('Q:')]
        assert "Q:regular_queue" in remaining_queues or regular_queue.queue_name in remaining_queues
        assert "test_Q:test_cleanup_queue" not in remaining_queues
        
    finally:
        # Restore environment
        if old_env:
            os.environ['PYTEST_CURRENT_TEST'] = old_env
        
        # Clean up the regular queue we created for this test
        try:
            import shutil
            from pathlib import Path
            # Remove the regular queue directory
            regular_queue_path = Path("regular_queue_queue")
            if regular_queue_path.exists():
                shutil.rmtree(regular_queue_path)
            # Remove the regular queue from syft-objects
            import subprocess
            # Use generic path based on Path.home()
            syftbox_path = Path.home() / "SyftBox"
            if syftbox_path.exists():
                subprocess.run(f"rm -f {syftbox_path}/datasites/*/public/objects/*regular_queue* {syftbox_path}/datasites/*/private/objects/*regular_queue* 2>/dev/null", shell=True)
        except:
            pass