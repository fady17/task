# alembic/env.py 

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

import os
import sys

# Add the project root to the Python path
# This allows us to import from the 'app' module
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

# Correctly import our settings, Base, and models
from app.db.config import settings
from app.db.database import Base
from app.db import models


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# ==============================================================================
# THE KEY FIX: Use the SYNC database URL for Alembic's operations.
# Alembic is a synchronous tool and cannot use the asyncpg driver.
config.set_main_option('sqlalchemy.url', settings.DATABASE_URL_SYNC)
# ==============================================================================


# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Set the target metadata for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    # This offline mode is less common for our use case, but we'll leave it
    # correctly configured. It uses the URL directly.
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
    """Run migrations in 'online' mode."""
    # This is the mode we typically use. It creates an engine and a
    # real connection to the database to perform the migration.
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