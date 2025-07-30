"""
Database management for fp-admin.

This module provides database connection management, session handling,
and utility functions for database operations.
"""

import logging
from contextlib import contextmanager
from typing import Any, Generator, Optional

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, SQLModel, create_engine, select

from fp_admin.exceptions import DatabaseError
from fp_admin.settings_loader import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database manager for handling connections and sessions."""

    def __init__(self, database_url: str, echo: bool = False):
        """Initialize database manager.

        Args:
            database_url: Database connection URL
            echo: Enable SQL query logging
        """
        self.database_url = database_url
        self.echo = echo
        self._engine: Optional[Engine] = None
        self._session_factory = None

    @property
    def engine(self) -> Engine:
        """Get database engine, creating it if necessary."""
        if self._engine is None:
            try:
                self._engine = create_engine(
                    self.database_url,
                    echo=self.echo,
                    pool_pre_ping=True,
                    pool_recycle=300,
                )
                logger.info("Database engine created for %s", self.database_url)
            except Exception as e:
                logger.error("Failed to create database engine: %s", e)
                raise DatabaseError(f"Failed to create database engine: {e}") from e
        return self._engine

    def create_tables(self) -> None:
        """Create all database tables."""
        try:
            SQLModel.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
        except SQLAlchemyError as e:
            logger.error("Failed to create database tables: %s", e)
            raise DatabaseError(f"Failed to create database tables: {e}") from e

    def drop_tables(self) -> None:
        """Drop all database tables."""
        try:
            SQLModel.metadata.drop_all(self.engine)
            logger.info("Database tables dropped successfully")
        except SQLAlchemyError as e:
            logger.error("Failed to drop database tables: %s", e)
            raise DatabaseError(f"Failed to drop database tables: {e}") from e

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get database session with automatic cleanup.

        Yields:
            Database session

        Example:
            with db_manager.get_session() as session:
                result = session.exec(select(User)).all()
        """
        session = Session(self.engine)
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def health_check(self) -> bool:
        """Check database connectivity.

        Returns:
            True if database is accessible, False otherwise
        """
        try:
            with self.get_session() as session:
                session.execute(select(1))
            return True
        except (SQLAlchemyError, ConnectionError, OSError) as e:
            logger.error("Database health check failed: %s", e)
            return False

    def get_table_names(self) -> list[str]:
        """Get list of table names in the database.

        Returns:
            List of table names
        """
        try:
            with self.get_session() as session:
                result = session.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table'")
                )
                return [row[0] for row in result]
        except (SQLAlchemyError, ConnectionError, OSError) as e:
            logger.error("Failed to get table names: %s", e)
            return []

    def get_table_info(self, table_name: str) -> dict[str, Any]:
        """Get information about a specific table.

        Args:
            table_name: Name of the table

        Returns:
            Dictionary with table information
        """
        try:
            with self.get_session() as session:
                result = session.execute(text(f"PRAGMA table_info({table_name})"))
                columns = []
                for row in result:
                    columns.append(
                        {
                            "name": row[1],
                            "type": row[2],
                            "not_null": bool(row[3]),
                            "primary_key": bool(row[5]),
                        }
                    )
                return {
                    "name": table_name,
                    "columns": columns,
                    "column_count": len(columns),
                }
        except (SQLAlchemyError, ConnectionError, OSError) as e:
            logger.error("Failed to get table info for %s: %s", table_name, e)
            return {"name": table_name, "columns": [], "column_count": 0}


# Global database manager instance
db_manager = DatabaseManager(
    database_url=settings.DATABASE_URL, echo=settings.DATABASE_ECHO
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database session.

    Yields:
        Database session
    """
    with db_manager.get_session() as session:
        yield session


def check_database_health() -> bool:
    """Check if database is healthy.

    Returns:
        True if database is healthy, False otherwise
    """
    return db_manager.health_check()


# Export for backward compatibility
__all__ = [
    "DatabaseManager",
    "db_manager",
    "get_db",
    "check_database_health",
]
