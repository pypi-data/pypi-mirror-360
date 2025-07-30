"""
Tests for pipeline.py to improve coverage
"""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from syft_queue import q, Job, JobStatus
from syft_queue.pipeline import (
    Pipeline, PipelineBuilder, PipelineStage, PipelineTransition
)


def test_pipeline_transition():
    """Test PipelineTransition class."""
    # Basic transition
    transition = PipelineTransition(
        from_stage=PipelineStage.INBOX,
        to_stage=PipelineStage.REVIEW
    )
    
    # Test is_valid_for
    mock_job = MagicMock()
    assert transition.is_valid_for(mock_job, PipelineStage.INBOX) is True
    assert transition.is_valid_for(mock_job, PipelineStage.REVIEW) is False
    
    # Test with condition
    def condition(job):
        return hasattr(job, 'priority') and job.priority == 'high'
    
    conditional_transition = PipelineTransition(
        from_stage=PipelineStage.INBOX,
        to_stage=PipelineStage.REVIEW,
        condition=condition
    )
    
    mock_job.priority = 'low'
    assert conditional_transition.is_valid_for(mock_job, PipelineStage.INBOX) is False
    
    mock_job.priority = 'high'
    assert conditional_transition.is_valid_for(mock_job, PipelineStage.INBOX) is True
    
    # Test execute with hook
    hook_called = False
    def hook(job):
        nonlocal hook_called
        hook_called = True
    
    transition_with_hook = PipelineTransition(
        from_stage=PipelineStage.INBOX,
        to_stage=PipelineStage.REVIEW,
        on_transition=hook
    )
    
    transition_with_hook.execute(mock_job)
    assert hook_called is True


def test_pipeline_builder(mock_syftbox_env):
    """Test PipelineBuilder class."""
    builder = PipelineBuilder("test_pipeline")
    
    # Test adding stages
    builder.add_stage(PipelineStage.INBOX)
    builder.add_stage(PipelineStage.REVIEW)
    builder.add_stage(PipelineStage.PROCESSING)
    builder.add_stage(PipelineStage.COMPLETED)
    
    # Test adding transitions
    builder.add_transition(PipelineStage.INBOX, PipelineStage.REVIEW)
    builder.add_transition(PipelineStage.REVIEW, PipelineStage.PROCESSING)
    builder.add_transition(PipelineStage.PROCESSING, PipelineStage.COMPLETED)
    
    # Test adding transition with condition
    def high_priority_only(job):
        return getattr(job, 'priority', None) == 'high'
    
    builder.add_transition(
        PipelineStage.INBOX,
        PipelineStage.PROCESSING,
        condition=high_priority_only
    )
    
    # Test adding transition with hook
    def log_transition(job):
        job.transition_logged = True
    
    builder.add_transition(
        PipelineStage.REVIEW,
        PipelineStage.REJECTED,
        on_transition=log_transition
    )
    
    # Build pipeline
    pipeline = builder.build()
    
    assert isinstance(pipeline, Pipeline)
    assert pipeline.name == "test_pipeline"
    assert len(pipeline.stages) == 4
    assert len(pipeline.transitions) == 5


def test_pipeline_creation_from_dict(mock_syftbox_env):
    """Test creating pipeline from dictionary configuration."""
    config = {
        "name": "approval_pipeline",
        "stages": ["inbox", "review", "approved", "completed"],
        "transitions": [
            {"from": "inbox", "to": "review"},
            {"from": "review", "to": "approved"},
            {"from": "approved", "to": "completed"},
            {"from": "review", "to": "rejected"}
        ]
    }
    
    pipeline = Pipeline.from_dict(config)
    
    assert pipeline.name == "approval_pipeline"
    assert len(pipeline.stages) == 4
    assert len(pipeline.transitions) == 4


def test_pipeline_job_operations(mock_syftbox_env):
    """Test pipeline operations with jobs."""
    # Create pipeline
    builder = PipelineBuilder("test_ops")
    builder.add_stage(PipelineStage.INBOX)
    builder.add_stage(PipelineStage.REVIEW)
    builder.add_stage(PipelineStage.PROCESSING)
    builder.add_stage(PipelineStage.COMPLETED)
    builder.add_stage(PipelineStage.REJECTED)
    
    builder.add_transition(PipelineStage.INBOX, PipelineStage.REVIEW)
    builder.add_transition(PipelineStage.REVIEW, PipelineStage.PROCESSING)
    builder.add_transition(PipelineStage.REVIEW, PipelineStage.REJECTED)
    builder.add_transition(PipelineStage.PROCESSING, PipelineStage.COMPLETED)
    
    pipeline = builder.build()
    
    # Create queue and job
    queue = q("pipeline_test")
    job = queue.create_job("test_job", "user@test.com", "owner@test.com")
    
    # Test can_advance
    assert pipeline.can_advance(job) is True
    
    # Test get_next_stages
    next_stages = pipeline.get_next_stages(job)
    assert PipelineStage.REVIEW in next_stages
    
    # Test advance
    advanced_job = pipeline.advance(job)
    assert advanced_job.status == JobStatus.approved  # REVIEW maps to approved
    
    # Test advance with specific stage
    job2 = queue.create_job("test_job2", "user@test.com", "owner@test.com")
    rejected_job = pipeline.advance(job2, to_stage=PipelineStage.REJECTED)
    assert rejected_job.status == JobStatus.rejected
    
    # Test invalid advance
    completed_job = queue.create_job("completed", "user@test.com", "owner@test.com")
    completed_job.update_status(JobStatus.completed)
    
    with pytest.raises(ValueError):
        pipeline.advance(completed_job)


def test_pipeline_bulk_operations(mock_syftbox_env):
    """Test pipeline bulk operations."""
    # Create pipeline
    pipeline = Pipeline.from_dict({
        "name": "bulk_pipeline",
        "stages": ["inbox", "approved", "completed"],
        "transitions": [
            {"from": "inbox", "to": "approved"},
            {"from": "approved", "to": "completed"}
        ]
    })
    
    # Create queue and jobs
    queue = q("bulk_test")
    jobs = []
    for i in range(5):
        job = queue.create_job(f"job_{i}", "user@test.com", "owner@test.com")
        jobs.append(job)
    
    # Test bulk advance
    advanced_jobs = pipeline.advance_all(jobs)
    assert len(advanced_jobs) == 5
    assert all(job.status == JobStatus.approved for job in advanced_jobs)
    
    # Test bulk advance with filter
    job6 = queue.create_job("special", "vip@test.com", "owner@test.com")
    jobs.append(job6)
    
    filtered_advance = pipeline.advance_all(
        jobs,
        filter_fn=lambda j: "vip" in j.requester_email
    )
    assert len(filtered_advance) == 1
    assert filtered_advance[0].name == "test_J:special"


def test_pipeline_stage_tracking(mock_syftbox_env):
    """Test pipeline stage tracking and history."""
    pipeline = Pipeline.from_dict({
        "name": "tracking_pipeline",
        "stages": ["inbox", "review", "processing", "completed"],
        "transitions": [
            {"from": "inbox", "to": "review"},
            {"from": "review", "to": "processing"},
            {"from": "processing", "to": "completed"}
        ]
    })
    
    queue = q("tracking_test")
    job = queue.create_job("tracked_job", "user@test.com", "owner@test.com")
    
    # Advance through stages
    job = pipeline.advance(job)  # -> review
    assert pipeline.get_current_stage(job) == PipelineStage.REVIEW
    
    job = pipeline.advance(job)  # -> processing
    assert pipeline.get_current_stage(job) == PipelineStage.PROCESSING
    
    job = pipeline.advance(job)  # -> completed
    assert pipeline.get_current_stage(job) == PipelineStage.COMPLETED


def test_pipeline_with_conditions(mock_syftbox_env):
    """Test pipeline with conditional transitions."""
    builder = PipelineBuilder("conditional_pipeline")
    
    # Add stages
    builder.add_stage(PipelineStage.INBOX)
    builder.add_stage(PipelineStage.REVIEW)
    builder.add_stage(PipelineStage.QUALITY_CHECK)
    builder.add_stage(PipelineStage.COMPLETED)
    builder.add_stage(PipelineStage.FAILED)
    
    # Add conditional transitions
    def needs_quality_check(job):
        return getattr(job, 'requires_qc', False)
    
    def quality_passed(job):
        return getattr(job, 'qc_passed', True)
    
    builder.add_transition(PipelineStage.INBOX, PipelineStage.REVIEW)
    builder.add_transition(
        PipelineStage.REVIEW,
        PipelineStage.QUALITY_CHECK,
        condition=needs_quality_check
    )
    builder.add_transition(
        PipelineStage.REVIEW,
        PipelineStage.COMPLETED,
        condition=lambda job: not needs_quality_check(job)
    )
    builder.add_transition(
        PipelineStage.QUALITY_CHECK,
        PipelineStage.COMPLETED,
        condition=quality_passed
    )
    builder.add_transition(
        PipelineStage.QUALITY_CHECK,
        PipelineStage.FAILED,
        condition=lambda job: not quality_passed(job)
    )
    
    pipeline = builder.build()
    
    # Test job that doesn't need QC
    queue = q("conditional_test")
    job1 = queue.create_job("no_qc", "user@test.com", "owner@test.com")
    job1.requires_qc = False
    
    job1 = pipeline.advance(job1)  # -> review
    job1 = pipeline.advance(job1)  # -> completed (skips QC)
    assert job1.status == JobStatus.completed
    
    # Test job that needs QC and passes
    job2 = queue.create_job("with_qc", "user@test.com", "owner@test.com")
    job2.requires_qc = True
    job2.qc_passed = True
    
    job2 = pipeline.advance(job2)  # -> review
    job2 = pipeline.advance(job2)  # -> quality_check
    assert job2.status == JobStatus.running  # QC maps to running
    job2 = pipeline.advance(job2)  # -> completed
    assert job2.status == JobStatus.completed
    
    # Test job that needs QC and fails
    job3 = queue.create_job("qc_fail", "user@test.com", "owner@test.com")
    job3.requires_qc = True
    job3.qc_passed = False
    
    job3 = pipeline.advance(job3)  # -> review
    job3 = pipeline.advance(job3)  # -> quality_check
    job3 = pipeline.advance(job3)  # -> failed
    assert job3.status == JobStatus.failed


def test_pipeline_hooks(mock_syftbox_env):
    """Test pipeline transition hooks."""
    hook_calls = []
    
    def log_hook(job):
        hook_calls.append(f"Transitioned: {job.name}")
    
    def email_hook(job):
        job.email_sent = True
    
    builder = PipelineBuilder("hook_pipeline")
    builder.add_stage(PipelineStage.INBOX)
    builder.add_stage(PipelineStage.REVIEW)
    builder.add_stage(PipelineStage.COMPLETED)
    
    builder.add_transition(
        PipelineStage.INBOX,
        PipelineStage.REVIEW,
        on_transition=log_hook
    )
    builder.add_transition(
        PipelineStage.REVIEW,
        PipelineStage.COMPLETED,
        on_transition=email_hook
    )
    
    pipeline = builder.build()
    
    queue = q("hook_test")
    job = queue.create_job("hooked_job", "user@test.com", "owner@test.com")
    
    # First transition
    job = pipeline.advance(job)
    assert len(hook_calls) == 1
    assert "J:hooked_job" in hook_calls[0]
    
    # Second transition
    job = pipeline.advance(job)
    assert hasattr(job, 'email_sent')
    assert job.email_sent is True


def test_pipeline_error_handling(mock_syftbox_env):
    """Test pipeline error conditions."""
    # Test empty pipeline
    empty_pipeline = Pipeline("empty", [], [])
    
    queue = q("error_test")
    job = queue.create_job("test_job", "user@test.com", "owner@test.com")
    
    with pytest.raises(ValueError):
        empty_pipeline.advance(job)
    
    # Test invalid stage mapping
    builder = PipelineBuilder("invalid")
    builder.add_stage("INVALID_STAGE")  # Not a valid PipelineStage
    
    with pytest.raises(AttributeError):
        builder.build()
    
    # Test circular transitions
    circular_builder = PipelineBuilder("circular")
    circular_builder.add_stage(PipelineStage.INBOX)
    circular_builder.add_stage(PipelineStage.REVIEW)
    circular_builder.add_transition(PipelineStage.INBOX, PipelineStage.REVIEW)
    circular_builder.add_transition(PipelineStage.REVIEW, PipelineStage.INBOX)
    
    circular_pipeline = circular_builder.build()
    
    job2 = queue.create_job("circular_job", "user@test.com", "owner@test.com")
    job2 = circular_pipeline.advance(job2)  # -> review
    job2 = circular_pipeline.advance(job2)  # -> inbox (circular)
    assert job2.status == JobStatus.inbox


def test_pipeline_custom_stages():
    """Test pipeline with custom stage mappings."""
    # Create custom pipeline with non-standard flow
    config = {
        "name": "custom_pipeline",
        "stages": ["inbox", "processing", "review", "completed"],
        "transitions": [
            {"from": "inbox", "to": "processing"},  # Skip approval
            {"from": "processing", "to": "review"},  # Review after processing
            {"from": "review", "to": "completed"}
        ]
    }
    
    pipeline = Pipeline.from_dict(config)
    
    # Verify stage order is preserved
    assert pipeline.stages[0] == PipelineStage.INBOX
    assert pipeline.stages[1] == PipelineStage.PROCESSING
    assert pipeline.stages[2] == PipelineStage.REVIEW
    assert pipeline.stages[3] == PipelineStage.COMPLETED