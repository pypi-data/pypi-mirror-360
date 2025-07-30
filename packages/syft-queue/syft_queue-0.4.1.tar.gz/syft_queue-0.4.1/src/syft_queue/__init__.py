"""
SyftQueue - A queue system for managing jobs across SyftBox datasites

This package provides a simple, portable queue system for SyftBox that uses
syft-objects natively for storage and supports relative paths for job portability.
"""

__version__ = "0.4.1"

# Import main components
from .queue import (
    # Core classes
    Job,
    BaseQueue,
    CodeQueue,
    DataQueue,
    Queue,  # Alias for CodeQueue (backward compatibility)
    JobStatus,
    
    # Main factory function
    q,
    queue,
    
    # Queue management
    get_queue,
    list_queues,
    queues,
    cleanup_orphaned_queues,
    recreate_missing_queue_directories,
    get_queues_path,
    
    # Job progression API
    approve,
    reject,
    start,
    complete,
    fail,
    timeout,
    advance,
    
    # Batch operations
    approve_all,
    process_queue,
    
    # Execution utilities
    prepare_job_for_execution,
    execute_job_with_context,
    
    # Internal utilities (for testing)
    _queue_exists,
    _cleanup_empty_queue_directory,
    _cleanup_ghost_job_folders,
    _cleanup_all_ghost_job_folders,
    _is_ghost_job_folder,
    _cleanup_orphaned_queue_directories,
    _cleanup_all_orphaned_queue_directories,
    _queue_has_valid_syftobject,
    _generate_mock_data,
    _get_queues_table,
    
    # Help
    help,
)

# Pipeline API (optional extended features)
try:
    from .pipeline import Pipeline, PipelineBuilder, PipelineStage
except ImportError:
    # Pipeline features are optional
    pass

# Note: sq module is available for import but not imported here to avoid circular imports

# Auto-install as SyftBox app if SyftBox is available
try:
    from .auto_install import auto_install, show_startup_banner
    auto_install()
    # Only show banner in interactive environments
    import sys
    if hasattr(sys, 'ps1') or sys.flags.interactive:
        show_startup_banner()
except Exception:
    # Don't let auto-install errors prevent import
    pass

# Create a queues collection similar to syft_objects.objects
class _QueuesCollection:
    """A collection that displays queues when accessed, similar to syft_objects.objects"""
    
    def __repr__(self):
        # Always try to use the iframe first, fall back to text only if server fails
        try:
            # Check if we're in a Jupyter-like environment
            import sys
            if 'ipykernel' in sys.modules or 'IPython' in sys.modules:
                return self._repr_html_()
        except:
            pass
        
        # Fallback to text table for non-Jupyter environments only
        from .queue import _get_queues_table
        return _get_queues_table()
    
    def __str__(self):
        from .queue import _get_queues_table
        return _get_queues_table()
    
    def _repr_html_(self):
        """Display the queues dashboard in an iframe for Jupyter"""
        from .server_utils import get_syft_queue_url, start_server
        
        # Ensure server is running
        if not start_server():
            return "<div>Error: Could not start SyftQueue server</div>"
        
        url = get_syft_queue_url("widget")
        
        return f"""
        <iframe 
            src="{url}" 
            width="100%" 
            height="600px"
            frameborder="0"
            style="border: 1px solid #ddd; border-radius: 4px;"
            title="SyftQueue Dashboard">
        </iframe>
        """
    
    def widget(self, width="100%", height="600px", url=None):
        """Display the syft-queue widget in an iframe with custom dimensions"""
        from .server_utils import get_syft_queue_url, start_server
        
        # Ensure server is running
        if not start_server():
            return "<div>Error: Could not start SyftQueue server</div>"
        
        if url is None:
            url = get_syft_queue_url("widget")
        
        return f"""
        <iframe 
            src="{url}" 
            width="{width}" 
            height="{height}"
            frameborder="0"
            style="border: 1px solid #ddd; border-radius: 4px;"
            title="SyftQueue Dashboard">
        </iframe>
        """

# Create the queues instance
queues = _QueuesCollection()

__all__ = [
    # Core
    "Job",
    "BaseQueue",
    "CodeQueue", 
    "DataQueue",
    "Queue",  # Alias for CodeQueue
    "JobStatus",
    "q",
    "queue",
    
    # Queue management
    "get_queue",
    "list_queues",
    "queues",
    "cleanup_orphaned_queues",
    "recreate_missing_queue_directories",
    "get_queues_path",
    
    # Job progression
    "approve",
    "reject",
    "start",
    "complete",
    "fail",
    "timeout",
    "advance",
    
    # Batch operations
    "approve_all",
    "process_queue",
    
    # Execution
    "prepare_job_for_execution",
    "execute_job_with_context",
    
    # Internal utilities (for testing)
    "_queue_exists",
    "_cleanup_empty_queue_directory",
    "_cleanup_ghost_job_folders",
    "_cleanup_all_ghost_job_folders",
    "_is_ghost_job_folder",
    "_cleanup_orphaned_queue_directories",
    "_cleanup_all_orphaned_queue_directories",
    "_queue_has_valid_syftobject",
    "_generate_mock_data",
    "_get_queues_table",
    
    # Help
    "help",

]

# Import test utilities if needed
try:
    from .test_utils import cleanup_all_test_artifacts, cleanup_test_objects, cleanup_test_queues
    __all__.extend(["cleanup_all_test_artifacts", "cleanup_test_objects", "cleanup_test_queues"])
except ImportError:
    pass  # Test utilities are optional

# Auto-cleanup ghost job folders and orphaned queue directories on import
# Note: Disabled to avoid slow UI loading - cleanup can be done manually if needed
# Note: The cleanup was causing job loading during import which slowed down syft_queue.queues
# try:
#     # Only run cleanup if not in test environment
#     import os
#     if not os.environ.get('PYTEST_CURRENT_TEST'):
#         # Suppress output during auto-cleanup
#         import io
#         import sys
#         old_stdout = sys.stdout
#         sys.stdout = io.StringIO()
#         try:
#             _cleanup_all_ghost_job_folders()
#             _cleanup_all_orphaned_queue_directories()
#         finally:
#             sys.stdout = old_stdout
# except Exception:
#     # Don't let cleanup errors prevent import
#     pass