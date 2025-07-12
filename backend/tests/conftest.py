"""
Global Test Configuration and Fixtures

This file contains shared fixtures and configuration used across all tests.
"""

import pytest
import sys
import os
from sqlalchemy.orm import Session

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "app"))

from app.core.database import get_db, create_tables, drop_tables, Base, engine
from app.models.user import User
from app.models.conversation import Conversation


@pytest.fixture
def db_session():
    """
    Create a fresh database session for each test.
    
    This fixture:
    1. Drops all tables (clean slate)
    2. Creates fresh tables
    3. Provides a database session
    4. Cleans up after test completes
    """
    drop_tables()
    create_tables()
    db = next(get_db())
    yield db
    db.close()
    drop_tables()


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
    """Provide access to the database engine for advanced tests."""
    return engine


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
