import csv
import json 
from app.core.logger import logger, get_logger_with_correlation_id
from app.db.models import Job, JobStatus  # Import the Job model
from datetime import datetime

# The heart of the service is the processor function
async def file_processor(job_id: str, file_path: str, correlation_id: str, db_session=None):
    """
    Process a file and log the progress.
    
    Args:
        job_id (str): Unique identifier for the job.
        file_path (str): Path to the file to be processed.
        correlation_id (str): Correlation ID for tracking logs.
    """
    logger = get_logger_with_correlation_id(correlation_id)
    logger.info(f"Starting processing for job {job_id} with file {file_path}")

    try:
        total = []
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            #TODO - adjust the fieldnames based on your CSV structure
            for row in reader:
                total.append(row)
                logger.info(f"Processed row: {row}")
        
        # Calculate aggregate data or perform any other processing
        aggregate_data = {
            "count": len(total),
            "sum": sum(float(row['value']) for row in total if 'value' in row),
            "average": sum(float(row['value']) for row in total if 'value' in row) / len(total) if total else 0
        }

        # Report file 
        with open(f"report_{job_id}.json", 'w') as report_file:
            json.dump(aggregate_data, report_file, indent=4)

        logger.info(f"Aggregate data: {json.dumps(aggregate_data)}")

        # Update the status of the job in the database
        await db_session.execute(
            Job.__table__.update().where(Job.correlation_id == correlation_id).values(
                status=JobStatus.COMPLETED, updated_at=datetime.utcnow()
            ))
        await db_session.commit()
        logger.info(f"Job {job_id} completed successfully.")

    except Exception as e:
        logger.error(f"Error processing job {job_id}: {str(e)}")
        
        # Update the status of the job in the database
        await db_session.execute(
            Job.__table__.update().where(Job.correlation_id == correlation_id).values(
                status=JobStatus.FAILED, updated_at=datetime.utcnow()
            ))
        await db_session.commit()
        logger.error(f"Job {job_id} failed with error: {str(e)}")
        
