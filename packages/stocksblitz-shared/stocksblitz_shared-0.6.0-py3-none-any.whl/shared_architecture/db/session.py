import os
import logging
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from shared_architecture.config.config_loader import config_loader

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Dynamically construct the database URL from environment variables
def get_database_url() -> str:
    try:
        # FIXED: Use tradmin as default user for tradingdb schema consistency
        db_user = os.getenv("TIMESCALEDB_USER", os.getenv("POSTGRES_USER", "tradmin"))
        db_password = os.getenv("TIMESCALEDB_PASSWORD", os.getenv("POSTGRES_PASSWORD", "tradpass"))
        db_host = os.getenv("TIMESCALEDB_HOST", os.getenv("POSTGRES_HOST", "localhost"))
        db_port = os.getenv("TIMESCALEDB_PORT", os.getenv("POSTGRES_PORT", "5432"))
        # FIXED: Use tradingdb as default database name
        db_name = os.getenv("TIMESCALEDB_DB", os.getenv("POSTGRES_DATABASE", "tradingdb"))

        database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        logger.info(f"DATABASE_URL: {database_url}")  # Debugging log
        return database_url

    except Exception as e:
        logger.error(f"Failed to construct database URL: {e}")
        raise RuntimeError(f"Failed to construct database URL: {e}") from e

DATABASE_URL = get_database_url()
# FIXED: Configure engine with tradingdb schema search path
engine = create_engine(
    DATABASE_URL,
    connect_args={"options": "-csearch_path=tradingdb,public"}
)

# Initial SessionLocal will be replaced by get_session_local() function
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
logger.info(f"Database session configuration loaded (schema: tradingdb)")  # Debugging log

# Dependency to provide database session
def get_db() -> Any:
    session_maker = get_session_local()
    db: Session = session_maker()
    try:
        logger.info(f"Database session created: {db.bind.url}")  # Debugging log
        yield db
    finally:
        logger.info("Closing database session")  # Debugging log
        db.close()


async def get_async_db() -> AsyncSession:
    """Async database session dependency for FastAPI"""
    session_maker = get_async_session_local()
    async with session_maker() as session:
        try:
            logger.info(f"Async database session created: {session.bind.url}")
            yield session
        finally:
            logger.info("Closing async database session")
            await session.close()

# Construct URLs from environment variables
db_user = os.getenv("TIMESCALEDB_USER", "tradmin")
db_password = os.getenv("TIMESCALEDB_PASSWORD", "tradpass")
db_host = os.getenv("TIMESCALEDB_HOST", "localhost")
db_port = os.getenv("TIMESCALEDB_PORT", "5432")
db_name = os.getenv("TIMESCALEDB_DB", "tradingdb")

DB_URL_ASYNC = config_loader.get("TIMESCALEDB_URL_ASYNC", f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")
DB_URL_SYNC = config_loader.get("TIMESCALEDB_URL", f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")

# === Async Engine (used for FastAPI + async ORM operations) ===
# FIXED: Configure async engine with tradingdb schema search path
# Defer engine creation to avoid import-time issues
async_engine = None

def get_async_engine():
    global async_engine
    if async_engine is None:
        try:
            async_engine = create_async_engine(
                DB_URL_ASYNC,
                echo=False,
                pool_pre_ping=True,
                future=True,
                connect_args={"server_settings": {"search_path": "tradingdb,public"}}
            )
        except Exception as e:
            logger.warning(f"Failed to create async engine: {e}")
            # Create a minimal fallback async engine for local development
            fallback_url = "postgresql+asyncpg://stocksblitz:stocksblitz@localhost:5432/stocksblitz"
            async_engine = create_async_engine(
                fallback_url,
                echo=False,
                pool_pre_ping=True,
                future=True,
                connect_args={"server_settings": {"search_path": "tradingdb,public"}}
            )
    return async_engine

# Async session maker for FastAPI
def get_async_session_local():
    return async_sessionmaker(
        bind=get_async_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
    )

# For backward compatibility
AsyncSessionLocal = None

# === Sync Engine (used for Alembic migrations or blocking operations) ===
# FIXED: Configure sync engine with tradingdb schema search path
# Defer engine creation to avoid import-time issues
sync_engine = None

def get_sync_engine():
    global sync_engine
    if sync_engine is None:
        try:
            sync_engine = create_engine(
                DB_URL_SYNC,
                pool_pre_ping=True,
                future=True,
                connect_args={"options": "-csearch_path=tradingdb,public"}
            )
        except Exception as e:
            logger.warning(f"Failed to create sync engine: {e}")
            # Create a minimal fallback sync engine for local development
            fallback_url = "postgresql://stocksblitz:stocksblitz@localhost:5432/stocksblitz"
            sync_engine = create_engine(
                fallback_url,
                pool_pre_ping=True,
                future=True,
                connect_args={"options": "-csearch_path=tradingdb,public"}
            )
    return sync_engine

# Sync session maker (override the earlier one with schema-aware engine)
def get_session_local():
    return sessionmaker(autocommit=False, autoflush=False, bind=get_sync_engine())

# For backward compatibility
SessionLocal = None