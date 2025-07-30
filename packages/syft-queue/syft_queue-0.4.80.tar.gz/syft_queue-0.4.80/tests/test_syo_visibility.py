"""Test that syft-queue jobs are visible in syo.objects"""

import pytest
import tempfile
import shutil
from pathlib import Path
import os
import sys

# Add the parent directory to the path so we can import from src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_job_visibility_in_syo_objects(tmp_path):
    """Test that jobs created by syft-queue appear in syo.objects"""
    
    # Set up a temporary SyftBox directory
    syftbox_dir = tmp_path / "syftbox_test"
    datasites_dir = syftbox_dir / "datasites"
    user_dir = datasites_dir / "test@example.com"
    app_data_dir = user_dir / "app_data"
    app_data_dir.mkdir(parents=True)
    
    # Mock the SyftBox environment
    os.environ["SYFTBOX_DATA_DIR"] = str(syftbox_dir)
    
    # Import after setting environment
    import syft_queue as sq
    import syft_objects as syo
    
    try:
        # Create a test queue and job
        q = sq.q("visibility_test_queue", owner_email="test@example.com", force=True)
        job = q.create_job(
            name="Test Visibility Job",
            description="Testing if job appears in syo.objects",
            requester_email="requester@example.com",
            target_email="test@example.com"
        )
        
        # The job should have created a job.syftobject.yaml file
        syftobject_file = job.object_path / "job.syftobject.yaml"
        assert syftobject_file.exists(), f"Expected {syftobject_file} to exist"
        
        # Refresh syo.objects and check if the job appears
        syo.objects.refresh()
        
        # Look for our job
        found = False
        for obj in syo.objects:
            if obj.name == "Test Visibility Job":
                found = True
                assert obj.description == "Testing if job appears in syo.objects"
                assert obj.object_type == "folder"
                assert "test@example.com" in obj.private_url
                assert "app_data/syft-queues" in obj.private_url
                break
        
        assert found, "Job was not found in syo.objects after refresh"
        
        # Clean up
        sq.delete_queue("visibility_test_queue", owner_email="test@example.com")
        
    finally:
        # Clean up environment
        if "SYFTBOX_DATA_DIR" in os.environ:
            del os.environ["SYFTBOX_DATA_DIR"]


if __name__ == "__main__":
    # Run the test directly
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        test_job_visibility_in_syo_objects(Path(tmp))
        print("✅ Test passed: Jobs are visible in syo.objects!")