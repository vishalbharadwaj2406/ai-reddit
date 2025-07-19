#!/usr/bin/env python3
"""
Quick test script for AI service integration
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.services.ai_service import AIService


async def test_ai_service():
    """Test AI service basic functionality"""
    
    print("🤖 Testing AI Service Integration...")
    
    # Initialize AI service
    ai_service = AIService()
    
    # Check health
    health = await ai_service.health_check()
    print(f"🏥 Health Check: {health}")
    
    # Test response generation
    print("\n💭 Testing response generation...")
    test_message = "Hello, tell me about quantum computing"
    
    full_response = ""
    async for chunk in ai_service.generate_ai_response(test_message):
        if chunk["content"]:
            # Clear line and show current progress
            print(f"\r📝 Response: {chunk['content'][:100]}{'...' if len(chunk['content']) > 100 else ''}", end="")
            full_response = chunk["content"]
            
        if chunk["is_complete"]:
            print(f"\n✅ Complete response received ({len(full_response)} characters)")
            break
    
    print(f"\n📄 Final Response:\n{full_response}")
    
    return True


if __name__ == "__main__":
    try:
        result = asyncio.run(test_ai_service())
        if result:
            print("\n🎉 AI Service test completed successfully!")
        else:
            print("\n❌ AI Service test failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
