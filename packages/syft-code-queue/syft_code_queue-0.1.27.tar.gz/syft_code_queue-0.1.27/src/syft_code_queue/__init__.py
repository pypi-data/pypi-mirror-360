"""
syft-code-queue: Simple code execution queue for SyftBox.

This package provides a lightweight way to submit code for execution on remote datasites.
Code is submitted as folders containing a run.sh script, and executed by SyftBox apps.

Architecture:
- Code is submitted using the unified API
- Jobs are stored in SyftBox app data directories
- SyftBox periodically calls run.sh which processes the queue
- No long-running server processes required

Usage:
    import syft_code_queue as q

    # Submit jobs to others
    job = q.submit_job("data-owner@university.edu", "./my_analysis", "Statistical Analysis")

    # Object-oriented job management
    q.jobs_for_me[0].approve("Looks safe")
    q.jobs_for_others[0].get_logs()
    q.jobs_for_me.pending().approve_all("Batch approval")

    # Functional API still available
    q.pending_for_me()
    q.approve("job-id", "reason")
"""

import sys
from pathlib import Path
from typing import Optional, Union
from uuid import UUID

from loguru import logger

from .client import CodeQueueClient, create_client
from .models import CodeJob, DataSitesCollection, JobCollection, JobStatus, QueueConfig

# Global VERBOSE flag to control logging level
VERBOSE = False


def _configure_logging():
    """Configure logging based on VERBOSE flag."""
    # Remove default logger first
    logger.remove()

    if VERBOSE:
        # Verbose mode: show DEBUG and above
        logger.add(
            sink=lambda msg: print(msg, end=""),
            level="DEBUG",
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        )
    else:
        # Quiet mode: only show WARNING and above
        logger.add(
            sink=lambda msg: print(msg, end=""),
            level="WARNING",
            format="<level>{level}</level>: {message}",
        )


def set_verbose(enabled: bool):
    """Set verbose logging on or off."""
    global VERBOSE
    VERBOSE = enabled
    _configure_logging()


# Configure logging on import
_configure_logging()

# Runner components moved to syft-simple-runner package
# App execution moved to syft-simple-runner package
from syft_core import Client as SyftBoxClient


class UnifiedAPI:
    """
    Unified API for syft-code-queue that handles both job submission and management.

    This provides both object-oriented and functional interfaces:
    - Object-oriented: q.jobs_for_me[0].approve("reason")
    - Functional: q.approve("job-id", "reason")
    """

    def __init__(self, config: Optional[QueueConfig] = None):
        """Initialize the unified API."""
        try:
            self.syftbox_client = SyftBoxClient.load()
            self.config = config or QueueConfig(queue_name="code-queue")
            self.client = CodeQueueClient(syftbox_client=self.syftbox_client, config=self.config)

            logger.info(f"Initialized syft-code-queue API for {self.email}")
        except Exception as e:
            logger.warning(f"Could not initialize syft-code-queue: {e}")
            # Set up in demo mode
            self.syftbox_client = SyftBoxClient()
            self.config = config or QueueConfig(queue_name="code-queue")
            self.client = None

        # Clean up corrupted jobs across all datasites before doing anything else
        self._cleanup_corrupted_jobs()

        # Clean up expired jobs across all datasites
        self._cleanup_expired_jobs()

        # Initialize datasites collection
        self._datasites_collection = None

    def _cleanup_corrupted_jobs(self):
        """Clean up corrupted jobs that only contain folders and syft.pub.yaml files across all datasites."""
        try:
            if not self.syftbox_client:
                return

            datasites_dir = self.syftbox_client.datasites
            if not datasites_dir.exists():
                logger.debug("Datasites directory does not exist, skipping cleanup")
                return

            logger.debug(f"Cleaning up corrupted jobs across all datasites in: {datasites_dir}")
            total_cleaned = 0
            datasites_checked = 0
            datasites_with_queues = 0

            # Iterate through all datasites
            all_datasites = list(datasites_dir.iterdir())
            logger.debug(f"Found {len(all_datasites)} items in datasites directory")

            for datasite_dir in all_datasites:
                if not datasite_dir.is_dir():
                    logger.debug(f"Skipping {datasite_dir.name} - not a directory")
                    continue

                # Check if it's a valid email-like datasite
                if "@" not in datasite_dir.name:
                    logger.debug(f"Skipping {datasite_dir.name} - not an email-like datasite")
                    continue

                datasites_checked += 1
                logger.debug(f"Checking datasite: {datasite_dir.name}")

                try:
                    # Check if this datasite has a code-queue app
                    queue_dir = datasite_dir / "app_data" / self.config.queue_name / "jobs"
                    if not queue_dir.exists():
                        logger.debug(f"No code-queue found at: {queue_dir}")
                        continue

                    datasites_with_queues += 1
                    logger.debug(f"Found code-queue in: {datasite_dir.name}")

                    # Check all status directories in this datasite
                    jobs_found = 0
                    for status in JobStatus:
                        status_dir = queue_dir / status.value
                        if not status_dir.exists():
                            logger.debug(f"No {status.value} directory in {datasite_dir.name}")
                            continue

                        # Check each job directory
                        job_dirs = list(status_dir.iterdir())
                        if job_dirs:
                            logger.debug(
                                f"Found {len(job_dirs)} {status.value} jobs in {datasite_dir.name}"
                            )

                        for job_dir in job_dirs:
                            if not job_dir.is_dir():
                                logger.debug(
                                    f"Skipping {job_dir.name} in {status.value} - not a directory"
                                )
                                continue

                            jobs_found += 1
                            try:
                                logger.debug(
                                    f"Checking job {job_dir.name} in {datasite_dir.name}/{status.value}"
                                )
                                if self._is_corrupted_job(job_dir):
                                    logger.info(
                                        f"🗑️  Removing corrupted {status.value} job: {datasite_dir.name}/{job_dir.name}"
                                    )
                                    import shutil

                                    shutil.rmtree(job_dir)
                                    total_cleaned += 1
                                else:
                                    # Log what we found for debugging
                                    items = list(job_dir.iterdir())
                                    logger.debug(
                                        f"✅ Job {job_dir.name} in {status.value} is valid - {len(items)} items: {[item.name for item in items[:5]]}"
                                    )
                            except Exception as e:
                                logger.warning(f"❌ Could not process job directory {job_dir}: {e}")

                    if jobs_found > 0:
                        logger.info(f"Processed {jobs_found} total jobs in {datasite_dir.name}")
                    else:
                        logger.debug(f"No jobs found in {datasite_dir.name}")

                except Exception as e:
                    logger.warning(f"Error cleaning up datasite {datasite_dir.name}: {e}")
                    continue

            # Final summary
            logger.debug(
                f"Cleanup Summary: Checked {datasites_checked} datasites, {datasites_with_queues} had code-queues"
            )
            if total_cleaned > 0:
                logger.info(f"🗑️  Cleaned up {total_cleaned} corrupted job directories")
            else:
                logger.debug("No corrupted jobs found - all clean!")

        except Exception as e:
            logger.warning(f"Error during job cleanup: {e}")

    def _is_corrupted_job(self, job_dir):
        """Check if a job directory only contains folders and syft.pub.yaml files (indicating corruption)."""
        try:
            # Get all items in the job directory
            items = list(job_dir.iterdir())
            if not items:
                # Empty directory is definitely corrupted
                logger.debug(f"Empty job directory found: {job_dir.name} - marking as corrupted")
                return True

            # Check what types of items we have
            has_actual_files = False
            file_count = 0
            yaml_count = 0
            dir_count = 0
            actual_files = []

            for item in items:
                if item.is_file():
                    file_count += 1
                    # Allow syft.pub.yaml files (they're part of the permission system)
                    if item.name == "syft.pub.yaml":
                        yaml_count += 1
                        continue
                    # If we find any other file, this job has content
                    actual_files.append(item.name)
                    has_actual_files = True
                elif item.is_dir():
                    dir_count += 1
                    # Check if the directory has any actual content (not just more syft.pub.yaml files)
                    if self._directory_has_content(item):
                        has_actual_files = True
                        actual_files.append(f"{item.name}/")

            # If we only found folders and syft.pub.yaml files, it's corrupted
            is_corrupted = not has_actual_files

            if is_corrupted:
                logger.debug(
                    f"Corrupted job detected: {job_dir.name} - {file_count} files ({yaml_count} yaml), {dir_count} dirs, no actual content"
                )
            else:
                logger.debug(f"Valid job: {job_dir.name} - actual files: {actual_files[:3]}")

            return is_corrupted

        except Exception as e:
            logger.warning(f"Error checking if job {job_dir} is corrupted: {e}")
            return False

    def _directory_has_content(self, directory):
        """Recursively check if a directory has any actual content (not just syft.pub.yaml files)."""
        try:
            for item in directory.rglob("*"):
                if item.is_file() and item.name != "syft.pub.yaml":
                    return True
            return False
        except Exception:
            return False

    def _cleanup_expired_jobs(self):
        """Clean up jobs that have exceeded their timeout across all datasites."""
        try:
            if not self.syftbox_client:
                return

            datasites_dir = self.syftbox_client.datasites
            if not datasites_dir.exists():
                logger.debug("Datasites directory does not exist, skipping timeout cleanup")
                return

            logger.debug(f"Cleaning up expired jobs across all datasites in: {datasites_dir}")
            total_expired = 0

            import json
            import shutil
            from datetime import datetime

            from .models import JobStatus

            # Iterate through all datasites
            for datasite_dir in datasites_dir.iterdir():
                if not datasite_dir.is_dir() or "@" not in datasite_dir.name:
                    continue

                try:
                    # Check if this datasite has a code-queue app
                    queue_dir = datasite_dir / "app_data" / self.config.queue_name / "jobs"
                    if not queue_dir.exists():
                        continue

                    # Check non-terminal status directories
                    non_terminal_statuses = [
                        JobStatus.pending,
                        JobStatus.approved,
                        JobStatus.running,
                    ]

                    for status in non_terminal_statuses:
                        status_dir = queue_dir / status.value
                        if not status_dir.exists():
                            continue

                        # Check each job directory
                        for job_dir in status_dir.iterdir():
                            if not job_dir.is_dir():
                                continue

                            try:
                                # Read job metadata to check timeout
                                metadata_file = job_dir / "metadata.json"
                                if not metadata_file.exists():
                                    continue

                                with open(metadata_file) as f:
                                    metadata = json.load(f)

                                # Check if job is expired
                                created_at_str = metadata.get("created_at")
                                timeout_seconds = metadata.get(
                                    "timeout_seconds", 86400
                                )  # Default 24 hours

                                if not created_at_str:
                                    continue

                                try:
                                    created_at = datetime.fromisoformat(created_at_str)
                                except ValueError:
                                    continue

                                now = datetime.now()
                                age_seconds = (now - created_at).total_seconds()

                                if age_seconds > timeout_seconds:
                                    # Job has expired, determine target status
                                    if status == JobStatus.pending:
                                        target_status = JobStatus.rejected
                                        reason = "Job expired - datasite owner did not respond within timeout period"
                                    else:  # approved or running
                                        target_status = JobStatus.failed
                                        reason = "Job expired - execution timeout exceeded"

                                    # Move job to target status directory
                                    target_dir = queue_dir / target_status.value
                                    target_dir.mkdir(exist_ok=True)
                                    target_job_dir = target_dir / job_dir.name

                                    # Update metadata with new status and error message
                                    metadata["status"] = target_status.value
                                    metadata["error_message"] = reason
                                    metadata["updated_at"] = now.isoformat()
                                    if target_status == JobStatus.failed:
                                        metadata["completed_at"] = now.isoformat()

                                    # Write updated metadata to new location
                                    shutil.move(str(job_dir), str(target_job_dir))

                                    # Update metadata in new location
                                    with open(target_job_dir / "metadata.json", "w") as f:
                                        json.dump(metadata, f, indent=2)

                                    logger.info(
                                        f"⏰ Expired job moved: {datasite_dir.name}/{job_dir.name} ({status.value} → {target_status.value})"
                                    )
                                    total_expired += 1

                            except Exception as e:
                                logger.warning(f"Could not process job {job_dir} for timeout: {e}")
                                continue

                except Exception as e:
                    logger.debug(
                        f"Error cleaning up expired jobs in datasite {datasite_dir.name}: {e}"
                    )
                    continue

            if total_expired > 0:
                logger.info(f"⏰ Cleaned up {total_expired} expired jobs")
            else:
                logger.debug("No expired jobs found")

        except Exception as e:
            logger.warning(f"Error during expired job cleanup: {e}")

    @property
    def email(self) -> str:
        """Get the current user's email."""
        return self.syftbox_client.email

    @property
    def datasites(self) -> DataSitesCollection:
        """Get collection of datasites with open code queues."""
        if self._datasites_collection is None:
            self._datasites_collection = DataSitesCollection(syftbox_client=self.syftbox_client)
        return self._datasites_collection

    def _connect_job_apis(self, job: CodeJob) -> CodeJob:
        """Connect a job to the appropriate APIs for method calls."""
        if self.client is not None:
            job._client = self.client
        return job

    def _connect_jobs_apis(self, jobs: list[CodeJob]) -> JobCollection:
        """Connect a list of jobs to the appropriate APIs."""
        connected_jobs = [self._connect_job_apis(job) for job in jobs]
        return JobCollection(connected_jobs)

    def list_jobs(
        self,
        status: Optional[JobStatus] = None,
        target_email: Optional[str] = None,
        limit: int = 50,
        search_all_datasites: bool = False,
    ) -> list[CodeJob]:
        """
        List jobs matching the given criteria.

        Args:
            status: Optional filter by job status
            target_email: Optional filter by target datasite
            limit: Maximum number of jobs to return
            search_all_datasites: If True, search across all datasites instead of just local queue

        Returns:
            List of CodeJob objects matching the criteria
        """
        if self.client is None:
            return []

        jobs = self.client.list_jobs(
            target_email=target_email,
            status=status,
            limit=limit,
            search_all_datasites=search_all_datasites,
        )
        return [self._connect_job_apis(job) for job in jobs]

    # Object-Oriented Properties

    @property
    def jobs_for_others(self) -> JobCollection:
        """Jobs I've submitted to other people."""
        if self.client is None:
            return JobCollection([])
        # Search across all datasites since jobs are stored in target's datasite
        jobs = self.list_jobs(search_all_datasites=True)
        return self._connect_jobs_apis([j for j in jobs if j.requester_email == self.email])

    @property
    def jobs_for_me(self) -> JobCollection:
        """Jobs submitted to me for approval/management."""
        if self.client is None:
            return JobCollection([])
        jobs = self.list_jobs()
        return self._connect_jobs_apis([j for j in jobs if j.target_email == self.email])

    @property
    def my_pending(self) -> JobCollection:
        """Jobs I've submitted that are still pending."""
        return self.jobs_for_others.by_status(JobStatus.pending)

    @property
    def my_running(self) -> JobCollection:
        """Jobs I've submitted that are currently running."""
        return self.jobs_for_others.by_status(JobStatus.running)

    @property
    def my_completed(self) -> JobCollection:
        """Jobs I've submitted that have completed."""
        return self.jobs_for_others.by_status(JobStatus.completed)

    @property
    def pending_for_others(self) -> JobCollection:
        """Jobs I've submitted to others that are still pending approval."""
        return self.jobs_for_others.by_status(JobStatus.pending)

    @property
    def pending_for_me(self) -> JobCollection:
        """Jobs submitted to me that need approval."""
        if self.client is None:
            return JobCollection([])

        # Use the same approach as jobs_for_me but filter by pending status
        jobs = self.list_jobs()
        pending_jobs = [
            j for j in jobs if j.target_email == self.email and j.status == JobStatus.pending
        ]
        return self._connect_jobs_apis(pending_jobs)

    @property
    def approved_by_me(self) -> JobCollection:
        """Jobs I've approved that are running/completed."""
        approved = self.jobs_for_me.by_status(JobStatus.approved)
        running = self.jobs_for_me.by_status(JobStatus.running)
        completed = self.jobs_for_me.by_status(JobStatus.completed)
        all_approved = JobCollection(list(approved) + list(running) + list(completed))
        return all_approved

    # Job Submission (Data Scientist functionality)

    def submit_job(
        self,
        target_email: str,
        code_folder: Union[str, Path],
        name: str,
        description: Optional[str] = None,
        timeout_seconds: int = 86400,  # 24 hours default
        tags: Optional[list[str]] = None,
    ) -> CodeJob:
        """
        Submit a code package for execution on a remote datasite.

        Args:
            target_email: Email of the data owner/datasite
            code_folder: Path to folder containing code and run.sh script
            name: Human-readable name for the job
            description: Optional description of what the job does
            timeout_seconds: Timeout in seconds after which job will be automatically timedout/failed (default: 24 hours)
            tags: Optional tags for categorization (e.g. ["privacy-safe", "aggregate"])

        Returns:
            CodeJob: The submitted job object with API methods attached
        """
        if self.client is None:
            raise RuntimeError("API not properly initialized")
        job = self.client.submit_code(
            target_email, code_folder, name, description, timeout_seconds, tags
        )
        return self._connect_job_apis(job)

    def submit_python(
        self,
        target_email: str,
        script_content: str,
        name: str,
        description: Optional[str] = None,
        requirements: Optional[list[str]] = None,
        timeout_seconds: int = 86400,  # 24 hours default
        tags: Optional[list[str]] = None,
    ) -> CodeJob:
        """
        Create and submit a Python job from script content.

        Args:
            target_email: Email of the data owner/datasite
            script_content: Python script content
            name: Human-readable name for the job
            description: Optional description
            requirements: Optional list of Python packages to install
            timeout_seconds: Timeout in seconds after which job will be automatically timedout/failed (default: 24 hours)
            tags: Optional tags for categorization

        Returns:
            CodeJob: The submitted job object with API methods attached
        """
        if self.client is None:
            raise RuntimeError("API not properly initialized")
        job = self.client.create_python_job(
            target_email, script_content, name, description, requirements, timeout_seconds, tags
        )
        return self._connect_job_apis(job)

    def submit_bash(
        self,
        target_email: str,
        script_content: str,
        name: str,
        description: Optional[str] = None,
        timeout_seconds: int = 86400,  # 24 hours default
        tags: Optional[list[str]] = None,
    ) -> CodeJob:
        """
        Create and submit a bash job from script content.

        Args:
            target_email: Email of the data owner/datasite
            script_content: Bash script content
            name: Human-readable name for the job
            description: Optional description
            timeout_seconds: Timeout in seconds after which job will be automatically timedout/failed (default: 24 hours)
            tags: Optional tags for categorization

        Returns:
            CodeJob: The submitted job object with API methods attached
        """
        if self.client is None:
            raise RuntimeError("API not properly initialized")
        job = self.client.create_bash_job(
            target_email, script_content, name, description, timeout_seconds, tags
        )
        return self._connect_job_apis(job)

    # Legacy Functional API (for backward compatibility)

    def my_jobs(self, status: Optional[JobStatus] = None, limit: int = 50) -> list[CodeJob]:
        """List jobs I've submitted to others (functional API)."""
        if status is None:
            return list(self.jobs_for_others[:limit])
        else:
            return list(self.jobs_for_others.by_status(status)[:limit])

    def get_job(self, job_uid: Union[str, UUID]) -> Optional[CodeJob]:
        """Get a specific job by its UID (functional API)."""
        if self.client is None:
            return None
        job = self.client.get_job(job_uid)
        return self._connect_job_apis(job) if job else None

    def get_job_output(self, job_uid: Union[str, UUID]) -> Optional[Path]:
        """Get the output directory for a completed job (functional API)."""
        if self.client is None:
            return None
        return self.client.get_job_output(job_uid)

    def get_job_logs(self, job_uid: Union[str, UUID]) -> Optional[str]:
        """Get the execution logs for a job (functional API)."""
        if self.client is None:
            return None
        return self.client.get_job_logs(job_uid)

    def wait_for_completion(self, job_uid: Union[str, UUID], timeout: int = 600) -> CodeJob:
        """Wait for a job to complete (functional API)."""
        if self.client is None:
            raise RuntimeError("API not properly initialized")
        job = self.client.wait_for_completion(job_uid, timeout)
        return self._connect_job_apis(job)

    # Legacy Job Management (Data Owner functionality)

    def all_jobs_for_me(self, status: Optional[JobStatus] = None, limit: int = 50) -> list[CodeJob]:
        """List all jobs submitted to me (functional API)."""
        if status is None:
            return list(self.jobs_for_me[:limit])
        else:
            return list(self.jobs_for_me.by_status(status)[:limit])

    def approve(self, job_uid: Union[str, UUID], reason: Optional[str] = None) -> bool:
        """Approve a job for execution (functional API)."""
        if self.client is None:
            return False
        return self.client.approve_job(job_uid, reason)

    def reject(self, job_uid: Union[str, UUID], reason: Optional[str] = None) -> bool:
        """Reject a job (functional API)."""
        if self.client is None:
            return False
        return self.client.reject_job(job_uid, reason)

    def review_job(self, job_uid: Union[str, UUID]) -> Optional[dict]:
        """Get detailed information about a job for review (functional API)."""
        if self.client is None:
            return None

        # Get the job and use its review method
        job = self.client.get_job(str(job_uid))
        if job is None:
            return None

        # Connect APIs and call review
        connected_job = self._connect_job_apis(job)
        return connected_job.review()

    def inspect_job(self, job_uid: Union[str, UUID]) -> None:
        """Print a detailed code review of a job (functional API)."""
        job = self.get_job(job_uid)
        if not job:
            print(f"❌ Job {job_uid} not found")
            return

        print(f"🔍 Code Review for Job: {job.name}")
        print(f"📧 Requested by: {job.requester_email}")
        print(f"📝 Description: {job.description or 'No description provided'}")
        print(f"🏷️ Tags: {job.tags or 'No tags'}")
        print("=" * 60)

        # Get file structure
        files = job.list_files()
        if files:
            print(f"📁 Files in job ({len(files)} total):")
            for file in files:
                print(f"  📄 {file}")
            print()

            # Show run script if it exists
            run_scripts = [f for f in files if f in ["run.sh", "run.py", "run.bash"]]
            if run_scripts:
                for script in run_scripts:
                    print(f"🚀 Execution Script: {script}")
                    print("-" * 40)
                    content = job.read_file(script)
                    if content:
                        print(content)
                    else:
                        print("❌ Could not read script content")
                    print("-" * 40)
                    print()

            # Show other important files
            important_files = [
                f
                for f in files
                if f.endswith((".py", ".txt", ".md", ".yml", ".yaml", ".json", ".csv"))
                and f not in run_scripts
            ]
            if important_files:
                print("📋 Other important files:")
                for file in important_files[:5]:  # Show first 5 files
                    print(f"\n📄 {file}:")
                    print("-" * 30)
                    content = job.read_file(file)
                    if content:
                        lines = content.split("\n")
                        if len(lines) > 20:
                            print("\n".join(lines[:20]))
                            print(f"... ({len(lines) - 20} more lines)")
                        else:
                            print(content)
                    else:
                        print("❌ Could not read file content")
                    print("-" * 30)

                if len(important_files) > 5:
                    print(f"\n... and {len(important_files) - 5} more files")
        else:
            print("❌ No files found in job")

        print("\n" + "=" * 60)
        print("💡 To approve: job.approve('reason')")
        print("💡 To reject: job.reject('reason')")

    def read_job_file(self, job_uid: Union[str, UUID], filename: str) -> Optional[str]:
        """Read a specific file from a job (functional API)."""
        job = self.get_job(job_uid)
        if not job:
            return None
        return job.read_file(filename)

    def list_job_files(self, job_uid: Union[str, UUID]) -> list[str]:
        """List all files in a job (functional API)."""
        job = self.get_job(job_uid)
        if not job:
            return []
        return job.list_files()

    # Status and Summary

    def status(self) -> dict:
        """Get overall status summary."""
        summary = {
            "email": self.email,
            "jobs_submitted_by_me": len(self.jobs_for_others),
            "jobs_submitted_to_me": len(self.jobs_for_me),
            "pending_for_approval": len(self.pending_for_me),
            "my_running_jobs": len(self.my_running),
        }
        return summary

    def refresh(self):
        """Refresh all job data to get latest statuses."""
        # Force refresh by invalidating any cached data
        # The properties will fetch fresh data on next access
        pass

    def help(self):
        """Show focused help for core workflow methods."""
        help_text = f"""
🎯 SyftBox Code Queue v{__version__} - Getting Started Guide

👋 Welcome! SyftBox Code Queue lets you run code on remote datasites securely.

🚀 QUICK START - Your First Job:
  1. Import the queue:
     >>> import syft_code_queue as q
  
  2. Find available datasites:
     >>> q.datasites                    # List all datasites with code queues
     >>> q.datasites.ping()              # Test which datasites are responsive
  
  3. Submit a simple job:
     >>> job = q.submit_python("owner@org.com", '''
     ... import pandas as pd
     ... print("Hello from SyftBox!")
     ... ''', "My First Job")
  
  4. Check job status:
     >>> q.pending_for_others            # See your pending jobs
     >>> job.status                      # Check specific job status
     >>> job.wait_for_completion()       # Wait for job to finish

📡 DataSite Discovery:
  q.datasites                           # Show all datasites with code queues
  q.datasites.responsive_to_me()        # Datasites that have responded to YOUR jobs
  q.datasites.responsive()              # Datasites that have responded to ANYONE
  q.datasites.with_pending_jobs()       # Datasites with jobs awaiting approval
  q.datasites.ping()                    # Send test jobs to all datasites

📤 Submit Jobs (as Data Scientist):
  # Submit a folder with run.sh script:
  q.submit_job("owner@org.com", "./my_analysis", "Statistical Analysis")
  
  # Submit Python code directly:
  q.submit_python("owner@org.com", "print('hello')", "Quick Test")
  
  # Submit bash commands:
  q.submit_bash("owner@org.com", "ls -la", "List Files")

📋 View Your Jobs:
  q.pending_for_me                      # Jobs awaiting YOUR approval (as Data Owner)
  q.pending_for_others                  # Jobs YOU submitted awaiting approval
  q.jobs_for_me                         # ALL jobs submitted to you
  q.jobs_for_others                     # ALL jobs you've submitted
  q.my_running                          # Your currently running jobs
  q.my_completed                        # Your completed jobs

✅ Manage Jobs (as Data Owner):
  # Review and approve/reject:
  job = q.pending_for_me[0]             # Get first pending job
  job.review()                          # See job details and code
  job.approve("Looks safe")             # Approve the job
  job.reject("Too broad access")        # Reject the job
  
  # Batch operations:
  q.pending_for_me.approve_all("Batch approved")

🔍 Monitor Jobs:
  job = q.get_job("job-123abc")         # Get specific job by ID
  job.status                            # Check current status
  job.logs                              # View execution logs
  job.output                            # Access output files
  job.wait_for_completion()             # Block until job finishes

📊 Job Lifecycle:
  submit → pending → approved → running → completed
                 ↘ rejected          ↘ failed/timedout

💡 Pro Tips:
  • Use q.VERBOSE=True for detailed logging
  • Jobs timeout after 24 hours by default
  • All jobs are sandboxed for security
  • Check q.status() for a quick overview

📚 Learn More:
  • Full docs: https://docs.syftbox.com/code-queue
  • Examples: See examples/ folder in the repository
  • Support: https://github.com/syftbox/syft-code-queue/issues
        """
        print(help_text)


# Create global instance
jobs = UnifiedAPI()
q = jobs  # Convenient alias

# Expose key functions at module level for convenience
submit_job = jobs.submit_job
submit_python = jobs.submit_python
submit_bash = jobs.submit_bash
my_jobs = jobs.my_jobs
get_job = jobs.get_job
get_job_output = jobs.get_job_output
get_job_logs = jobs.get_job_logs
wait_for_completion = jobs.wait_for_completion
all_jobs_for_me = jobs.all_jobs_for_me
approve = jobs.approve
reject = jobs.reject
review_job = jobs.review_job
inspect_job = jobs.inspect_job
read_job_file = jobs.read_job_file
list_job_files = jobs.list_job_files

status = jobs.status
help = jobs.help


# Quick help function for getting started
def quick_help():
    """Show a quick getting started guide."""
    print("""
🚀 SyftBox Code Queue - Quick Start

1. Import: import syft_code_queue as q
2. Find datasites: q.datasites
3. Submit job: q.submit_python("user@org.com", "print('Hello!')", "Test")
4. Check status: q.pending_for_others
5. Full help: q.help()
""")
    return None


# Override module attribute access to provide fresh data from backend
def __getattr__(name):
    """Module-level attribute access that always fetches fresh data."""
    if name == "jobs_for_others":
        return jobs.jobs_for_others
    elif name == "jobs_for_me":
        return jobs.jobs_for_me
    elif name == "pending_for_me":
        return jobs.pending_for_me
    elif name == "pending_for_others":
        return jobs.pending_for_others
    elif name == "my_pending":
        return jobs.my_pending
    elif name == "my_running":
        return jobs.my_running
    elif name == "my_completed":
        return jobs.my_completed
    elif name == "approved_by_me":
        return jobs.approved_by_me
    elif name == "datasites":
        return jobs.datasites
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def __dir__():
    """Return list of available attributes for tab completion - only essential methods."""
    return [
        # DataSite discovery
        "datasites",
        # Job submission
        "submit_job",
        "submit_python",
        "submit_bash",
        # Job collections
        "pending_for_me",
        "pending_for_others",
        "jobs_for_me",
        "jobs_for_others",
        # Job management
        "approve",
        "reject",
        # Basic monitoring
        "get_job",
        "wait_for_completion",
    ]


# Module-level attribute setter to handle VERBOSE flag changes

_this_module = sys.modules[__name__]
_original_setattr = getattr(_this_module, "__setattr__", None)


def _module_setattr(name, value):
    """Intercept module-level attribute setting to handle VERBOSE flag."""
    if name == "VERBOSE":
        global VERBOSE
        VERBOSE = value
        _configure_logging()
    elif _original_setattr:
        _original_setattr(name, value)
    else:
        # Fallback to direct setting
        globals()[name] = value


# Replace the module's __setattr__ method
setattr(_this_module, "__setattr__", _module_setattr)


__version__ = "0.1.27"
__all__ = [
    # Global unified API
    "jobs",
    "q",
    # Object-oriented properties
    "jobs_for_others",
    "jobs_for_me",
    "pending_for_me",
    "pending_for_others",
    "my_pending",
    "my_running",
    "my_completed",
    "approved_by_me",
    "datasites",
    # Convenience functions
    "submit_job",
    "submit_python",
    "submit_bash",
    "my_jobs",
    "get_job",
    "get_job_output",
    "get_job_logs",
    "wait_for_completion",
    "all_jobs_for_me",
    "approve",
    "reject",
    "review_job",
    "inspect_job",
    "read_job_file",
    "list_job_files",
    "status",
    "help",
    "quick_help",
    # Logging control
    "VERBOSE",
    "set_verbose",
    # Lower-level APIs
    "CodeQueueClient",
    "create_client",
    # Models
    "CodeJob",
    "JobStatus",
    "QueueConfig",
    "JobCollection",
    "DataSitesCollection",
]


# Legacy convenience function for backward compatibility
def submit_code(target_email: str, code_folder, name: str, **kwargs) -> CodeJob:
    """
    Legacy function for backward compatibility.
    Use submit_job() instead.
    """
    return submit_job(target_email, code_folder, name, **kwargs)
