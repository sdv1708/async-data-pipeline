#!/usr/bin/env python3
"""
Script to run RQ worker for processing jobs.

This script starts a Redis Queue worker that processes background jobs.
"""

import sys
import os
import signal
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.workers.worker import create_worker
from app.core.logger import configure_logger, get_logger_with_correlation_id

# Configure logging
configure_logger()
logger = get_logger_with_correlation_id("worker-startup")


def signal_handler(signum, frame):
    """Handle graceful shutdown on SIGINT/SIGTERM."""
    logger.info(f"Received signal {signum}, shutting down worker gracefully...")
    sys.exit(0)


def main():
    """
    Main function to start the RQ worker.
    
    TODO: Add the following features:
    - Command-line argument parsing
    - Multiple queue support
    - Worker scaling
    - Health monitoring
    - Metrics collection
    """
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Starting RQ worker for async data pipeline...")
    
    # TODO: Add command-line arguments
    # parser = argparse.ArgumentParser(description='RQ Worker for Async Data Pipeline')
    # parser.add_argument('--queues', nargs='+', default=['file-processor'], help='Queue names to process')
    # parser.add_argument('--concurrency', type=int, default=1, help='Number of concurrent workers')
    # args = parser.parse_args()
    
    try:
        # Create and start worker
        worker = create_worker()
        logger.info(f"Worker started, processing queue: {worker.queues}")
        
        # Start processing jobs
        worker.work()
        
    except Exception as e:
        logger.error(f"Worker failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()