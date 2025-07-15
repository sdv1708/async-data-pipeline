import redis
from rq import Queue, Retry
from app.core.config import settings

# Initialize Redis connection
redis_conn = redis.from_url(settings.REDIS_URL)

# Create a Redis queue
queue = Queue('file-processor',connection=redis_conn)

def enqueue_task(job_id, file_path, correlation_id):
    """
    Enqueue a job to process a file with the given job_id and correlation_id.
    """
    from app.workers.worker import process_file  # Import here to avoid circular imports
    job = queue.enqueue(
        process_file, 
        job_id, 
        file_path, 
        correlation_id, 
        result_ttl=3600, 
        timeout=600, 
        retry=Retry(max=3, interval=[10, 30, 60]))
    
    return job
