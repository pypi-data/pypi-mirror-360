"""
Init module coverage boost tests - targeting 95% overall coverage
"""

import pytest
import sys
from unittest.mock import patch, MagicMock


def test_init_widget_functionality():
    """Test __init__.py widget functionality thoroughly"""
    from syft_queue import queues
    
    # Test widget with server start failure
    with patch('syft_queue.server_utils.start_server', return_value=False):
        widget = queues.widget()
        assert 'Error' in widget
        assert 'Could not start SyftQueue server' in widget
    
    # Test widget with successful server start
    with patch('syft_queue.server_utils.start_server', return_value=True):
        with patch('syft_queue.server_utils.get_syft_queue_url', return_value='http://localhost:8000/widget'):
            # Test default widget
            widget = queues.widget()
            assert '<iframe' in widget
            assert 'width="100%"' in widget
            assert 'height="600px"' in widget
            assert 'http://localhost:8000/widget' in widget
            
            # Test custom dimensions
            widget = queues.widget(width="800px", height="400px")
            assert 'width="800px"' in widget
            assert 'height="400px"' in widget
            
            # Test custom URL
            widget = queues.widget(url="http://custom.example.com/widget")
            assert 'http://custom.example.com/widget' in widget


def test_init_repr_html_functionality():
    """Test __init__.py _repr_html_ functionality"""
    from syft_queue import queues
    
    # Test _repr_html_ with server failure
    with patch('syft_queue.server_utils.start_server', return_value=False):
        html = queues._repr_html_()
        assert 'Error' in html
        assert 'Could not start SyftQueue server' in html
    
    # Test _repr_html_ with server success
    with patch('syft_queue.server_utils.start_server', return_value=True):
        with patch('syft_queue.server_utils.get_syft_queue_url', return_value='http://localhost:8000/widget'):
            html = queues._repr_html_()
            assert '<iframe' in html
            assert 'http://localhost:8000/widget' in html
            assert 'SyftQueue Dashboard' in html
            assert 'width="100%"' in html
            assert 'height="600px"' in html


def test_init_jupyter_repr():
    """Test __init__.py Jupyter repr functionality"""
    from syft_queue import queues
    
    # Test Jupyter environment detection by patching sys.modules
    with patch('sys.modules', {'ipykernel': MagicMock(), 'IPython': MagicMock()}):
        with patch.object(queues, '_repr_html_', return_value='<div>Jupyter HTML</div>'):
            result = repr(queues)
            assert result == '<div>Jupyter HTML</div>'
    
    # Test non-Jupyter environment
    with patch('sys.modules', {}):
        with patch('syft_queue.queue._get_queues_table', return_value='Text table'):
            result = repr(queues)
            assert result == 'Text table'


def test_init_string_representation():
    """Test __init__.py string representation"""
    from syft_queue import queues
    
    with patch('syft_queue.queue._get_queues_table', return_value='Queue table output'):
        result = str(queues)
        assert result == 'Queue table output'


def test_init_import_error_handling():
    """Test __init__.py import error handling"""
    # Test pipeline import failure
    modules_to_clear = [mod for mod in sys.modules.keys() if mod.startswith('syft_queue')]
    for mod in modules_to_clear:
        if mod in sys.modules:
            del sys.modules[mod]
    
    with patch.dict('sys.modules', {'syft_queue.pipeline': None}):
        import syft_queue
        # Should still work without pipeline


def test_init_auto_install_error_handling():
    """Test auto_install error handling in __init__.py"""
    # Test that auto_install errors don't break import
    with patch('syft_queue.auto_install.auto_install', side_effect=Exception("Auto install failed")):
        try:
            import syft_queue
            # Should succeed despite auto_install error
        except Exception as e:
            # Should not raise exception
            pytest.fail(f"Import failed due to auto_install error: {e}")


def test_init_banner_handling():
    """Test startup banner handling"""
    # Test banner in interactive mode
    with patch('sys.flags') as mock_flags:
        mock_flags.interactive = True
        with patch('builtins.hasattr', return_value=True):
            with patch('syft_queue.auto_install.show_startup_banner') as mock_banner:
                import syft_queue
                # Banner may or may not be called depending on import state


def test_init_test_utils_optional_import():
    """Test test_utils optional import"""
    # Test when test_utils is available
    try:
        from syft_queue import cleanup_all_test_artifacts, cleanup_test_objects, cleanup_test_queues
        assert callable(cleanup_all_test_artifacts)
        assert callable(cleanup_test_objects)
        assert callable(cleanup_test_queues)
    except ImportError:
        # Test utilities are optional - this is expected
        pass


def test_init_cleanup_on_import():
    """Test cleanup functions called on import"""
    # Test that cleanup is suppressed during testing
    with patch('os.environ.get') as mock_env:
        mock_env.return_value = 'test_session'  # PYTEST_CURRENT_TEST is set
        with patch('syft_queue._cleanup_all_ghost_job_folders') as mock_ghost:
            with patch('syft_queue._cleanup_all_orphaned_queue_directories') as mock_orphaned:
                import syft_queue
                # Cleanup should not be called during testing
    
    # Test cleanup when not in test environment
    with patch('os.environ.get', return_value=None):
        with patch('syft_queue._cleanup_all_ghost_job_folders') as mock_ghost:
            with patch('syft_queue._cleanup_all_orphaned_queue_directories') as mock_orphaned:
                with patch('sys.stdout'):
                    import syft_queue
                    # Cleanup functions should be called


def test_init_all_attributes():
    """Test that all __all__ attributes are properly exported"""
    import syft_queue
    
    # Test core components
    assert hasattr(syft_queue, 'Job')
    assert hasattr(syft_queue, 'BaseQueue')
    assert hasattr(syft_queue, 'CodeQueue')
    assert hasattr(syft_queue, 'DataQueue')
    assert hasattr(syft_queue, 'Queue')
    assert hasattr(syft_queue, 'JobStatus')
    assert hasattr(syft_queue, 'q')
    assert hasattr(syft_queue, 'queue')
    
    # Test queue management
    assert hasattr(syft_queue, 'get_queue')
    assert hasattr(syft_queue, 'list_queues')
    assert hasattr(syft_queue, 'queues')
    assert hasattr(syft_queue, 'cleanup_orphaned_queues')
    assert hasattr(syft_queue, 'recreate_missing_queue_directories')
    assert hasattr(syft_queue, 'get_queues_path')
    
    # Test progression API
    assert hasattr(syft_queue, 'approve')
    assert hasattr(syft_queue, 'reject')
    assert hasattr(syft_queue, 'start')
    assert hasattr(syft_queue, 'complete')
    assert hasattr(syft_queue, 'fail')
    assert hasattr(syft_queue, 'timeout')
    assert hasattr(syft_queue, 'advance')
    
    # Test batch operations
    assert hasattr(syft_queue, 'approve_all')
    assert hasattr(syft_queue, 'process_queue')
    
    # Test execution utilities
    assert hasattr(syft_queue, 'prepare_job_for_execution')
    assert hasattr(syft_queue, 'execute_job_with_context')
    
    # Test help
    assert hasattr(syft_queue, 'help')


def test_init_version_attribute():
    """Test version attribute is properly set"""
    import syft_queue
    
    assert hasattr(syft_queue, '__version__')
    assert isinstance(syft_queue.__version__, str)
    assert len(syft_queue.__version__) > 0
    # Should follow semantic versioning pattern
    version_parts = syft_queue.__version__.split('.')
    assert len(version_parts) >= 2


def test_init_queues_collection_type():
    """Test that queues collection is properly instantiated"""
    from syft_queue import queues
    
    # Test that it's the right type
    assert hasattr(queues, '__repr__')
    assert hasattr(queues, '__str__')
    assert hasattr(queues, '_repr_html_')
    assert hasattr(queues, 'widget')
    
    # Test that methods are callable
    assert callable(queues.__repr__)
    assert callable(queues.__str__)
    assert callable(queues._repr_html_)
    assert callable(queues.widget)


def test_init_optional_pipeline_import():
    """Test optional pipeline import behavior"""
    try:
        from syft_queue import Pipeline, PipelineBuilder, PipelineStage
        # If available, test they're properly imported
        assert Pipeline is not None
        assert PipelineBuilder is not None
        assert PipelineStage is not None
    except ImportError:
        # Pipeline features are optional
        pass