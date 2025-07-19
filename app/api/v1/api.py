"""
API Router Configuration

This module configures the main API router and includes all endpoint modules.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import jobs, health

# Create the main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(health.router, prefix="/health", tags=["Health"])

# TODO: Add more endpoint routers as needed
# api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
# api_router.include_router(files.router, prefix="/files", tags=["Files"])
# api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])