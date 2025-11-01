"""Alembic environment configuration for async migrations."""
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Import Base and all models for autogeneration
from app.database import Base
from app.models import Brand, Template, DOMSelector, CodeRule, GeneratedCode

# This is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the target metadata for autogeneration
target_metadata = Base.metadata


def get_url():
    """Get database URL from environment or config."""
    from app.config import settings
    return settings.DATABASE_URL


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations using the provided connection."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode with async engine."""
    # Get config section
    alembic_config = config.get_section(config.config_ini_section, {})
    
    # Set the URL
    alembic_config["sqlalchemy.url"] = get_url()
    
    # Transform DATABASE_URL to use asyncpg driver
    if "sqlalchemy.url" in alembic_config:
        database_url = alembic_config["sqlalchemy.url"]
        if database_url.startswith("postgresql://"):
            alembic_config["sqlalchemy.url"] = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif database_url.startswith("postgres://"):
            alembic_config["sqlalchemy.url"] = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    
    connectable = async_engine_from_config(
        alembic_config,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())