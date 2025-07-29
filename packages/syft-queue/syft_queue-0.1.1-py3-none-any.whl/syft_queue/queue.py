"""
SyftBox Queue System

A queue system for managing jobs across SyftBox datasites, inspired by syft-code-queue.
This implementation uses syft-objects natively with syo.syobj().
"""

import enum
import json
import os
import random
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Union, List, Dict, Any, Callable, Tuple
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

# Import syft-objects natively
import syft_objects as syo


class JobStatus(str, enum.Enum):
    """Status of a job in the queue."""
    
    inbox = "inbox"          # Waiting for approval
    approved = "approved"    # Approved, waiting to run
    running = "running"      # Currently executing
    completed = "completed"  # Finished successfully
    failed = "failed"        # Execution failed
    rejected = "rejected"    # Rejected by data owner
    timedout = "timedout"    # Timed out waiting for approval


def _detect_syftbox_queues_path() -> Path:
    """Detect the SyftBox queues directory path."""
    # Try to detect user email from various sources
    email = None
    
    # Try environment variable first
    email = os.getenv("SYFTBOX_EMAIL")
    
    # Try SyftBox config file
    if not email:
        home = Path.home()
        syftbox_config = home / ".syftbox" / "config.yaml"
        if syftbox_config.exists():
            try:
                import yaml
                with open(syftbox_config) as f:
                    config = yaml.safe_load(f)
                    email = config.get("email")
            except ImportError:
                # Try to read basic YAML manually if PyYAML not available
                try:
                    with open(syftbox_config) as f:
                        for line in f:
                            if line.strip().startswith("email:"):
                                email = line.split(":", 1)[1].strip().strip("'\"")
                                break
                except:
                    pass
            except:
                pass
    
    # Try git config as fallback
    if not email:
        try:
            import subprocess
            result = subprocess.run(["git", "config", "user.email"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                email = result.stdout.strip()
        except:
            pass
    
    # Find SyftBox directory
    syftbox_dir = None
    home = Path.home()
    
    # Common SyftBox locations
    possible_locations = [
        home / "SyftBox",
        home / "syftbox", 
        home / ".syftbox" / "SyftBox",
        Path("/opt/syftbox"),
        Path("/usr/local/syftbox")
    ]
    
    for location in possible_locations:
        if location.exists() and (location / "datasites").exists():
            syftbox_dir = location
            break
    
    if syftbox_dir and email:
        # Standard SyftBox path: SyftBox/datasites/<email>/app_data/syft-queues
        queues_path = syftbox_dir / "datasites" / email / "app_data" / "syft-queues"
        queues_path.mkdir(parents=True, exist_ok=True)
        return queues_path
    
    # Fallback to current directory
    return Path(".")


def _generate_mock_data(real_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate mock data with same structure as real data but randomized values."""
    
    def randomize_value(value: Any, key: str = "") -> Any:
        """Randomize a value based on its type and key context."""
        if isinstance(value, dict):
            return {k: randomize_value(v, k) for k, v in value.items()}
        elif isinstance(value, list):
            return [randomize_value(item) for item in value]
        elif isinstance(value, str):
            # Generate contextual mock strings
            if "email" in key.lower():
                return f"mock_{random.choice(['alice', 'bob', 'charlie', 'diana'])}@example.com"
            elif "name" in key.lower():
                return f"mock-{random.choice(['queue', 'system', 'service', 'processor'])}-{random.randint(1, 999)}"
            elif "description" in key.lower():
                return f"Mock {random.choice(['queue', 'system', 'service'])} for demonstration purposes"
            elif "version" in key.lower():
                return f"{random.randint(1, 3)}.{random.randint(0, 9)}.{random.randint(0, 9)}"
            elif "_at" in key.lower() or "time" in key.lower():
                # Keep ISO format for timestamps
                mock_date = datetime.now() - timedelta(days=random.randint(0, 30))
                return mock_date.isoformat()
            else:
                return f"mock_{key}_{random.randint(1000, 9999)}"
        elif isinstance(value, int):
            # Generate reasonable mock numbers based on context
            if "timeout" in key.lower():
                return random.randint(60, 3600)  # 1 minute to 1 hour
            elif "jobs" in key.lower():
                return random.randint(0, 50)  # Job counts
            elif "concurrent" in key.lower():
                return random.randint(1, 10)  # Concurrent limits
            elif "after" in key.lower():
                return random.randint(3600, 86400)  # Cleanup times
            else:
                return random.randint(1, 100)
        elif isinstance(value, float):
            return round(random.uniform(0.1, 100.0), 2)
        elif isinstance(value, bool):
            return random.choice([True, False])
        elif value is None:
            return None
        else:
            return f"mock_{type(value).__name__}_{random.randint(1000, 9999)}"
    
    return randomize_value(real_data)


class Job:
    """
    A job object that uses syft-objects natively for storage.
    
    All job metadata is stored in a syft-object that appears in syo.objects.
    Supports relative paths for portability across pipeline stages.
    """
    
    def __init__(self, folder_path: Union[str, Path], owner_email: str = None, **kwargs):
        """
        Initialize a Job.
        
        Args:
            folder_path: Path to the job folder
            owner_email: Email of the owner (if None, will auto-detect)
            **kwargs: Job attributes (uid, name, requester_email, etc.)
        """
        self.object_path = Path(folder_path).absolute()
        self.object_path.mkdir(parents=True, exist_ok=True)
        
        # Set job attributes
        self.uid = kwargs.get('uid', uuid4())
        # Add J: prefix to job name if not already present
        name = kwargs.get('name', '')
        self.name = name if name.startswith("J:") else f"J:{name}"
        self.requester_email = kwargs.get('requester_email', '')
        self.target_email = kwargs.get('target_email', '')
        self.code_folder = kwargs.get('code_folder', '')
        self.description = kwargs.get('description', '')
        self.created_at = kwargs.get('created_at', datetime.now())
        self.timeout_seconds = kwargs.get('timeout_seconds', 86400)  # 24 hours
        self.tags = kwargs.get('tags', [])
        self.status = kwargs.get('status', JobStatus.inbox)
        self.updated_at = kwargs.get('updated_at', datetime.now())
        self.started_at = kwargs.get('started_at', None)
        self.completed_at = kwargs.get('completed_at', None)
        self.output_folder = kwargs.get('output_folder', None)
        self.error_message = kwargs.get('error_message', None)
        self.exit_code = kwargs.get('exit_code', None)
        self.logs = kwargs.get('logs', None)
        self.queue_name = kwargs.get('queue_name', 'unknown')  # For better syft-object naming
        self._queue_ref = kwargs.get('_queue_ref', None)  # Reference to queue for movement
        
        # New fields for relative path support
        self.base_path = kwargs.get('base_path', str(self.object_path))
        self.code_folder_relative = kwargs.get('code_folder_relative', None)
        self.output_folder_relative = kwargs.get('output_folder_relative', None)
        self.code_folder_absolute_fallback = kwargs.get('code_folder_absolute_fallback', None)
        self.output_folder_absolute_fallback = kwargs.get('output_folder_absolute_fallback', None)
        
        # Load existing job or create new structure
        if self._load_existing_job():
            print(f"Loaded existing job: {self.uid}")
        else:
            # Create job folder structure with syft-object inside
            self._create_job_structure(owner_email)
    
    def _resolve_path(self, path_field: str) -> Optional[Path]:
        """
        Resolve a path using multiple strategies:
        1. Try relative path if base_path exists
        2. Try absolute path
        3. Try absolute fallback path
        4. Search common locations
        """
        # Strategy 1: Relative path
        relative_field = f"{path_field}_relative"
        if hasattr(self, relative_field):
            relative_path = getattr(self, relative_field)
            if relative_path and self.base_path:
                base = Path(self.base_path)
                if not base.is_absolute():
                    base = Path.cwd() / base
                
                candidate = base / relative_path
                if candidate.exists():
                    return candidate.absolute()
        
        # Strategy 2: Absolute path
        absolute_path = getattr(self, path_field, None)
        if absolute_path:
            abs_path = Path(absolute_path)
            if abs_path.exists():
                return abs_path.absolute()
        
        # Strategy 3: Absolute fallback
        fallback_field = f"{path_field}_absolute_fallback"
        if hasattr(self, fallback_field):
            fallback = getattr(self, fallback_field, None)
            if fallback:
                fallback_path = Path(fallback)
                if fallback_path.exists():
                    return fallback_path.absolute()
        
        # Strategy 4: Search within job directory
        if path_field == "code_folder":
            code_dir = self.object_path / "code"
            if code_dir.exists():
                return code_dir.absolute()
        elif path_field == "output_folder":
            output_dir = self.object_path / "output"
            if output_dir.exists():
                return output_dir.absolute()
        
        return None
    
    def _make_relative(self, absolute_path: Union[str, Path]) -> Optional[str]:
        """Convert an absolute path to relative path from base_path."""
        if not absolute_path or not self.base_path:
            return None
        
        try:
            abs_path = Path(absolute_path).absolute()
            base = Path(self.base_path).absolute()
            
            # Try to make relative path
            return str(abs_path.relative_to(base))
        except ValueError:
            # Path is not relative to base_path
            # Try to find common parent
            try:
                # Use os.path.relpath as fallback
                import os
                return os.path.relpath(abs_path, base)
            except:
                return None
    
    def update_relative_paths(self):
        """Update relative paths based on current absolute paths."""
        # Update code_folder relative path
        if self.code_folder:
            self.code_folder_relative = self._make_relative(self.code_folder)
            self.code_folder_absolute_fallback = str(Path(self.code_folder).absolute())
        
        # Update output_folder relative path
        if self.output_folder:
            self.output_folder_relative = self._make_relative(self.output_folder)
            self.output_folder_absolute_fallback = str(Path(self.output_folder).absolute())
    
    @property
    def resolved_code_folder(self) -> Optional[Path]:
        """Get resolved code folder path."""
        return self._resolve_path('code_folder')
    
    @property
    def resolved_output_folder(self) -> Optional[Path]:
        """Get resolved output folder path."""
        return self._resolve_path('output_folder')
    
    def _create_job_structure(self, owner_email: str = None):
        """Create the job folder structure with syft-object inside."""
        # Create job subfolders
        self.mock_folder = self.object_path / "mock"
        self.private_folder = self.object_path / "private" 
        self.code_folder_path = self.object_path / "code"
        
        # Create directories
        self.mock_folder.mkdir(exist_ok=True)
        self.private_folder.mkdir(exist_ok=True)
        self.code_folder_path.mkdir(exist_ok=True)
        
        # Create syft.pub.yaml for the job folder
        self._create_job_permissions()
        
        # Prepare job data
        job_data = {
            "uid": str(self.uid),
            "name": self.name,
            "requester_email": self.requester_email,
            "target_email": self.target_email,
            "code_folder": self.code_folder,
            "description": self.description,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "timeout_seconds": self.timeout_seconds,
            "tags": self.tags,
            "status": self.status.value if isinstance(self.status, JobStatus) else self.status,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            "started_at": self.started_at.isoformat() if self.started_at and isinstance(self.started_at, datetime) else self.started_at,
            "completed_at": self.completed_at.isoformat() if self.completed_at and isinstance(self.completed_at, datetime) else self.completed_at,
            "output_folder": self.output_folder,
            "error_message": self.error_message,
            "exit_code": self.exit_code,
            "logs": self.logs,
            # Relative path fields
            "base_path": self.base_path,
            "code_folder_relative": self.code_folder_relative,
            "output_folder_relative": self.output_folder_relative,
            "code_folder_absolute_fallback": self.code_folder_absolute_fallback,
            "output_folder_absolute_fallback": self.output_folder_absolute_fallback,
        }
        
        # Create private content (full job data)
        private_content = json.dumps(job_data, indent=2)
        
        # Create mock content (same structure as private data but with random values)
        mock_data = _generate_mock_data(job_data)
        mock_data["type"] = "SyftBox Job"  # Keep type field real for identification
        mock_content = json.dumps(mock_data, indent=2)
        
        # Save files in job folder structure
        (self.private_folder / "job_data.json").write_text(private_content)
        (self.mock_folder / "job_data.json").write_text(mock_content)
        
        # Create proper syft-object using syo.syobj() so it appears in syo.objects
        # self.name already has J: prefix
        job_name = f"{self.name}_{str(self.uid)[:8]}"
        
        # Create detailed description
        description = f"Job '{self.name}' in queue '{self.queue_name}' | Status: {job_data['status']} | From: {self.requester_email} | To: {self.target_email} | Created: {self.created_at.strftime('%Y-%m-%d %H:%M') if isinstance(self.created_at, datetime) else self.created_at}"
        
        # Create minimal syft-object metadata
        syft_metadata = {
            "type": "SyftBox Job",
            "status": job_data["status"]
        }
        
        # Create proper syft-object that will appear in syo.objects
        self._syft_object = syo.syobj(
            name=job_name,
            private_contents=private_content,
            mock_contents=mock_content,
            private_read=[self.target_email, self.requester_email],
            private_write=[self.target_email],
            mock_read=["public"],
            mock_write=[],
            metadata={
                "type": "SyftBox Job",
                "status": job_data["status"],
                "description": description
            }
        )
        
        # Also create local syftobject.yaml for folder structure compatibility
        import yaml
        (self.object_path / "syftobject.yaml").write_text(yaml.dump(syft_metadata, default_flow_style=False))
        
        print(f"Created job structure at: {self.object_path}")
    
    def _load_existing_job(self):
        """Load existing job from folder structure."""
        try:
            # Check if job folder structure exists
            syft_yaml_file = self.object_path / "syftobject.yaml"
            if not syft_yaml_file.exists():
                return False
            
            # Load metadata
            import yaml
            with open(syft_yaml_file) as f:
                metadata = yaml.safe_load(f)
            
            # Set folder paths
            self.mock_folder = self.object_path / "mock"
            self.private_folder = self.object_path / "private"
            self.code_folder_path = self.object_path / "code"
            
            # Load job data from private folder
            private_file = self.private_folder / "job_data.json"
            if private_file.exists():
                job_data = json.loads(private_file.read_text())
                
                # Update job attributes from loaded data
                self.status = JobStatus(job_data.get("status", self.status))
                self.updated_at = datetime.fromisoformat(job_data["updated_at"]) if job_data.get("updated_at") else self.updated_at
                self.started_at = datetime.fromisoformat(job_data["started_at"]) if job_data.get("started_at") else None
                self.completed_at = datetime.fromisoformat(job_data["completed_at"]) if job_data.get("completed_at") else None
                self.error_message = job_data.get("error_message")
                self.exit_code = job_data.get("exit_code")
                self.logs = job_data.get("logs")
                
                # Load relative path fields
                self.base_path = job_data.get("base_path", self.base_path)
                self.code_folder_relative = job_data.get("code_folder_relative")
                self.output_folder_relative = job_data.get("output_folder_relative")
                self.code_folder_absolute_fallback = job_data.get("code_folder_absolute_fallback")
                self.output_folder_absolute_fallback = job_data.get("output_folder_absolute_fallback")
                
            return True
            
        except Exception as e:
            print(f"Error loading existing job {self.uid}: {e}")
            return False
    
    def _create_job_permissions(self):
        """Create syft.pub.yaml for job folder."""
        syft_pub_content = f"""rules:
- pattern: 'mock/**'
  access:
    read:
    - '*'
- pattern: 'private/**'
  access:
    read:
    - '{self.target_email}'
    - '{self.requester_email}'
    write:
    - '{self.target_email}'
- pattern: 'code/**'
  access:
    read:
    - '{self.target_email}'
    - '{self.requester_email}'
- pattern: 'syftobject.yaml'
  access:
    read:
    - '*'
    write:
    - '{self.target_email}'
"""
        syft_pub_file = self.object_path / "syft.pub.yaml"
        syft_pub_file.write_text(syft_pub_content)
    
    def _update_syft_object(self):
        """Update the job data files in the job folder."""
        # Update relative paths before saving
        self.update_relative_paths()
        
        # Get current job data
        job_data = {
            "uid": str(self.uid),
            "name": self.name,
            "requester_email": self.requester_email,
            "target_email": self.target_email,
            "code_folder": self.code_folder,
            "description": self.description,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "timeout_seconds": self.timeout_seconds,
            "tags": self.tags,
            "status": self.status.value if isinstance(self.status, JobStatus) else self.status,
            "updated_at": datetime.now().isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at and isinstance(self.started_at, datetime) else self.started_at,
            "completed_at": self.completed_at.isoformat() if self.completed_at and isinstance(self.completed_at, datetime) else self.completed_at,
            "output_folder": self.output_folder,
            "error_message": self.error_message,
            "exit_code": self.exit_code,
            "logs": self.logs,
            # Relative path fields
            "base_path": self.base_path,
            "code_folder_relative": self.code_folder_relative,
            "output_folder_relative": self.output_folder_relative,
            "code_folder_absolute_fallback": self.code_folder_absolute_fallback,
            "output_folder_absolute_fallback": self.output_folder_absolute_fallback,
        }
        
        # Update private content
        private_content = json.dumps(job_data, indent=2)
        
        # Update mock content (same structure as private data but with random values)
        mock_data = _generate_mock_data(job_data)
        mock_data["type"] = "SyftBox Job"  # Keep type field real for identification
        mock_content = json.dumps(mock_data, indent=2)
        
        try:
            # Update files in job folder structure
            if hasattr(self, 'private_folder') and hasattr(self, 'mock_folder'):
                private_file = self.private_folder / "job_data.json"
                mock_file = self.mock_folder / "job_data.json"
                
                if private_file.exists() and mock_file.exists():
                    private_file.write_text(private_content)
                    mock_file.write_text(mock_content)
                    
                    # Update syftobject.yaml metadata
                    # Update description with current status
                    description = f"Job '{self.name}' in queue '{self.queue_name}' | Status: {job_data['status']} | From: {self.requester_email} | To: {self.target_email} | Updated: {job_data['updated_at'][:16] if job_data.get('updated_at') else 'unknown'}"
                    
                    # Create minimal metadata
                    syft_metadata = {
                        "type": "SyftBox Job",
                        "status": job_data["status"]
                    }
                    
                    # Update the proper syft-object if it exists
                    if hasattr(self, '_syft_object') and self._syft_object:
                        # Update syft-object metadata and description
                        syft_metadata["description"] = description
                        self._syft_object.metadata.update(syft_metadata)
                        # Save the updated metadata to the original syft-object file
                        if hasattr(self._syft_object, 'syftobject_path') and self._syft_object.syftobject_path:
                            self._syft_object.save_yaml(self._syft_object.syftobject_path)
                    
                    # Also update local syftobject.yaml for folder structure compatibility
                    import yaml
                    syft_yaml_file = self.object_path / "syftobject.yaml"
                    syft_yaml_file.write_text(yaml.dump(syft_metadata, default_flow_style=False))
                else:
                    print(f"Warning: Job data files missing for job {self.uid}, skipping update")
            else:
                print(f"Warning: Job folder structure not found for job {self.uid}, skipping update")
        except Exception as e:
            print(f"Error updating job data for job {self.uid}: {e}")
        
        # Update timestamps
        self.updated_at = datetime.now()
    
    def move_to_status(self, new_status: JobStatus, queue_instance=None):
        """Move the entire job folder to a new status directory."""
        if not queue_instance:
            print(f"Warning: Cannot move job without queue instance")
            return
            
        # Get current and target directories
        current_dir = self.object_path
        target_status_dir = queue_instance.get_status_directory(new_status)
        target_dir = target_status_dir / str(self.uid)
        
        try:
            import shutil
            
            # Create target status directory if it doesn't exist
            target_status_dir.mkdir(parents=True, exist_ok=True)
            
            # Move entire job folder
            if current_dir.exists() and current_dir != target_dir:
                if target_dir.exists():
                    shutil.rmtree(target_dir)  # Remove any existing target
                shutil.move(str(current_dir), str(target_dir))
                
                # Update object_path to new location
                self.object_path = target_dir
                
                # Update folder references
                self.mock_folder = self.object_path / "mock"
                self.private_folder = self.object_path / "private"
                self.code_folder_path = self.object_path / "code"
                
                print(f"Moved job {self.uid} from {current_dir.parent.name} to {new_status.value}")
            
        except Exception as e:
            print(f"Error moving job {self.uid} to {new_status.value}: {e}")
    
    @property
    def is_terminal(self) -> bool:
        """Check if job is in a terminal state."""
        return self.status in [JobStatus.completed, JobStatus.failed, JobStatus.rejected, JobStatus.timedout]
    
    @property
    def is_expired(self) -> bool:
        """Check if job has expired."""
        if self.is_terminal:
            return False
        
        elapsed = (datetime.now() - self.created_at).total_seconds()
        return elapsed > self.timeout_seconds
    
    def update_status(self, new_status: JobStatus, error_message: Optional[str] = None):
        """Update job status with optional error message and move job folder."""
        old_status = self.status
        self.status = new_status
        if error_message:
            self.error_message = error_message
        
        # Update timing information
        now = datetime.now()
        if new_status == JobStatus.running:
            self.started_at = now
        elif new_status in [JobStatus.completed, JobStatus.failed, JobStatus.rejected, JobStatus.timedout]:
            self.completed_at = now
        
        # Move job folder if status changed and we have a queue reference
        if old_status != new_status and self._queue_ref:
            self.move_to_status(new_status, self._queue_ref)
        
        # Update syft-object
        self._update_syft_object()
    
    def __str__(self) -> str:
        """String representation of job."""
        return f"Job({self.name}, {self.status.value}, {self.requester_email} -> {self.target_email})"
    
    def __repr__(self) -> str:
        """Detailed representation of job."""
        return f"Job(uid={self.uid}, name='{self.name}', status={self.status.value})"


class BaseQueue(ABC):
    """
    A queue for managing jobs across SyftBox datasites.
    
    Uses syft-objects natively for metadata storage.
    """
    
    def __init__(self, folder_path: Union[str, Path], queue_name: str = "default-queue", owner_email: str = None, **kwargs):
        """
        Initialize a Queue.
        
        Args:
            folder_path: Path to the queue folder
            queue_name: Name of the queue
            owner_email: Email of the owner (if None, will auto-detect)
            **kwargs: Additional queue configuration
        """
        self.object_path = Path(folder_path)
        self.object_path.mkdir(parents=True, exist_ok=True)
        
        # Add Q: prefix to queue name if not already present
        self.queue_name = queue_name if queue_name.startswith("Q:") else f"Q:{queue_name}"
        self._owner_email = owner_email
        
        # Queue configuration
        self.max_concurrent_jobs = kwargs.get('max_concurrent_jobs', 3)
        self.job_timeout = kwargs.get('job_timeout', 300)  # 5 minutes
        self.cleanup_completed_after = kwargs.get('cleanup_completed_after', 86400)  # 24 hours
        self.created_at = kwargs.get('created_at', datetime.now())
        self.version = kwargs.get('version', '1.0.0')
        self.description = kwargs.get('description', f'SyftBox Queue: {queue_name}')
        self.last_activity = kwargs.get('last_activity', datetime.now())
        
        # Queue statistics
        self.total_jobs = 0
        self.inbox_jobs = 0
        self.approved_jobs = 0
        self.running_jobs = 0
        self.completed_jobs = 0
        self.failed_jobs = 0
        self.rejected_jobs = 0
        self.timedout_jobs = 0
        self.stats_last_updated = datetime.now()
        
        # Initialize queue structure and syft-object
        self._initialize_queue_structure()
        self._create_syft_object()
    
    def _create_syft_object(self):
        """Create or load the syft-object for this queue."""
        # Prepare queue data
        queue_data = {
            "queue_name": self.queue_name,
            "max_concurrent_jobs": self.max_concurrent_jobs,
            "job_timeout": self.job_timeout,
            "cleanup_completed_after": self.cleanup_completed_after,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "version": self.version,
            "description": self.description,
            "last_activity": self.last_activity.isoformat() if isinstance(self.last_activity, datetime) else self.last_activity,
            "owner_email": self._owner_email,
            "statistics": {
                "total_jobs": self.total_jobs,
                "inbox_jobs": self.inbox_jobs,
                "approved_jobs": self.approved_jobs,
                "running_jobs": self.running_jobs,
                "completed_jobs": self.completed_jobs,
                "failed_jobs": self.failed_jobs,
                "rejected_jobs": self.rejected_jobs,
                "timedout_jobs": self.timedout_jobs,
                "stats_last_updated": self.stats_last_updated.isoformat() if isinstance(self.stats_last_updated, datetime) else self.stats_last_updated
            }
        }
        
        # Create private content (full queue data)
        private_content = json.dumps(queue_data, indent=2)
        
        # Create mock content (same structure as private data but with random values)
        mock_data = _generate_mock_data(queue_data)
        mock_data["type"] = "SyftBox Queue"  # Keep type field real for identification
        mock_content = json.dumps(mock_data, indent=2)
        
        # Create syft-object with the queue name (already has Q: prefix)
        object_name = self.queue_name
        
        # Create detailed description
        queue_type = "CodeQueue" if isinstance(self, CodeQueue) else "DataQueue" if isinstance(self, DataQueue) else "Queue"
        description = f"{queue_type} '{self.queue_name}' | Owner: {self._owner_email} | Total jobs: {self.total_jobs} | Active: {self.inbox_jobs + self.approved_jobs + self.running_jobs} | Created: {self.created_at.strftime('%Y-%m-%d') if isinstance(self.created_at, datetime) else self.created_at}"
        
        self._syft_object = syo.syobj(
            name=object_name,
            private_contents=private_content,
            mock_contents=mock_content,
            private_read=[self._owner_email] if self._owner_email else ["public"],
            private_write=[self._owner_email] if self._owner_email else [],
            mock_read=["public"],
            mock_write=[],
            metadata={
                "type": "SyftBox Queue",
                "queue_type": queue_type,
                "description": description
            }
        )
    
    def _update_syft_object(self):
        """Update the syft-object with current queue data."""
        # Get current queue data
        queue_data = {
            "queue_name": self.queue_name,
            "max_concurrent_jobs": self.max_concurrent_jobs,
            "job_timeout": self.job_timeout,
            "cleanup_completed_after": self.cleanup_completed_after,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "version": self.version,
            "description": self.description,
            "last_activity": datetime.now().isoformat(),
            "owner_email": self._owner_email,
            "statistics": {
                "total_jobs": self.total_jobs,
                "inbox_jobs": self.inbox_jobs,
                "approved_jobs": self.approved_jobs,
                "running_jobs": self.running_jobs,
                "completed_jobs": self.completed_jobs,
                "failed_jobs": self.failed_jobs,
                "rejected_jobs": self.rejected_jobs,
                "timedout_jobs": self.timedout_jobs,
                "stats_last_updated": datetime.now().isoformat()
            }
        }
        
        # Update private content
        private_content = json.dumps(queue_data, indent=2)
        
        # Update mock content (same structure as private data but with random values)
        mock_data = _generate_mock_data(queue_data)
        mock_data["type"] = "SyftBox Queue"  # Keep type field real for identification
        mock_content = json.dumps(mock_data, indent=2)
        
        try:
            # Only update if we have an existing syft-object
            if hasattr(self, '_syft_object') and self._syft_object:
                # Try to write to the files directly using Path
                try:
                    from pathlib import Path
                    private_path = Path(self._syft_object.private_path)
                    mock_path = Path(self._syft_object.mock_path)
                    
                    if private_path.exists() and mock_path.exists():
                        # Try to update file permissions if needed
                        private_path.chmod(0o664)  # rw-rw-r--
                        mock_path.chmod(0o664)
                        
                        private_path.write_text(private_content)
                        mock_path.write_text(mock_content)
                    else:
                        print(f"Warning: Syft-object files missing for queue {self.queue_name}, skipping update")
                except PermissionError:
                    print(f"Warning: Permission denied updating queue {self.queue_name}, skipping update")
                except Exception as write_error:
                    # Fallback to syft-object API
                    if hasattr(self._syft_object.private.file, 'write_text'):
                        self._syft_object.private.file.write_text(private_content)
                        self._syft_object.mock.file.write_text(mock_content)
                    else:
                        self._syft_object.private.file.write(private_content)
                        self._syft_object.mock.file.write(mock_content)
            else:
                print(f"Warning: No syft-object found for queue {self.queue_name}, skipping update")
        except Exception as e:
            print(f"Error updating queue syft-object for {self.queue_name}: {e}")
            # Don't create a new object, just log the error
        
        # Update timestamps
        self.last_activity = datetime.now()
        self.stats_last_updated = datetime.now()
    
    def _initialize_queue_structure(self):
        """Initialize the queue directory structure with proper permissions."""
        # Create jobs directory
        jobs_dir = self.object_path / "jobs"
        jobs_dir.mkdir(parents=True, exist_ok=True)
        
        # Create status directories with proper permissions
        for status in JobStatus:
            status_dir = jobs_dir / status.value
            status_dir.mkdir(parents=True, exist_ok=True)
            
            # Create appropriate syft.pub.yaml permissions
            if status == JobStatus.inbox:
                # Inbox directory gets read/write permissions for cross-datasite job submission
                self._create_inbox_permissions(status_dir)
            else:
                # Other directories get read-only permissions for visibility
                self._create_readonly_permissions(status_dir)
    
    def _create_inbox_permissions(self, inbox_dir: Path):
        """Create syft.pub.yaml file for inbox directory with read/write permissions."""
        syft_pub_content = """rules:
- pattern: '**'
  access:
    read:
    - '*'
    write:
    - '*'
"""
        self._create_syft_pub_yaml(inbox_dir, syft_pub_content)
    
    def _create_readonly_permissions(self, status_dir: Path):
        """Create syft.pub.yaml file for status directory with read-only permissions."""
        syft_pub_content = """rules:
- pattern: '**'
  access:
    read:
    - '*'
"""
        self._create_syft_pub_yaml(status_dir, syft_pub_content)
    
    def _create_syft_pub_yaml(self, directory: Path, content: str):
        """Create or update syft.pub.yaml file in the given directory."""
        syft_pub_file = directory / "syft.pub.yaml"
        
        # Check if file exists and has correct content
        needs_creation = True
        if syft_pub_file.exists():
            try:
                existing_content = syft_pub_file.read_text().strip()
                if existing_content == content.strip():
                    needs_creation = False
            except Exception:
                pass  # Fall through to recreate
        
        if needs_creation:
            syft_pub_file.write_text(content)
    
    def update_last_activity(self, force_update: bool = False):
        """Update the last activity timestamp."""
        self.last_activity = datetime.now()
        
        # Only update syft-object if forced or if significant time has passed
        if force_update:
            self._update_syft_object()
        else:
            # Throttle updates - only update every 30 seconds
            if not hasattr(self, '_last_syft_update'):
                self._last_syft_update = datetime.now()
                self._update_syft_object()
            else:
                time_since_update = (datetime.now() - self._last_syft_update).total_seconds()
                if time_since_update > 30:  # 30 seconds throttle
                    self._last_syft_update = datetime.now()
                    self._update_syft_object()
    
    def get_status_directory(self, status: JobStatus) -> Path:
        """Get the directory for a specific job status."""
        return self.object_path / "jobs" / status.value
    
    def get_job_directory(self, job_uid: UUID, status: JobStatus) -> Path:
        """Get the directory for a specific job."""
        return self.get_status_directory(status) / str(job_uid)
    
    def create_job(self, name: str, requester_email: str, target_email: str, **kwargs) -> Job:
        """
        Create a new job in the queue with support for relative paths.
        
        Args:
            name: Job name
            requester_email: Email of the job requester
            target_email: Email of the target (data owner)
            **kwargs: Additional job attributes including:
                - uid: Specific UUID for job coordination (optional)
                - code_folder: Path to code (will be made relative)
                - use_relative_paths: Whether to use relative paths (default: True)
                - base_path: Base path for relative paths (default: job directory)
            
        Returns:
            Job: The created job object
        """
        # Allow passing a specific UID for job coordination between queues
        job_uid = kwargs.pop('uid', uuid4())
        if isinstance(job_uid, str):
            job_uid = UUID(job_uid)
        
        # Create job directory
        job_dir = self.get_job_directory(job_uid, JobStatus.inbox)
        job_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract path-related options
        use_relative_paths = kwargs.pop('use_relative_paths', True)
        base_path = kwargs.pop('base_path', str(job_dir))
        
        # Process code_folder to support relative paths
        code_folder = kwargs.get('code_folder')
        if code_folder and use_relative_paths:
            # Copy code to job directory
            code_source = Path(code_folder)
            if code_source.exists():
                job_code_dir = job_dir / "code"
                job_code_dir.mkdir(exist_ok=True)
                
                # Copy code files
                if code_source.is_dir():
                    import shutil
                    shutil.copytree(code_source, job_code_dir, dirs_exist_ok=True)
                else:
                    import shutil
                    shutil.copy2(code_source, job_code_dir)
                
                # Update code_folder to be relative to job directory
                kwargs['code_folder'] = str(job_code_dir)
                kwargs['code_folder_relative'] = "code"
                kwargs['code_folder_absolute_fallback'] = str(job_code_dir.absolute())
        
        # Create job object
        job_data = {
            'uid': job_uid,
            'name': name,
            'requester_email': requester_email,
            'target_email': target_email,
            'status': JobStatus.inbox,
            'created_at': datetime.now(),
            'base_path': base_path,
            'queue_name': self.queue_name,  # Add queue name for better syft-object naming
            **kwargs
        }
        
        job = Job(job_dir, owner_email=self._owner_email, _queue_ref=self, **job_data)
        
        # Update relative paths after creation
        if use_relative_paths:
            job.update_relative_paths()
            # Note: No need to call _update_syft_object() again,
            # it was already called in the Job constructor
        
        # Update queue statistics
        self._update_stats('total_jobs', 1)
        self._update_stats('inbox_jobs', 1)
        
        return job
    
    def get_job(self, job_uid: UUID) -> Optional[Job]:
        """
        Get a job by its UID.
        
        Args:
            job_uid: The job's unique identifier
            
        Returns:
            Job or None: The job object if found
        """
        # Search through all status directories
        for status in JobStatus:
            job_dir = self.get_job_directory(job_uid, status)
            if job_dir.exists():
                return Job(job_dir, owner_email=self._owner_email, queue_name=self.queue_name, _queue_ref=self)
        return None
    
    def list_jobs(self, status: Optional[JobStatus] = None, limit: int = 50) -> List[Job]:
        """
        List jobs in the queue.
        
        Args:
            status: Filter by job status (None for all)
            limit: Maximum number of jobs to return
            
        Returns:
            List[Job]: List of job objects
        """
        jobs = []
        
        # Determine which status directories to search
        statuses = [status] if status else list(JobStatus)
        
        for job_status in statuses:
            status_dir = self.get_status_directory(job_status)
            if not status_dir.exists():
                continue
                
            # Get job directories (UUID folders)
            for job_dir in status_dir.iterdir():
                if job_dir.is_dir() and len(str(job_dir.name)) == 36:  # UUID length
                    try:
                        job = Job(job_dir, owner_email=self._owner_email, queue_name=self.queue_name, _queue_ref=self)
                        jobs.append(job)
                        if len(jobs) >= limit:
                            break
                    except Exception:
                        continue  # Skip corrupted jobs
            
            if len(jobs) >= limit:
                break
        
        return jobs
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        return {
            'total_jobs': self.total_jobs,
            'inbox_jobs': self.inbox_jobs,
            'approved_jobs': self.approved_jobs,
            'running_jobs': self.running_jobs,
            'completed_jobs': self.completed_jobs,
            'failed_jobs': self.failed_jobs,
            'rejected_jobs': self.rejected_jobs,
            'timedout_jobs': self.timedout_jobs,
            'stats_last_updated': self.stats_last_updated.isoformat() if isinstance(self.stats_last_updated, datetime) else self.stats_last_updated
        }
    
    def refresh_stats(self):
        """Refresh queue statistics by counting jobs in each status directory."""
        stats = {
            'total_jobs': 0,
            'inbox_jobs': 0,
            'approved_jobs': 0,
            'running_jobs': 0,
            'completed_jobs': 0,
            'failed_jobs': 0,
            'rejected_jobs': 0,
            'timedout_jobs': 0,
        }
        
        # Count jobs in each status directory
        for status in JobStatus:
            status_dir = self.get_status_directory(status)
            if status_dir.exists():
                count = len([d for d in status_dir.iterdir() if d.is_dir()])
                stats[f'{status.value}_jobs'] = count
                stats['total_jobs'] += count
        
        # Update stats attributes
        for stat_name, value in stats.items():
            setattr(self, stat_name, value)
        
        self.stats_last_updated = datetime.now()
        self.update_last_activity()
    
    def _update_stats(self, stat_name: str, increment: int):
        """Update a specific statistic."""
        current_value = getattr(self, stat_name, 0)
        setattr(self, stat_name, current_value + increment)
        self.stats_last_updated = datetime.now()
        self.update_last_activity()
    
    def __str__(self) -> str:
        """String representation of queue."""
        return f"Queue({self.queue_name}, {self.total_jobs} jobs)"
    
    def __repr__(self) -> str:
        """Detailed representation of queue."""
        return f"Queue(name='{self.queue_name}', path='{self.object_path}')"
    
    def help(self):
        """Show help and getting started guide for SyftQueue."""
        from . import __version__
        help_text = f"""
🎯 SyftQueue v{__version__} - Getting Started Guide

👋 Welcome! SyftQueue is a portable queue system for SyftBox with native syft-objects support.

🚀 QUICK START - Your First Queue:
  1. Import and create a queue:
     >>> from syft_queue import q
     >>> my_queue = q("analytics")  # Creates or gets queue
  
  2. Create a job:
     >>> job = my_queue.create_job(
     ...     name="data-analysis",
     ...     requester_email="alice@example.com",
     ...     target_email="bob@example.com"
     ... )
  
  3. Add code to the job:
     >>> job.code_folder_path.mkdir(exist_ok=True)
     >>> (job.code_folder_path / "run.sh").write_text("echo 'Hello SyftBox!'")
  
  4. Submit and track:
     >>> my_queue.submit_job(job)
     >>> print(f"Job status: {{job.status.value}}")

📦 Key Features:
  • Native syft-objects integration with syo.syobj()
  • Portable jobs with relative path support
  • Automatic mock data generation for privacy
  • Cross-datasite job submission
  • Built-in permission management

🔄 Job Lifecycle:
  inbox → approved → running → completed
                 ↘ rejected      ↘ failed/timedout

📋 Queue Operations:
  # List all jobs
  jobs = my_queue.get_jobs()
  
  # Filter by status
  pending = my_queue.get_jobs(status=JobStatus.inbox)
  
  # Get specific job
  job = my_queue.get_job(job_uid)
  
  # Approve/reject jobs
  from syft_queue import approve, reject
  approve(job, approver="owner@datasite.com")
  reject(job, reason="Insufficient permissions")

🔧 Job Progression API:
  from syft_queue import start, complete, fail, advance
  
  # Move job through pipeline
  start(job)      # inbox/approved → running
  complete(job)   # running → completed
  fail(job, "error message")  # → failed
  
  # Or use advance for automatic progression
  advance(job)    # Moves to next logical state

🏭 Pipeline Support:
  from syft_queue import Pipeline, PipelineBuilder
  
  # Build multi-stage pipeline
  pipeline = (PipelineBuilder()
    .add_stage("preprocess", preprocess_fn)
    .add_stage("analyze", analyze_fn)
    .add_stage("report", report_fn)
    .build())
  
  # Execute pipeline
  pipeline.execute(job)

💡 Pro Tips:
  • Jobs are stored in {{queue_name}}_queue/jobs/{{status}}/{{job_uid}}
  • Each job is a syft-object with mock data for privacy
  • Use q() for quick queue creation with auto-detection
  • Relative paths make jobs portable across datasites

📚 Learn More:
  • Docs: https://github.com/OpenMined/syft-queue
  • Examples: See examples/ folder
  • Support: https://github.com/OpenMined/syft-queue/issues
        """
        print(help_text)
    
    @abstractmethod
    def get_execution_context(self, job: 'Job') -> Dict[str, Any]:
        """
        Get execution context for running a job.
        
        Args:
            job: The job to get context for
            
        Returns:
            Dict with environment variables and paths for job execution
        """
        pass


class CodeQueue(BaseQueue):
    """
    A queue for executing code jobs (run.sh scripts).
    
    Code jobs wait for all required data inputs with the same job_id
    before execution begins.
    """
    
    def get_execution_context(self, job: 'Job') -> Dict[str, Any]:
        """Get execution context for code jobs."""
        # Check for input data from data queues with same job_id
        input_files = self._collect_input_data_for_job(job.uid)
        
        context = {
            'job_uid': str(job.uid),
            'job_name': job.name,
            'job_dir': str(job.object_path),
            'code_path': str(job.code_folder_path) if hasattr(job, 'code_folder_path') else str(job.object_path / 'code'),
            'output_path': str(job.object_path / 'output'),
            'working_dir': str(job.object_path),
            'input_files': input_files,  # List of data files from data queues
            'job_type': 'code'
        }
        
        return context
    
    def _collect_input_data_for_job(self, job_uid: UUID, timeout: int = 300) -> List[str]:
        """
        Collect input data files from data queues for a specific job ID.
        
        This method looks for output files from data queues that have the same job_id.
        It can wait (with timeout) for all expected inputs to arrive.
        """
        # For now, return empty list - this will be enhanced when we implement
        # cross-queue coordination
        return []


class DataQueue(BaseQueue):
    """
    A queue for processing data jobs.
    
    Data jobs process input data and output results, typically feeding
    into code queues or other data queues.
    """
    
    def get_execution_context(self, job: 'Job') -> Dict[str, Any]:
        """Get execution context for data jobs."""
        # Data jobs process input data and produce output data
        context = {
            'job_uid': str(job.uid),
            'job_name': job.name,
            'job_dir': str(job.object_path),
            'code_path': str(job.code_folder_path) if hasattr(job, 'code_folder_path') else str(job.object_path / 'code'),
            'input_file': str(job.object_path / 'input' / 'data'),
            'output_file': str(job.object_path / 'output' / 'data'),
            'working_dir': str(job.object_path),
            'job_type': 'data'
        }
        
        return context


# For backward compatibility, create a Queue alias
Queue = CodeQueue


def _queue_exists(name: str) -> bool:
    """Check if a queue with the given name already exists."""
    queues_base_path = _detect_syftbox_queues_path()
    folder_path = queues_base_path / f"{name}_queue"
    
    # Check if directory exists
    if not folder_path.exists():
        return False
    
    # Also check if the queue's syft-object exists
    # If directory exists but syft-object is gone, consider it deleted
    try:
        from pathlib import Path
        objects_dir = Path.home() / "SyftBox" / "datasites" / "liamtrask@gmail.com" / "public" / "objects"
        if objects_dir.exists():
            queue_objects = list(objects_dir.glob(f"q:{name}*"))
            if len(queue_objects) == 0:
                # Queue syft-object deleted, cleanup the empty directory
                _cleanup_empty_queue_directory(folder_path)
                return False
            return True
    except Exception as e:
        print(f"Warning: Error checking queue objects for {name}: {e}")
    
    # Fallback to directory existence
    return True


def _cleanup_empty_queue_directory(queue_dir: Path):
    """Cleanup empty queue directory when syft-objects are deleted."""
    try:
        import shutil
        
        # Check if directory is safe to delete (only contains expected structure)
        if not queue_dir.exists():
            return
            
        jobs_dir = queue_dir / "jobs"
        if not jobs_dir.exists():
            # No jobs directory, safe to delete
            shutil.rmtree(queue_dir)
            print(f"Cleaned up empty queue directory: {queue_dir.name}")
            return
            
        # Check if all job status directories are empty (only contain syft.pub.yaml)
        all_empty = True
        for status_dir in jobs_dir.iterdir():
            if status_dir.is_dir():
                # Count non-yaml files and directories
                contents = [item for item in status_dir.iterdir() 
                          if not item.name.endswith('.yaml')]
                if len(contents) > 0:
                    all_empty = False
                    break
        
        if all_empty:
            shutil.rmtree(queue_dir)
            print(f"Cleaned up empty queue directory: {queue_dir.name}")
        else:
            print(f"Queue directory {queue_dir.name} contains jobs, skipping cleanup")
            
    except Exception as e:
        print(f"Warning: Could not cleanup queue directory {queue_dir}: {e}")


def get_queues_path() -> Path:
    """Get the path where queues are created."""
    return _detect_syftbox_queues_path()


def list_queues() -> List[str]:
    """List all existing queue names."""
    queues_path = get_queues_path()
    if not queues_path.exists():
        return []
    
    queue_names = []
    for item in queues_path.iterdir():
        if item.is_dir() and item.name.endswith("_queue"):
            # Remove the "_queue" suffix to get the queue name
            queue_name = item.name[:-6]  # Remove "_queue" (6 characters)
            queue_names.append(queue_name)
    
    return sorted(queue_names)


# ========== Path Resolution Utilities for Job Execution ==========

def prepare_job_for_execution(job: Job) -> Dict[str, Any]:
    """
    Prepare a job for execution by resolving all paths.
    
    Args:
        job: The job to prepare
        
    Returns:
        Dict containing resolved paths and execution context
    """
    execution_context = {
        'job_uid': str(job.uid),
        'job_name': job.name,
        'job_dir': str(job.object_path),
        'code_path': None,
        'output_path': None,
        'working_dir': str(job.object_path),
    }
    
    # Resolve code folder
    code_path = job.resolved_code_folder
    if code_path:
        execution_context['code_path'] = str(code_path)
    else:
        # Fallback to job directory code folder
        job_code = job.object_path / "code"
        if job_code.exists():
            execution_context['code_path'] = str(job_code)
    
    # Resolve or create output folder
    output_path = job.resolved_output_folder
    if output_path:
        execution_context['output_path'] = str(output_path)
    else:
        # Create output directory in job folder
        job_output = job.object_path / "output"
        job_output.mkdir(exist_ok=True)
        execution_context['output_path'] = str(job_output)
        
        # Update job with output folder
        job.output_folder = str(job_output)
        job.output_folder_relative = "output"
        job.update_relative_paths()
    
    return execution_context


def execute_job_with_context(job: Job, runner_command: Optional[str] = None) -> Tuple[bool, str]:
    """
    Execute a job with proper path resolution.
    
    Args:
        job: The job to execute
        runner_command: Optional custom runner command
        
    Returns:
        Tuple of (success, output_or_error)
    """
    import subprocess
    import os
    
    # Prepare execution context
    context = prepare_job_for_execution(job)
    
    if not context['code_path']:
        return False, "No code folder found for job"
    
    # Default runner command
    if not runner_command:
        # Look for run.sh in code directory
        run_script = Path(context['code_path']) / "run.sh"
        if run_script.exists():
            runner_command = f"bash {run_script}"
        else:
            return False, "No run.sh script found in code directory"
    
    # Set up environment
    env = os.environ.copy()
    env['JOB_UID'] = context['job_uid']
    env['JOB_NAME'] = context['job_name']
    env['JOB_DIR'] = context['job_dir']
    env['CODE_PATH'] = context['code_path']
    env['OUTPUT_PATH'] = context['output_path']
    
    # Execute the job
    try:
        result = subprocess.run(
            runner_command,
            shell=True,
            cwd=context['working_dir'],
            env=env,
            capture_output=True,
            text=True,
            timeout=job.timeout_seconds
        )
        
        # Store output
        output = f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
        job.logs = output
        job.exit_code = result.returncode
        
        if result.returncode == 0:
            job.update_status(JobStatus.completed)
            return True, output
        else:
            job.update_status(JobStatus.failed, f"Exit code: {result.returncode}")
            return False, output
            
    except subprocess.TimeoutExpired:
        error = f"Job timed out after {job.timeout_seconds} seconds"
        job.update_status(JobStatus.timedout, error)
        return False, error
    except Exception as e:
        error = f"Job execution failed: {str(e)}"
        job.update_status(JobStatus.failed, error)
        return False, error


def get_queue(name: str) -> Optional[Queue]:
    """Get an existing queue by name."""
    if not _queue_exists(name):
        return None
    
    queues_base_path = _detect_syftbox_queues_path()
    folder_path = queues_base_path / f"{name}_queue"
    
    try:
        return Queue(folder_path, name)
    except Exception:
        return None


def help():
    """Show help and getting started guide for SyftQueue."""
    # Create a temporary queue instance just to call the help method
    from . import __version__
    print(f"\n🎯 SyftQueue v{__version__} - Getting Started Guide")
    print("=" * 60)
    
    # Use the BaseQueue help method by creating a temporary instance
    try:
        queues_path = get_queues_path()
        temp_queue = BaseQueue.__new__(BaseQueue)
        temp_queue.help()
    except:
        # Fallback if queue creation fails
        print("""
👋 Welcome! SyftQueue is a portable queue system for SyftBox.

Quick Start:
  from syft_queue import q
  my_queue = q("analytics")
  
For full help, create a queue and run: my_queue.help()
""")


# ========== Pipeline Progression API ==========

def approve(job: Job, approver: Optional[str] = None, notes: Optional[str] = None) -> Job:
    """
    Approve a job for processing.
    
    Args:
        job: The job to approve
        approver: Email of the approver
        notes: Optional approval notes
        
    Returns:
        The updated job
        
    Example:
        job = queue.get_job(job_uid)
        approve(job, approver="admin@company.com", notes="Code review passed")
    """
    if job.status != JobStatus.inbox:
        raise ValueError(f"Can only approve jobs in inbox, job is in {job.status.value}")
    
    job.update_status(JobStatus.approved)
    
    # Store approval metadata
    if not hasattr(job, 'approval_info'):
        job.approval_info = {}
    
    job.approval_info = {
        'approver': approver or 'system',
        'approved_at': datetime.now().isoformat(),
        'notes': notes
    }
    job._update_syft_object()
    
    return job


def reject(job: Job, reason: str, reviewer: Optional[str] = None) -> Job:
    """
    Reject a job with a reason.
    
    Args:
        job: The job to reject
        reason: Reason for rejection
        reviewer: Email of the reviewer
        
    Returns:
        The updated job
        
    Example:
        reject(job, reason="Unauthorized data access", reviewer="security@company.com")
    """
    if job.is_terminal:
        raise ValueError(f"Cannot reject job in terminal state {job.status.value}")
    
    job.update_status(JobStatus.rejected, error_message=reason)
    
    # Store rejection metadata
    if not hasattr(job, 'rejection_info'):
        job.rejection_info = {}
        
    job.rejection_info = {
        'reviewer': reviewer or 'system',
        'rejected_at': datetime.now().isoformat(),
        'reason': reason
    }
    job._update_syft_object()
    
    return job


def start(job: Job, runner: Optional[str] = None) -> Job:
    """
    Start running a job.
    
    Args:
        job: The job to start
        runner: Identifier of the runner/worker
        
    Returns:
        The updated job
        
    Example:
        start(job, runner="worker-001")
    """
    if job.status != JobStatus.approved:
        raise ValueError(f"Can only start approved jobs, job is in {job.status.value}")
    
    job.started_at = datetime.now()
    job.update_status(JobStatus.running)
    
    if runner:
        job.runner = runner
        job._update_syft_object()
    
    return job


def complete(job: Job, 
            output_path: Optional[str] = None,
            metrics: Optional[Dict[str, Any]] = None) -> Job:
    """
    Mark a job as completed.
    
    Args:
        job: The job to complete
        output_path: Path to output files
        metrics: Optional performance metrics
        
    Returns:
        The updated job
        
    Example:
        complete(job, 
                output_path="output/results.json",
                metrics={"accuracy": 0.95, "runtime": 3600})
    """
    if job.status != JobStatus.running:
        raise ValueError(f"Can only complete running jobs, job is in {job.status.value}")
    
    job.completed_at = datetime.now()
    
    if output_path:
        job.output_folder = output_path
        job.update_relative_paths()
    
    job.update_status(JobStatus.completed)
    
    if metrics:
        job.metrics = metrics
        job._update_syft_object()
    
    return job


def fail(job: Job, error: str, exit_code: Optional[int] = None) -> Job:
    """
    Mark a job as failed.
    
    Args:
        job: The job to fail
        error: Error message
        exit_code: Optional process exit code
        
    Returns:
        The updated job
        
    Example:
        fail(job, error="Out of memory", exit_code=137)
    """
    if not job.status == JobStatus.running:
        raise ValueError(f"Can only fail running jobs, job is in {job.status.value}")
    
    job.completed_at = datetime.now()
    job.exit_code = exit_code
    job.update_status(JobStatus.failed, error_message=error)
    
    return job


def timeout(job: Job) -> Job:
    """
    Mark a job as timed out.
    
    Args:
        job: The job that timed out
        
    Returns:
        The updated job
    """
    if not job.status == JobStatus.running:
        raise ValueError(f"Can only timeout running jobs, job is in {job.status.value}")
    
    job.completed_at = datetime.now()
    elapsed = (job.completed_at - job.created_at).total_seconds()
    job.update_status(JobStatus.timedout, 
                     error_message=f"Job timed out after {elapsed:.0f} seconds")
    
    return job


def advance(job: Job, to_status: Optional[JobStatus] = None) -> Job:
    """
    Advance a job to the next logical status or a specific status.
    
    Args:
        job: The job to advance
        to_status: Target status (optional)
        
    Returns:
        The updated job
        
    Example:
        # Natural progression
        advance(job)  # inbox -> approved
        advance(job)  # approved -> running
        
        # Jump to specific status
        advance(job, JobStatus.rejected)
    """
    if job.is_terminal:
        raise ValueError(f"Cannot advance job in terminal state {job.status.value}")
    
    if to_status:
        # Direct transition to specific status
        if to_status == JobStatus.approved:
            return approve(job)
        elif to_status == JobStatus.rejected:
            return reject(job, reason="Manually rejected")
        elif to_status == JobStatus.running:
            return start(job)
        elif to_status == JobStatus.completed:
            return complete(job)
        elif to_status == JobStatus.failed:
            return fail(job, error="Manually failed")
        elif to_status == JobStatus.timedout:
            return timeout(job)
    else:
        # Natural progression
        if job.status == JobStatus.inbox:
            return approve(job)
        elif job.status == JobStatus.approved:
            return start(job)
        elif job.status == JobStatus.running:
            return complete(job)
        else:
            raise ValueError(f"No natural progression from {job.status.value}")
    
    return job


# ========== Batch Operations ==========

def approve_all(jobs: List[Job], 
                approver: Optional[str] = None,
                condition: Optional[Callable[[Job], bool]] = None) -> List[Job]:
    """
    Approve multiple jobs at once.
    
    Args:
        jobs: List of jobs to approve
        approver: Email of the approver
        condition: Optional condition function
        
    Returns:
        List of approved jobs
        
    Example:
        # Approve all jobs from trusted sources
        inbox_jobs = queue.list_jobs(JobStatus.inbox)
        approved = approve_all(
            inbox_jobs,
            approver="admin@company.com",
            condition=lambda j: j.requester_email.endswith("@trusted.org")
        )
    """
    approved = []
    for job in jobs:
        if job.status == JobStatus.inbox and (condition is None or condition(job)):
            try:
                approve(job, approver=approver)
                approved.append(job)
            except Exception:
                continue
    return approved


def process_queue(queue: Queue, 
                 max_jobs: int = 10,
                 auto_approve: Optional[Callable[[Job], bool]] = None,
                 auto_reject: Optional[Callable[[Job], str]] = None) -> Dict[str, List[Job]]:
    """
    Process jobs in a queue with optional auto-approval/rejection.
    
    Args:
        queue: The queue to process
        max_jobs: Maximum number of jobs to process
        auto_approve: Function that returns True if job should be auto-approved
        auto_reject: Function that returns rejection reason if job should be rejected
        
    Returns:
        Dict with lists of processed jobs by outcome
        
    Example:
        results = process_queue(
            queue,
            max_jobs=50,
            auto_approve=lambda j: j.requester_email.endswith("@university.edu"),
            auto_reject=lambda j: "Missing code" if not j.code_folder else None
        )
    """
    results = {
        'approved': [],
        'rejected': [],
        'skipped': []
    }
    
    inbox_jobs = queue.list_jobs(JobStatus.inbox, limit=max_jobs)
    
    for job in inbox_jobs:
        # Check auto-reject first
        if auto_reject:
            reject_reason = auto_reject(job)
            if reject_reason:
                reject(job, reason=reject_reason)
                results['rejected'].append(job)
                continue
        
        # Check auto-approve
        if auto_approve and auto_approve(job):
            approve(job)
            results['approved'].append(job)
        else:
            results['skipped'].append(job)
    
    return results


def queue(name: str = "default-queue", queue_type: str = "code", owner_email: str = None, force: bool = False, **kwargs) -> BaseQueue:
    """
    Create a new queue with automatic path creation.
    
    Queues are created in SyftBox/datasites/<email>/app_data/syft-queues/ by default.
    Falls back to current directory if SyftBox is not configured.
    
    Args:
        name: Name of the queue (will be used as folder name)
        queue_type: Type of queue - "code" for CodeQueue, "data" for DataQueue
        owner_email: Email of the owner (if None, will auto-detect)
        force: If True, replace existing queue with same name
        **kwargs: Additional queue configuration
        
    Returns:
        BaseQueue: The created queue object (CodeQueue or DataQueue)
        
    Raises:
        ValueError: If queue already exists and force=False, or invalid queue_type
    """
    # Validate queue type
    if queue_type not in ["code", "data"]:
        raise ValueError(f"Invalid queue_type '{queue_type}'. Must be 'code' or 'data'.")
    
    # Check if queue already exists
    if _queue_exists(name) and not force:
        raise ValueError(
            f"Queue '{name}' already exists. "
            f"Use force=True to replace it: q('{name}', force=True)"
        )
    
    # Auto-create folder path in SyftBox directory
    queues_base_path = _detect_syftbox_queues_path()
    folder_path = queues_base_path / f"{name}_queue"
    
    # If force=True and queue exists, remove the old one first
    if force and folder_path.exists():
        import shutil
        shutil.rmtree(folder_path)
    
    # Create the appropriate queue type
    if queue_type == "code":
        return CodeQueue(folder_path, name, owner_email=owner_email, **kwargs)
    else:  # queue_type == "data"
        return DataQueue(folder_path, name, owner_email=owner_email, **kwargs)


def q(name: str = "default-queue", queue_type: str = "code", owner_email: str = None, force: bool = False, **kwargs) -> BaseQueue:
    """
    Create a new queue with automatic path creation (short alias).
    
    Queues are created in SyftBox/datasites/<email>/app_data/syft-queues/ by default.
    Falls back to current directory if SyftBox is not configured.
    
    Args:
        name: Name of the queue (will be used as folder name)
        queue_type: Type of queue - "code" for CodeQueue, "data" for DataQueue
        owner_email: Email of the owner (if None, will auto-detect)
        force: If True, replace existing queue with same name
        **kwargs: Additional queue configuration
        
    Returns:
        BaseQueue: The created queue object (CodeQueue or DataQueue)
        
    Raises:
        ValueError: If queue already exists and force=False, or invalid queue_type
    """
    return queue(name, queue_type=queue_type, owner_email=owner_email, force=force, **kwargs)


def create_queue(folder_path: Union[str, Path], queue_name: str = "default-queue", owner_email: str = None, **kwargs) -> Queue:
    """
    Create a new queue (legacy function - use queue() or q() instead).
    
    Args:
        folder_path: Path where the queue should be created
        queue_name: Name of the queue
        owner_email: Email of the owner (if None, will auto-detect)
        **kwargs: Additional queue configuration
        
    Returns:
        Queue: The created queue object
    """
    return Queue(folder_path, queue_name, owner_email=owner_email, **kwargs)


def create_job(queue: Queue, name: str, requester_email: str, target_email: str, **kwargs) -> Job:
    """
    Create a new job in the specified queue.
    
    Args:
        queue: The queue to create the job in
        name: Job name
        requester_email: Email of the job requester
        target_email: Email of the target (data owner)
        **kwargs: Additional job attributes
        
    Returns:
        Job: The created job object
    """
    return queue.create_job(name, requester_email, target_email, **kwargs) 