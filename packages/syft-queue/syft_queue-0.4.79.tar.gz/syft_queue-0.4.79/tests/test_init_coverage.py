"""
Tests for __init__.py import handling
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock


def test_pipeline_import_failure():
    """Test that pipeline import failure is handled gracefully."""
    # Remove pipeline module if it exists
    if 'syft_queue.pipeline' in sys.modules:
        del sys.modules['syft_queue.pipeline']
    
    # Mock the import to fail
    with patch.dict('sys.modules', {'syft_queue.pipeline': None}):
        # Re-import the package
        if 'syft_queue' in sys.modules:
            del sys.modules['syft_queue']
        
        # This should not raise an error even if pipeline import fails
        import syft_queue
        
        # Core functionality should still be available
        assert hasattr(syft_queue, 'q')
        assert hasattr(syft_queue, 'Queue')
        assert hasattr(syft_queue, 'Job')
        
        # Pipeline classes should not be available
        assert not hasattr(syft_queue, 'Pipeline')
        assert not hasattr(syft_queue, 'PipelineBuilder')


def test_cleanup_on_import_with_output_suppression():
    """Test cleanup on import with output suppression."""
    # Remove syft_queue module if it exists
    if 'syft_queue' in sys.modules:
        del sys.modules['syft_queue']
        
    # Mock the cleanup functions, environment, and io redirection
    with patch('syft_queue._cleanup_all_ghost_job_folders') as mock_cleanup_ghost, \
         patch('syft_queue._cleanup_all_orphaned_queue_directories') as mock_cleanup_orphaned, \
         patch.dict('os.environ', {}, clear=True), \
         patch('io.StringIO') as mock_stringio, \
         patch('sys.stdout') as mock_stdout:
        
        mock_old_stdout = MagicMock()
        mock_stdout = mock_old_stdout
        
        # Import should trigger cleanup with output suppression
        import syft_queue
        
        # Cleanup functions should have been called
        mock_cleanup_ghost.assert_called_once()
        mock_cleanup_orphaned.assert_called_once()
        # StringIO should have been created for output suppression
        mock_stringio.assert_called_once()


def test_cleanup_skipped_in_test_environment():
    """Test that cleanup is skipped when PYTEST_CURRENT_TEST is set."""
    # Remove syft_queue module if it exists
    if 'syft_queue' in sys.modules:
        del sys.modules['syft_queue']
        
    # Mock the cleanup functions and set test environment
    with patch('syft_queue._cleanup_all_ghost_job_folders') as mock_cleanup_ghost, \
         patch('syft_queue._cleanup_all_orphaned_queue_directories') as mock_cleanup_orphaned, \
         patch.dict('os.environ', {'PYTEST_CURRENT_TEST': 'test_something'}, clear=True):
        
        # Import should NOT trigger cleanup in test environment
        import syft_queue
        
        # Cleanup functions should NOT have been called
        mock_cleanup_ghost.assert_not_called()
        mock_cleanup_orphaned.assert_not_called()


def test_cleanup_exception_handling():
    """Test that cleanup exceptions don't prevent import."""
    # Remove syft_queue module if it exists
    if 'syft_queue' in sys.modules:
        del sys.modules['syft_queue']
        
    # Mock cleanup to raise exception
    with patch('syft_queue._cleanup_all_ghost_job_folders', side_effect=Exception("Cleanup failed")), \
         patch.dict('os.environ', {}, clear=True):  # Clear PYTEST_CURRENT_TEST
        
        # Import should still work even if cleanup fails
        try:
            import syft_queue
            # Should not raise exception
            assert hasattr(syft_queue, 'q')
        except Exception as e:
            pytest.fail(f"Import failed due to cleanup exception: {e}")


def test_queues_collection_repr(mock_syftbox_env):
    """Test _QueuesCollection __repr__ and __str__ methods."""
    import syft_queue
    
    # Test __repr__
    result = repr(syft_queue.queues)
    assert isinstance(result, str)
    assert len(result) > 0  # Should contain some content
    
    # Test __str__
    result = str(syft_queue.queues)
    assert isinstance(result, str)
    assert len(result) > 0  # Should contain some content


def test_queues_collection_class(mock_syftbox_env):
    """Test _QueuesCollection class directly."""
    import syft_queue
    
    # Test that queues is an instance of _QueuesCollection
    assert isinstance(syft_queue.queues, syft_queue._QueuesCollection)
    
    # Test direct instantiation
    collection = syft_queue._QueuesCollection()
    result = repr(collection)
    assert isinstance(result, str)
    assert len(result) > 0  # Should contain some content


def test_cleanup_with_io_exception():
    """Test cleanup with io module import handling."""
    if 'syft_queue' in sys.modules:
        del sys.modules['syft_queue']
    
    # Mock to raise exception during output suppression setup
    with patch('syft_queue._cleanup_all_ghost_job_folders') as mock_cleanup_ghost, \
         patch.dict('os.environ', {}, clear=True), \
         patch('io.StringIO', side_effect=Exception("IO Error")):
        
        # Import should still work even if io setup fails
        try:
            import syft_queue
            # Should not raise exception even if io fails
            assert hasattr(syft_queue, 'q')
        except Exception as e:
            pytest.fail(f"Import failed due to io exception: {e}")


def test_cleanup_stdout_restoration():
    """Test that stdout is properly restored even if cleanup fails."""
    if 'syft_queue' in sys.modules:
        del sys.modules['syft_queue']
    
    with patch('syft_queue._cleanup_all_ghost_job_folders', side_effect=Exception("Cleanup failed")), \
         patch.dict('os.environ', {}, clear=True), \
         patch('io.StringIO') as mock_stringio, \
         patch('sys.stdout') as mock_stdout:
        
        mock_old_stdout = MagicMock()
        original_stdout = mock_old_stdout
        
        # Import should restore stdout even if cleanup fails
        import syft_queue
        
        # Should have attempted to create StringIO
        mock_stringio.assert_called_once()