"""
FastAPI Application Entry Point

This module sets up the FastAPI application with all necessary middleware,
exception handlers, and route configurations for the async data pipeline.
"""

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logger import configure_logger, get_logger_with_correlation_id
from app.db.base import engine
from app.db.models import Base

# Configure logging on startup
configure_logger()
logger = get_logger_with_correlation_id("app-startup")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    
    TODO: Implement the following:
    - Database connection initialization
    - Redis connection verification
    - Health check setup
    - Graceful shutdown handling
    """
    logger.info("Starting up the FastAPI application...")
    
    # TODO: Add database table creation (for development)
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    
    # TODO: Verify Redis connection
    # from app.workers.worker import redis_conn
    # redis_conn.ping()
    
    logger.info("Application startup complete")
    yield
    
    # Shutdown
    logger.info("Shutting down the FastAPI application...")
    
    # TODO: Add cleanup tasks
    # - Close database connections
    # - Close Redis connections
    # - Cancel background tasks
    
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """
    Application factory function that creates and configures the FastAPI app.
    
    Returns:
        FastAPI: Configured FastAPI application instance
    
    TODO: Add the following configurations:
    - API versioning
    - Security middleware
    - Rate limiting
    - Request/response logging
    - Custom exception handlers
    """
    
    app = FastAPI(
        title="Async Data Pipeline API",
        description="A production-style backend for processing CSV datasets asynchronously",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    
    # TODO: Add security middleware
    # from fastapi.middleware.trustedhost import TrustedHostMiddleware
    # app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])
    
    # CORS middleware configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO: Configure for production with specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # TODO: Add request logging middleware
    @app.middleware("http")
    async def logging_middleware(request: Request, call_next):
        """
        Middleware to log requests and responses with correlation IDs.
        
        TODO: Implement the following:
        - Extract or generate correlation ID from headers
        - Log request details (method, path, headers)
        - Measure request duration
        - Log response details (status, duration)
        - Add correlation ID to response headers
        """
        # correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        # request.state.correlation_id = correlation_id
        
        response = await call_next(request)
        
        # TODO: Add correlation ID to response headers
        # response.headers["X-Correlation-ID"] = correlation_id
        
        return response
    
    # Register API routes
    from app.api.v1.api import api_router
    app.include_router(api_router, prefix="/api/v1")
    
    return app


# Global exception handlers
def setup_exception_handlers(app: FastAPI) -> None:
    """
    Setup global exception handlers for the FastAPI application.
    
    TODO: Implement handlers for:
    - Database connection errors
    - Redis connection errors
    - File processing errors
    - Authentication errors
    - Rate limiting errors
    """
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        Handle request validation errors.
        
        TODO: Enhance with:
        - Detailed error messages
        - Correlation ID logging
        - Client-friendly error format
        """
        logger.error(f"Validation error for {request.url}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation Error",
                "message": "The request data is invalid",
                "details": exc.errors(),
            },
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """
        Handle general exceptions.
        
        TODO: Enhance with:
        - Error classification
        - Detailed logging
        - Error tracking/monitoring
        - Client-safe error messages
        """
        logger.error(f"Unhandled exception for {request.url}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
            },
        )


# Create the FastAPI application instance
app = create_app()
setup_exception_handlers(app)


# Basic health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Basic health check endpoint.
    
    TODO: Enhance with:
    - Database connectivity check
    - Redis connectivity check
    - Worker queue status
    - System resource checks
    - Service dependencies status
    """
    return {
        "status": "healthy",
        "service": "async-data-pipeline",
        "version": "0.1.0",
        # TODO: Add more detailed health information
        # "database": "connected",
        # "redis": "connected",
        # "workers": "active",
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def read_root():
    """
    Root endpoint providing API information.
    
    TODO: Add:
    - API version information
    - Available endpoints summary
    - Documentation links
    """
    return {
        "message": "Async Data Pipeline API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }


if __name__ == "__main__":
    """
    Development server entry point.
    
    TODO: Configure for production deployment:
    - Remove debug mode
    - Configure proper host/port
    - Add SSL/TLS configuration
    - Set up process management
    """
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # TODO: Set to False in production
        log_level=settings.LOG_LEVEL.lower(),
    )