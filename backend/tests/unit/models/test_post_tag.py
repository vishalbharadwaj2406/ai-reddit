"""
PostTag Model Tests

Comprehensive test suite for the PostTag model.
Tests cover:
- PostTag creation and validation
- Many-to-many relationship functionality
- Composite primary key constraints
- Cascade behavior
- Helper methods and properties
"""

import pytest
import warnings
from sqlalchemy.exc import IntegrityError

from app.models.post_tag import PostTag
from app.models.post import Post
from app.models.tag import Tag
from app.models.user import User
from app.models.conversation import Conversation


class TestPostTagModel:
    """Test cases for the PostTag model."""
    
    def test_post_tag_creation_basic(self, db_session, sample_user, sample_post):
        """Test basic post-tag association creation."""
        # Create a tag
        tag = Tag(name="python")
        db_session.add(tag)
        db_session.commit()
        
        # Create post-tag association
        post_tag = PostTag(
            post_id=sample_post.post_id,
            tag_id=tag.tag_id
        )
        
        db_session.add(post_tag)
        db_session.commit()
        
        # Verify association was created
        assert post_tag.post_id == sample_post.post_id
        assert post_tag.tag_id == tag.tag_id
    
    def test_post_tag_relationships(self, db_session, sample_user, sample_post):
        """Test post-tag relationship access."""
        # Create a tag
        tag = Tag(name="web-development")
        db_session.add(tag)
        db_session.commit()
        
        # Create post-tag association
        post_tag = PostTag(
            post_id=sample_post.post_id,
            tag_id=tag.tag_id
        )
        
        db_session.add(post_tag)
        db_session.commit()
        
        # Test relationship access
        assert post_tag.post == sample_post
        assert post_tag.tag == tag
        assert post_tag in sample_post.post_tags
        assert post_tag in tag.post_tags
    
    def test_post_tag_duplicate_prevention(self, db_session, sample_user, sample_post):
        """Test that duplicate post-tag associations are prevented."""
        # Create a tag
        tag = Tag(name="javascript")
        db_session.add(tag)
        db_session.commit()
        
        # Create first post-tag association
        post_tag1 = PostTag(
            post_id=sample_post.post_id,
            tag_id=tag.tag_id
        )
        db_session.add(post_tag1)
        db_session.commit()
        
        # Try to create duplicate association
        post_tag2 = PostTag(
            post_id=sample_post.post_id,
            tag_id=tag.tag_id
        )
        db_session.add(post_tag2)
        
        # Suppress expected SQLAlchemy warning for duplicate test
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=Warning)
            with pytest.raises(IntegrityError):
                db_session.commit()
    
    def test_post_tag_without_post_fails(self, db_session):
        """Test that post-tag creation fails without a valid post."""
        # Create a tag
        tag = Tag(name="testing")
        db_session.add(tag)
        db_session.commit()
        
        # Try to create post-tag without valid post
        post_tag = PostTag(
            post_id=None,  # Invalid
            tag_id=tag.tag_id
        )
        
        db_session.add(post_tag)
        # Suppress expected SQLAlchemy warning for validation test
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=Warning)
            with pytest.raises(IntegrityError):
                db_session.commit()
    
    def test_post_tag_without_tag_fails(self, db_session, sample_post):
        """Test that post-tag creation fails without a valid tag."""
        # Try to create post-tag without valid tag
        post_tag = PostTag(
            post_id=sample_post.post_id,
            tag_id=None  # Invalid
        )
        
        db_session.add(post_tag)
        # Suppress expected SQLAlchemy warning for validation test
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=Warning)
            with pytest.raises(IntegrityError):
                db_session.commit()
    
    def test_post_tag_cascade_on_post_deletion(self, db_session, sample_user):
        """Test that post-tag associations are deleted when post is deleted."""
        # Create conversation and post
        conversation = Conversation(
            user_id=sample_user.user_id,
            title="Test Conversation"
        )
        db_session.add(conversation)
        db_session.commit()
        
        post = Post(
            user_id=sample_user.user_id,
            conversation_id=conversation.conversation_id,
            title="Test Post",
            content="Test content"
        )
        db_session.add(post)
        db_session.commit()
        
        # Create tags and associations
        tags = [Tag(name=f"tag{i}") for i in range(3)]
        db_session.add_all(tags)
        db_session.commit()
        
        post_tags = [
            PostTag(post_id=post.post_id, tag_id=tag.tag_id)
            for tag in tags
        ]
        db_session.add_all(post_tags)
        db_session.commit()
        
        # Verify associations exist
        assert len(post.post_tags) == 3
        
        # Delete the post
        db_session.delete(post)
        db_session.commit()
        
        # Verify post-tag associations are gone but tags remain
        for tag in tags:
            db_session.refresh(tag)
            assert len(tag.post_tags) == 0
        
        # Tags should still exist
        remaining_tags = db_session.query(Tag).filter(Tag.name.in_([t.name for t in tags])).all()
        assert len(remaining_tags) == 3
    
    def test_post_tag_cascade_on_tag_deletion(self, db_session, sample_user, sample_post):
        """Test that post-tag associations are deleted when tag is deleted."""
        # Create a tag
        tag = Tag(name="temporary-tag")
        db_session.add(tag)
        db_session.commit()
        
        # Create post-tag association
        post_tag = PostTag(
            post_id=sample_post.post_id,
            tag_id=tag.tag_id
        )
        db_session.add(post_tag)
        db_session.commit()
        
        # Verify association exists
        assert len(sample_post.post_tags) >= 1
        assert len(tag.post_tags) == 1
        
        # Delete the tag
        db_session.delete(tag)
        db_session.commit()
        
        # Refresh post and verify association is gone
        db_session.refresh(sample_post)
        # Note: We can't check the exact count since sample_post might have other tags
        # But we can verify the specific association is gone
        remaining_post_tags = [pt for pt in sample_post.post_tags if pt.tag_id == tag.tag_id]
        assert len(remaining_post_tags) == 0
    
    def test_post_tag_helper_properties(self, db_session, sample_user, sample_post):
        """Test helper properties for accessing tag and post info."""
        # Create a tag
        tag = Tag(name="machine-learning")
        db_session.add(tag)
        db_session.commit()
        
        # Create post-tag association
        post_tag = PostTag(
            post_id=sample_post.post_id,
            tag_id=tag.tag_id
        )
        db_session.add(post_tag)
        db_session.commit()
        
        # Test helper properties
        assert post_tag.tag_name == "machine-learning"
        assert post_tag.post_title == sample_post.title
    
    def test_post_tag_string_representations(self, db_session, sample_user, sample_post):
        """Test string representation methods."""
        # Create a tag
        tag = Tag(name="data-science")
        db_session.add(tag)
        db_session.commit()
        
        # Create post-tag association
        post_tag = PostTag(
            post_id=sample_post.post_id,
            tag_id=tag.tag_id
        )
        db_session.add(post_tag)
        db_session.commit()
        
        # Test __repr__
        repr_str = repr(post_tag)
        assert "PostTag" in repr_str
        assert str(sample_post.post_id) in repr_str
        assert str(tag.tag_id) in repr_str
        
        # Test __str__ with loaded relationships
        str_repr = str(post_tag)
        assert sample_post.title in str_repr
        assert "data-science" in str_repr
    
    def test_multiple_tags_per_post(self, db_session, sample_user, sample_post):
        """Test that a single post can have multiple tags."""
        # Create multiple tags
        tag_names = ["python", "web-dev", "backend", "api"]
        tags = [Tag(name=name) for name in tag_names]
        db_session.add_all(tags)
        db_session.commit()
        
        # Create post-tag associations
        post_tags = [
            PostTag(post_id=sample_post.post_id, tag_id=tag.tag_id)
            for tag in tags
        ]
        db_session.add_all(post_tags)
        db_session.commit()
        
        # Verify all associations exist
        db_session.refresh(sample_post)
        assert len(sample_post.post_tags) >= 4  # >= because sample_post might have other tags
        
        # Verify each tag is associated
        tag_ids = [pt.tag_id for pt in sample_post.post_tags]
        for tag in tags:
            assert tag.tag_id in tag_ids
    
    def test_multiple_posts_per_tag(self, db_session, sample_user):
        """Test that a single tag can be applied to multiple posts."""
        # Create a tag
        tag = Tag(name="tutorial")
        db_session.add(tag)
        db_session.commit()
        
        # Create conversation
        conversation = Conversation(
            user_id=sample_user.user_id,
            title="Test Conversation"
        )
        db_session.add(conversation)
        db_session.commit()
        
        # Create multiple posts
        posts = []
        for i in range(3):
            post = Post(
                user_id=sample_user.user_id,
                conversation_id=conversation.conversation_id,
                title=f"Tutorial Post {i}",
                content=f"Tutorial content {i}"
            )
            posts.append(post)
        
        db_session.add_all(posts)
        db_session.commit()
        
        # Apply the same tag to all posts
        post_tags = [
            PostTag(post_id=post.post_id, tag_id=tag.tag_id)
            for post in posts
        ]
        db_session.add_all(post_tags)
        db_session.commit()
        
        # Verify all associations exist
        db_session.refresh(tag)
        assert len(tag.post_tags) == 3
        
        # Verify each post is associated
        post_ids = [pt.post_id for pt in tag.post_tags]
        for post in posts:
            assert post.post_id in post_ids
    
    def test_post_tag_foreign_key_constraints(self, db_session):
        """Test that foreign key constraints are enforced."""
        import uuid
        
        # Try to create post-tag with non-existent post
        fake_post_id = uuid.uuid4()
        fake_tag_id = uuid.uuid4()
        
        post_tag = PostTag(
            post_id=fake_post_id,
            tag_id=fake_tag_id
        )
        
        db_session.add(post_tag)
        # Suppress expected SQLAlchemy warning for validation test
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=Warning)
            with pytest.raises(IntegrityError):
                db_session.commit()
    
    def test_post_tag_complex_scenario(self, db_session, sample_user):
        """Test a complex scenario with multiple posts and tags."""
        # Create conversation
        conversation = Conversation(
            user_id=sample_user.user_id,
            title="Tech Blog"
        )
        db_session.add(conversation)
        db_session.commit()
        
        # Create posts
        posts = [
            Post(
                user_id=sample_user.user_id,
                conversation_id=conversation.conversation_id,
                title="Python Tutorial",
                content="Learn Python basics"
            ),
            Post(
                user_id=sample_user.user_id,
                conversation_id=conversation.conversation_id,
                title="JavaScript Guide",
                content="Modern JS techniques"
            ),
            Post(
                user_id=sample_user.user_id,
                conversation_id=conversation.conversation_id,
                title="Full Stack Development",
                content="Building complete applications"
            )
        ]
        db_session.add_all(posts)
        db_session.commit()
        
        # Create tags
        tags = [
            Tag(name="python"),
            Tag(name="javascript"), 
            Tag(name="tutorial"),
            Tag(name="programming"),
            Tag(name="web-dev")
        ]
        db_session.add_all(tags)
        db_session.commit()
        
        # Create complex tag associations
        associations = [
            # Python post: python, tutorial, programming
            PostTag(post_id=posts[0].post_id, tag_id=tags[0].tag_id),
            PostTag(post_id=posts[0].post_id, tag_id=tags[2].tag_id),
            PostTag(post_id=posts[0].post_id, tag_id=tags[3].tag_id),
            
            # JavaScript post: javascript, tutorial, programming, web-dev
            PostTag(post_id=posts[1].post_id, tag_id=tags[1].tag_id),
            PostTag(post_id=posts[1].post_id, tag_id=tags[2].tag_id),
            PostTag(post_id=posts[1].post_id, tag_id=tags[3].tag_id),
            PostTag(post_id=posts[1].post_id, tag_id=tags[4].tag_id),
            
            # Full stack post: python, javascript, programming, web-dev
            PostTag(post_id=posts[2].post_id, tag_id=tags[0].tag_id),
            PostTag(post_id=posts[2].post_id, tag_id=tags[1].tag_id),
            PostTag(post_id=posts[2].post_id, tag_id=tags[3].tag_id),
            PostTag(post_id=posts[2].post_id, tag_id=tags[4].tag_id),
        ]
        
        db_session.add_all(associations)
        db_session.commit()
        
        # Verify associations
        # Python post should have 3 tags
        db_session.refresh(posts[0])
        assert len(posts[0].post_tags) == 3
        
        # JavaScript post should have 4 tags
        db_session.refresh(posts[1])
        assert len(posts[1].post_tags) == 4
        
        # Full stack post should have 4 tags
        db_session.refresh(posts[2])
        assert len(posts[2].post_tags) == 4
        
        # Programming tag should be on 3 posts
        db_session.refresh(tags[3])  # programming tag
        assert len(tags[3].post_tags) == 3
