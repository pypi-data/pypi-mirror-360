"""Test utilities for syft-queue tests"""

import shutil
from pathlib import Path
from typing import List, Optional

# Test naming constants
TEST_QUEUE_PREFIX = "test_Q:"
TEST_JOB_PREFIX = "test_J:"

def cleanup_test_objects():
    """Clean up all test queue and job objects from syft-objects."""
    try:
        import syft_objects as syo
        
        # Find all test objects
        test_objects = []
        for obj in syo.objects:
            if obj.name.startswith(TEST_QUEUE_PREFIX) or obj.name.startswith(TEST_JOB_PREFIX):
                test_objects.append(obj)
        
        # Also do direct file cleanup since syft-objects files might use lowercase prefixes
        try:
            # Find SyftBox directory
            syftbox_path = Path.home() / "SyftBox"
            if syftbox_path.exists():
                # Look for datasites directory
                datasites = syftbox_path / "datasites"
                if datasites.exists():
                    for datasite in datasites.iterdir():
                        if datasite.is_dir():
                            # Check both private and public object directories
                            for subdir in ["private/objects", "public/objects"]:
                                objects_dir = datasite / subdir
                                if objects_dir.exists():
                                    # Delete test files with both uppercase and lowercase prefixes
                                    for pattern in ["test_j:*", "test_J:*", "test_q:*", "test_Q:*"]:
                                        for file_path in objects_dir.glob(pattern):
                                            try:
                                                file_path.unlink()
                                            except Exception as e:
                                                print(f"Warning: Could not delete {file_path}: {e}")
        except Exception as e:
            print(f"Warning during direct file cleanup: {e}")
        
        # Delete test objects by removing their files
        deleted_count = 0
        for obj in test_objects:
            try:
                # The most reliable way is to delete the files directly
                deleted = False
                
                # Try to get the file paths
                paths_to_delete = []
                if hasattr(obj, 'private') and hasattr(obj.private, 'path'):
                    path = Path(obj.private.path)
                    # Skip if path is just "." which indicates a bad path
                    if str(path) != ".":
                        paths_to_delete.append(path)
                if hasattr(obj, 'mock') and hasattr(obj.mock, 'path'):
                    path = Path(obj.mock.path) 
                    if str(path) != ".":
                        paths_to_delete.append(path)
                if hasattr(obj, 'syftobject') and hasattr(obj.syftobject, 'path'):
                    path = Path(obj.syftobject.path)
                    if str(path) != ".":
                        paths_to_delete.append(path)
                
                # Delete the files
                for path in paths_to_delete:
                    if path.exists():
                        path.unlink()
                        deleted = True
                
                # Also try to remove parent directory if empty
                if paths_to_delete and deleted:
                    parent = paths_to_delete[0].parent
                    if parent.exists() and parent != Path(".") and not any(parent.iterdir()):
                        try:
                            parent.rmdir()
                        except:
                            pass
                    deleted_count += 1
                    
            except Exception as e:
                print(f"Warning: Could not delete test object {obj.name}: {e}")
        
        print(f"Deleted {deleted_count} test objects from syft-objects")
        
        # Force refresh of syft-objects - this is critical!
        # The objects won't disappear from syo.objects until we reload the module
        import sys
        if 'syft_objects' in sys.modules:
            # Remove from module cache
            del sys.modules['syft_objects']
            # Force garbage collection
            import gc
            gc.collect()
            # Re-import to get fresh object list
            import syft_objects as syo_refreshed
            # Verify deletion worked
            remaining = [obj for obj in syo_refreshed.objects if obj.name.startswith((TEST_QUEUE_PREFIX, TEST_JOB_PREFIX))]
            if remaining:
                print(f"Warning: {len(remaining)} test objects still visible after refresh")
            else:
                print("All test objects successfully removed from syft-objects")
        
    except ImportError:
        print("Warning: syft-objects not available, skipping object cleanup")
    except Exception as e:
        print(f"Error during test object cleanup: {e}")


def cleanup_test_queues():
    """Clean up all test queue directories from filesystem."""
    from .queue import get_queues_path
    
    try:
        queues_path = get_queues_path()
        if not queues_path.exists():
            return
        
        test_queue_dirs = []
        
        # Find all test queue directories
        # Look for queues created in test mode (they won't have test_ prefix in directory name)
        for queue_dir in queues_path.iterdir():
            if queue_dir.is_dir() and queue_dir.name.endswith("_queue"):
                # Check if this queue has test objects by looking for a test_Q: syft-object
                queue_name = queue_dir.name[:-6]  # Remove "_queue" suffix
                
                # Check if this queue was created in test mode
                # Test queues may not have test_ prefix in directory name
                # but will have test_Q: prefix in syft-objects
                try:
                    import syft_objects as syo
                    is_test_queue = False
                    for obj in syo.objects:
                        if obj.name == f"test_Q:{queue_name}":
                            is_test_queue = True
                            break
                    
                    if is_test_queue or queue_name.startswith("test_"):
                        test_queue_dirs.append(queue_dir)
                except:
                    # If we can't check syft-objects, use name prefix
                    if queue_name.startswith("test_") or "cleanup" in queue_name:
                        test_queue_dirs.append(queue_dir)
        
        # Delete test queue directories
        for queue_dir in test_queue_dirs:
            try:
                shutil.rmtree(queue_dir)
                print(f"Deleted test queue directory: {queue_dir.name}")
            except Exception as e:
                print(f"Warning: Could not delete {queue_dir}: {e}")
        
        print(f"Cleaned up {len(test_queue_dirs)} test queue directories")
        
    except Exception as e:
        print(f"Error during test queue cleanup: {e}")


def cleanup_all_test_artifacts():
    """Clean up all test artifacts including objects and directories."""
    print("Cleaning up test artifacts...")
    cleanup_test_objects()
    cleanup_test_queues()
    print("Test cleanup complete")


def make_test_queue_name(base_name: str) -> str:
    """Convert a base name to a test queue name with test prefix."""
    # Remove any existing Q: prefix
    if base_name.startswith("Q:"):
        base_name = base_name[2:]
    # Add test_ prefix if not already present
    if not base_name.startswith("test_"):
        base_name = f"test_{base_name}"
    return base_name


def make_test_job_name(base_name: str) -> str:
    """Convert a base name to a test job name with test prefix."""
    # Remove any existing J: prefix
    if base_name.startswith("J:"):
        base_name = base_name[2:]
    # Add test_ prefix if not already present
    if not base_name.startswith("test_"):
        base_name = f"test_{base_name}"
    return base_name