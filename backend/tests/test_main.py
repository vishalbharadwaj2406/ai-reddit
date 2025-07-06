"""
Test Main Application

Basic tests to verify the FastAPI application is set up correctly.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

# Create test client
client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint returns correct response."""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data
    assert data["message"] == "AIkya API is running!"


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"


def test_docs_available():
    """Test that API documentation is available."""
    response = client.get("/docs")
    assert response.status_code == 200

    response = client.get("/redoc")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_app_startup():
    """Test that the app can start up without errors."""
    # This test ensures our app factory works correctly
    from app.main import create_application

    test_app = create_application()
    assert test_app is not None
    assert test_app.title == "AIkya"