"""
Global Test Configuration and Fixtures

This file contains shared fixtures and configuration used across all tests.
"""

import pytest
import sys
import os
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "app"))

from app.core.database import get_db, Base
from app.models.user import User
from app.models.conversation import Conversation
from app.main import app


# =====================================================
# TEST DATABASE CONFIGURATION  
# =====================================================
# SAFETY: Use local PostgreSQL test database to prevent
# accidentally affecting production Supabase database

# Use local PostgreSQL test database - complete production parity
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", 
    "postgresql://test_user:test_password@localhost:5432/ai_social_test"
)

# Create separate test engine and session
test_engine = create_engine(
    TEST_DATABASE_URL,
    echo=False  # Set to True for SQL debugging  
)

TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False, 
    bind=test_engine
)


@pytest.fixture(scope="function")  
def db_session():
    """
    Create a database session with transaction rollback for complete test isolation.
    
    SAFETY: Uses local PostgreSQL test database to prevent
    accidentally affecting production Supabase database.
    
    This fixture:
    1. Creates fresh tables in local PostgreSQL test database
    2. Starts a transaction for each test
    3. Provides a clean database session with production parity  
    4. Rolls back the transaction after each test (no data persists)
    """
    # Create all tables in the local PostgreSQL test database
    Base.metadata.create_all(bind=test_engine)
    
    # Create a connection and start a transaction
    connection = test_engine.connect()
    transaction = connection.begin()
    
    # Create a session bound to this connection
    session = TestSessionLocal(bind=connection)
    
    try:
        yield session
    finally:
        # Clean shutdown: close session first, then rollback, then close connection
        try:
            session.close()
        except:
            pass
        try:
            transaction.rollback()
        except:
            pass
        try:
            connection.close()
        except:
            pass


@pytest.fixture
def client(db_session):
    """
    Create a FastAPI test client with isolated test database session.
    
    SAFETY: This overrides the get_db dependency to use our
    isolated local PostgreSQL test database instead of production Supabase.
    
    This fixture:
    1. Overrides get_db to use test database session
    2. Creates a TestClient for making API requests  
    3. Provides complete isolation between tests with production parity
    """
    # Override the get_db dependency to use our test database session
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test client
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user(db_session):
    """
    Create a sample user for tests that need a user.
    
    This creates a basic user that can be used in relationship tests.
    """
    user = User(
        user_name="test_user",
        email="test@example.com"
    )
    db_session.add(user)
    db_session.commit()
    return user


# Database utility fixtures

@pytest.fixture
def db_engine():
    """Provide access to the TEST database engine for advanced tests."""
    return test_engine


@pytest.fixture
def db_metadata():
    """Provide access to SQLAlchemy metadata for schema tests."""
    return Base.metadata


# Test configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for component interactions"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take longer than 1 second"
    )
