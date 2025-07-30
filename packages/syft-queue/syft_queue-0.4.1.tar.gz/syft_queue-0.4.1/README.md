# SyftQueue

A portable queue system for SyftBox that manages jobs across datasites with built-in support for relative paths and pipeline progression.

## Features

- **Simple API**: Create and manage job queues with just `q("queue_name")`
- **Portable Jobs**: Jobs are self-contained folders with `run.sh` as the entry point
- **Relative Path Support**: Jobs maintain file references when moved between stages
- **Pipeline Progression**: Built-in API for advancing jobs through lifecycle stages
- **Native Integration**: Uses syft-objects for storage and permissions
- **Cross-Datasite**: Submit jobs between different SyftBox datasites

## Installation

```bash
pip install syft-queue
```

Or install from source:

```bash
git clone https://github.com/OpenMined/syft-queue.git
cd syft-queue
pip install -e .
```

## Quick Start

### Creating a Queue and Job

```python
from syft_queue import q

# Create or get a queue
queue = q("analysis_queue")

# Create a job
job = queue.create_job(
    name="data_analysis",
    requester_email="researcher@university.edu",
    target_email="data_owner@hospital.org",
    code_folder="./my_analysis_code"
)
```

### Job Structure

Jobs are simple folders containing:
- `run.sh` - The entry point script
- Any supporting files/folders the script needs

Example job structure:
```
my_analysis/
├── run.sh          # #!/bin/bash
│                   # python analyze.py data.csv
├── analyze.py
├── requirements.txt
└── data.csv
```

### Pipeline Progression

```python
from syft_queue import approve, start, complete

# Progress job through stages
approve(job, approver="data_owner@hospital.org")
start(job, runner="compute-node-1")

# After execution
complete(job, 
    output_path="results/",
    metrics={"runtime": 3600, "success": True}
)
```

### Batch Operations

```python
from syft_queue import process_queue

# Auto-process queue with rules
results = process_queue(
    queue,
    auto_approve=lambda job: job.requester_email.endswith("@trusted.org"),
    auto_reject=lambda job: "No code" if not job.code_folder else None
)
```

## Core Concepts

### Job Lifecycle

Jobs progress through these statuses:
1. **inbox** - Newly submitted, awaiting review
2. **approved** - Approved, waiting for resources
3. **running** - Currently executing
4. **completed** - Successfully finished
5. **failed** - Execution failed
6. **rejected** - Denied by reviewer
7. **timedout** - Exceeded time limit

### Relative Path Support

Jobs automatically maintain relative paths when moved:

```python
# Create job with relative path support (default)
job = queue.create_job(
    name="portable_job",
    code_folder="./code",
    use_relative_paths=True  # Default
)

# Job can be moved between stages/systems and paths still work
```

### Execution Environment

When jobs run, they receive these environment variables:
- `JOB_UID` - Unique job identifier
- `JOB_NAME` - Human-readable job name
- `JOB_DIR` - Job's working directory
- `CODE_PATH` - Path to code folder
- `OUTPUT_PATH` - Where to write outputs

## Advanced Usage

### Custom Approval Logic

```python
def review_job(job):
    """Custom job review logic"""
    if not job.code_folder:
        return reject(job, "Missing code")
    
    if "sensitive" in job.description:
        return reject(job, "Contains sensitive keywords")
    
    if job.requester_email.endswith("@university.edu"):
        return approve(job, approver="auto-system")
    
    # Needs manual review
    return None

# Apply to all inbox jobs
for job in queue.list_jobs(JobStatus.inbox):
    review_job(job)
```

### Pipeline Builder (Extended API)

```python
from syft_queue import PipelineBuilder

pipeline = (PipelineBuilder("ml_pipeline")
    .stage("validation", JobStatus.inbox)
    .stage("preprocessing", JobStatus.running)
    .stage("training", JobStatus.running)
    .stage("deployment", JobStatus.completed)
    .transition("validation", "preprocessing",
               condition=lambda j: validate_data(j))
    .transition("preprocessing", "training")
    .transition("training", "deployment",
               condition=lambda j: check_accuracy(j) > 0.9)
    .build()
)

# Process job through pipeline
pipeline.advance(job)
```

## API Reference

### Queue Management

- `q(name)` - Create or get a queue
- `list_queues()` - List all queues
- `get_queue(name)` - Get existing queue

### Job Operations

- `queue.create_job(...)` - Create new job
- `queue.get_job(uid)` - Get job by ID
- `queue.list_jobs(status)` - List jobs by status

### Job Progression

- `approve(job, approver, notes)` - Approve job
- `reject(job, reason, reviewer)` - Reject job
- `start(job, runner)` - Start execution
- `complete(job, output_path, metrics)` - Mark complete
- `fail(job, error, exit_code)` - Mark failed
- `advance(job, to_status)` - Progress to next/specific status

### Batch Operations

- `approve_all(jobs, condition)` - Approve multiple jobs
- `process_queue(queue, auto_approve, auto_reject)` - Process with rules

## Examples

See the `examples/` directory for:
- `basic_usage.py` - Simple queue operations
- `pipeline_progression.py` - Using the progression API
- `portable_jobs.py` - Job portability demos
- `batch_processing.py` - Processing multiple jobs

## Development

### Setup Development Environment

```bash
git clone https://github.com/OpenMined/syft-queue.git
cd syft-queue
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Style

```bash
black src/
ruff check src/
mypy src/
```

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

- 📧 Email: contact@openmined.org
- 💬 Slack: [Join #syftbox channel](https://openmined.slack.com)
- 🐛 Issues: [GitHub Issues](https://github.com/OpenMined/syft-queue/issues)