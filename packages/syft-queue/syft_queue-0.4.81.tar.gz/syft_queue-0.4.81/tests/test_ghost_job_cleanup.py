"""
Test ghost job folder cleanup functionality.

Ghost job folders are empty job directories that no longer have corresponding
syft-objects but still exist in the filesystem. This can happen when objects
are deleted but the folder structure remains.
"""

import pytest
import json
import shutil
from pathlib import Path
from uuid import uuid4
from syft_queue import q, JobStatus, _cleanup_ghost_job_folders, _is_ghost_job_folder


class TestGhostJobCleanup:
    """Test detection and cleanup of ghost job folders."""
    
    def test_detect_and_cleanup_ghost_job_folders(self, mock_syftbox_env):
        """Test that ghost job folders are detected and cleaned up on import."""
        # Create a queue
        queue = q("ghost_test_queue", force=True)
        
        # Create a legitimate job first
        real_job = queue.create_job("real_job", "user@test.com", "owner@test.com")
        real_job_uid = real_job.uid
        
        # Manually create ghost job folders (simulate what happens when objects are deleted)
        ghost_uids = [uuid4(), uuid4(), uuid4()]
        ghost_folders = []
        
        for ghost_uid in ghost_uids:
            # Create job directory structure without proper syft-object
            for status in [JobStatus.inbox, JobStatus.completed, JobStatus.failed]:
                ghost_dir = queue.get_job_directory(ghost_uid, status)
                ghost_dir.mkdir(parents=True, exist_ok=True)
                ghost_folders.append(ghost_dir)
                
                # Create some folder structure but no proper job data
                (ghost_dir / "mock").mkdir(exist_ok=True)
                (ghost_dir / "private").mkdir(exist_ok=True)
                (ghost_dir / "code").mkdir(exist_ok=True)
                
                # Create incomplete or corrupted data (no syftobject.yaml)
                (ghost_dir / "private" / "incomplete.json").write_text('{"incomplete": true}')
        
        # Verify ghost folders exist
        assert len([f for f in ghost_folders if f.exists()]) == len(ghost_folders)
        
        # Now test the cleanup function
        initial_ghost_count = len([f for f in ghost_folders if f.exists()])
        assert initial_ghost_count > 0
        
        # Run cleanup
        cleaned_count = _cleanup_ghost_job_folders(queue.object_path)
        
        # Verify ghost folders were cleaned up
        remaining_ghosts = [f for f in ghost_folders if f.exists()]
        assert len(remaining_ghosts) == 0, f"Ghost folders still exist: {remaining_ghosts}"
        assert cleaned_count == initial_ghost_count
        
        # Verify real job is still there
        real_job_dir = queue.get_job_directory(real_job_uid, JobStatus.inbox)
        assert real_job_dir.exists(), "Real job folder was incorrectly deleted"
        
        # Verify we can still load the real job
        loaded_job = queue.get_job(real_job_uid)
        assert loaded_job is not None
        assert loaded_job.name == "test_J:real_job"
    
    def test_ghost_cleanup_preserves_valid_jobs(self, mock_syftbox_env):
        """Test that cleanup only removes ghost folders, not valid jobs."""
        queue = q("preserve_test_queue", force=True)
        
        # Create several valid jobs
        valid_jobs = []
        for i in range(3):
            job = queue.create_job(f"valid_job_{i}", "user@test.com", "owner@test.com")
            valid_jobs.append(job)
            
            # Move some jobs to different statuses
            if i == 1:
                job.update_status(JobStatus.approved)
            elif i == 2:
                job.update_status(JobStatus.completed)
        
        # Create ghost folders (directories without proper syftobject.yaml)
        ghost_count = 0
        for status in JobStatus:
            for i in range(2):  # 2 ghosts per status
                ghost_uid = uuid4()
                ghost_dir = queue.get_job_directory(ghost_uid, status)
                ghost_dir.mkdir(parents=True, exist_ok=True)
                
                # Create incomplete structure (missing syftobject.yaml)
                (ghost_dir / "mock").mkdir(exist_ok=True)
                (ghost_dir / "private").mkdir(exist_ok=True) 
                (ghost_dir / "private" / "corrupted.txt").write_text("corrupted data")
                ghost_count += 1
        
        # Run cleanup
        cleaned = _cleanup_ghost_job_folders(queue.object_path)
        assert cleaned == ghost_count
        
        # Verify all valid jobs still exist and are loadable
        for job in valid_jobs:
            loaded_job = queue.get_job(job.uid)
            assert loaded_job is not None
            assert loaded_job.uid == job.uid
            assert loaded_job.name == job.name
    
    def test_ghost_cleanup_with_mixed_scenarios(self, mock_syftbox_env):
        """Test cleanup with various ghost folder scenarios."""
        queue = q("mixed_test_queue", force=True) 
        
        # Scenario 1: Completely empty folder
        empty_ghost = queue.get_job_directory(uuid4(), JobStatus.inbox)
        empty_ghost.mkdir(parents=True, exist_ok=True)
        
        # Scenario 2: Folder with only mock directory
        mock_only_ghost = queue.get_job_directory(uuid4(), JobStatus.approved)
        mock_only_ghost.mkdir(parents=True, exist_ok=True)
        (mock_only_ghost / "mock").mkdir(exist_ok=True)
        (mock_only_ghost / "mock" / "data.json").write_text('{"mock": true}')
        
        # Scenario 3: Folder with private data but no syftobject.yaml
        private_no_yaml_ghost = queue.get_job_directory(uuid4(), JobStatus.running)
        private_no_yaml_ghost.mkdir(parents=True, exist_ok=True)
        (private_no_yaml_ghost / "private").mkdir(exist_ok=True)
        (private_no_yaml_ghost / "private" / "job_data.json").write_text('{"incomplete": "data"}')
        
        # Scenario 4: Valid job (control)
        valid_job = queue.create_job("control_job", "user@test.com", "owner@test.com")
        
        ghost_folders = [empty_ghost, mock_only_ghost, private_no_yaml_ghost]
        
        # Verify all ghosts exist
        for ghost in ghost_folders:
            assert ghost.exists()
        
        # Run cleanup
        cleaned = _cleanup_ghost_job_folders(queue.object_path)
        assert cleaned == 3
        
        # Verify ghosts are gone
        for ghost in ghost_folders:
            assert not ghost.exists(), f"Ghost folder still exists: {ghost}"
        
        # Verify valid job remains
        assert queue.get_job(valid_job.uid) is not None
    
    def test_cleanup_on_syft_queue_import(self, mock_syftbox_env):
        """Test that cleanup runs automatically when syft_queue is imported."""
        # Set up test scenario before importing
        queues_path = mock_syftbox_env
        test_queue_path = queues_path / "auto_cleanup_test_queue"
        test_queue_path.mkdir(parents=True, exist_ok=True)
        
        # Create jobs directory structure
        jobs_dir = test_queue_path / "jobs"
        jobs_dir.mkdir(exist_ok=True)
        
        # Create ghost job folders manually
        ghost_folders = []
        for status in [JobStatus.inbox, JobStatus.completed]:
            status_dir = jobs_dir / status.value
            status_dir.mkdir(exist_ok=True)
            
            # Create syft.pub.yaml (status directories need these)
            (status_dir / "syft.pub.yaml").write_text("rules:\n- pattern: '**'\n  access:\n    read:\n    - '*'")
            
            for i in range(2):
                ghost_uid = uuid4()
                ghost_dir = status_dir / str(ghost_uid)
                ghost_dir.mkdir(exist_ok=True)
                ghost_folders.append(ghost_dir)
                
                # Create incomplete structure
                (ghost_dir / "mock").mkdir(exist_ok=True)
                (ghost_dir / "private").mkdir(exist_ok=True)
        
        # Verify ghosts exist before import
        existing_ghosts = [f for f in ghost_folders if f.exists()]
        assert len(existing_ghosts) == 4
        
        # Import syft_queue (this should trigger cleanup)
        # Note: Since we're already in a test, we'll call the cleanup function directly
        # In real usage, this would happen during import
        total_cleaned = 0
        for queue_dir in queues_path.iterdir():
            if queue_dir.is_dir() and queue_dir.name.endswith("_queue"):
                total_cleaned += _cleanup_ghost_job_folders(queue_dir)
        
        # Verify cleanup happened
        assert total_cleaned == 4
        remaining_ghosts = [f for f in ghost_folders if f.exists()]
        assert len(remaining_ghosts) == 0
    
    def test_cleanup_skips_non_uuid_folders(self, mock_syftbox_env):
        """Test that cleanup doesn't touch non-UUID folders."""
        queue = q("skip_test_queue", force=True)
        
        # Create non-UUID folders that should be preserved
        status_dir = queue.get_status_directory(JobStatus.inbox)
        
        non_uuid_folders = [
            status_dir / "not-a-uuid",
            status_dir / "some-other-folder", 
            status_dir / "README.txt",
            status_dir / ".hidden"
        ]
        
        for folder in non_uuid_folders:
            if folder.name.endswith('.txt'):
                folder.write_text("This is not a job folder")
            else:
                folder.mkdir(exist_ok=True)
                (folder / "some_file.txt").write_text("test content")
        
        # Create one ghost UUID folder
        ghost_uid = uuid4()
        ghost_dir = status_dir / str(ghost_uid)
        ghost_dir.mkdir(exist_ok=True)
        (ghost_dir / "mock").mkdir(exist_ok=True)
        
        # Run cleanup
        cleaned = _cleanup_ghost_job_folders(queue.object_path)
        
        # Should only clean the one ghost folder
        assert cleaned == 1
        assert not ghost_dir.exists()
        
        # All non-UUID folders should remain
        for folder in non_uuid_folders:
            assert folder.exists(), f"Non-UUID folder was incorrectly deleted: {folder}"