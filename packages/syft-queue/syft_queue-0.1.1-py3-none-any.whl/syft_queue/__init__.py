"""
SyftQueue - A queue system for managing jobs across SyftBox datasites

This package provides a simple, portable queue system for SyftBox that uses
syft-objects natively for storage and supports relative paths for job portability.
"""

__version__ = "0.1.1"

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
    
    # Help
    help,
)

# Pipeline API (optional extended features)
try:
    from .pipeline import Pipeline, PipelineBuilder, PipelineStage
except ImportError:
    # Pipeline features are optional
    pass

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
    
    # Help
    "help",
]