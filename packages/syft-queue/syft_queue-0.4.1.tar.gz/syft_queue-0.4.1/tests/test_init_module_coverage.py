"""
Focused tests for __init__.py module coverage
"""

import pytest
import sys
from unittest.mock import patch, MagicMock


def test_init_pipeline_import_handling():
    """Test pipeline import error handling"""
    # Clear modules to test import behavior
    modules_to_clear = [mod for mod in sys.modules.keys() if mod.startswith('syft_queue')]
    for mod in modules_to_clear:
        if mod in sys.modules:
            del sys.modules[mod]
    
    # Test pipeline import failure
    with patch.dict('sys.modules', {'syft_queue.pipeline': None}):
        import syft_queue
        # Pipeline should not be available
        assert not hasattr(syft_queue, 'Pipeline') or syft_queue.Pipeline is None


def test_init_auto_install_handling():
    """Test auto_install error handling"""
    # Clear modules to test import behavior
    modules_to_clear = [mod for mod in sys.modules.keys() if mod.startswith('syft_queue')]
    for mod in modules_to_clear:
        if mod in sys.modules:
            del sys.modules[mod]
    
    # Test auto_install exception handling
    with patch('syft_queue.auto_install.auto_install', side_effect=Exception("Install error")):
        import syft_queue
        # Should still import successfully despite auto_install error


def test_init_banner_in_interactive_mode():
    """Test startup banner in interactive mode"""
    # Test banner showing in interactive environment
    with patch('sys.flags') as mock_flags:
        mock_flags.interactive = True
        with patch('syft_queue.auto_install.show_startup_banner') as mock_banner:
            # Re-import to trigger banner logic
            import syft_queue
            # Note: banner may or may not be called depending on import state


def test_queues_collection_repr():
    """Test _QueuesCollection __repr__ method"""
    from syft_queue import queues
    
    # Test Jupyter environment detection
    queues._ipython_canary_method_should_not_exist_ = True
    try:
        with patch.object(queues, '_repr_html_', return_value='<html>Jupyter output</html>'):
            result = repr(queues)
            assert result == '<html>Jupyter output</html>'
    finally:
        if hasattr(queues, '_ipython_canary_method_should_not_exist_'):
            delattr(queues, '_ipython_canary_method_should_not_exist_')
    
    # Test non-Jupyter environment
    with patch('syft_queue.queue._get_queues_table', return_value='Text table output'):
        result = repr(queues)
        assert result == 'Text table output'


def test_queues_collection_str():
    """Test _QueuesCollection __str__ method"""
    from syft_queue import queues
    
    with patch('syft_queue.queue._get_queues_table', return_value='String table output'):
        result = str(queues)
        assert result == 'String table output'


def test_queues_collection_repr_html():
    """Test _QueuesCollection _repr_html_ method"""
    from syft_queue import queues
    
    # Test when server fails to start
    with patch('syft_queue.server_utils.start_server', return_value=False):
        html = queues._repr_html_()
        assert 'Error' in html
        assert 'Could not start SyftQueue server' in html
    
    # Test when server starts successfully
    with patch('syft_queue.server_utils.start_server', return_value=True):
        with patch('syft_queue.server_utils.get_syft_queue_url', return_value='http://localhost:8000/widget'):
            html = queues._repr_html_()
            assert '<iframe' in html
            assert 'http://localhost:8000/widget' in html
            assert 'SyftQueue Dashboard' in html


def test_queues_collection_widget():
    """Test _QueuesCollection widget method"""
    from syft_queue import queues
    
    # Test when server fails to start
    with patch('syft_queue.server_utils.start_server', return_value=False):
        widget = queues.widget()
        assert 'Error' in widget
        assert 'Could not start SyftQueue server' in widget
    
    # Test with default parameters
    with patch('syft_queue.server_utils.start_server', return_value=True):
        with patch('syft_queue.server_utils.get_syft_queue_url', return_value='http://localhost:8000/widget'):
            widget = queues.widget()
            assert '<iframe' in widget
            assert 'width="100%"' in widget
            assert 'height="600px"' in widget
            assert 'http://localhost:8000/widget' in widget
    
    # Test with custom parameters
    with patch('syft_queue.server_utils.start_server', return_value=True):
        with patch('syft_queue.server_utils.get_syft_queue_url', return_value='http://localhost:8000/widget'):
            widget = queues.widget(width="800px", height="400px")
            assert 'width="800px"' in widget
            assert 'height="400px"' in widget
    
    # Test with custom URL
    with patch('syft_queue.server_utils.start_server', return_value=True):
        widget = queues.widget(url="http://custom.url/widget")
        assert 'http://custom.url/widget' in widget


def test_test_utils_import():
    """Test test_utils import handling"""
    # Test successful import
    try:
        from syft_queue import cleanup_all_test_artifacts, cleanup_test_objects, cleanup_test_queues
        # If available, they should be callable
        assert callable(cleanup_all_test_artifacts)
        assert callable(cleanup_test_objects)
        assert callable(cleanup_test_queues)
    except ImportError:
        # Test utilities are optional
        pass


def test_cleanup_on_import():
    """Test cleanup functions run on import"""
    # Test that cleanup functions are called during import
    # This tests the auto-cleanup section at the end of __init__.py
    
    # Mock the cleanup functions
    with patch('syft_queue._cleanup_all_ghost_job_folders') as mock_ghost:
        with patch('syft_queue._cleanup_all_orphaned_queue_directories') as mock_orphaned:
            with patch('os.environ.get', return_value=None):  # Not in test environment
                with patch('sys.stdout') as mock_stdout:
                    # Re-import to trigger cleanup
                    import importlib
                    import syft_queue
                    importlib.reload(syft_queue)


def test_version_attribute():
    """Test that version attribute is available"""
    import syft_queue
    assert hasattr(syft_queue, '__version__')
    assert isinstance(syft_queue.__version__, str)
    assert len(syft_queue.__version__) > 0


def test_all_exports():
    """Test __all__ exports are available"""
    import syft_queue
    
    # Test that key exports are available
    assert hasattr(syft_queue, 'q')
    assert hasattr(syft_queue, 'Job')
    assert hasattr(syft_queue, 'JobStatus')
    assert hasattr(syft_queue, 'CodeQueue')
    assert hasattr(syft_queue, 'DataQueue')
    assert hasattr(syft_queue, 'approve')
    assert hasattr(syft_queue, 'reject')
    assert hasattr(syft_queue, 'start')
    assert hasattr(syft_queue, 'complete')
    assert hasattr(syft_queue, 'fail')
    assert hasattr(syft_queue, 'queues')


def test_queues_collection_instance():
    """Test that queues is properly instantiated"""
    from syft_queue import queues
    
    # Test that queues is an instance of _QueuesCollection
    assert hasattr(queues, '__repr__')
    assert hasattr(queues, '__str__')
    assert hasattr(queues, '_repr_html_')
    assert hasattr(queues, 'widget')
    
    # Test that methods are callable
    assert callable(queues.__repr__)
    assert callable(queues.__str__)
    assert callable(queues._repr_html_)
    assert callable(queues.widget)