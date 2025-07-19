-- Database initialization script for async-data-pipeline
-- This script runs when the PostgreSQL container starts for the first time

-- Create database (if not exists)
-- Note: This is typically handled by POSTGRES_DB environment variable

-- Create user (if not exists)
-- Note: This is typically handled by POSTGRES_USER environment variable

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE async_pipeline TO pipeline_user;

-- TODO: Add additional database setup
-- - Create additional schemas
-- - Set up database-specific configurations
-- - Create indexes for performance
-- - Set up database roles and permissions
-- - Configure database extensions (if needed)

-- Example: Enable UUID extension
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Example: Create schemas
-- CREATE SCHEMA IF NOT EXISTS audit;
-- CREATE SCHEMA IF NOT EXISTS reporting;

-- Example: Create additional users
-- CREATE USER readonly_user WITH PASSWORD 'readonly_pass';
-- GRANT CONNECT ON DATABASE async_pipeline TO readonly_user;
-- GRANT USAGE ON SCHEMA public TO readonly_user;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;

-- Set up database configuration
-- ALTER DATABASE async_pipeline SET timezone TO 'UTC';
-- ALTER DATABASE async_pipeline SET log_statement TO 'all';

-- TODO: Add production-specific database setup
-- - Security configurations
-- - Performance tuning
-- - Backup setup
-- - Monitoring configuration