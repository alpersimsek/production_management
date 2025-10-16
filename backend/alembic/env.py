from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import Base

# Import all models to ensure they are registered with Base.metadata
from app.models import *

config = context.config
if config.get_main_option('sqlalchemy.url', default=None) is None:
    # Use environment variable or default
    database_url = os.getenv('DATABASE_URL', 'postgresql+psycopg://olgahan:olgahan@localhost:5433/olgahan')
    config.set_main_option('sqlalchemy.url', database_url)

fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    # Get database URL from environment or config
    database_url = os.getenv('DATABASE_URL', 'postgresql+psycopg://olgahan:olgahan@localhost:5433/olgahan')
    
    # Create engine with the database URL
    connectable = engine_from_config(
        {"sqlalchemy.url": database_url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool
    )
    
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()