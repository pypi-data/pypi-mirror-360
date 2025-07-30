"""Test that jobs create proper syftobject files"""

import pytest
from pathlib import Path


def test_job_creates_syftobject_file(mock_syftbox_env):
    """Test that jobs create job.syftobject.yaml files with correct content"""
    from syft_queue import q
    import yaml
    
    # Create a test queue and job
    queue = q("syftobject_test", force=True)
    job = queue.create_job(
        name="Test SyftObject Job",
        description="Testing syftobject file creation",
        requester_email="requester@example.com",
        target_email="owner@example.com"
    )
    
    # Check that job.syftobject.yaml was created
    syftobject_file = job.object_path / "job.syftobject.yaml"
    assert syftobject_file.exists(), f"Expected {syftobject_file} to exist"
    
    # Load and verify the content
    with open(syftobject_file) as f:
        data = yaml.safe_load(f)
    
    # Verify key fields
    # The name includes prefix and UID, so just check it contains our name
    assert "Test SyftObject Job" in data['name']
    # Description is auto-generated to include job metadata
    assert "requester@example.com" in data['description']
    assert "owner@example.com" in data['description']
    assert data['object_type'] == "folder"
    
    # Verify URLs point to app_data location
    assert "app_data/syft-queues" in data['private_url']
    assert data['private_url'] == data['mock_url']  # For jobs, both should be same
    assert data['syftobject'].endswith("/job.syftobject.yaml")
    
    # Verify the old syftobject.yaml file doesn't exist
    old_file = job.object_path / "syftobject.yaml"
    assert not old_file.exists(), f"Old syftobject.yaml file should not exist"
    
    print(f"✅ Job created proper syftobject file at: {syftobject_file}")
    print(f"   Name: {data['name']}")
    print(f"   URL: {data['private_url']}")