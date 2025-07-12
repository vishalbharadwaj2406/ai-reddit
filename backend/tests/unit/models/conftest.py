"""
Model-Specific Test Fixtures

This file contains fixtures specific to model testing.
"""

import pytest
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message


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


# Future fixtures will go here as we add more models
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

# @pytest.fixture  
# def sample_post(db_session, sample_user):
#     """Create a sample post for tests."""
#     pass
