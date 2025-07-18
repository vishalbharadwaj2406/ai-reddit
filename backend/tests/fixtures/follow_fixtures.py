"""
Follow Test Fixtures

Fixtures for testing follow relationships and Instagram-like privacy features.
"""

import pytest
from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import Mock

from app.models.follow import Follow
from app.models.user import User


@pytest.fixture
def sample_follow_pending():
    """Create a sample pending follow request"""
    return Follow(
        follower_id=uuid4(),
        following_id=uuid4(),
        status="pending",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


@pytest.fixture
def sample_follow_accepted():
    """Create a sample accepted follow relationship"""
    return Follow(
        follower_id=uuid4(),
        following_id=uuid4(),
        status="accepted",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


@pytest.fixture
def sample_private_user():
    """Create a sample private user"""
    return User(
        user_id=uuid4(),
        user_name="private_user",
        email="private@example.com",
        google_id="google_12345",
        is_private=True,
        status="active",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


@pytest.fixture
def sample_public_user():
    """Create a sample public user"""
    return User(
        user_id=uuid4(),
        user_name="public_user",
        email="public@example.com",
        google_id="google_67890",
        is_private=False,
        status="active",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


@pytest.fixture
def mock_follow_repository():
    """Mock FollowRepository for testing"""
    mock_repo = Mock()
    mock_repo.get_follow_relationship.return_value = None
    mock_repo.create_follow_request.return_value = None
    mock_repo.create_instant_follow.return_value = None
    mock_repo.accept_follow_request.return_value = None
    mock_repo.reject_follow_request.return_value = False
    mock_repo.unfollow.return_value = False
    mock_repo.get_followers.return_value = []
    mock_repo.get_following.return_value = []
    mock_repo.get_pending_requests.return_value = []
    mock_repo.get_follower_count.return_value = 0
    mock_repo.get_following_count.return_value = 0
    return mock_repo


@pytest.fixture
def mock_follow_service():
    """Mock FollowService for testing"""
    mock_service = Mock()
    mock_service.follow_user.return_value = {
        "success": True,
        "message": "Follow request sent",
        "follow_status": "pending"
    }
    mock_service.unfollow_user.return_value = {
        "success": True,
        "message": "Unfollowed user successfully",
        "follow_status": "none"
    }
    mock_service.get_follow_status.return_value = "none"
    mock_service.accept_follow_request.return_value = {
        "success": True,
        "message": "Follow request accepted"
    }
    mock_service.reject_follow_request.return_value = {
        "success": True,
        "message": "Follow request rejected"
    }
    mock_service.get_follow_requests.return_value = {
        "success": True,
        "message": "Follow requests retrieved successfully",
        "data": {"requests": [], "count": 0}
    }
    mock_service.get_enhanced_follow_status.return_value = {
        "follow_status": "none",
        "is_following": False,
        "request_pending": False,
        "follows_you": False,
        "ui_context": {
            "button_text": "Follow",
            "button_action": "follow",
            "can_send_request": True
        }
    }
    return mock_service


@pytest.fixture
def sample_follower_data():
    """Sample follower data for testing"""
    return {
        "user_id": str(uuid4()),
        "user_name": "follower1",
        "profile_picture": "https://example.com/follower1.jpg",
        "is_private": False,
        "followed_at": "2024-01-01T00:00:00Z",
        "follow_status": {
            "follow_status": "none",
            "is_following": False,
            "request_pending": False,
            "follows_you": False
        }
    }


@pytest.fixture
def sample_following_data():
    """Sample following data for testing"""
    return {
        "user_id": str(uuid4()),
        "user_name": "following1",
        "profile_picture": "https://example.com/following1.jpg",
        "is_private": False,
        "followed_at": "2024-01-01T00:00:00Z",
        "follow_status": {
            "follow_status": "accepted",
            "is_following": True,
            "request_pending": False,
            "follows_you": False
        }
    }


@pytest.fixture
def sample_pagination_data():
    """Sample pagination data for testing"""
    return {
        "total_count": 25,
        "limit": 10,
        "offset": 10,
        "has_next": True,
        "has_previous": True
    }


@pytest.fixture
def mock_follow_relationships(sample_user, sample_public_user, sample_private_user):
    """Mock follow relationships for testing"""
    return [
        Follow(
            follower_id=sample_user.user_id,
            following_id=sample_public_user.user_id,
            status="accepted",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ),
        Follow(
            follower_id=sample_user.user_id,
            following_id=sample_private_user.user_id,
            status="pending",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
    ]
