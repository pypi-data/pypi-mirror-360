"""Test that jobs have correct UIDs, admin field, type, and updating descriptions"""

import pytest
from pathlib import Path
import yaml
import json


def test_job_syftobject_properties(mock_syftbox_env):
    """Test that jobs have correct properties in their syftobject"""
    from syft_queue import q
    
    # Create a test queue and job
    queue = q("properties_test", force=True)
    job = queue.create_job(
        name="Test Properties Job",
        description="Testing job properties",
        requester_email="requester@example.com",
        target_email="admin@example.com"
    )
    
    # Load the syftobject file
    syftobject_file = job.object_path / "job.syftobject.yaml"
    assert syftobject_file.exists()
    
    with open(syftobject_file) as f:
        data = yaml.safe_load(f)
    
    # Test 1: UID should match the job's UID (and folder name)
    assert str(data['uid']) == str(job.uid)
    assert job.object_path.name == str(job.uid)
    print(f"✅ UID matches: {job.uid}")
    
    # Test 2: Admin email should be in metadata
    assert 'admin_email' in data['metadata']
    assert data['metadata']['admin_email'] == "admin@example.com"
    print(f"✅ Admin email in metadata: {data['metadata']['admin_email']}")
    
    # Test 3: Type should be "folder"
    assert data['object_type'] == "folder"
    print(f"✅ Object type is: {data['object_type']}")
    
    # Test 4: Description should include status
    assert "Status: inbox" in data['description']
    assert "From: requester@example.com" in data['description']
    print(f"✅ Description includes status: {data['description']}")


def test_job_description_updates_with_status(mock_syftbox_env):
    """Test that job description updates when status changes"""
    from syft_queue import q, approve, start, complete
    
    # Create a test queue and job
    queue = q("status_update_test", force=True)
    job = queue.create_job(
        name="Test Status Update",
        description="My custom job",
        requester_email="requester@example.com",
        target_email="admin@example.com"
    )
    
    # Check initial description
    syftobject_file = job.object_path / "job.syftobject.yaml"
    with open(syftobject_file) as f:
        data = yaml.safe_load(f)
    
    assert "My custom job | Status: inbox" in data['description']
    initial_desc = data['description']
    print(f"Initial description: {initial_desc}")
    
    # Approve the job
    approved_job = approve(job)
    
    # Check description updated
    syftobject_file = approved_job.object_path / "job.syftobject.yaml"
    with open(syftobject_file) as f:
        data = yaml.safe_load(f)
    
    assert "My custom job | Status: approved" in data['description']
    assert data['description'] != initial_desc
    print(f"After approval: {data['description']}")
    
    # Start the job
    running_job = start(approved_job)
    
    # Check description updated again
    syftobject_file = running_job.object_path / "job.syftobject.yaml"
    with open(syftobject_file) as f:
        data = yaml.safe_load(f)
    
    assert "My custom job | Status: running" in data['description']
    print(f"After starting: {data['description']}")
    
    # Complete the job
    completed_job = complete(running_job)
    
    # Check final description
    syftobject_file = completed_job.object_path / "job.syftobject.yaml"
    with open(syftobject_file) as f:
        data = yaml.safe_load(f)
    
    assert "My custom job | Status: completed" in data['description']
    print(f"After completion: {data['description']}")
    
    print("✅ Description updates with status changes!")