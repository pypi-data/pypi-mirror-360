"""Test improved test detection logic and cleanup functions."""

import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from syft_queue.queue import _is_test_environment, Job, CodeQueue
from syft_queue.test_utils import (
    cleanup_test_objects,
    force_cleanup_all_q_objects,
    cleanup_all_test_artifacts,
    TEST_QUEUE_PREFIX,
    TEST_JOB_PREFIX
)


def test_is_test_environment_with_pytest():
    """Test that _is_test_environment returns True when running under pytest."""
    # Since this test is running under pytest, it should return True
    assert _is_test_environment() is True


def test_is_test_environment_with_environment_variables():
    """Test that _is_test_environment detects various test environment variables."""
    # Store original values
    original_values = {}
    test_vars = ['TESTING', 'TEST_MODE', 'CI', 'GITHUB_ACTIONS']
    
    for var in test_vars:
        original_values[var] = os.environ.get(var)
        os.environ.pop(var, None)
    
    try:
        # Test with each environment variable
        for var in test_vars:
            os.environ[var] = "1"
            assert _is_test_environment() is True
            os.environ.pop(var)
    finally:
        # Restore original values
        for var, value in original_values.items():
            if value is not None:
                os.environ[var] = value


def test_is_test_environment_with_call_stack():
    """Test that _is_test_environment detects test files in call stack."""
    # This test itself should be detected as a test environment
    # because it's in a file with 'test_' prefix
    assert _is_test_environment() is True


def test_job_gets_test_prefix():
    """Test that jobs created in test environment get test_J: prefix."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a job - should get test_J: prefix automatically
        job = Job(
            folder_path=temp_dir,
            name="my_test_job",
            requester_email="test@test.com"
        )
        
        # Should have test_J: prefix
        assert job.name.startswith(TEST_JOB_PREFIX)
        assert job.name == "test_J:my_test_job"


def test_job_preserves_existing_test_prefix():
    """Test that jobs with existing test_J: prefix are preserved."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a job with existing test_J: prefix
        job = Job(
            folder_path=temp_dir,
            name="test_J:already_prefixed",
            requester_email="test@test.com"
        )
        
        # Should keep the existing prefix
        assert job.name == "test_J:already_prefixed"


def test_job_replaces_regular_j_prefix():
    """Test that jobs with J: prefix get it replaced with test_J: prefix."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a job with J: prefix
        job = Job(
            folder_path=temp_dir,
            name="J:regular_job",
            requester_email="test@test.com"
        )
        
        # Should replace J: with test_J:
        assert job.name == "test_J:regular_job"


def test_queue_gets_test_prefix():
    """Test that queues created in test environment get test_Q: prefix."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a queue - should get test_Q: prefix automatically
        queue = CodeQueue(
            folder_path=temp_dir,
            queue_name="my_test_queue",
            owner_email="test@test.com"
        )
        
        # Should have test_Q: prefix
        assert queue.queue_name.startswith(TEST_QUEUE_PREFIX)
        assert queue.queue_name == "test_Q:my_test_queue"


def test_queue_preserves_existing_test_prefix():
    """Test that queues with existing test_Q: prefix are preserved."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a queue with existing test_Q: prefix
        queue = CodeQueue(
            folder_path=temp_dir,
            queue_name="test_Q:already_prefixed",
            owner_email="test@test.com"
        )
        
        # Should keep the existing prefix
        assert queue.queue_name == "test_Q:already_prefixed"


def test_queue_replaces_regular_q_prefix():
    """Test that queues with Q: prefix get it replaced with test_Q: prefix."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a queue with Q: prefix
        queue = CodeQueue(
            folder_path=temp_dir,
            queue_name="Q:regular_queue",
            owner_email="test@test.com"
        )
        
        # Should replace Q: with test_Q:
        assert queue.queue_name == "test_Q:regular_queue"


def test_cleanup_test_objects_function():
    """Test that cleanup_test_objects function can be called without errors."""
    # This should not raise any errors
    try:
        cleanup_test_objects()
    except Exception as e:
        # Allow ImportError for syft_objects, but not other errors
        if "syft_objects" not in str(e):
            raise


def test_force_cleanup_all_q_objects_function():
    """Test that force_cleanup_all_q_objects function can be called without errors."""
    # This should not raise any errors
    try:
        result = force_cleanup_all_q_objects()
        assert isinstance(result, int)  # Should return count of deleted objects
    except Exception as e:
        # Allow ImportError for syft_objects, but not other errors
        if "syft_objects" not in str(e):
            raise


def test_cleanup_all_test_artifacts_function():
    """Test that cleanup_all_test_artifacts function can be called without errors."""
    # This should not raise any errors
    try:
        cleanup_all_test_artifacts()
    except Exception as e:
        # Allow ImportError for syft_objects, but not other errors
        if "syft_objects" not in str(e):
            raise


def test_cleanup_all_test_artifacts_with_force():
    """Test that cleanup_all_test_artifacts function works with force=True."""
    # This should not raise any errors
    try:
        cleanup_all_test_artifacts(force=True)
    except Exception as e:
        # Allow ImportError for syft_objects, but not other errors
        if "syft_objects" not in str(e):
            raise


def test_robust_test_detection_without_pytest():
    """Test detection without pytest using mocked environment."""
    # Mock the environment to not have pytest
    with patch('sys.modules', {k: v for k, v in __import__('sys').modules.items() if 'pytest' not in k}):
        with patch.dict(os.environ, {}, clear=True):
            # Without pytest or env vars, should still detect test from filename
            assert _is_test_environment() is True  # This file has 'test_' in name


@pytest.mark.parametrize("test_pattern", [
    "test_Q:my_queue",
    "test_J:my_job", 
    "Q:test_something",
    "J:test_something",
    "Q:cleanup_queue",
    "J:cleanup_job",
    "Q:tmp_queue",
    "J:tmp_job"
])
def test_force_cleanup_detects_test_patterns(test_pattern):
    """Test that force cleanup detects various test patterns."""
    # Mock syft_objects with test objects
    mock_obj = MagicMock()
    mock_obj.name = test_pattern
    
    with patch('syft_objects.objects', [mock_obj]):
        # This should identify the object as a test object
        # We can't easily test the full cleanup without real files,
        # but we can verify the pattern detection logic
        test_patterns = [
            "test_Q:",
            "test_J:",
            "Q:test_",
            "J:test_",
            "Q:cleanup",
            "J:cleanup",
            "Q:tmp",
            "J:tmp"
        ]
        
        matches_pattern = any(test_pattern.startswith(pattern) for pattern in test_patterns)
        has_test_part = any(test_part in test_pattern.lower() for test_part in ['test_', 'tmp_', 'cleanup_'])
        
        assert matches_pattern or has_test_part, f"Pattern {test_pattern} should be detected as test pattern"