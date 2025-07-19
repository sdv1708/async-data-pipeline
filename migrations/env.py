"""
Alembic Environment Configuration

This module configures Alembic for database migrations with async support.
"""

import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine
from alembic import context

# Import your models here for autogenerate support
from app.db.models import Base
from app.core.config import settings

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for 'autogenerate' support
target_metadata = Base.metadata

# TODO: Add model imports for autogenerate support
# from app.db.models import User, FileUpload, ProcessingResult
# target_metadata = [Base.metadata, OtherBase.metadata]


def get_database_url():
    """
    Get database URL from environment or configuration.
    
    Returns:
        str: Database URL
    
    TODO: Add the following enhancements:
    - Multiple environment support
    - Secure URL handling
    - Connection validation
    - Database URL encryption
    """
    # Get URL from environment variable (preferred)
    if hasattr(settings, 'DATABASE_URL'):
        return settings.DATABASE_URL
    
    # Fallback to config file
    return config.get_main_option("sqlalchemy.url")


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    
    This configures the context with just a URL and not an Engine.
    
    TODO: Add the following offline migration features:
    - SQL script generation
    - Migration validation
    - Dry-run mode
    - Migration documentation
    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # TODO: Add offline migration options
        # compare_type=True,
        # compare_server_default=True,
        # include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """
    Run migrations with a database connection.
    
    Args:
        connection: Database connection
    
    TODO: Add the following migration features:
    - Migration hooks (before/after)
    - Custom migration context
    - Migration validation
    - Progress tracking
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # TODO: Add migration options
        # compare_type=True,
        # compare_server_default=True,
        # include_object=include_object,
        # process_revision_directives=process_revision_directives,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode with async support.
    
    TODO: Add the following online migration features:
    - Connection pooling
    - Transaction management
    - Migration locks
    - Progress reporting
    - Error handling and rollback
    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_database_url()
    
    # Create async engine
    connectable = AsyncEngine(
        engine_from_config(
            configuration,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


# TODO: Add custom migration functions
# def include_object(object, name, type_, reflected, compare_to):
#     """
#     Filter objects to include in migrations.
#     
#     Args:
#         object: Database object
#         name: Object name
#         type_: Object type
#         reflected: Whether object was reflected
#         compare_to: Object to compare to
#     
#     Returns:
#         bool: Whether to include object
#     """
#     # Skip temporary tables
#     if type_ == "table" and name.startswith("temp_"):
#         return False
#     
#     # Skip certain schemas
#     if hasattr(object, "schema") and object.schema in ["information_schema", "pg_catalog"]:
#         return False
#     
#     return True
#
# def process_revision_directives(context, revision, directives):
#     """
#     Process revision directives for custom migration logic.
#     
#     Args:
#         context: Migration context
#         revision: Revision identifier
#         directives: Migration directives
#     """
#     # Add custom migration logic here
#     pass


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())