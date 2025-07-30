"""
Fixed tests for pipeline.py to improve coverage
"""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from syft_queue import q, Job, JobStatus
from syft_queue.pipeline import (
    Pipeline, PipelineStage, PipelineTransition
)


def test_pipeline_stage_enum():
    """Test PipelineStage enum values."""
    assert PipelineStage.INBOX.value == "inbox"
    assert PipelineStage.REVIEW.value == "approved"
    assert PipelineStage.PROCESSING.value == "running"
    assert PipelineStage.COMPLETED.value == "completed"
    assert PipelineStage.FAILED.value == "failed"
    assert PipelineStage.REJECTED.value == "rejected"


def test_pipeline_transition():
    """Test PipelineTransition class."""
    # Basic transition
    transition = PipelineTransition(
        from_stage="inbox",
        to_stage="review"
    )
    
    # Test is_valid_for
    mock_job = MagicMock()
    assert transition.is_valid_for(mock_job, "inbox") is True
    assert transition.is_valid_for(mock_job, "review") is False
    
    # Test with condition
    def condition(job):
        return hasattr(job, 'priority') and job.priority == 'high'
    
    conditional_transition = PipelineTransition(
        from_stage="inbox",
        to_stage="review",
        condition=condition
    )
    
    mock_job.priority = 'low'
    assert conditional_transition.is_valid_for(mock_job, "inbox") is False
    
    mock_job.priority = 'high'
    assert conditional_transition.is_valid_for(mock_job, "inbox") is True
    
    # Test execute with hook
    hook_called = False
    def hook(job):
        nonlocal hook_called
        hook_called = True
    
    transition_with_hook = PipelineTransition(
        from_stage="inbox",
        to_stage="review",
        on_transition=hook
    )
    
    transition_with_hook.execute(mock_job)
    assert hook_called is True


def test_pipeline_creation():
    """Test Pipeline creation and stage management."""
    pipeline = Pipeline("test_pipeline")
    
    assert pipeline.name == "test_pipeline"
    assert len(pipeline.stages) == 0
    assert len(pipeline.transitions) == 0
    
    # Test adding stages
    pipeline.add_stage("inbox", JobStatus.inbox)
    pipeline.add_stage("review", JobStatus.approved)
    pipeline.add_stage("processing", JobStatus.running)
    pipeline.add_stage("completed", JobStatus.completed)
    
    assert len(pipeline.stages) == 4
    assert pipeline.stages["inbox"] == JobStatus.inbox
    assert pipeline.stages["review"] == JobStatus.approved
    
    # Test adding transitions
    pipeline.add_transition("inbox", "review")
    pipeline.add_transition("review", "processing")
    pipeline.add_transition("processing", "completed")
    
    assert len(pipeline.transitions) == 3


def test_pipeline_with_base_path(tmp_path):
    """Test Pipeline with base path and stage paths."""
    pipeline = Pipeline("path_pipeline", base_path=tmp_path)
    
    assert pipeline.base_path == tmp_path
    
    # Add stages - they should get paths automatically
    pipeline.add_stage("inbox", JobStatus.inbox)
    pipeline.add_stage("review", JobStatus.approved)
    
    assert pipeline.stage_paths["inbox"] == tmp_path / "inbox"
    assert pipeline.stage_paths["review"] == tmp_path / "review"


def test_pipeline_stage_handlers():
    """Test Pipeline stage handlers."""
    pipeline = Pipeline("handler_pipeline")
    
    handler_called = False
    def test_handler(job):
        nonlocal handler_called
        handler_called = True
    
    # Add stage with handler
    pipeline.add_stage("processing", JobStatus.running, handler=test_handler)
    
    assert "processing" in pipeline.stage_handlers
    assert pipeline.stage_handlers["processing"] == test_handler


def test_pipeline_job_stage_detection(mock_syftbox_env):
    """Test pipeline job stage detection."""
    pipeline = Pipeline("stage_test")
    pipeline.add_stage("inbox", JobStatus.inbox)
    pipeline.add_stage("review", JobStatus.approved)
    pipeline.add_stage("processing", JobStatus.running)
    
    # Create a job
    queue = q("stage_test_queue")
    job = queue.create_job("test_job", "user@test.com", "owner@test.com")
    
    # Test stage detection based on status
    stage = pipeline.get_job_stage(job)
    assert stage == "inbox"  # Job starts in inbox status
    
    # Change job status
    job.status = JobStatus.approved
    stage = pipeline.get_job_stage(job)
    assert stage == "review"
    
    # Test with pipeline_stage attribute
    job.pipeline_stage = "custom_stage"
    stage = pipeline.get_job_stage(job)
    assert stage == "custom_stage"  # Should use explicit pipeline_stage


def test_pipeline_advancement_errors():
    """Test Pipeline advancement error cases."""
    pipeline = Pipeline("error_test")
    pipeline.add_stage("inbox", JobStatus.inbox)
    
    # Create mock job
    mock_job = MagicMock()
    mock_job.status = JobStatus.completed  # Not in any pipeline stage
    
    # Mock get_job_stage to return None
    with patch.object(pipeline, 'get_job_stage', return_value=None):
        with pytest.raises(ValueError, match="not in any pipeline stage"):
            pipeline.advance(mock_job)


def test_pipeline_transition_validation():
    """Test Pipeline transition validation."""
    pipeline = Pipeline("validation_test")
    pipeline.add_stage("inbox", JobStatus.inbox)
    
    # Test adding transition to unknown stage
    with pytest.raises(ValueError, match="Unknown stage: unknown"):
        pipeline.add_transition("inbox", "unknown")
    
    with pytest.raises(ValueError, match="Unknown stage: unknown"):
        pipeline.add_transition("unknown", "inbox")


def test_pipeline_conditional_transitions():
    """Test Pipeline with conditional transitions."""
    pipeline = Pipeline("conditional_test")
    
    # Add stages
    pipeline.add_stage("inbox", JobStatus.inbox)
    pipeline.add_stage("review", JobStatus.approved)
    pipeline.add_stage("fast_track", JobStatus.running)
    pipeline.add_stage("completed", JobStatus.completed)
    
    # Add conditional transitions
    def is_high_priority(job):
        return getattr(job, 'priority', 'normal') == 'high'
    
    pipeline.add_transition("inbox", "review")
    pipeline.add_transition("inbox", "fast_track", condition=is_high_priority)
    pipeline.add_transition("review", "completed")
    pipeline.add_transition("fast_track", "completed")
    
    # Test with mock jobs
    normal_job = MagicMock()
    normal_job.status = JobStatus.inbox
    normal_job.priority = 'normal'
    
    high_priority_job = MagicMock()
    high_priority_job.status = JobStatus.inbox
    high_priority_job.priority = 'high'
    
    # Mock get_job_stage
    with patch.object(pipeline, 'get_job_stage', return_value="inbox"):
        with patch.object(pipeline, '_execute_transition'):
            # Normal job should go to review
            result = pipeline.advance(normal_job)
            assert result is True
            
            # High priority job should have option for both paths
            # When no specific stage is requested, first valid transition is used
            result = pipeline.advance(high_priority_job)
            assert result is True
            
            # High priority job can be directed to fast_track
            result = pipeline.advance(high_priority_job, to_stage="fast_track")
            assert result is True


def test_pipeline_transition_hooks():
    """Test Pipeline transition hooks."""
    pipeline = Pipeline("hook_test")
    
    # Add stages
    pipeline.add_stage("inbox", JobStatus.inbox)
    pipeline.add_stage("review", JobStatus.approved)
    
    # Track hook calls
    hook_calls = []
    
    def transition_hook(job):
        hook_calls.append(f"transitioned {job.name}")
    
    # Add transition with hook
    pipeline.add_transition("inbox", "review", on_transition=transition_hook)
    
    # Create mock job
    mock_job = MagicMock()
    mock_job.name = "test_job"
    mock_job.status = JobStatus.inbox
    
    # Mock methods
    with patch.object(pipeline, 'get_job_stage', return_value="inbox"):
        with patch.object(pipeline, '_execute_transition'):
            result = pipeline.advance(mock_job)
            assert result is True
            assert len(hook_calls) == 1
            assert "transitioned test_job" in hook_calls[0]


def test_pipeline_no_valid_transitions():
    """Test Pipeline when no valid transitions exist."""
    pipeline = Pipeline("no_transition_test")
    
    # Add stage with no outgoing transitions
    pipeline.add_stage("terminal", JobStatus.completed)
    
    mock_job = MagicMock()
    mock_job.status = JobStatus.completed
    
    with patch.object(pipeline, 'get_job_stage', return_value="terminal"):
        result = pipeline.advance(mock_job)
        assert result is False


def test_pipeline_specific_stage_transition_not_found():
    """Test Pipeline when specific stage transition is not valid."""
    pipeline = Pipeline("specific_test")
    
    # Add stages
    pipeline.add_stage("inbox", JobStatus.inbox)
    pipeline.add_stage("review", JobStatus.approved)
    pipeline.add_stage("processing", JobStatus.running)
    
    # Add only one transition
    pipeline.add_transition("inbox", "review")
    
    mock_job = MagicMock()
    mock_job.status = JobStatus.inbox
    
    with patch.object(pipeline, 'get_job_stage', return_value="inbox"):
        # Should fail when trying to go to processing (no direct transition)
        result = pipeline.advance(mock_job, to_stage="processing")
        assert result is False


def test_pipeline_execute_transition():
    """Test Pipeline _execute_transition method."""
    pipeline = Pipeline("execute_test")
    
    # Add stages
    pipeline.add_stage("inbox", JobStatus.inbox)
    pipeline.add_stage("review", JobStatus.approved)
    
    # Create mock job
    mock_job = MagicMock()
    mock_job.status = JobStatus.inbox
    
    # Execute transition
    pipeline._execute_transition(mock_job, "inbox", "review")
    
    # Check that job status was updated
    assert mock_job.status == JobStatus.approved
    assert mock_job.pipeline_stage == "review"
    
    # Check that methods were called
    mock_job.update_relative_paths.assert_called_once()
    mock_job._update_syft_object.assert_called_once()


def test_pipeline_execute_transition_with_paths(tmp_path):
    """Test Pipeline _execute_transition with path movement."""
    pipeline = Pipeline("path_move_test", base_path=tmp_path)
    
    # Add stages with paths
    pipeline.add_stage("inbox", JobStatus.inbox)
    pipeline.add_stage("review", JobStatus.approved)
    
    # Create actual directories and files to simulate real scenario
    inbox_dir = tmp_path / "inbox"
    review_dir = tmp_path / "review"
    inbox_dir.mkdir()
    review_dir.mkdir()
    
    job_uid = "test-job-123"
    job_path = inbox_dir / job_uid
    job_path.mkdir()
    (job_path / "test_file.txt").write_text("test content")
    
    # Create mock job
    mock_job = MagicMock()
    mock_job.uid = job_uid
    mock_job.object_path = job_path
    
    # Execute transition
    pipeline._execute_transition(mock_job, "inbox", "review")
    
    # Check that directory was moved
    old_path = inbox_dir / job_uid
    new_path = review_dir / job_uid
    
    assert not old_path.exists()
    assert new_path.exists()
    assert (new_path / "test_file.txt").exists()
    
    # Check that job path was updated
    assert mock_job.object_path == new_path
    assert mock_job.base_path == str(new_path)