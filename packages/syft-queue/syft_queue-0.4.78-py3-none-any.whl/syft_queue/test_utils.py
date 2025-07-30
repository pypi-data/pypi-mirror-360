"""Test utilities for syft-queue tests"""

import shutil
import os
from pathlib import Path
from typing import List, Optional, Set

# Test naming constants
TEST_QUEUE_PREFIX = "test_Q:"
TEST_JOB_PREFIX = "test_J:"


def _remove_objects_with_cleanup(objects_to_remove):
    """
    Remove objects with comprehensive cleanup including files and directories.
    
    Args:
        objects_to_remove: List of objects to remove
        
    Returns:
        int: Number of objects successfully removed
    """
    deleted_count = 0
    
    # First, do direct file cleanup
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
                                # Delete test files with various prefixes
                                for pattern in ["test_j:*", "test_J:*", "test_q:*", "test_Q:*", 
                                              "Q:test_*", "J:test_*", "Q:cleanup*", "J:cleanup*",
                                              "Q:tmp*", "J:tmp*"]:
                                    for path in objects_dir.glob(pattern):
                                        try:
                                            if path.is_file():
                                                path.unlink()
                                                print(f"Deleted file: {path}")
                                            elif path.is_dir():
                                                shutil.rmtree(path)
                                                print(f"Deleted directory: {path}")
                                        except Exception as e:
                                            print(f"Warning: Could not delete {path}: {e}")
    except Exception as e:
        print(f"Warning during direct file cleanup: {e}")
    
    # Remove objects by deleting their files
    for obj in objects_to_remove:
        try:
            deleted = False
            
            # Try to get the file paths
            paths_to_delete = []
            
            # Check all possible path attributes
            for attr_name in ['private', 'mock', 'syftobject', 'public']:
                if hasattr(obj, attr_name):
                    attr_obj = getattr(obj, attr_name)
                    if hasattr(attr_obj, 'path'):
                        path = Path(attr_obj.path)
                        # Skip if path is just "." which indicates a bad path
                        if str(path) != "." and path.exists():
                            paths_to_delete.append(path)
            
            # Also try direct path attribute
            if hasattr(obj, 'path'):
                path = Path(obj.path)
                if str(path) != "." and path.exists():
                    paths_to_delete.append(path)
            
            # Delete the files
            for path in paths_to_delete:
                try:
                    if path.exists():
                        if path.is_file():
                            path.unlink()
                            print(f"Deleted object file: {path}")
                            deleted = True
                        elif path.is_dir():
                            shutil.rmtree(path)
                            print(f"Deleted object directory: {path}")
                            deleted = True
                except Exception as e:
                    print(f"Warning: Could not delete {path}: {e}")
            
            # Also try to remove parent directory if empty
            if paths_to_delete and deleted:
                for path in paths_to_delete:
                    try:
                        parent = path.parent
                        if parent.exists() and parent != Path(".") and parent != Path.home():
                            # Only remove if directory is empty
                            if parent.is_dir() and not any(parent.iterdir()):
                                parent.rmdir()
                                print(f"Removed empty directory: {parent}")
                    except Exception as e:
                        # It's okay if we can't remove the parent directory
                        pass
            
            if deleted:
                deleted_count += 1
                
        except Exception as e:
            print(f"Warning: Could not delete test object {getattr(obj, 'name', 'unknown')}: {e}")
    
    return deleted_count

def force_cleanup_all_q_objects():
    """
    Force cleanup of ALL Q: objects that match test patterns.
    This is a more aggressive cleanup to handle the duplication issue.
    """
    try:
        import syft_objects as syo
        
        # Find all Q: objects that look like test objects
        objects_to_remove = []
        test_patterns = [
            TEST_QUEUE_PREFIX,
            TEST_JOB_PREFIX,
            "Q:test_",
            "J:test_",
            "Q:cleanup",
            "J:cleanup",
            "Q:tmp",
            "J:tmp"
        ]
        
        print(f"Scanning {len(syo.objects)} objects for test patterns...")
        
        # Track unique names to identify duplicates
        name_counts = {}
        for obj in syo.objects:
            if hasattr(obj, 'name'):
                name = obj.name
                name_counts[name] = name_counts.get(name, 0) + 1
                
                # Check if this object matches any test pattern
                for pattern in test_patterns:
                    if name.startswith(pattern):
                        objects_to_remove.append(obj)
                        break
                    # Also check for patterns that might be in the middle of the name
                    if any(test_part in name.lower() for test_part in ['test_', 'tmp_', 'cleanup_']):
                        objects_to_remove.append(obj)
                        break
        
        # Report on duplicates
        duplicates = {name: count for name, count in name_counts.items() if count > 1}
        if duplicates:
            print(f"Found {len(duplicates)} duplicate object names:")
            for name, count in sorted(duplicates.items()):
                print(f"  {name}: {count} copies")
        
        # Remove duplicates and test objects
        print(f"Found {len(objects_to_remove)} objects to remove")
        return _remove_objects_with_cleanup(objects_to_remove)
        
    except ImportError:
        print("Warning: syft-objects not available, skipping object cleanup")
        return 0
    except Exception as e:
        print(f"Error during force cleanup: {e}")
        return 0


def cleanup_test_objects():
    """Clean up all test queue and job objects from syft-objects."""
    try:
        import syft_objects as syo
        
        # Find all test objects
        test_objects = []
        for obj in syo.objects:
            if hasattr(obj, 'name'):
                name = obj.name
                if name.startswith(TEST_QUEUE_PREFIX) or name.startswith(TEST_JOB_PREFIX):
                    test_objects.append(obj)
        
        # Use the comprehensive cleanup function
        deleted_count = _remove_objects_with_cleanup(test_objects)
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


def cleanup_all_test_artifacts(force=False):
    """
    Clean up all test artifacts including objects and directories.
    
    Args:
        force: If True, use aggressive cleanup for all Q: objects matching test patterns
    """
    print("Cleaning up test artifacts...")
    
    if force:
        print("Using force cleanup mode for all Q: objects...")
        force_cleanup_all_q_objects()
    else:
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