"""Test that Job objects properly expose their paths."""

import pytest
from pathlib import Path
import tempfile
import shutil
import os
from unittest.mock import patch

from syft_queue import q, get_queue, JobStatus


def test_job_has_object_path_attribute():
    """Test that job objects have an object_path attribute accessible for the Path button."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Mock the SyftBox environment to use temp directory
        with patch.dict(os.environ, {'SYFTBOX_DATA_FOLDER': tmpdir}):
            # Create a queue
            queue = q("test_queue")
        
            # Create a job
            job = queue.create_job(
                name="test_job",
                requester_email="test@example.com",
                target_email="target@example.com",
                description="Test job for Path button"
            )
            
            # Verify job has object_path attribute
            assert hasattr(job, 'object_path')
            assert isinstance(job.object_path, Path)
            assert job.object_path.exists()
            assert job.object_path.is_dir()
            
            # Verify path contains the job UID
            assert str(job.uid) in str(job.object_path)
            
            # Verify the path can be converted to string (for API)
            path_str = str(job.object_path)
            assert isinstance(path_str, str)
            assert len(path_str) > 0


def test_job_path_attribute_serialization():
    """Test that job path can be serialized for API responses."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Mock the SyftBox environment to use temp directory
        with patch.dict(os.environ, {'SYFTBOX_DATA_FOLDER': tmpdir}):
            # Create a queue
            queue = q("test_queue")
        
            # Create a job
            job = queue.create_job(
                name="test_job",
                requester_email="test@example.com",
                target_email="target@example.com",
                description="Test job for API serialization"
            )
            
            # Simulate what the API does - convert path to string
            job_data = {
                "uid": str(job.uid),
                "name": job.name.replace("J:", ""),
                "description": job.description or "",
                "path": str(job.object_path)  # This is what we added
            }
            
            # Verify the serialized data
            assert "path" in job_data
            assert isinstance(job_data["path"], str)
            assert len(job_data["path"]) > 0
            assert str(job.uid) in job_data["path"]