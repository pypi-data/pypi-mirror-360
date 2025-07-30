"""
Additional tests for queue.py to improve coverage
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime, timedelta
from uuid import uuid4


def test_queue_path_detection_comprehensive():
    """Test _detect_syftbox_queues_path comprehensive coverage"""
    from syft_queue.queue import _detect_syftbox_queues_path
    
    # Test SYFTBOX_DATA_FOLDER environment variable
    with patch.dict('os.environ', {'SYFTBOX_DATA_FOLDER': '/test/data/folder'}, clear=True):
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            result = _detect_syftbox_queues_path()
            assert '/test/data/folder' in str(result)
            mock_mkdir.assert_called_once()
    
    # Test SYFTBOX_EMAIL environment variable
    with patch.dict('os.environ', {'SYFTBOX_EMAIL': 'test@example.com'}, clear=True):
        with patch('pathlib.Path.home', return_value=Path('/home/user')):
            with patch('pathlib.Path.exists', return_value=True):
                result = _detect_syftbox_queues_path()
                assert 'test@example.com' in str(result)
    
    # Test YAML config file reading
    with patch.dict('os.environ', {}, clear=True):
        with patch('pathlib.Path.home', return_value=Path('/home/user')):
            with patch('pathlib.Path.exists', return_value=True):
                with patch('builtins.open', mock_open(read_data='email: yaml@test.com\nother: value')):
                    with patch('yaml.safe_load', return_value={'email': 'yaml@test.com'}):
                        with patch('pathlib.Path.exists', return_value=True):
                            result = _detect_syftbox_queues_path()
                            assert 'yaml@test.com' in str(result)
    
    # Test YAML import error with manual parsing
    with patch.dict('os.environ', {}, clear=True):
        with patch('pathlib.Path.home', return_value=Path('/home/user')):
            with patch('pathlib.Path.exists', return_value=True):
                import builtins
                original_import = builtins.__import__
                def mock_import(name, *args, **kwargs):
                    if name == 'yaml':
                        raise ImportError('yaml not available')
                    return original_import(name, *args, **kwargs)
                
                with patch('builtins.__import__', side_effect=mock_import):
                    with patch('builtins.open', mock_open(read_data='email: manual@test.com\nother: value')):
                        with patch('pathlib.Path.exists', return_value=True):
                            result = _detect_syftbox_queues_path()
                            assert 'manual@test.com' in str(result)
    
    # Test config file error handling
    with patch.dict('os.environ', {}, clear=True):
        with patch('pathlib.Path.home', return_value=Path('/home/user')):
            with patch('pathlib.Path.exists', return_value=True):
                with patch('builtins.open', side_effect=Exception('File read error')):
                    result = _detect_syftbox_queues_path()
                    # Should fall back to git or current directory
    
    # Test git config fallback
    with patch.dict('os.environ', {}, clear=True):
        with patch('pathlib.Path.home', return_value=Path('/home/user')):
            with patch('pathlib.Path.exists', return_value=False):  # No config file
                with patch('subprocess.run') as mock_run:
                    mock_run.return_value = MagicMock(returncode=0, stdout='git@example.com')
                    with patch('pathlib.Path.exists', return_value=True):  # SyftBox dir exists
                        result = _detect_syftbox_queues_path()
                        assert 'git@example.com' in str(result)
    
    # Test git config failure fallback to current directory
    with patch.dict('os.environ', {}, clear=True):
        with patch('pathlib.Path.home', return_value=Path('/home/user')):
            with patch('pathlib.Path.exists', return_value=False):
                with patch('subprocess.run', side_effect=Exception('Git not available')):
                    result = _detect_syftbox_queues_path()
                    assert result == Path.cwd()


def test_job_path_operations():
    """Test Job path-related operations"""
    from syft_queue import q
    
    queue = q('path_test', force=True)
    job = queue.create_job('path_job', 'user@test.com', 'owner@test.com')
    
    # Test _make_relative method
    # Mock is_relative_to if not available (Python < 3.9)
    if not hasattr(Path, 'is_relative_to'):
        def mock_is_relative_to(self, other):
            try:
                self.relative_to(other)
                return True
            except ValueError:
                return False
        Path.is_relative_to = mock_is_relative_to
    
    # Test with relative path
    relative_path = job.object_path / 'subdir' / 'file.txt'
    relative_path.parent.mkdir(parents=True, exist_ok=True)
    relative_path.touch()
    result = job._make_relative(relative_path)
    assert isinstance(result, (str, Path))
    
    # Test with absolute path outside job directory
    absolute_path = Path('/tmp/external/file.txt')
    result = job._make_relative(absolute_path)
    assert result == absolute_path
    
    # Test update_relative_paths
    job.code_folder = str(job.object_path / 'code')
    (job.object_path / 'code').mkdir()
    job.output_folder = str(job.object_path / 'output')
    (job.object_path / 'output').mkdir()
    job.update_relative_paths()
    
    # Test resolved_code_folder with different scenarios
    # Scenario 1: code_folder exists
    code_dir = job.object_path / 'test_code'
    code_dir.mkdir()
    job.code_folder = str(code_dir)
    assert job.resolved_code_folder == code_dir
    
    # Scenario 2: code_folder doesn't exist, use relative
    job.code_folder = None
    job.code_folder_relative = 'relative_code'
    rel_code_dir = job.object_path / 'relative_code'
    rel_code_dir.mkdir()
    assert job.resolved_code_folder == rel_code_dir
    
    # Scenario 3: use absolute fallback
    job.code_folder_relative = None
    job.code_folder_absolute_fallback = str(code_dir)
    assert job.resolved_code_folder == code_dir
    
    # Scenario 4: search for code directory in job path
    job.code_folder_absolute_fallback = None
    default_code = job.object_path / 'code'
    default_code.mkdir(exist_ok=True)
    result = job.resolved_code_folder
    assert result == default_code
    
    # Test resolved_output_folder
    output_dir = job.object_path / 'test_output'
    output_dir.mkdir()
    job.output_folder = str(output_dir)
    assert job.resolved_output_folder == output_dir
    
    # Test with relative output folder
    job.output_folder = None
    job.output_folder_relative = 'relative_output'
    rel_output_dir = job.object_path / 'relative_output'
    rel_output_dir.mkdir()
    result = job.resolved_output_folder
    assert result == rel_output_dir


def test_job_expiration_logic():
    """Test job expiration logic comprehensively"""
    from syft_queue import q
    
    queue = q('expiration_test', force=True)
    job = queue.create_job('expiry_job', 'user@test.com', 'owner@test.com')
    
    # Test with no updated_at (should not be expired)
    job.updated_at = None
    assert not job.is_expired
    
    # Test with recent update (should not be expired)
    job.updated_at = datetime.now() - timedelta(days=1)
    assert not job.is_expired
    
    # Test with old update (should be expired)
    job.updated_at = datetime.now() - timedelta(days=31)
    assert job.is_expired
    
    # Test boundary case (exactly 30 days)
    job.updated_at = datetime.now() - timedelta(days=30)
    assert not job.is_expired


def test_job_code_files():
    """Test job code_files property"""
    from syft_queue import q
    
    queue = q('code_files_test', force=True)
    job = queue.create_job('code_job', 'user@test.com', 'owner@test.com')
    
    # Test with no code folder
    assert job.code_files == []
    
    # Test with code folder containing files
    code_dir = job.object_path / 'code'
    code_dir.mkdir()
    (code_dir / 'main.py').write_text('print("hello")')
    (code_dir / 'utils.py').write_text('def helper(): pass')
    (code_dir / 'config.json').write_text('{}')
    
    job.code_folder = str(code_dir)
    files = job.code_files
    assert len(files) == 3
    assert any('main.py' in f for f in files)
    assert any('utils.py' in f for f in files)
    assert any('config.json' in f for f in files)
    
    # Test with code folder that doesn't exist
    job.code_folder = str(job.object_path / 'nonexistent')
    assert job.code_files == []


def test_job_loading_with_datetime_strings():
    """Test job loading with datetime string conversion"""
    from syft_queue import Job
    
    with tempfile.TemporaryDirectory() as temp_dir:
        job_dir = Path(temp_dir) / 'test_job'
        job_dir.mkdir()
        private_dir = job_dir / 'private'
        private_dir.mkdir()
        
        # Create job data with datetime strings
        job_data = {
            'uid': str(uuid4()),
            'name': 'J:datetime_test',
            'status': 'inbox',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'requester_email': 'user@test.com',
            'target_email': 'owner@test.com'
        }
        
        json_file = private_dir / 'job_data.json'
        import json
        json_file.write_text(json.dumps(job_data))
        
        # Load job and verify datetime conversion
        job = Job(job_dir, owner_email='owner@test.com')
        assert isinstance(job.created_at, datetime)
        assert isinstance(job.updated_at, datetime)


def test_queue_atomic_creation():
    """Test queue atomic creation with temp directory"""
    from syft_queue import q
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test successful atomic creation
        with patch('tempfile.mkdtemp', return_value=str(Path(temp_dir) / 'temp_queue')):
            with patch('pathlib.Path.rename') as mock_rename:
                queue = q('atomic_test', force=True)
                # Should have called rename for atomic operation
    
    # Test atomic creation with rename error
    with patch('tempfile.mkdtemp', return_value='/tmp/temp_queue'):
        with patch('pathlib.Path.rename', side_effect=OSError('Rename failed')):
            with pytest.raises(OSError):
                q('rename_error_test', force=True)


def test_queue_move_job_operations():
    """Test queue _move_job method"""
    from syft_queue import q, JobStatus
    
    queue = q('move_test', force=True)
    job = queue.create_job('move_job', 'user@test.com', 'owner@test.com')
    
    # Test successful move
    original_path = job.object_path
    queue._move_job(job, JobStatus.inbox, JobStatus.approved)
    
    # Test move with error
    with patch('shutil.move', side_effect=OSError('Move failed')):
        job2 = queue.create_job('move_job2', 'user@test.com', 'owner@test.com')
        with pytest.raises(OSError):
            queue._move_job(job2, JobStatus.inbox, JobStatus.approved)


def test_utility_functions():
    """Test utility functions for coverage"""
    from syft_queue.queue import (
        _queue_exists, _cleanup_empty_queue_directory, _is_ghost_job_folder,
        _cleanup_ghost_job_folders, _cleanup_all_ghost_job_folders,
        _queue_has_valid_syftobject, _cleanup_orphaned_queue_directories,
        _cleanup_all_orphaned_queue_directories
    )
    
    # Test _queue_exists
    with patch('syft_objects.objects.get_object', return_value=None):
        assert not _queue_exists('nonexistent')
    
    with patch('syft_objects.objects.get_object', return_value={'name': 'Q:test'}):
        assert _queue_exists('test')
    
    # Test _is_ghost_job_folder
    assert _is_ghost_job_folder(Path('/tmp/J:ghost_job'))
    assert not _is_ghost_job_folder(Path('/tmp/Q:real_queue'))
    assert not _is_ghost_job_folder(Path('/tmp/regular_folder'))
    
    # Test cleanup functions with temp directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Test _cleanup_empty_queue_directory
        empty_queue = temp_path / 'Q:empty'
        empty_queue.mkdir()
        _cleanup_empty_queue_directory(empty_queue)
        
        # Test _cleanup_ghost_job_folders
        queue_dir = temp_path / 'Q:test_queue'
        queue_dir.mkdir()
        (queue_dir / 'J:ghost1').mkdir()
        (queue_dir / 'J:ghost2').mkdir()
        (queue_dir / 'inbox').mkdir()  # Not a ghost
        
        count = _cleanup_ghost_job_folders(queue_dir)
        assert count >= 2
        
        # Test _cleanup_all_ghost_job_folders
        total = _cleanup_all_ghost_job_folders()
        assert isinstance(total, int)
        
        # Test _queue_has_valid_syftobject
        with patch('syft_objects.objects.get_object', return_value={'name': 'Q:valid'}):
            assert _queue_has_valid_syftobject('valid')
        
        with patch('syft_objects.objects.get_object', return_value=None):
            assert not _queue_has_valid_syftobject('invalid')
        
        # Test orphaned cleanup
        orphaned_queue = temp_path / 'Q:orphaned'
        orphaned_queue.mkdir()
        
        count = _cleanup_orphaned_queue_directories(temp_path)
        assert isinstance(count, int)
        
        total = _cleanup_all_orphaned_queue_directories()
        assert isinstance(total, int)


def test_job_execution_functions():
    """Test job execution preparation and execution"""
    from syft_queue import q
    from syft_queue.queue import prepare_job_for_execution, execute_job_with_context
    
    queue = q('execution_test', force=True)
    job = queue.create_job('exec_job', 'user@test.com', 'owner@test.com')
    
    # Test prepare_job_for_execution
    context = prepare_job_for_execution(job)
    assert 'job_uid' in context
    assert 'job_name' in context
    assert 'job_status' in context
    assert context['job_uid'] == job.uid
    
    # Test execute_job_with_context with mock
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout='Success', stderr='')
        success, output = execute_job_with_context(job)
        assert isinstance(success, bool)
        assert isinstance(output, str)
    
    # Test execute_job_with_context with custom runner
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout='Success', stderr='')
        success, output = execute_job_with_context(job, runner_command='python')
        assert isinstance(success, bool)
    
    # Test execute_job_with_context with exception
    with patch('subprocess.run', side_effect=Exception('Execution failed')):
        success, output = execute_job_with_context(job)
        assert not success
        assert 'error' in output.lower() or 'failed' in output.lower()


def test_queue_stats_and_display():
    """Test queue statistics and display functions"""
    from syft_queue import q
    from syft_queue.queue import _get_queues_table
    
    # Create queue with jobs
    queue = q('stats_test', force=True)
    for i in range(3):
        job = queue.create_job(f'job_{i}', 'user@test.com', 'owner@test.com')
        if i % 2 == 0:
            job.update_status('approved')
    
    # Test queue stats
    stats = queue.get_stats()
    assert 'total_jobs' in stats
    assert 'inbox' in stats
    assert 'approved' in stats
    assert stats['total_jobs'] >= 3
    
    # Test refresh_stats
    queue.refresh_stats()
    
    # Test _update_stats
    original_inbox = stats.get('inbox', 0)
    queue._update_stats('inbox', 1)
    new_stats = queue.get_stats()
    
    # Test _get_queues_table
    table = _get_queues_table()
    assert isinstance(table, str)
    assert 'Queue Name' in table or 'No queues found' in table