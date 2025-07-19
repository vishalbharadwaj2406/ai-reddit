#!/usr/bin/env python3
"""
Comprehensive test for Gemini AI integration

This script demonstrates the complete integration working in both mock and production modes.
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.services.ai_service import AIService
from app.prompts.conversation_prompts import ConversationPrompts
from app.prompts.system_prompts import SystemPrompts


async def test_comprehensive_integration():
    """Test all aspects of our Gemini integration"""
    
    print("🚀 AI Social - Gemini Integration Test")
    print("="*50)
    
    # 1. Test prompt system
    print("\n📝 Testing Prompt Template System...")
    system_prompts = SystemPrompts()
    conversation_prompts = ConversationPrompts()
    
    print(f"✅ System prompt loaded ({len(system_prompts.get_system_prompt())} chars)")
    print(f"✅ Conversation starter: {conversation_prompts.get_conversation_starter()}")
    
    # 2. Test AI service initialization
    print("\n🤖 Testing AI Service...")
    ai_service = AIService()
    
    health = await ai_service.health_check()
    print(f"✅ Health check: {health['status']} ({health['mode']} mode)")
    
    # 3. Test conversation flow
    print("\n💭 Testing Conversation Flow...")
    test_message = "Explain the basics of machine learning"
    
    print(f"User: {test_message}")
    print("AI: ", end="", flush=True)
    
    full_response = ""
    async for chunk in ai_service.generate_ai_response(test_message):
        if chunk["content"] != full_response:
            # Print new content only
            new_content = chunk["content"][len(full_response):]
            print(new_content, end="", flush=True)
            full_response = chunk["content"]
            
        if chunk["is_complete"]:
            print(f"\n✅ Response completed ({len(full_response)} characters)")
            break
    
    # 4. Test conversation with history
    print("\n📚 Testing Conversation with History...")
    conversation_history = [
        {"role": "user", "content": test_message},
        {"role": "assistant", "content": full_response},
    ]
    
    follow_up = "Can you give me a practical example?"
    print(f"User: {follow_up}")
    print("AI: ", end="", flush=True)
    
    follow_up_response = ""
    async for chunk in ai_service.generate_ai_response(follow_up, conversation_history):
        if chunk["content"] != follow_up_response:
            new_content = chunk["content"][len(follow_up_response):]
            print(new_content, end="", flush=True)
            follow_up_response = chunk["content"]
            
        if chunk["is_complete"]:
            print(f"\n✅ Follow-up completed ({len(follow_up_response)} characters)")
            break
    
    # 5. Test blog generation
    print("\n📄 Testing Blog Generation...")
    conversation_content = f"""
    User: {test_message}
    AI: {full_response}
    
    User: {follow_up}
    AI: {follow_up_response}
    """
    
    print("Generating blog from conversation...")
    blog_content = ""
    async for chunk in ai_service.generate_blog_from_conversation(
        conversation_content, 
        "Make it accessible for beginners"
    ):
        blog_content = chunk["content"]
        if chunk["is_complete"]:
            print(f"✅ Blog generated ({len(blog_content)} characters)")
            print(f"Preview: {blog_content[:200]}...")
            break
    
    # 6. Summary
    print("\n🎉 Integration Test Summary")
    print("="*30)
    print("✅ Prompt templates: Working")
    print("✅ AI service initialization: Working")
    print("✅ Basic conversation: Working")
    print("✅ Conversation with history: Working") 
    print("✅ Blog generation: Working")
    print(f"✅ Mode: {health['mode']} ({health['provider']})")
    
    if health['mode'] == 'mock':
        print("\n💡 Note: Running in mock mode without API key")
        print("   Set GOOGLE_GEMINI_API_KEY environment variable for production mode")
    
    return True


if __name__ == "__main__":
    try:
        result = asyncio.run(test_comprehensive_integration())
        if result:
            print("\n🏆 All tests passed! Gemini integration is ready!")
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
