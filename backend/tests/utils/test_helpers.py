"""
Test Utilities and Helpers

Common utilities and helper functions for testing.
Reduces code duplication across test files.
"""

from typing import Dict, Any, Optional
from unittest.mock import Mock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class MockQueryResult:
    """Mock SQLAlchemy query result."""
    
    def __init__(self, return_value: Any = None, scalar_return: Any = None):
        self.return_value = return_value
        self.scalar_return = scalar_return or 0
    
    def scalar_one_or_none(self):
        """Mock scalar_one_or_none method."""
        return self.return_value
    
    def scalar(self):
        """Mock scalar method."""
        return self.scalar_return


def create_mock_db_session(user_return: Any = None, count_return: int = 0) -> Mock:
    """
    Create a mock database session with common query patterns.
    
    Args:
        user_return: What to return for user queries
        count_return: What to return for count queries
        
    Returns:
        Mock database session
    """
    mock_db = Mock(spec=Session)
    
    # Mock user query
    mock_db.execute.return_value = MockQueryResult(user_return, count_return)
    
    # Mock transaction methods - these should not raise exceptions
    mock_db.commit.return_value = None
    mock_db.rollback.return_value = None
    mock_db.refresh.return_value = None
    mock_db.add.return_value = None  # This is key - add() should not fail
    
    return mock_db


def create_auth_headers(token: str) -> Dict[str, str]:
    """
    Create authentication headers for testing.
    
    Args:
        token: JWT token
        
    Returns:
        Headers dictionary
    """
    return {"Authorization": f"Bearer {token}"}


def assert_api_response_format(response_data: Dict[str, Any], success: bool = True):
    """
    Assert that API response follows our standard format.
    
    Args:
        response_data: Response JSON data
        success: Expected success status
    """
    assert "success" in response_data
    assert "data" in response_data
    assert "message" in response_data
    assert "errorCode" in response_data
    assert response_data["success"] == success
    
    if success:
        assert response_data["errorCode"] is None
    else:
        assert response_data["errorCode"] is not None
        assert isinstance(response_data["errorCode"], str)
        # For error cases, data should be None
        assert response_data["data"] is None


def assert_user_data_format(user_data: Dict[str, Any]):
    """
    Assert that user data follows the expected format.
    
    Args:
        user_data: User data dictionary
    """
    required_fields = [
        "user_id", "user_name", "email", "profile_picture", 
        "created_at", "follower_count", "following_count", "is_private"
    ]
    
    for field in required_fields:
        assert field in user_data, f"Missing required field: {field}"


class APITestClient:
    """Enhanced test client with convenience methods."""
    
    def __init__(self, client: TestClient):
        self.client = client
    
    def get_with_auth(self, url: str, token: str, **kwargs):
        """Make GET request with authentication."""
        headers = create_auth_headers(token)
        return self.client.get(url, headers=headers, **kwargs)
    
    def post_with_auth(self, url: str, token: str, json_data: Dict = None, **kwargs):
        """Make POST request with authentication."""
        headers = create_auth_headers(token)
        return self.client.post(url, headers=headers, json=json_data, **kwargs)
    
    def patch_with_auth(self, url: str, data: dict, token: str):
        """Make PATCH request with authentication."""
        headers = create_auth_headers(token)
        return self.client.patch(url, json=data, headers=headers)

    def delete_with_auth(self, url: str, token: str, **kwargs):
        """Make DELETE request with authentication."""
        headers = create_auth_headers(token)
        return self.client.delete(url, headers=headers, **kwargs)


def mock_dependency_override(app, dependency, override_value):
    """
    Context manager for temporarily overriding FastAPI dependencies.
    
    Args:
        app: FastAPI app instance
        dependency: Dependency to override
        override_value: Value to override with
    """
    class DependencyOverride:
        def __enter__(self):
            app.dependency_overrides[dependency] = lambda: override_value
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            app.dependency_overrides.pop(dependency, None)
    
    return DependencyOverride()


# Constants for testing
TEST_USER_ID = "550e8400-e29b-41d4-a716-446655440000"
TEST_PRIVATE_USER_ID = "550e8400-e29b-41d4-a716-446655440001"
TEST_EMAIL = "test@example.com"
TEST_USERNAME = "testuser"
TEST_PROFILE_PICTURE = "https://example.com/photo.jpg"

# Common test data
SAMPLE_USER_DATA = {
    "user_id": TEST_USER_ID,
    "user_name": TEST_USERNAME,
    "email": TEST_EMAIL,
    "profile_picture": TEST_PROFILE_PICTURE,
    "is_private": False,
    "follower_count": 0,
    "following_count": 0
}
