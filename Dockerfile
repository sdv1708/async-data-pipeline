# Multi-stage Dockerfile for Async Data Pipeline
# Stage 1: Base image with Python dependencies
FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Configure Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Set work directory
WORKDIR /app

# Copy Poetry files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --only=main && rm -rf $POETRY_CACHE_DIR

# Stage 2: Development image
FROM base as development

# Install development dependencies
RUN poetry install && rm -rf $POETRY_CACHE_DIR

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# TODO: Add development-specific configurations
# - Hot reload setup
# - Debug mode configuration
# - Development database setup
# - Test runner configuration

# Command for development
CMD ["poetry", "run", "python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Stage 3: Production image
FROM base as production

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# TODO: Add production-specific configurations
# - SSL/TLS setup
# - Security hardening
# - Performance optimization
# - Monitoring setup
# - Health check configuration

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Command for production
CMD ["poetry", "run", "python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# Stage 4: Worker image
FROM base as worker

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash worker && chown -R worker:worker /app
USER worker

# TODO: Add worker-specific configurations
# - Worker scaling setup
# - Resource limits
# - Job queue configuration
# - Monitoring setup

# Command for worker
CMD ["poetry", "run", "python", "-m", "rq", "worker", "--url", "${REDIS_URL}", "file-processor"]