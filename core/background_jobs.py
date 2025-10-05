"""
Background Job System for Sprint 3 Architecture Improvements
Provides a simple background job system for asynchronous task processing.
"""

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import json
from concurrent.futures import ThreadPoolExecutor
import traceback

from core.config import get_config
from core.event_system import event_handler, EventTypes

logger = logging.getLogger(__name__)

class JobStatus(Enum):
    """Job status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

class JobPriority(Enum):
    """Job priority enumeration."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Job:
    """Represents a background job."""
    id: str
    name: str
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    status: JobStatus = JobStatus.PENDING
    priority: JobPriority = JobPriority.NORMAL
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    retry_delay: int = 60  # seconds
    scheduled_at: Optional[datetime] = None
    timeout: Optional[int] = None  # seconds
    metadata: dict = field(default_factory=dict)

class JobQueue:
    """Manages a queue of background jobs."""
    
    def __init__(self, name: str = "default", max_workers: int = 4):
        self.name = name
        self.max_workers = max_workers
        self._jobs: Dict[str, Job] = {}
        self._queue: List[str] = []  # Job IDs in priority order
        self._running: Dict[str, asyncio.Task] = {}
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._shutdown = False
        self._stats = {
            "total_jobs": 0,
            "completed_jobs": 0,
            "failed_jobs": 0,
            "cancelled_jobs": 0
        }
    
    def add_job(
        self,
        name: str,
        func: Callable,
        args: tuple = (),
        kwargs: dict = None,
        priority: JobPriority = JobPriority.NORMAL,
        max_retries: int = 3,
        retry_delay: int = 60,
        scheduled_at: Optional[datetime] = None,
        timeout: Optional[int] = None,
        metadata: dict = None
    ) -> str:
        """Add a job to the queue."""
        if kwargs is None:
            kwargs = {}
        if metadata is None:
            metadata = {}
        
        job_id = str(uuid.uuid4())
        job = Job(
            id=job_id,
            name=name,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            max_retries=max_retries,
            retry_delay=retry_delay,
            scheduled_at=scheduled_at,
            timeout=timeout,
            metadata=metadata
        )
        
        self._jobs[job_id] = job
        self._stats["total_jobs"] += 1
        
        # Add to queue if not scheduled for later
        if scheduled_at is None or scheduled_at <= datetime.now():
            self._enqueue_job(job_id)
        
        logger.info(f"Added job {name} (ID: {job_id}) to queue {self.name}")
        
        # Emit job created event
        asyncio.create_task(event_handler.emit(
            EventTypes.SYSTEM_STARTUP,  # We'll add a JOB_CREATED event type
            {
                "job_id": job_id,
                "job_name": name,
                "queue_name": self.name,
                "priority": priority.value
            },
            source="job_queue"
        ))
        
        return job_id
    
    def _enqueue_job(self, job_id: str) -> None:
        """Add a job to the execution queue in priority order."""
        if job_id in self._queue:
            return
        
        job = self._jobs[job_id]
        
        # Insert in priority order (higher priority first)
        insert_index = 0
        for i, queued_job_id in enumerate(self._queue):
            queued_job = self._jobs[queued_job_id]
            if job.priority.value > queued_job.priority.value:
                insert_index = i
                break
            insert_index = i + 1
        
        self._queue.insert(insert_index, job_id)
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get a job by ID."""
        return self._jobs.get(job_id)
    
    def get_job_status(self, job_id: str) -> Optional[JobStatus]:
        """Get the status of a job."""
        job = self._jobs.get(job_id)
        return job.status if job else None
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a job."""
        job = self._jobs.get(job_id)
        if not job:
            return False
        
        if job.status == JobStatus.PENDING:
            job.status = JobStatus.CANCELLED
            if job_id in self._queue:
                self._queue.remove(job_id)
            self._stats["cancelled_jobs"] += 1
            logger.info(f"Cancelled job {job.name} (ID: {job_id})")
            return True
        
        elif job.status == JobStatus.RUNNING:
            # Try to cancel the running task
            if job_id in self._running:
                self._running[job_id].cancel()
                job.status = JobStatus.CANCELLED
                self._stats["cancelled_jobs"] += 1
                logger.info(f"Cancelled running job {job.name} (ID: {job_id})")
                return True
        
        return False
    
    def get_queue_stats(self) -> dict:
        """Get queue statistics."""
        return {
            "queue_name": self.name,
            "max_workers": self.max_workers,
            "active_workers": len(self._running),
            "queued_jobs": len(self._queue),
            "total_jobs": len(self._jobs),
            "stats": self._stats.copy()
        }
    
    def get_jobs_by_status(self, status: JobStatus) -> List[Job]:
        """Get all jobs with a specific status."""
        return [job for job in self._jobs.values() if job.status == status]
    
    async def start(self) -> None:
        """Start the job queue worker."""
        logger.info(f"Starting job queue {self.name} with {self.max_workers} workers")
        
        while not self._shutdown:
            try:
                # Process scheduled jobs
                await self._process_scheduled_jobs()
                
                # Start new jobs if we have capacity
                await self._start_available_jobs()
                
                # Clean up completed jobs
                await self._cleanup_completed_jobs()
                
                # Wait a bit before next iteration
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in job queue {self.name}: {e}")
                await asyncio.sleep(5)
    
    async def _process_scheduled_jobs(self) -> None:
        """Process jobs that are scheduled to run now."""
        now = datetime.now()
        for job_id, job in self._jobs.items():
            if (job.status == JobStatus.PENDING and 
                job.scheduled_at and 
                job.scheduled_at <= now and 
                job_id not in self._queue):
                self._enqueue_job(job_id)
    
    async def _start_available_jobs(self) -> None:
        """Start available jobs if we have worker capacity."""
        while (len(self._running) < self.max_workers and 
               self._queue and 
               not self._shutdown):
            
            job_id = self._queue.pop(0)
            job = self._jobs[job_id]
            
            if job.status == JobStatus.CANCELLED:
                continue
            
            # Start the job
            task = asyncio.create_task(self._execute_job(job))
            self._running[job_id] = task
    
    async def _execute_job(self, job: Job) -> None:
        """Execute a job."""
        job.status = JobStatus.RUNNING
        job.started_at = datetime.now()
        
        logger.info(f"Starting job {job.name} (ID: {job.id})")
        
        try:
            # Execute the job function
            if asyncio.iscoroutinefunction(job.func):
                result = await asyncio.wait_for(
                    job.func(*job.args, **job.kwargs),
                    timeout=job.timeout
                )
            else:
                # Run sync function in thread pool
                loop = asyncio.get_event_loop()
                result = await asyncio.wait_for(
                    loop.run_in_executor(
                        self._executor,
                        lambda: job.func(*job.args, **job.kwargs)
                    ),
                    timeout=job.timeout
                )
            
            job.result = result
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now()
            self._stats["completed_jobs"] += 1
            
            logger.info(f"Completed job {job.name} (ID: {job.id})")
            
        except asyncio.CancelledError:
            job.status = JobStatus.CANCELLED
            job.completed_at = datetime.now()
            self._stats["cancelled_jobs"] += 1
            logger.info(f"Cancelled job {job.name} (ID: {job.id})")
            
        except Exception as e:
            job.error = str(e)
            job.retry_count += 1
            
            if job.retry_count <= job.max_retries:
                job.status = JobStatus.RETRYING
                # Schedule retry
                retry_time = datetime.now() + timedelta(seconds=job.retry_delay)
                job.scheduled_at = retry_time
                logger.warning(f"Job {job.name} (ID: {job.id}) failed, retrying in {job.retry_delay}s: {e}")
            else:
                job.status = JobStatus.FAILED
                job.completed_at = datetime.now()
                self._stats["failed_jobs"] += 1
                logger.error(f"Job {job.name} (ID: {job.id}) failed permanently: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
        
        finally:
            # Remove from running jobs
            if job.id in self._running:
                del self._running[job.id]
    
    async def _cleanup_completed_jobs(self) -> None:
        """Clean up old completed jobs."""
        cutoff_time = datetime.now() - timedelta(hours=24)  # Keep jobs for 24 hours
        
        jobs_to_remove = []
        for job_id, job in self._jobs.items():
            if (job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED] and
                job.completed_at and
                job.completed_at < cutoff_time):
                jobs_to_remove.append(job_id)
        
        for job_id in jobs_to_remove:
            del self._jobs[job_id]
    
    async def shutdown(self) -> None:
        """Shutdown the job queue."""
        logger.info(f"Shutting down job queue {self.name}")
        self._shutdown = True
        
        # Cancel all running jobs
        for task in self._running.values():
            task.cancel()
        
        # Wait for tasks to complete
        if self._running:
            await asyncio.gather(*self._running.values(), return_exceptions=True)
        
        # Shutdown executor
        self._executor.shutdown(wait=True)

class JobManager:
    """Manages multiple job queues."""
    
    def __init__(self):
        self._queues: Dict[str, JobQueue] = {}
        self._tasks: Dict[str, asyncio.Task] = {}
        self._config = get_config()
    
    def create_queue(self, name: str, max_workers: int = 4) -> JobQueue:
        """Create a new job queue."""
        if name in self._queues:
            raise ValueError(f"Queue {name} already exists")
        
        queue = JobQueue(name, max_workers)
        self._queues[name] = queue
        logger.info(f"Created job queue: {name}")
        return queue
    
    def get_queue(self, name: str) -> Optional[JobQueue]:
        """Get a job queue by name."""
        return self._queues.get(name)
    
    def get_default_queue(self) -> JobQueue:
        """Get the default job queue."""
        if "default" not in self._queues:
            self.create_queue("default")
        return self._queues["default"]
    
    async def start_all_queues(self) -> None:
        """Start all job queues."""
        for name, queue in self._queues.items():
            task = asyncio.create_task(queue.start())
            self._tasks[name] = task
            logger.info(f"Started job queue: {name}")
    
    async def shutdown_all_queues(self) -> None:
        """Shutdown all job queues."""
        for name, queue in self._queues.items():
            await queue.shutdown()
            logger.info(f"Shutdown job queue: {name}")
        
        # Cancel all tasks
        for task in self._tasks.values():
            task.cancel()
        
        # Wait for tasks to complete
        if self._tasks:
            await asyncio.gather(*self._tasks.values(), return_exceptions=True)
    
    def get_all_stats(self) -> Dict[str, dict]:
        """Get statistics for all queues."""
        return {name: queue.get_queue_stats() for name, queue in self._queues.items()}

# Global job manager
job_manager = JobManager()

# Convenience functions
def get_default_queue() -> JobQueue:
    """Get the default job queue."""
    return job_manager.get_default_queue()

def add_job(
    name: str,
    func: Callable,
    args: tuple = (),
    kwargs: dict = None,
    priority: JobPriority = JobPriority.NORMAL,
    queue_name: str = "default",
    **job_kwargs
) -> str:
    """Add a job to a queue."""
    queue = job_manager.get_queue(queue_name)
    if not queue:
        queue = job_manager.create_queue(queue_name)
    
    return queue.add_job(name, func, args, kwargs or {}, priority, **job_kwargs)

def get_job_status(job_id: str, queue_name: str = "default") -> Optional[JobStatus]:
    """Get the status of a job."""
    queue = job_manager.get_queue(queue_name)
    return queue.get_job_status(job_id) if queue else None

def cancel_job(job_id: str, queue_name: str = "default") -> bool:
    """Cancel a job."""
    queue = job_manager.get_queue(queue_name)
    return queue.cancel_job(job_id) if queue else False

async def start_background_jobs() -> None:
    """Start all background job queues."""
    await job_manager.start_all_queues()

async def shutdown_background_jobs() -> None:
    """Shutdown all background job queues."""
    await job_manager.shutdown_all_queues()

def get_job_stats() -> Dict[str, dict]:
    """Get statistics for all job queues."""
    return job_manager.get_all_stats()

# Example background jobs
async def cleanup_old_data():
    """Example background job to cleanup old data."""
    logger.info("Running cleanup of old data...")
    # Implementation would go here
    await asyncio.sleep(1)  # Simulate work
    logger.info("Cleanup completed")

async def send_notifications():
    """Example background job to send notifications."""
    logger.info("Sending notifications...")
    # Implementation would go here
    await asyncio.sleep(1)  # Simulate work
    logger.info("Notifications sent")

def sync_data_processing():
    """Example synchronous background job."""
    logger.info("Processing data synchronously...")
    # Implementation would go here
    import time
    time.sleep(1)  # Simulate work
    logger.info("Data processing completed")
