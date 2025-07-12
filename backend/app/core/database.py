"""
Database Connection and Session Management

This file sets up SQLAlchemy for database operations.
It provides:
1. Database engine creation
2. Session management
3. Base model class for all database models
4. Dependency for getting database sessions in routes

Why SQLAlchemy?
- ORM: Object-Relational Mapping makes database operations more Pythonic
- Type safety: Works well with Python type hints
- Migration support: Alembic integration for schema changes
- Performance: Connection pooling and lazy loading
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from typing import Generator

from app.core.config import settings


# Create Base class for all database models using SQLAlchemy 2.0 syntax
class Base(DeclarativeBase):
    pass


# Create SQLAlchemy engine
# This manages the actual database connections
engine = create_engine(
    settings.DATABASE_URL,
    # Connection pool settings for production
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,    # Recycle connections every 5 minutes
    echo=settings.DEBUG  # Log SQL queries in debug mode
)

# Create SessionLocal class
# Each instance will be a database session
SessionLocal = sessionmaker(
    autocommit=False,    # Don't auto-commit transactions
    autoflush=False,     # Don't auto-flush changes
    bind=engine          # Bind to our database engine
)


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency.

    This function is used with FastAPI's dependency injection system.
    It provides a database session to route handlers and automatically
    closes the session when the request is complete.

    Usage in routes:
        @router.get("/users/")
        def get_users(db: Session = Depends(get_db)):
            # Use db here for database operations
            return db.query(User).all()

    The 'yield' keyword makes this a generator function, which FastAPI
    uses to handle cleanup automatically.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all database tables.

    This function creates all tables defined in our models.
    In production, we'll use Alembic migrations instead.

    Usage:
        from app.core.database import create_tables
        create_tables()
    """
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """
    Drop all database tables.

    ⚠️  DANGER: This deletes all data!
    Only use for development/testing.
    """
    Base.metadata.drop_all(bind=engine)


# Database utility functions

class DatabaseManager:
    """
    Database management utilities.

    This class provides helpful methods for database operations
    that you might need during development or testing.
    """

    @staticmethod
    def get_session() -> Session:
        """
        Get a database session outside of FastAPI routes.

        Useful for:
        - Database scripts
        - Testing
        - Background tasks

        Remember to close the session when done!
        """
        return SessionLocal()

    @staticmethod
    def health_check() -> bool:
        """
        Check if database connection is healthy.

        Returns True if database is accessible, False otherwise.
        """
        try:
            from sqlalchemy import text
            db = SessionLocal()
            # Try a simple query using SQLAlchemy 2.0 syntax
            db.execute(text("SELECT 1"))
            db.close()
            return True
        except Exception as e:
            print(f"Database health check failed: {e}")
            return False

    @staticmethod
    def get_table_info():
        """
        Get information about database tables.

        Useful for debugging and development.
        """
        from sqlalchemy import inspect

        inspector = inspect(engine)
        tables = inspector.get_table_names()

        print("📊 Database Tables:")
        for table in tables:
            columns = inspector.get_columns(table)
            print(f"  {table}:")
            for column in columns:
                print(f"    - {column['name']} ({column['type']})")


# Example usage in your code:
#
# # In a route handler:
# @router.get("/users/")
# def get_users(db: Session = Depends(get_db)):
#     users = db.query(User).all()
#     return users
#
# # In a script:
# from app.core.database import DatabaseManager
# db = DatabaseManager.get_session()
# users = db.query(User).all()
# db.close()