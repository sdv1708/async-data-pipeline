"""
Redis Queue Worker Implementation

This module handles background job processing using Redis Queue (RQ).
"""

import asyncio
import redis
from rq import Queue, Retry, Worker
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logger import get_logger_with_correlation_id
from app.db.base import AsyncSessionLocal
from app.services.processor import file_processor

# Initialize Redis connection
redis_conn = redis.from_url(settings.REDIS_URL)

# Create a Redis queue
queue = Queue("file-processor", connection=redis_conn)


def enqueue_task(job_id: str, file_path: str, correlation_id: str):
    """
    Enqueue a job to process a file with the given job_id and correlation_id.
    
    Args:
        job_id: Unique identifier for the job
        file_path: Path to the file to be processed
        correlation_id: Correlation ID for request tracking
    
    Returns:
        RQ Job instance
    
    TODO: Add the following enhancements:
    - Job priority support
    - Custom queue routing based on file type/size
    - Job dependency management
    - Scheduled job support
    - Job metadata storage
    """
    logger = get_logger_with_correlation_id(correlation_id)
    logger.info(f"Enqueuing job {job_id} for file processing")
    
    # TODO: Add job validation
    # if not os.path.exists(file_path):
    #     raise FileNotFoundError(f"File not found: {file_path}")
    
    # TODO: Add file size check for queue routing
    # file_size = os.path.getsize(file_path)
    # queue_name = "large-files" if file_size > LARGE_FILE_THRESHOLD else "file-processor"
    
    job = queue.enqueue(
        process_file,
        job_id,
        file_path,
        correlation_id,
        result_ttl=3600,  # Keep results for 1 hour
        timeout=600,      # 10 minutes timeout
        retry=Retry(max=3, interval=[10, 30, 60]),  # Retry up to 3 times
        # TODO: Add more job options
        # job_timeout=get_job_timeout(file_size),
        # depends_on=dependent_job_id,
        # meta={"file_size": file_size, "file_type": file_type},
    )
    
    logger.info(f"Job {job_id} enqueued successfully with RQ job ID: {job.id}")
    return job


def process_file(job_id: str, file_path: str, correlation_id: str):
    """
    Process a file job (RQ worker function).
    
    This function is called by RQ workers to process files.
    It wraps the async file_processor function to work with RQ.
    
    Args:
        job_id: Unique identifier for the job
        file_path: Path to the file to be processed
        correlation_id: Correlation ID for request tracking
    
    TODO: Add the following enhancements:
    - Progress tracking and reporting
    - Intermediate result storage
    - Job cancellation support
    - Resource usage monitoring
    - Custom error handling per job type
    """
    logger = get_logger_with_correlation_id(correlation_id)
    logger.info(f"Worker processing job {job_id}")
    
    # TODO: Add job start notification
    # await notify_job_started(job_id)
    
    # TODO: Add resource monitoring
    # monitor = ResourceMonitor(job_id)
    # monitor.start()
    
    try:
        # Run the async processor in a new event loop
        asyncio.run(_process_file_async(job_id, file_path, correlation_id))
        
        logger.info(f"Worker completed job {job_id} successfully")
        
        # TODO: Add job completion notification
        # await notify_job_completed(job_id)
        
    except Exception as e:
        logger.error(f"Worker failed to process job {job_id}: {str(e)}")
        
        # TODO: Add job failure notification
        # await notify_job_failed(job_id, str(e))
        
        raise  # Re-raise for RQ to handle retries
    
    # TODO: Add resource cleanup
    # finally:
    #     monitor.stop()
    #     cleanup_temporary_files(job_id)


async def _process_file_async(job_id: str, file_path: str, correlation_id: str):
    """
    Async wrapper for file processing with database session management.
    
    Args:
        job_id: Unique identifier for the job
        file_path: Path to the file to be processed
        correlation_id: Correlation ID for request tracking
    
    TODO: Add the following enhancements:
    - Connection pool management
    - Transaction retry logic
    - Progress tracking updates
    - Result caching
    """
    logger = get_logger_with_correlation_id(correlation_id)
    
    # Create async database session
    async with AsyncSessionLocal() as db_session:
        try:
            # TODO: Add progress tracking initialization
            # await update_job_progress(job_id, 0, "Starting processing")
            
            # Process the file
            await file_processor(job_id, file_path, correlation_id, db_session)
            
            # TODO: Add final progress update
            # await update_job_progress(job_id, 100, "Processing completed")
            
            logger.info(f"Async processing completed for job {job_id}")
            
        except Exception as e:
            logger.error(f"Async processing failed for job {job_id}: {str(e)}")
            
            # TODO: Add error details to database
            # await update_job_error(job_id, str(e))
            
            raise
        finally:
            # Ensure session is properly closed
            await db_session.close()


def create_worker(queue_names: list = None):
    """
    Create an RQ worker instance.
    
    Args:
        queue_names: List of queue names to process (default: ["file-processor"])
    
    Returns:
        RQ Worker instance
    
    TODO: Add the following worker enhancements:
    - Worker health monitoring
    - Custom job failure handling
    - Worker-specific metrics
    - Graceful shutdown handling
    - Multi-queue priority handling
    """
    if queue_names is None:
        queue_names = ["file-processor"]
    
    queues = [Queue(name, connection=redis_conn) for name in queue_names]
    
    worker = Worker(
        queues,
        connection=redis_conn,
        # TODO: Add worker configuration
        # name=f"worker-{os.getpid()}",
        # default_result_ttl=3600,
        # default_worker_ttl=1800,
        # job_monitoring_interval=30,
    )
    
    return worker


def get_queue_info():
    """
    Get information about the job queue.
    
    Returns:
        Dictionary with queue information
    
    TODO: Add the following queue information:
    - Worker status and count
    - Job processing rates
    - Queue health metrics
    - Failed job analysis
    """
    return {
        "queue_name": queue.name,
        "job_count": len(queue),
        "failed_job_count": len(queue.failed_job_registry),
        "started_job_count": len(queue.started_job_registry),
        "finished_job_count": len(queue.finished_job_registry),
        # TODO: Add more queue metrics
        # "workers": queue.workers,
        # "oldest_job_age": queue.get_oldest_job_age(),
        # "average_processing_time": queue.get_average_processing_time(),
    }


def cancel_job(job_id: str):
    """
    Cancel a job by ID.
    
    Args:
        job_id: RQ job ID to cancel
    
    TODO: Add the following cancellation features:
    - Database status update
    - Resource cleanup
    - Notification system
    - Graceful cancellation
    """
    try:
        job = queue.fetch_job(job_id)
        if job:
            job.cancel()
            logger = get_logger_with_correlation_id("job-cancellation")
            logger.info(f"Job {job_id} cancelled successfully")
            return True
        else:
            logger.warning(f"Job {job_id} not found for cancellation")
            return False
    except Exception as e:
        logger.error(f"Failed to cancel job {job_id}: {str(e)}")
        return False


# TODO: Add more worker management functions
# def retry_failed_jobs():
#     """Retry all failed jobs in the queue."""
#     pass
#
# def clear_failed_jobs():
#     """Clear all failed jobs from the queue."""
#     pass
#
# def get_job_status(job_id: str):
#     """Get the status of a specific job."""
#     pass
#
# def pause_queue():
#     """Pause job processing."""
#     pass
#
# def resume_queue():
#     """Resume job processing."""
#     pass
