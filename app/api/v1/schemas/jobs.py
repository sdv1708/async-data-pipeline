"""
Job API Schemas

Pydantic models for job-related API requests and responses.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, validator

from app.db.models import JobStatus


class JobBase(BaseModel):
    """Base job schema with common fields."""
    pass


class JobCreate(JobBase):
    """Schema for creating a new job."""
    file_name: str = Field(..., description="Name of the file to process")
    file_path: Optional[str] = Field(None, description="Path to the file (optional)")
    
    # TODO: Add more job creation fields
    # file_size: Optional[int] = Field(None, description="Size of the file in bytes")
    # processing_options: Optional[Dict[str, Any]] = Field(None, description="Processing configuration")
    # priority: Optional[int] = Field(1, ge=1, le=5, description="Job priority (1-5)")
    # callback_url: Optional[str] = Field(None, description="URL to call when job completes")
    
    @validator('file_name')
    def validate_file_name(cls, v):
        """
        Validate file name format.
        
        TODO: Add more comprehensive validation:
        - File extension validation
        - File name length limits
        - Invalid character checking
        - Security validation
        """
        if not v or not v.strip():
            raise ValueError('File name cannot be empty')
        
        # TODO: Add file extension validation
        # if not v.lower().endswith('.csv'):
        #     raise ValueError('Only CSV files are supported')
        
        return v.strip()


class JobResponse(JobBase):
    """Schema for job response data."""
    id: UUID = Field(..., description="Unique job identifier")
    correlation_id: str = Field(..., description="Correlation ID for request tracking")
    status: JobStatus = Field(..., description="Current job status")
    created_at: datetime = Field(..., description="Job creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    # TODO: Add more response fields
    # file_name: Optional[str] = Field(None, description="Original file name")
    # file_size: Optional[int] = Field(None, description="File size in bytes")
    # progress_percentage: Optional[float] = Field(None, ge=0, le=100, description="Processing progress")
    # error_message: Optional[str] = Field(None, description="Error message if failed")
    # result_summary: Optional[Dict[str, Any]] = Field(None, description="Processing results summary")
    # processing_time: Optional[float] = Field(None, description="Total processing time in seconds")
    
    class Config:
        from_attributes = True


class JobStatusResponse(BaseModel):
    """Schema for job status response."""
    job_id: UUID = Field(..., description="Job identifier")
    status: JobStatus = Field(..., description="Current job status")
    last_updated: datetime = Field(..., description="Last status update timestamp")
    
    # TODO: Add more status fields
    # progress_percentage: Optional[float] = Field(None, ge=0, le=100, description="Processing progress")
    # estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    # error_details: Optional[Dict[str, Any]] = Field(None, description="Error details if failed")
    # metrics: Optional[Dict[str, Any]] = Field(None, description="Processing metrics")
    
    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    """Schema for paginated job list response."""
    jobs: List[JobResponse] = Field(..., description="List of jobs")
    total: int = Field(..., description="Total number of jobs")
    skip: int = Field(..., description="Number of jobs skipped")
    limit: int = Field(..., description="Maximum number of jobs returned")
    
    # TODO: Add more pagination fields
    # page: int = Field(..., description="Current page number")
    # pages: int = Field(..., description="Total number of pages")
    # has_next: bool = Field(..., description="Whether there are more pages")
    # has_previous: bool = Field(..., description="Whether there are previous pages")


class JobUpdate(BaseModel):
    """Schema for updating job data."""
    # TODO: Add updatable fields
    # priority: Optional[int] = Field(None, ge=1, le=5, description="Job priority")
    # callback_url: Optional[str] = Field(None, description="Callback URL")
    # processing_options: Optional[Dict[str, Any]] = Field(None, description="Processing options")
    pass


class JobResultsResponse(BaseModel):
    """Schema for job results response."""
    job_id: UUID = Field(..., description="Job identifier")
    results: Dict[str, Any] = Field(..., description="Processing results")
    generated_at: datetime = Field(..., description="Results generation timestamp")
    
    # TODO: Add more result fields
    # file_urls: Optional[List[str]] = Field(None, description="URLs to result files")
    # summary_statistics: Optional[Dict[str, Any]] = Field(None, description="Summary statistics")
    # processing_metadata: Optional[Dict[str, Any]] = Field(None, description="Processing metadata")
    
    class Config:
        from_attributes = True


class JobProgressResponse(BaseModel):
    """Schema for job progress response."""
    job_id: UUID = Field(..., description="Job identifier")
    progress_percentage: float = Field(..., ge=0, le=100, description="Processing progress")
    current_step: str = Field(..., description="Current processing step")
    total_steps: int = Field(..., description="Total number of processing steps")
    
    # TODO: Add more progress fields
    # estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    # processing_rate: Optional[float] = Field(None, description="Processing rate (items/second)")
    # items_processed: Optional[int] = Field(None, description="Number of items processed")
    # total_items: Optional[int] = Field(None, description="Total number of items to process")
    
    class Config:
        from_attributes = True


# TODO: Add more specialized schemas
# class JobStatisticsResponse(BaseModel):
#     """Schema for job statistics response."""
#     total_jobs: int
#     jobs_by_status: Dict[JobStatus, int]
#     average_processing_time: float
#     success_rate: float
#     
# class JobRetryRequest(BaseModel):
#     """Schema for job retry request."""
#     job_id: UUID
#     max_retries: Optional[int] = Field(3, ge=1, le=10)
#     
# class JobCancelRequest(BaseModel):
#     """Schema for job cancellation request."""
#     job_id: UUID
#     reason: Optional[str] = Field(None, max_length=500)