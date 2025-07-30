"""
SyftQueue Pipeline API Design

This module defines a clean API for progressing jobs through pipeline stages.
"""

from typing import Optional, List, Dict, Any, Callable, Union
from enum import Enum
from pathlib import Path
from datetime import datetime
from uuid import UUID
import shutil

from syft_queue import Job, Queue, JobStatus, q


class PipelineStage(Enum):
    """Standard pipeline stages that map to job statuses."""
    INBOX = "inbox"
    REVIEW = "approved"  # Maps to approved status
    PROCESSING = "running"
    QUALITY_CHECK = "running"  # Can have multiple stages with same status
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"


class PipelineTransition:
    """Represents a valid transition between pipeline stages."""
    
    def __init__(self, 
                 from_stage: PipelineStage, 
                 to_stage: PipelineStage,
                 condition: Optional[Callable[[Job], bool]] = None,
                 on_transition: Optional[Callable[[Job], None]] = None):
        self.from_stage = from_stage
        self.to_stage = to_stage
        self.condition = condition or (lambda job: True)
        self.on_transition = on_transition
    
    def is_valid_for(self, job: Job, current_stage: PipelineStage) -> bool:
        """Check if this transition is valid for the given job."""
        return current_stage == self.from_stage and self.condition(job)
    
    def execute(self, job: Job) -> None:
        """Execute any transition hooks."""
        if self.on_transition:
            self.on_transition(job)


class Pipeline:
    """
    A pipeline that manages job progression through stages.
    
    Example:
        # Define a simple ML pipeline
        ml_pipeline = Pipeline("ml_training")
        ml_pipeline.add_stage("data_prep", JobStatus.inbox)
        ml_pipeline.add_stage("review", JobStatus.approved)
        ml_pipeline.add_stage("training", JobStatus.running)
        ml_pipeline.add_stage("evaluation", JobStatus.running)
        ml_pipeline.add_stage("deployment", JobStatus.completed)
        
        # Define transitions
        ml_pipeline.add_transition("data_prep", "review", 
                                 condition=lambda job: job.code_folder is not None)
        ml_pipeline.add_transition("review", "training")
        ml_pipeline.add_transition("training", "evaluation",
                                 condition=lambda job: job.output_folder is not None)
        ml_pipeline.add_transition("evaluation", "deployment",
                                 condition=lambda job: check_model_metrics(job))
    """
    
    def __init__(self, name: str, base_path: Optional[Path] = None):
        self.name = name
        self.base_path = Path(base_path) if base_path else None
        self.stages: Dict[str, JobStatus] = {}
        self.stage_paths: Dict[str, Path] = {}
        self.transitions: List[PipelineTransition] = []
        self.stage_handlers: Dict[str, Callable] = {}
        
    def add_stage(self, 
                  name: str, 
                  status: JobStatus,
                  path: Optional[Path] = None,
                  handler: Optional[Callable[[Job], None]] = None) -> 'Pipeline':
        """Add a stage to the pipeline."""
        self.stages[name] = status
        
        if path:
            self.stage_paths[name] = path
        elif self.base_path:
            self.stage_paths[name] = self.base_path / name
            
        if handler:
            self.stage_handlers[name] = handler
            
        return self
    
    def add_transition(self,
                      from_stage: str,
                      to_stage: str,
                      condition: Optional[Callable[[Job], bool]] = None,
                      on_transition: Optional[Callable[[Job], None]] = None) -> 'Pipeline':
        """Add a valid transition between stages."""
        if from_stage not in self.stages:
            raise ValueError(f"Unknown stage: {from_stage}")
        if to_stage not in self.stages:
            raise ValueError(f"Unknown stage: {to_stage}")
            
        transition = PipelineTransition(
            from_stage=from_stage,
            to_stage=to_stage,
            condition=condition,
            on_transition=on_transition
        )
        self.transitions.append(transition)
        return self
    
    def get_job_stage(self, job: Job) -> Optional[str]:
        """Get the current stage of a job."""
        # Try to get from job metadata first
        if hasattr(job, 'pipeline_stage'):
            return job.pipeline_stage
            
        # Otherwise infer from status
        for stage_name, stage_status in self.stages.items():
            if job.status == stage_status:
                return stage_name
                
        return None
    
    def advance(self, job: Job, to_stage: Optional[str] = None) -> bool:
        """
        Advance a job to the next stage or a specific stage.
        
        Returns:
            bool: True if job was advanced, False otherwise
        """
        current_stage = self.get_job_stage(job)
        if not current_stage:
            raise ValueError(f"Job {job.uid} is not in any pipeline stage")
        
        # Find valid transitions
        valid_transitions = [
            t for t in self.transitions
            if t.from_stage == current_stage and t.is_valid_for(job, current_stage)
        ]
        
        if to_stage:
            # Find specific transition
            transition = next(
                (t for t in valid_transitions if t.to_stage == to_stage),
                None
            )
            if not transition:
                return False
        else:
            # Use first valid transition
            if not valid_transitions:
                return False
            transition = valid_transitions[0]
        
        # Execute transition
        self._execute_transition(job, current_stage, transition.to_stage)
        transition.execute(job)
        
        # Run stage handler if defined
        if transition.to_stage in self.stage_handlers:
            self.stage_handlers[transition.to_stage](job)
            
        return True
    
    def _execute_transition(self, job: Job, from_stage: str, to_stage: str):
        """Execute the physical transition of a job between stages."""
        # Update job status
        job.status = self.stages[to_stage]
        job.pipeline_stage = to_stage
        job.update_relative_paths()
        job._update_syft_object()
        
        # Move job directory if paths are defined
        if from_stage in self.stage_paths and to_stage in self.stage_paths:
            from_path = self.stage_paths[from_stage] / str(job.uid)
            to_path = self.stage_paths[to_stage] / str(job.uid)
            
            if from_path.exists() and from_path != to_path:
                to_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(from_path), str(to_path))
                
                # Update job's object_path
                job.object_path = to_path
                job.base_path = str(to_path)
                job.update_relative_paths()


# ============ Convenience API Functions ============

def advance_job(job: Union[Job, UUID, str], 
                to_status: Optional[JobStatus] = None,
                reason: Optional[str] = None,
                **kwargs) -> Job:
    """
    Advance a job to the next status or a specific status.
    
    Args:
        job: Job object, UUID, or string UUID
        to_status: Target status (if None, advances to natural next status)
        reason: Reason for the transition
        **kwargs: Additional metadata to store
        
    Example:
        # Simple advancement
        advance_job(job)  # inbox -> approved
        advance_job(job, JobStatus.running)  # any -> running
        
        # With metadata
        advance_job(job, JobStatus.rejected, reason="Invalid code structure")
        advance_job(job, JobStatus.completed, metrics={"accuracy": 0.95})
    """
    # Get job object if needed
    if isinstance(job, (UUID, str)):
        # Would need queue context to look up job
        raise NotImplementedError("Looking up jobs by UUID requires queue context")
    
    # Determine next status
    if to_status is None:
        # Natural progression
        status_flow = {
            JobStatus.inbox: JobStatus.approved,
            JobStatus.approved: JobStatus.running,
            JobStatus.running: JobStatus.completed,
        }
        to_status = status_flow.get(job.status)
        
    if not to_status:
        raise ValueError(f"Cannot advance job from status {job.status}")
    
    # Update job
    job.update_status(to_status, error_message=reason)
    
    # Store additional metadata
    if kwargs:
        if not hasattr(job, 'transition_metadata'):
            job.transition_metadata = {}
        job.transition_metadata[to_status.value] = {
            'timestamp': datetime.now().isoformat(),
            'reason': reason,
            **kwargs
        }
        job._update_syft_object()
    
    return job


def approve_job(job: Job, approver: Optional[str] = None, notes: Optional[str] = None) -> Job:
    """Approve a job for processing."""
    return advance_job(
        job, 
        JobStatus.approved,
        reason=notes,
        approver=approver,
        approved_at=datetime.now().isoformat()
    )


def reject_job(job: Job, reason: str, reviewer: Optional[str] = None) -> Job:
    """Reject a job with a reason."""
    return advance_job(
        job,
        JobStatus.rejected,
        reason=reason,
        reviewer=reviewer,
        rejected_at=datetime.now().isoformat()
    )


def start_job(job: Job, runner: Optional[str] = None) -> Job:
    """Mark a job as running."""
    job.started_at = datetime.now()
    return advance_job(
        job,
        JobStatus.running,
        runner=runner
    )


def complete_job(job: Job, 
                 output_path: Optional[str] = None,
                 metrics: Optional[Dict[str, Any]] = None) -> Job:
    """Mark a job as completed with optional outputs."""
    job.completed_at = datetime.now()
    if output_path:
        job.output_folder = output_path
        job.update_relative_paths()
    
    return advance_job(
        job,
        JobStatus.completed,
        metrics=metrics,
        duration=(job.completed_at - job.started_at).total_seconds() if job.started_at else None
    )


def fail_job(job: Job, error: str, exit_code: Optional[int] = None) -> Job:
    """Mark a job as failed with error details."""
    job.exit_code = exit_code
    return advance_job(
        job,
        JobStatus.failed,
        reason=error,
        exit_code=exit_code
    )


# ============ Batch Operations ============

def advance_jobs(jobs: List[Job], 
                 to_status: Optional[JobStatus] = None,
                 condition: Optional[Callable[[Job], bool]] = None) -> List[Job]:
    """
    Advance multiple jobs matching a condition.
    
    Example:
        # Approve all jobs from a specific requester
        advance_jobs(
            inbox_jobs,
            JobStatus.approved,
            condition=lambda j: j.requester_email == "trusted@example.com"
        )
    """
    advanced = []
    for job in jobs:
        if condition is None or condition(job):
            try:
                advance_job(job, to_status)
                advanced.append(job)
            except Exception:
                continue  # Skip jobs that can't be advanced
    return advanced


# ============ Pipeline Builder API ============

class PipelineBuilder:
    """
    Fluent API for building pipelines.
    
    Example:
        pipeline = (PipelineBuilder("ml_pipeline")
            .stage("data_prep", JobStatus.inbox)
            .stage("review", JobStatus.approved)
            .stage("training", JobStatus.running)
            .stage("evaluation", JobStatus.running)
            .stage("deployment", JobStatus.completed)
            .transition("data_prep", "review")
            .transition("review", "training", 
                       condition=lambda j: j.requester_email.endswith("@trusted.org"))
            .transition("training", "evaluation")
            .transition("evaluation", "deployment",
                       condition=lambda j: get_metric(j, "accuracy") > 0.9)
            .on_enter("training", start_training)
            .on_enter("deployment", deploy_model)
            .build()
        )
    """
    
    def __init__(self, name: str):
        self.pipeline = Pipeline(name)
    
    def stage(self, name: str, status: JobStatus, path: Optional[Path] = None) -> 'PipelineBuilder':
        self.pipeline.add_stage(name, status, path)
        return self
    
    def transition(self, from_stage: str, to_stage: str, 
                  condition: Optional[Callable] = None) -> 'PipelineBuilder':
        self.pipeline.add_transition(from_stage, to_stage, condition)
        return self
    
    def on_enter(self, stage: str, handler: Callable[[Job], None]) -> 'PipelineBuilder':
        self.pipeline.stage_handlers[stage] = handler
        return self
    
    def build(self) -> Pipeline:
        return self.pipeline


# ============ Usage Examples ============

def example_simple_approval_flow():
    """Simple approval flow example."""
    # Get queue and job
    queue = q("research")
    job = queue.create_job(
        "analyze_data",
        "researcher@uni.edu",
        "data_owner@company.com"
    )
    
    # Simple progression
    approve_job(job, approver="data_owner@company.com", notes="Approved for research")
    start_job(job, runner="compute_node_1")
    complete_job(job, output_path="/results/analysis_001", metrics={"rows_processed": 1000000})


def example_complex_ml_pipeline():
    """Complex ML pipeline example."""
    # Define pipeline
    ml_pipeline = (PipelineBuilder("ml_training")
        .stage("data_validation", JobStatus.inbox)
        .stage("approved", JobStatus.approved)
        .stage("preprocessing", JobStatus.running)
        .stage("training", JobStatus.running)
        .stage("evaluation", JobStatus.running)
        .stage("deployed", JobStatus.completed)
        .transition("data_validation", "approved",
                   condition=lambda j: validate_data_schema(j))
        .transition("approved", "preprocessing")
        .transition("preprocessing", "training",
                   condition=lambda j: j.output_folder is not None)
        .transition("training", "evaluation")
        .transition("evaluation", "deployed",
                   condition=lambda j: check_model_performance(j))
        .on_enter("preprocessing", lambda j: print(f"Starting preprocessing for {j.name}"))
        .on_enter("training", lambda j: allocate_gpu_resources(j))
        .on_enter("deployed", lambda j: register_model_endpoint(j))
        .build()
    )
    
    # Process job through pipeline
    job = queue.create_job("train_model_v2", "ml@company.com", "data@company.com")
    
    # Validate and approve
    if ml_pipeline.advance(job):  # data_validation -> approved
        print("Data validation passed")
    
    # Continue processing
    while not job.is_terminal:
        if not ml_pipeline.advance(job):
            print(f"Job stuck at stage: {ml_pipeline.get_job_stage(job)}")
            break
        print(f"Job advanced to: {ml_pipeline.get_job_stage(job)}")


def example_review_queue_batch_operations():
    """Batch operations for review queue."""
    queue = q("review_queue")
    
    # Get all inbox jobs
    inbox_jobs = queue.list_jobs(JobStatus.inbox)
    
    # Auto-approve jobs from trusted sources
    trusted_domains = ["@university.edu", "@research.org"]
    
    approved = advance_jobs(
        inbox_jobs,
        JobStatus.approved,
        condition=lambda j: any(j.requester_email.endswith(domain) for domain in trusted_domains)
    )
    
    print(f"Auto-approved {len(approved)} jobs from trusted sources")
    
    # Reject jobs missing required information
    rejected = []
    for job in inbox_jobs:
        if not job.code_folder or not job.description:
            reject_job(job, "Missing required information: code_folder or description")
            rejected.append(job)
    
    print(f"Rejected {len(rejected)} incomplete jobs")


# ============ Helper Functions ============

def validate_data_schema(job: Job) -> bool:
    """Example validation function."""
    # Check if job has required data schema
    return job.code_folder is not None


def check_model_performance(job: Job) -> bool:
    """Example performance check function."""
    # Check if model metrics meet threshold
    if hasattr(job, 'transition_metadata'):
        metrics = job.transition_metadata.get('evaluation', {}).get('metrics', {})
        return metrics.get('accuracy', 0) > 0.9
    return False


def allocate_gpu_resources(job: Job):
    """Example resource allocation function."""
    print(f"Allocating GPU for job {job.uid}")


def register_model_endpoint(job: Job):
    """Example deployment function."""
    print(f"Registering model endpoint for job {job.uid}")


if __name__ == "__main__":
    print("SyftQueue Pipeline API Examples")
    print("=" * 50)
    
    # These would run if we had a real queue
    # example_simple_approval_flow()
    # example_complex_ml_pipeline()
    # example_review_queue_batch_operations()