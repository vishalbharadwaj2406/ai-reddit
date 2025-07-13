"""
Model-Specific Test Fixtures

This file contains fixtures specific to model testing.
"""

import pytest
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.post import Post
from app.models.comment import Comment


@pytest.fixture
def sample_user(db_session):
    """
    Create a sample user for general testing.
    
    This is a basic user that can be used across different model tests.
    """
    user = User(
        user_name="sample_user",
        email="sample@example.com"
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def conversation_user(db_session):
    """
    Create a user specifically for conversation tests.
    
    This user has a more descriptive name for conversation-related tests.
    """
    user = User(
        user_name="conversation_user",
        email="conv@example.com"
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def sample_conversation(db_session, conversation_user):
    """
    Create a sample conversation for tests that need one.
    
    This creates a basic conversation linked to conversation_user.
    """
    conversation = Conversation(
        user_id=conversation_user.user_id,
        title="Sample Conversation"
    )
    db_session.add(conversation)
    db_session.commit()
    return conversation


@pytest.fixture
def sample_message(db_session, sample_conversation):
    """Create a sample message for tests."""
    message = Message(
        conversation_id=sample_conversation.conversation_id,
        user_id=sample_conversation.user_id,
        role="user",
        content="Sample message for testing"
    )
    db_session.add(message)
    db_session.commit()
    return message


@pytest.fixture
def sample_post(db_session, sample_user):
    """Create a sample post for tests."""
    # First create a conversation for the post
    conversation = Conversation(
        user_id=sample_user.user_id,
        title="Sample Conversation for Post"
    )
    db_session.add(conversation)
    db_session.commit()
    
    # Then create the post
    post = Post(
        user_id=sample_user.user_id,
        conversation_id=conversation.conversation_id,
        title="Sample Post",
        content="This is a sample post for testing purposes."
    )
    db_session.add(post)
    db_session.commit()
    return post


@pytest.fixture
def sample_comment(db_session, sample_user, sample_post):
    """Create a sample comment for tests."""
    comment = Comment(
        post_id=sample_post.post_id,
        user_id=sample_user.user_id,
        content="This is a sample comment for testing."
    )
    db_session.add(comment)
    db_session.commit()
    return comment
