"""
Database test application helper for creating and managing test data.
"""

from uuid import UUID, uuid4
from datetime import datetime, timezone
from app.core.database import get_db
from app.models.user import User
from app.models.post import Post
from app.models.conversation import Conversation
from app.models.message import Message
from sqlalchemy.orm import Session


class TestApp:
    """Helper class for managing test database setup and teardown"""
    
    def __init__(self):
        """Initialize test app with database session"""
        self.db: Session = next(get_db())
        self._created_objects = []
    
    def create_test_user(self, user_id: str = None, username: str = "test_user", email: str = "test@example.com"):
        """Create a test user"""
        if user_id is None:
            from uuid import uuid4
            user_id = str(uuid4())
        
        user = User(
            user_id=UUID(user_id),
            user_name=username,
            email=email,
            status="active",
            created_at=datetime.now(timezone.utc)
        )
        
        self.db.add(user)
        self.db.flush()
        self._created_objects.append(user)
        return user
    
    def create_test_post(self, post_id: str, user_id: str, title: str = "Test Post", 
                        content: str = "Test content", fork_count: int = 0):
        """Create a test post"""
        # Ensure user exists
        user = self.db.query(User).filter(User.user_id == UUID(user_id)).first()
        if not user:
            user = self.create_test_user(user_id=user_id)
        
        # Create a conversation for the post
        conversation = Conversation(
            conversation_id=uuid4(),
            user_id=UUID(user_id),
            title=f"Conversation for {title}",
            status="active",
            created_at=datetime.now(timezone.utc)
        )
        
        self.db.add(conversation)
        self.db.flush()
        self._created_objects.append(conversation)
        
        post = Post(
            post_id=UUID(post_id),
            user_id=UUID(user_id),
            conversation_id=conversation.conversation_id,
            title=title,
            content=content,
            status="active",
            fork_count=fork_count,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        self.db.add(post)
        self.db.flush()
        self._created_objects.append(post)
        return post
    
    def delete_post(self, post_id: str):
        """Mark a post as deleted"""
        post = self.db.query(Post).filter(Post.post_id == UUID(post_id)).first()
        if post:
            post.status = "deleted"
            self.db.flush()
    
    def teardown(self):
        """Clean up test data"""
        try:
            # Roll back any uncommitted changes
            self.db.rollback()
            
            # Delete created objects in reverse order
            for obj in reversed(self._created_objects):
                try:
                    self.db.delete(obj)
                except Exception:
                    pass  # Object might already be deleted
            
            self.db.commit()
        except Exception:
            self.db.rollback()
        finally:
            self.db.close()
            self._created_objects.clear()
