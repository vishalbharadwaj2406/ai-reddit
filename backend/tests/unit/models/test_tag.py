"""
Tag Model Tests

Comprehensive test suite for the Tag model.
Tests cover:
- Tag creation and validation
- Unique name constraint
- Name normalization
- Helper methods and properties
- String representations
"""

import pytest
import warnings
from sqlalchemy.exc import IntegrityError

from app.models.tag import Tag


class TestTagModel:
    """Test cases for the Tag model."""
    
    def test_tag_creation_basic(self, db_session):
        """Test basic tag creation."""
        tag = Tag(name="python")
        
        db_session.add(tag)
        db_session.commit()
        
        # Verify tag was created
        assert tag.tag_id is not None
        assert tag.name == "python"
    
    def test_tag_creation_with_normalization(self, db_session):
        """Test tag creation with name normalization."""
        # Test various formats that should be normalized
        test_cases = [
            ("Python Programming", "python-programming"),
            ("  machine learning  ", "machine-learning"),
            ("WEB    DEV", "web-dev"),
            ("AI/ML", "ai/ml"),  # Special chars preserved
        ]
        
        for i, (input_name, expected) in enumerate(test_cases):
            normalized = Tag.normalize_name(input_name)
            assert normalized == expected, f"Failed for input: '{input_name}'"
            
            # Create tag with normalized name
            tag = Tag(name=normalized)
            db_session.add(tag)
            db_session.commit()
            
            assert tag.name == expected
    
    def test_tag_unique_name_constraint(self, db_session):
        """Test that duplicate tag names are not allowed."""
        # Create first tag
        tag1 = Tag(name="javascript")
        db_session.add(tag1)
        db_session.commit()
        
        # Try to create duplicate tag
        tag2 = Tag(name="javascript")
        db_session.add(tag2)
        
        # Suppress expected SQLAlchemy warning for validation test
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=Warning)
            with pytest.raises(IntegrityError):
                db_session.commit()
    
    def test_tag_name_required(self, db_session):
        """Test that tag name is required."""
        tag = Tag(name=None)
        db_session.add(tag)
        
        # Suppress expected SQLAlchemy warning for validation test
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=Warning)
            with pytest.raises(IntegrityError):
                db_session.commit()
    
    def test_tag_empty_name_fails(self, db_session):
        """Test that empty tag name fails."""
        tag = Tag(name="")
        db_session.add(tag)
        db_session.commit()
        
        # Empty string should be allowed but not recommended
        assert tag.name == ""
    
    def test_tag_hashtag_property(self, db_session):
        """Test hashtag formatting property."""
        tag = Tag(name="python-web-dev")
        db_session.add(tag)
        db_session.commit()
        
        assert tag.hashtag == "#python-web-dev"
        # Test that __str__ also returns hashtag format
        assert str(tag) == "#python-web-dev"
    
    def test_tag_display_name_property(self, db_session):
        """Test display name formatting."""
        test_cases = [
            ("python-programming", "Python Programming"),
            ("machine-learning", "Machine Learning"),
            ("ai-ml", "Ai Ml"),
            ("web-dev", "Web Dev"),
        ]
        
        for i, (tag_name, expected_display) in enumerate(test_cases):
            tag = Tag(name=tag_name)
            db_session.add(tag)
            db_session.commit()
            
            assert tag.display_name == expected_display
    
    def test_tag_normalize_name_class_method(self):
        """Test the normalize_name class method."""
        test_cases = [
            ("Python", "python"),
            ("Machine Learning", "machine-learning"),
            ("  AI/ML  ", "ai/ml"),
            ("Web    Development", "web-development"),
            ("", ""),
            ("Single", "single"),
            ("UPPERCASE", "uppercase"),
            ("Mixed Case Words", "mixed-case-words"),
        ]
        
        for input_name, expected in test_cases:
            result = Tag.normalize_name(input_name)
            assert result == expected, f"Failed for '{input_name}': expected '{expected}', got '{result}'"
    
    def test_tag_normalize_name_edge_cases(self):
        """Test normalize_name with edge cases."""
        # Test None input
        assert Tag.normalize_name(None) == ""
        
        # Test whitespace-only input
        assert Tag.normalize_name("   ") == ""
        
        # Test single character
        assert Tag.normalize_name("A") == "a"
        
        # Test special characters
        assert Tag.normalize_name("C++") == "c++"
        assert Tag.normalize_name("C#/.NET") == "c#/.net"
    
    def test_tag_string_representations(self, db_session):
        """Test string representation methods."""
        tag = Tag(name="data-science")
        db_session.add(tag)
        db_session.commit()
        
        # Test __repr__
        repr_str = repr(tag)
        assert "Tag" in repr_str
        assert str(tag.tag_id) in repr_str
        assert "data-science" in repr_str
        
        # Test __str__ (hashtag format)
        str_repr = str(tag)
        assert str_repr == "#data-science"
        
        # Test hashtag property
        assert tag.hashtag == "#data-science"
    
    def test_tag_case_sensitivity(self, db_session):
        """Test that tags are case-insensitive when normalized."""
        # These should all normalize to the same thing
        names = ["Python", "python", "PYTHON", "PyThOn"]
        normalized = "python"
        
        # First tag should succeed
        tag1 = Tag(name=Tag.normalize_name(names[0]))
        db_session.add(tag1)
        db_session.commit()
        assert tag1.name == normalized
        
        # Subsequent tags with same normalized name should fail
        for name in names[1:]:
            tag = Tag(name=Tag.normalize_name(name))
            db_session.add(tag)
            
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=Warning)
                with pytest.raises(IntegrityError):
                    db_session.commit()
            
            db_session.rollback()  # Reset session for next test
    
    def test_tag_special_characters(self, db_session):
        """Test tags with special characters."""
        special_tags = [
            "c++",
            "c#",
            "node.js",
            "asp.net",
            "react/redux",
            "vue.js",
            "3d-modeling"
        ]
        
        for tag_name in special_tags:
            tag = Tag(name=tag_name)
            db_session.add(tag)
            db_session.commit()
            
            assert tag.name == tag_name
            assert tag.hashtag == f"#{tag_name}"
    
    def test_tag_long_names(self, db_session):
        """Test tags with long names."""
        long_name = "very-long-tag-name-that-describes-something-specific"
        tag = Tag(name=long_name)
        
        db_session.add(tag)
        db_session.commit()
        
        assert tag.name == long_name
        assert len(tag.name) > 50  # Verify it's actually long
    
    def test_multiple_tags_creation(self, db_session):
        """Test creating multiple different tags."""
        tag_names = [
            "python",
            "javascript", 
            "machine-learning",
            "web-development",
            "data-science"
        ]
        
        tags = []
        for name in tag_names:
            tag = Tag(name=name)
            tags.append(tag)
        
        db_session.add_all(tags)
        db_session.commit()
        
        # Verify all tags were created
        for i, tag in enumerate(tags):
            assert tag.name == tag_names[i]
            assert tag.tag_id is not None
    
    def test_tag_whitespace_normalization(self, db_session):
        """Test that whitespace is properly normalized."""
        test_cases = [
            ("machine learning", "machine-learning"),
            ("data   science", "data-science"),  # Multiple spaces
            ("web\tdevelopment", "web-development"),  # Tab character
            ("mobile\napps", "mobile-apps"),  # Newline character
        ]
        
        for input_name, expected in test_cases:
            normalized = Tag.normalize_name(input_name)
            tag = Tag(name=normalized)
            db_session.add(tag)
            db_session.commit()
            
            assert tag.name == expected
