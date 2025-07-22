"""
Enhanced test fixtures for posts API with better data isolation.
"""

import pytest
from datetime import datetime, timezone, timedelta
import uuid

from app.models.user import User
from app.models.tag import Tag
from app.models.conversation import Conversation
from app.models.post import Post
from app.models.post_tag import PostTag
from app.models.post_reaction import PostReaction


@pytest.fixture
def comprehensive_test_data(db_session):
    """
    Create a comprehensive set of test data for posts API testing.
    
    This fixture creates all related data (users, tags, conversations, posts, reactions)
    in a single transaction to ensure data consistency and visibility.
    """
    # Create users
    users = []
    for i in range(5):
        user = User(
            user_name=f"test_user_{i}",
            email=f"test{i}@example.com",
            status="active"
        )
        db_session.add(user)
        users.append(user)
    
    # Flush to get user IDs
    db_session.flush()
    
    # Create tags
    tag_names = ["ai", "tech", "python", "javascript", "machine-learning", "web-dev", "data-science"]
    tags = []
    for name in tag_names:
        tag = Tag(name=name)
        db_session.add(tag)
        tags.append(tag)
    
    # Flush to get tag IDs
    db_session.flush()
    
    # Create conversations
    conversations = []
    for i, user in enumerate(users):
        conversation = Conversation(
            user_id=user.user_id,
            title=f"Test Conversation {i + 1}",
            status="active"
        )
        db_session.add(conversation)
        conversations.append(conversation)
    
    # Flush to get conversation IDs
    db_session.flush()
    
    # Create posts with varied timestamps
    posts = []
    base_time = datetime.now(timezone.utc)
    time_offsets = [
        timedelta(minutes=15),     # Very recent
        timedelta(minutes=45),     # Recent
        timedelta(hours=2),        # Few hours ago
        timedelta(hours=6),        # Earlier today
        timedelta(days=1),         # Yesterday
        timedelta(days=3),         # Few days ago
        timedelta(days=7),         # Week ago
        timedelta(days=15),        # Two weeks ago
        timedelta(days=30),        # Month ago
        timedelta(days=45),        # Over a month ago
    ]
    
    post_titles = [
        "Introduction to Machine Learning",
        "Best Practices in Python Development", 
        "JavaScript Framework Comparison",
        "Building Scalable Web Applications",
        "Data Science Tools and Techniques",
        "AI Ethics and Responsible Development",
        "Modern Frontend Development",
        "Backend Architecture Patterns",
        "Cloud Computing Fundamentals",
        "Open Source Contribution Guide"
    ]
    
    for i in range(min(len(time_offsets), len(post_titles))):
        user_idx = i % len(users)
        conversation_idx = i % len(conversations)
        
        post = Post(
            user_id=users[user_idx].user_id,
            conversation_id=conversations[conversation_idx].conversation_id,
            title=post_titles[i],
            content=f"This is the content for {post_titles[i]}. " + 
                   "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 5,
            is_conversation_visible=True,
            edited=False,
            status="active",
            created_at=base_time - time_offsets[i],
            updated_at=base_time - time_offsets[i]
        )
        db_session.add(post)
        posts.append(post)
    
    # Flush again to get post IDs
    db_session.flush()
    
    # Add tags to posts (varied distribution)
    for i, post in enumerate(posts):
        # Each post gets 1-3 tags
        num_tags = (i % 3) + 1
        for j in range(num_tags):
            tag_index = (i + j) % len(tags)
            post_tag = PostTag(
                post_id=post.post_id,
                tag_id=tags[tag_index].tag_id
            )
            db_session.add(post_tag)
    
    # Create realistic reactions for voting (ensure unique user-post combinations)
    reactions = []
    reaction_patterns = [
        {"upvotes": 3, "downvotes": 1},   # Positive feedback
        {"upvotes": 4, "downvotes": 0},   # Well received
        {"upvotes": 2, "downvotes": 1},   # Mixed
        {"upvotes": 1, "downvotes": 2},   # Negative
        {"upvotes": 5, "downvotes": 0},   # Very popular
        {"upvotes": 0, "downvotes": 1},   # Downvoted
        {"upvotes": 3, "downvotes": 2},   # Controversial
        {"upvotes": 1, "downvotes": 0},   # Minimal engagement
        {"upvotes": 4, "downvotes": 1},   # Good reception
        {"upvotes": 0, "downvotes": 0},   # No votes yet
    ]
    
    for i, post in enumerate(posts):
        if i < len(reaction_patterns):
            pattern = reaction_patterns[i]
            used_users = set()  # Track users who already voted on this post
            
            # Add upvotes (ensure unique users per post)
            upvotes_added = 0
            for j in range(pattern["upvotes"]):
                user_idx = (i + j) % len(users)
                if users[user_idx].user_id not in used_users and upvotes_added < pattern["upvotes"]:
                    reaction = PostReaction(
                        user_id=users[user_idx].user_id,
                        post_id=post.post_id,
                        reaction="upvote",
                        status="active"
                    )
                    db_session.add(reaction)
                    reactions.append(reaction)
                    used_users.add(users[user_idx].user_id)
                    upvotes_added += 1
            
            # Add downvotes (ensure unique users per post)
            downvotes_added = 0
            for j in range(pattern["downvotes"]):
                user_idx = (i + j + pattern["upvotes"]) % len(users)
                if users[user_idx].user_id not in used_users and downvotes_added < pattern["downvotes"]:
                    reaction = PostReaction(
                        user_id=users[user_idx].user_id,
                        post_id=post.post_id,
                        reaction="downvote",
                        status="active"
                    )
                    db_session.add(reaction)
                    reactions.append(reaction)
                    used_users.add(users[user_idx].user_id)
                    downvotes_added += 1
    
    # Commit all data
    db_session.commit()
    
    return {
        "users": users,
        "tags": tags,
        "conversations": conversations,
        "posts": posts,
        "reactions": reactions
    }
