#!/usr/bin/env python3
"""
Debug script to understand the posts endpoint issues
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.user import User
from app.models.post import Post
from app.core.database import get_db


def test_posts_endpoint_debug():
    """Debug the posts endpoint"""
    print("=== DEBUGGING POSTS ENDPOINT ===")
    
    # Create sample user
    user = Mock()
    user.user_id = uuid4()
    user.user_name = "testuser"
    user.email = "test@example.com"
    user.profile_picture = "https://example.com/pic.jpg"
    user.created_at = datetime.now()
    
    # Create sample post
    post = Mock()
    post.post_id = uuid4()
    post.title = "Test Post"
    post.content = "Test content"
    post.user_id = user.user_id
    post.created_at = datetime.now()
    post.updated_at = datetime.now()
    post.is_conversation_visible = True
    post.status = "published"
    post.fork_count = 0
    post.user = user  # Add user reference
    
    # Mock database
    mock_db = Mock(spec=Session)
    
    # Test 1: Empty result (should work)
    print("Test 1: Empty result")
    mock_db.query.return_value.join.return_value.outerjoin.return_value.group_by.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
    app.dependency_overrides[get_db] = lambda: mock_db
    
    client = TestClient(app)
    response = client.get("/api/v1/posts/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 2: With sample posts
    print("\nTest 2: With sample posts")
    mock_db.query.return_value.join.return_value.outerjoin.return_value.group_by.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [post]
    
    # Mock the _create_post_response method calls
    # We need to mock Tag queries
    mock_db.query.return_value.join.return_value.filter.return_value.all.return_value = []  # tags
    
    # Mock reaction queries  
    mock_db.query.return_value.filter.return_value.group_by.return_value.all.return_value = []  # reactions
    
    response = client.get("/api/v1/posts/")
    print(f"Status: {response.status_code}")
    print(f"Response text: {response.text}")
    
    app.dependency_overrides.clear()


if __name__ == "__main__":
    test_posts_endpoint_debug()
