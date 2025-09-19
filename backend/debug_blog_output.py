#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from app.services.ai_service import AIService

async def test_blog_generation():
    """Test blog generation and show exact JSON output"""

    ai_service = AIService()

    # Create a simple conversation context
    conversation_context = [
        {"role": "user", "content": "What are the benefits of renewable energy?"},
        {"role": "assistant", "content": "Renewable energy offers several key benefits: it's environmentally friendly, reduces carbon emissions, provides energy independence, and creates sustainable jobs. Solar and wind power are becoming increasingly cost-effective alternatives to fossil fuels."}
    ]

    print("🔄 Generating blog from conversation...")
    print("=" * 60)

    # Generate blog content
    blog_result = ""
    async for chunk in ai_service.generate_blog_from_conversation(
        conversation_context,
        "Make it suitable for a general audience"
    ):
        if isinstance(chunk, dict) and "content" in chunk:
            blog_result = chunk["content"]  # This is the final cleaned JSON
            break

    print("📝 EXACT JSON WRITTEN TO DATABASE:")
    print("=" * 60)
    print(blog_result)
    print("=" * 60)

    # Parse and validate to show structure
    import json
    try:
        blog_data = json.loads(blog_result)
        print("\n🔍 PARSED STRUCTURE:")
        print(f"Title: {blog_data['title']}")
        print(f"Content Length: {len(blog_data['content'])} characters")
        print(f"Tags: {blog_data['tags']}")
        print(f"Number of Tags: {len(blog_data['tags'])}")

        print("\n📋 CONTENT PREVIEW:")
        print(blog_data['content'][:200] + "..." if len(blog_data['content']) > 200 else blog_data['content'])

    except json.JSONDecodeError as e:
        print(f"❌ JSON Parse Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_blog_generation())
