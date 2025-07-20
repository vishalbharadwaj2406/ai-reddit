#!/usr/bin/env python3

import asyncio
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.core.database import engine
from app.services.post_service import PostService

async def test_post_service():
    """Quick test to see what's failing in the post service"""
    
    # Create a test session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Initialize post service
        post_service = PostService(db)
        
        # Try to call get_posts_feed
        print("Testing get_posts_feed...")
        posts = await post_service.get_posts_feed(
            db=db,
            limit=5,
            offset=0,
            sort="hot",
            time_range="all",
            tag=None,
            user_id=None
        )
        print(f"Success! Got {len(posts)} posts")
        for post in posts:
            print(f"- Post: {post.title}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_post_service())
