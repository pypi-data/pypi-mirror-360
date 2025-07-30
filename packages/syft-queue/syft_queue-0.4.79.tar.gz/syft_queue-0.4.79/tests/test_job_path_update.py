"""Test job path updates when moving between status folders."""
import tempfile
import os
from pathlib import Path
import json
import yaml
from unittest.mock import patch

import pytest
from syft_queue import q, load_queue, JobStatus
from syft_queue.test_utils import cleanup_all_test_artifacts


class TestJobPathUpdate:
    """Test job path updates when moving between status folders."""
    
    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Clean up test artifacts before and after tests."""
        cleanup_all_test_artifacts()
        yield
        cleanup_all_test_artifacts()
    
    def test_job_paths_update_on_move(self):
        """Test that job paths in metadata are updated when job moves between folders."""
        # Create queue
        queue = q("test_path_update_queue_" + str(os.getpid()))
        
        # Create a job
        job = queue.create_job(
            name="test_path_job",
            requester_email="user@test.com",
            target_email="admin@test.com",
            code_folder="/test/code/path",
            description="Test job for path updates"
        )
        
        # Verify initial paths in inbox
        inbox_path = queue.get_job_directory(job.uid, JobStatus.inbox)
        assert job.object_path == inbox_path
        assert str(job.mock_folder) == str(inbox_path / "mock")
        assert str(job.private_folder) == str(inbox_path / "private")
        assert str(job.code_folder_path) == str(inbox_path / "code")
        
        # Check syft-object metadata
        job_syft_yaml = inbox_path / "job.syftobject.yaml"
        assert job_syft_yaml.exists()
        
        with open(job_syft_yaml) as f:
            syft_data = yaml.safe_load(f)
        
        # Verify initial paths in metadata
        assert "folders" in syft_data["metadata"]
        assert syft_data["metadata"]["folders"]["mock"] == str(inbox_path / "mock")
        assert syft_data["metadata"]["folders"]["private"] == str(inbox_path / "private")
        assert syft_data["metadata"]["folders"]["code"] == str(inbox_path / "code")
        
        # Move job to approved status
        job.move_to_status(JobStatus.approved, queue)
        
        # Verify paths have been updated
        approved_path = queue.get_job_directory(job.uid, JobStatus.approved)
        assert job.object_path == approved_path
        assert str(job.mock_folder) == str(approved_path / "mock")
        assert str(job.private_folder) == str(approved_path / "private")
        assert str(job.code_folder_path) == str(approved_path / "code")
        
        # Check that the job was physically moved
        assert not inbox_path.exists()
        assert approved_path.exists()
        
        # Check updated syft-object metadata
        job_syft_yaml_new = approved_path / "job.syftobject.yaml"
        assert job_syft_yaml_new.exists()
        
        with open(job_syft_yaml_new) as f:
            syft_data_new = yaml.safe_load(f)
        
        # Verify updated paths in metadata
        assert "folders" in syft_data_new["metadata"]
        assert syft_data_new["metadata"]["folders"]["mock"] == str(approved_path / "mock")
        assert syft_data_new["metadata"]["folders"]["private"] == str(approved_path / "private")
        assert syft_data_new["metadata"]["folders"]["code"] == str(approved_path / "code")
        
        # Move job to running status
        job.move_to_status(JobStatus.running, queue)
        
        # Verify paths updated again
        running_path = queue.get_job_directory(job.uid, JobStatus.running)
        assert job.object_path == running_path
        assert str(job.mock_folder) == str(running_path / "mock")
        assert str(job.private_folder) == str(running_path / "private")
        assert str(job.code_folder_path) == str(running_path / "code")
        
        # Check syft-object metadata one more time
        job_syft_yaml_final = running_path / "job.syftobject.yaml"
        with open(job_syft_yaml_final) as f:
            syft_data_final = yaml.safe_load(f)
        
        assert syft_data_final["metadata"]["folders"]["mock"] == str(running_path / "mock")
        assert syft_data_final["metadata"]["folders"]["private"] == str(running_path / "private")
        assert syft_data_final["metadata"]["folders"]["code"] == str(running_path / "code")
    
    def test_job_paths_persist_after_reload(self):
        """Test that updated paths persist when job is reloaded from disk."""
        # Create queue
        queue = q("test_reload_queue_" + str(os.getpid()))
        
        # Create and submit a job
        job = queue.create_job(
            name="test_reload_job",
            requester_email="user@test.com",
            target_email="admin@test.com",
            code_folder="/test/code/path",
            description="Test job reload"
        )
        job_uid = job.uid
        
        # Move job to approved
        job.move_to_status(JobStatus.approved, queue)
        approved_path = queue.get_job_directory(job_uid, JobStatus.approved)
        
        # Load the existing queue instance
        queue2 = load_queue("test_reload_queue_" + str(os.getpid()))
        
        # Get the job from the new queue instance
        jobs = queue2.list_jobs(status=JobStatus.approved)
        assert len(jobs) == 1
        
        reloaded_job = jobs[0]
        
        # Verify the reloaded job has correct paths
        assert reloaded_job.object_path == approved_path
        assert str(reloaded_job.mock_folder) == str(approved_path / "mock")
        assert str(reloaded_job.private_folder) == str(approved_path / "private")
        assert str(reloaded_job.code_folder_path) == str(approved_path / "code")
        
        # Verify syft-object was loaded correctly
        assert hasattr(reloaded_job, '_syft_object')
        if reloaded_job._syft_object:
            assert "folders" in reloaded_job._syft_object.metadata
            assert reloaded_job._syft_object.metadata["folders"]["mock"] == str(approved_path / "mock")