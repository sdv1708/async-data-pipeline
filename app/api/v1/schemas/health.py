"""
Health Check API Schemas

Pydantic models for health check API responses.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum

from pydantic import BaseModel, Field


class HealthStatus(str, Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    WARNING = "warning"
    UNKNOWN = "unknown"


class ComponentStatus(str, Enum):
    """Component status enumeration."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    WARNING = "warning"
    UNKNOWN = "unknown"


class HealthResponse(BaseModel):
    """Schema for basic health check response."""
    status: HealthStatus = Field(..., description="Overall health status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    
    class Config:
        from_attributes = True


class ComponentHealth(BaseModel):
    """Schema for individual component health."""
    status: ComponentStatus = Field(..., description="Component health status")
    message: str = Field(..., description="Health check message")
    
    # TODO: Add more component health fields
    # response_time: Optional[float] = Field(None, description="Component response time in seconds")
    # last_check: Optional[datetime] = Field(None, description="Last health check timestamp")
    # metrics: Optional[Dict[str, Any]] = Field(None, description="Component-specific metrics")
    
    class Config:
        from_attributes = True


class DatabaseHealth(ComponentHealth):
    """Schema for database health details."""
    # TODO: Add database-specific health fields
    # connection_pool_size: Optional[int] = Field(None, description="Current connection pool size")
    # active_connections: Optional[int] = Field(None, description="Number of active connections")
    # query_response_time: Optional[float] = Field(None, description="Average query response time")
    pass


class RedisHealth(ComponentHealth):
    """Schema for Redis health details."""
    # TODO: Add Redis-specific health fields
    # memory_usage: Optional[float] = Field(None, description="Memory usage percentage")
    # connected_clients: Optional[int] = Field(None, description="Number of connected clients")
    # keys_count: Optional[int] = Field(None, description="Total number of keys")
    pass


class WorkerQueueHealth(ComponentHealth):
    """Schema for worker queue health details."""
    # TODO: Add worker queue-specific health fields
    # queue_size: Optional[int] = Field(None, description="Number of jobs in queue")
    # active_workers: Optional[int] = Field(None, description="Number of active workers")
    # failed_jobs: Optional[int] = Field(None, description="Number of failed jobs")
    pass


class SystemResourcesHealth(ComponentHealth):
    """Schema for system resources health details."""
    # TODO: Add system resources-specific health fields
    # memory_usage_percent: Optional[float] = Field(None, description="Memory usage percentage")
    # cpu_usage_percent: Optional[float] = Field(None, description="CPU usage percentage")
    # disk_usage_percent: Optional[float] = Field(None, description="Disk usage percentage")
    # available_memory: Optional[int] = Field(None, description="Available memory in bytes")
    # load_average: Optional[float] = Field(None, description="System load average")
    pass


class DetailedHealthResponse(BaseModel):
    """Schema for detailed health check response."""
    status: HealthStatus = Field(..., description="Overall health status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    checks: Dict[str, ComponentHealth] = Field(..., description="Individual component health checks")
    
    # TODO: Add more detailed health fields
    # uptime: Optional[float] = Field(None, description="Service uptime in seconds")
    # environment: Optional[str] = Field(None, description="Deployment environment")
    # build_info: Optional[Dict[str, str]] = Field(None, description="Build information")
    # dependencies: Optional[List[str]] = Field(None, description="Service dependencies")
    
    class Config:
        from_attributes = True


class ReadinessResponse(BaseModel):
    """Schema for readiness check response."""
    status: str = Field(..., description="Readiness status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Readiness check timestamp")
    
    # TODO: Add readiness-specific fields
    # ready_components: Optional[List[str]] = Field(None, description="List of ready components")
    # not_ready_components: Optional[List[str]] = Field(None, description="List of not ready components")
    # error: Optional[str] = Field(None, description="Error message if not ready")
    
    class Config:
        from_attributes = True


class LivenessResponse(BaseModel):
    """Schema for liveness check response."""
    status: str = Field(..., description="Liveness status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Liveness check timestamp")
    
    # TODO: Add liveness-specific fields
    # alive_components: Optional[List[str]] = Field(None, description="List of alive components")
    # dead_components: Optional[List[str]] = Field(None, description="List of dead components")
    # error: Optional[str] = Field(None, description="Error message if not alive")
    
    class Config:
        from_attributes = True


# TODO: Add more specialized health schemas
# class HealthHistoryResponse(BaseModel):
#     """Schema for health check history response."""
#     checks: List[HealthResponse]
#     period_start: datetime
#     period_end: datetime
#     
# class HealthMetricsResponse(BaseModel):
#     """Schema for health metrics response."""
#     availability_percentage: float
#     average_response_time: float
#     error_rate: float
#     uptime_percentage: float
#     
# class HealthAlertResponse(BaseModel):
#     """Schema for health alert response."""
#     alert_id: str
#     severity: str
#     component: str
#     message: str
#     triggered_at: datetime