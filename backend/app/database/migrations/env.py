"""
GDPR Tool Database Migrations - Alembic Environment Configuration

This module provides the Alembic environment configuration for database migrations
in the GDPR compliance tool. It handles both online and offline migration modes
with proper database connection and metadata management.

Key Components:
- Alembic Configuration: Database URL and metadata configuration
- Migration Modes: Online and offline migration support
- Database Connection: SQLAlchemy engine configuration for migrations
- Metadata Management: Base model metadata for autogenerate support

Migration Features:
- Online Migrations: Live database migrations with active connections
- Offline Migrations: Offline migrations for script generation
- Autogenerate Support: Automatic migration generation from model changes
- Database URL Configuration: Dynamic database URL from settings
- Logging Configuration: Proper logging setup for migration operations
- Connection Pooling: Null pool configuration for migration operations

Configuration:
- Database URL: Automatically configured from settings.DATABASE_URL
- Metadata: Uses Base.metadata from database models
- Logging: Configures logging from alembic.ini file
- Connection: SQLAlchemy engine configuration for migrations

Migration Modes:
- Online Mode: Creates database engine and runs migrations with live connection
- Offline Mode: Generates migration scripts without database connection
- Context Management: Proper transaction and connection management

The module ensures proper database migration execution and provides a robust
foundation for schema evolution in the GDPR compliance tool.
"""

from logging.config import fileConfig
from database.models import Base
from sqlalchemy import engine_from_config
from sqlalchemy import pool
import settings
from alembic import context
import logging

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()
            

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
