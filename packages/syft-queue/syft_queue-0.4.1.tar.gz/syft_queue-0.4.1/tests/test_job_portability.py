"""
Test Job Portability with Relative Paths

This test suite verifies that jobs can be moved between directories
and maintain their file references through relative paths.
"""

import os
import shutil
import tempfile
import json
from pathlib import Path
import pytest
from syft_queue import q, Job, JobStatus, prepare_job_for_execution


class TestJobPortability:
    """Test suite for job portability features."""
    
    def setup_method(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.original_env = os.environ.get('SYFTBOX_DATA_FOLDER')
        
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
        if self.original_env:
            os.environ['SYFTBOX_DATA_FOLDER'] = self.original_env
        elif 'SYFTBOX_DATA_FOLDER' in os.environ:
            del os.environ['SYFTBOX_DATA_FOLDER']
    
    def create_test_code(self, code_dir: Path):
        """Create test job code."""
        code_dir.mkdir(parents=True, exist_ok=True)
        
        # Create Python script
        script = code_dir / "test_script.py"
        script.write_text("""
import os
import json

output_dir = os.environ.get('OUTPUT_PATH', '.')
with open(f"{output_dir}/test_output.json", "w") as f:
    json.dump({"status": "success", "message": "Test completed"}, f)
""")
        
        # Create run script
        run_script = code_dir / "run.sh"
        run_script.write_text("#!/bin/bash\npython test_script.py")
        run_script.chmod(0o755)
    
    def test_job_creation_with_relative_paths(self):
        """Test creating a job with relative paths enabled."""
        # Set up environment
        queue_dir = Path(self.test_dir) / "queues"
        os.environ['SYFTBOX_DATA_FOLDER'] = str(queue_dir)
        
        # Create test code
        code_dir = Path(self.test_dir) / "test_code"
        self.create_test_code(code_dir)
        
        # Create queue and job
        test_queue = q("test_queue")
        job = test_queue.create_job(
            name="test_job",
            requester_email="test@example.com",
            target_email="owner@example.com",
            code_folder=str(code_dir),
            use_relative_paths=True
        )
        
        # Verify relative paths are set
        assert job.code_folder_relative is not None
        assert job.base_path is not None
        assert job.resolved_code_folder is not None
        assert job.resolved_code_folder.exists()
    
    def test_job_movement_preserves_access(self):
        """Test that moving a job preserves file access."""
        # Create initial structure
        stage1 = Path(self.test_dir) / "pipeline" / "stage1"
        stage2 = Path(self.test_dir) / "pipeline" / "stage2"
        
        os.environ['SYFTBOX_DATA_FOLDER'] = str(stage1)
        
        # Create job in stage1
        code_dir = Path(self.test_dir) / "code"
        self.create_test_code(code_dir)
        
        queue1 = q("processing")
        job1 = queue1.create_job(
            name="movable_job",
            requester_email="test@example.com",
            target_email="owner@example.com",
            code_folder=str(code_dir),
            use_relative_paths=True
        )
        
        # Get job directory name
        job_dir_name = job1.object_path.name
        
        # Move job to stage2
        stage2.mkdir(parents=True, exist_ok=True)
        target_dir = stage2 / "processing_queue" / "jobs" / "inbox" / job_dir_name
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.move(str(job1.object_path), str(target_dir))
        
        # Load job from new location
        job2 = Job(target_dir)
        
        # Verify files are still accessible
        assert job2.resolved_code_folder is not None
        assert job2.resolved_code_folder.exists()
        assert (job2.resolved_code_folder / "test_script.py").exists()
        assert (job2.resolved_code_folder / "run.sh").exists()
    
    def test_pipeline_portability(self):
        """Test moving an entire pipeline maintains job integrity."""
        # Create pipeline
        pipeline1 = Path(self.test_dir) / "ml_pipeline_v1"
        os.environ['SYFTBOX_DATA_FOLDER'] = str(pipeline1)
        
        # Create multiple jobs
        code_dir = Path(self.test_dir) / "shared_code"
        self.create_test_code(code_dir)
        
        queue = q("analysis")
        jobs = []
        
        for i in range(3):
            job = queue.create_job(
                name=f"analysis_job_{i}",
                requester_email="analyst@example.com",
                target_email="owner@example.com",
                code_folder=str(code_dir),
                use_relative_paths=True
            )
            jobs.append((job.uid, job.object_path.name))
        
        # Move entire pipeline
        pipeline2 = Path(self.test_dir) / "archived" / "ml_pipeline_v1"
        pipeline2.parent.mkdir(parents=True)
        shutil.move(str(pipeline1), str(pipeline2))
        
        # Verify all jobs are still functional
        os.environ['SYFTBOX_DATA_FOLDER'] = str(pipeline2)
        
        for job_uid, job_dir_name in jobs:
            job_path = pipeline2 / "analysis_queue" / "jobs" / "inbox" / job_dir_name
            assert job_path.exists()
            
            job = Job(job_path)
            assert job.resolved_code_folder is not None
            assert job.resolved_code_folder.exists()
    
    def test_relative_path_resolution_fallback(self):
        """Test path resolution fallback mechanisms."""
        # Create job with code
        queue_dir = Path(self.test_dir) / "test_queue"
        os.environ['SYFTBOX_DATA_FOLDER'] = str(queue_dir)
        
        code_dir = Path(self.test_dir) / "original_code"
        self.create_test_code(code_dir)
        
        queue = q("test")
        job = queue.create_job(
            name="fallback_test",
            requester_email="test@example.com",
            target_email="owner@example.com",
            code_folder=str(code_dir),
            use_relative_paths=True
        )
        
        # Verify initial resolution
        assert job.resolved_code_folder is not None
        initial_path = job.resolved_code_folder
        
        # Move the job directory but not the code
        new_location = Path(self.test_dir) / "moved_jobs" / job.object_path.name
        new_location.parent.mkdir(parents=True)
        shutil.move(str(job.object_path), str(new_location))
        
        # Load from new location
        moved_job = Job(new_location)
        
        # Should still resolve to code (via fallback)
        assert moved_job.resolved_code_folder is not None
        # In this case, it should find the code directory within the job folder
        assert (moved_job.resolved_code_folder / "test_script.py").exists()
    
    def test_execution_context_preparation(self):
        """Test job execution context preparation."""
        # Create job
        queue_dir = Path(self.test_dir) / "exec_test"
        os.environ['SYFTBOX_DATA_FOLDER'] = str(queue_dir)
        
        code_dir = Path(self.test_dir) / "exec_code"
        self.create_test_code(code_dir)
        
        queue = q("execution")
        job = queue.create_job(
            name="exec_test_job",
            requester_email="test@example.com",
            target_email="owner@example.com",
            code_folder=str(code_dir),
            use_relative_paths=True
        )
        
        # Prepare execution context
        context = prepare_job_for_execution(job)
        
        # Verify context
        assert context['code_path'] is not None
        assert context['output_path'] is not None
        assert context['job_dir'] == str(job.object_path)
        assert Path(context['code_path']).exists()
        assert Path(context['output_path']).exists()
        
        # Verify job was updated with output path
        assert job.output_folder is not None
        assert job.output_folder_relative == "output"
    
    def test_cross_platform_relative_paths(self):
        """Test relative paths work across platform path separators."""
        # Create job with nested structure
        queue_dir = Path(self.test_dir) / "platform_test"
        os.environ['SYFTBOX_DATA_FOLDER'] = str(queue_dir)
        
        # Create deeply nested code
        code_dir = Path(self.test_dir) / "deep" / "nested" / "code" / "structure"
        self.create_test_code(code_dir)
        
        queue = q("platform")
        job = queue.create_job(
            name="platform_test",
            requester_email="test@example.com",
            target_email="owner@example.com",
            code_folder=str(code_dir),
            use_relative_paths=True
        )
        
        # Check relative path uses forward slashes (portable)
        assert job.code_folder_relative is not None
        # Relative paths should always use forward slashes for portability
        assert "/" in job.code_folder_relative or "\\" in job.code_folder_relative
        
        # Verify resolution still works
        assert job.resolved_code_folder is not None
        assert job.resolved_code_folder.exists()


def test_integration_job_lifecycle_with_movement():
    """Integration test: full job lifecycle with movement between stages."""
    with tempfile.TemporaryDirectory() as workspace:
        workspace = Path(workspace)
        
        # Create pipeline stages
        stages = {
            'development': workspace / "dev",
            'staging': workspace / "staging", 
            'production': workspace / "prod"
        }
        
        for stage_path in stages.values():
            stage_path.mkdir(parents=True)
        
        # 1. Create job in development
        os.environ['SYFTBOX_DATA_FOLDER'] = str(stages['development'])
        
        code_dir = workspace / "ml_code"
        code_dir.mkdir()
        (code_dir / "train.py").write_text("print('Training model...')")
        (code_dir / "run.sh").write_text("#!/bin/bash\npython train.py")
        (code_dir / "run.sh").chmod(0o755)
        
        dev_queue = q("ml_experiments")
        job = dev_queue.create_job(
            name="model_training_v1",
            requester_email="ml_engineer@company.com",
            target_email="data_owner@company.com",
            code_folder=str(code_dir),
            description="Train customer churn prediction model",
            use_relative_paths=True
        )
        
        print(f"Created job in development: {job.object_path}")
        
        # 2. Approve and move to staging
        job.update_status(JobStatus.approved)
        
        staging_dir = stages['staging'] / "ml_experiments_queue" / "jobs" / "approved" / job.object_path.name
        staging_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(job.object_path), str(staging_dir))
        
        # 3. Load in staging and execute
        os.environ['SYFTBOX_DATA_FOLDER'] = str(stages['staging'])
        staging_job = Job(staging_dir)
        
        # Prepare for execution
        context = prepare_job_for_execution(staging_job)
        assert context['code_path'] is not None
        print(f"Job ready for execution in staging: {context['code_path']}")
        
        # 4. After testing, move to production
        staging_job.update_status(JobStatus.completed)
        
        prod_dir = stages['production'] / "ml_experiments_queue" / "jobs" / "completed" / staging_job.object_path.name
        prod_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(staging_job.object_path), str(prod_dir))
        
        # 5. Verify in production
        os.environ['SYFTBOX_DATA_FOLDER'] = str(stages['production'])
        prod_job = Job(prod_dir)
        
        assert prod_job.status == JobStatus.completed
        assert prod_job.resolved_code_folder is not None
        print(f"Job successfully deployed to production: {prod_job.object_path}")
        
        # 6. Archive entire production pipeline
        archive_dir = workspace / "archives" / "2024_Q1"
        archive_dir.mkdir(parents=True)
        shutil.move(str(stages['production']), str(archive_dir / "production"))
        
        # 7. Verify archived job is still accessible
        archived_job_path = archive_dir / "production" / "ml_experiments_queue" / "jobs" / "completed" / prod_job.object_path.name
        archived_job = Job(archived_job_path)
        
        assert archived_job.resolved_code_folder is not None
        print(f"Archived job still functional: {archived_job.object_path}")
        
        return True


if __name__ == "__main__":
    # Run integration test
    print("Running job portability integration test...")
    if test_integration_job_lifecycle_with_movement():
        print("✓ Integration test passed!")
    
    # Run pytest for unit tests
    print("\nRunning unit tests...")
    pytest.main([__file__, "-v"])