# Gemini 2.5 Flash Integration

Technical documentation for LangChain + Google Gemini 2.5 Flash AI integration.

## Architecture Overview

The AI service uses LangChain as an abstraction layer with Google Gemini 2.5 Flash as the production model. This architecture provides future-proofing for easy provider switching while maintaining consistent interfaces.

```
User Request → FastAPI Endpoint → AI Service → LangChain → Gemini 2.5 Flash → Streaming Response
```

## Integration Components

### LangChain Framework
- **Purpose**: Provider-agnostic AI abstraction layer
- **Model Class**: `ChatGoogleGenerativeAI`
- **Message Types**: `HumanMessage`, `AIMessage`, `SystemMessage`
- **Streaming**: Native async streaming support via `astream()`

### Google Gemini 2.5 Flash
- **Model ID**: `gemini-2.5-flash-latest`
- **Context Window**: 8,192 tokens
- **Strengths**: Optimized for speed and cost-effectiveness
- **Rate Limits**: 15 RPM, 1M TPM (free tier)

### Database Integration
- **Session Isolation**: Separate DB sessions for streaming contexts
- **Message Persistence**: AI responses saved after streaming completion
- **Context Preservation**: Conversation history maintained across interactions

## Implementation Details

### Service Initialization

```python
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings

class AIService:
    def __init__(self):
        if settings.GOOGLE_GEMINI_API_KEY:
            self.llm = ChatGoogleGenerativeAI(
                model=settings.AI_MODEL_NAME,
                temperature=settings.AI_TEMPERATURE,
                max_tokens=settings.AI_MAX_TOKENS,
                top_p=settings.AI_TOP_P,
                top_k=settings.AI_TOP_K,
                google_api_key=settings.GOOGLE_GEMINI_API_KEY
            )
            self.mock_mode = False
        else:
            self.mock_mode = True
```

### Streaming Implementation

```python
async def generate_ai_response(
    self,
    user_message: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    conversation_id: Optional[UUID] = None
) -> AsyncGenerator[Dict[str, Any], None]:
    
    # Build message history for context
    messages = []
    if conversation_history:
        for msg in conversation_history[-10:]:  # Last 10 messages
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
    
    # Add current user message
    messages.append(HumanMessage(content=user_message))
    
    # Stream response
    complete_response = ""
    async for chunk in self.llm.astream(messages):
        token = chunk.content
        complete_response += token
        
        yield {
            "content": complete_response,
            "is_complete": False
        }
    
    # Final complete response
    yield {
        "content": complete_response,
        "is_complete": True
    }
```

### Database Session Management

```python
async def stream_ai_response(conversation_id: UUID, message_id: UUID, ...):
    # Main endpoint uses existing DB session for validation
    conversation = db.query(Conversation).filter(...).first()
    
    # Stream AI response
    complete_response = ""
    async for chunk in ai_service.generate_ai_response(...):
        # Stream to client via SSE
        yield f"data: {json.dumps(chunk)}\n\n"
        if chunk["is_complete"]:
            complete_response = chunk["content"]
    
    # Save AI response using separate session
    from app.core.database import SessionLocal
    new_db = SessionLocal()
    try:
        ai_message = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=complete_response,
            ...
        )
        new_db.add(ai_message)
        new_db.commit()
    finally:
        new_db.close()
```

## Configuration Options

### Model Parameters

**Temperature (0.0-1.0)**
- Controls randomness in responses
- `0.7`: Balanced creativity (default)
- `0.0`: Deterministic responses
- `1.0`: Maximum creativity

**Max Tokens (1-8192)**  
- Maximum response length
- `2048`: Default for conversations
- `4096`: Longer content like blogs
- `8192`: Maximum context window

**Top-P (0.0-1.0)**
- Nucleus sampling parameter
- `0.9`: Default recommendation
- Lower values = more focused responses

**Top-K (1-100)**
- Number of top tokens to consider
- `40`: Default recommendation  
- Lower values = more deterministic

### Safety Configuration

```python
AI_ENABLE_SAFETY_FILTERS=true
AI_REQUEST_TIMEOUT=30
AI_RATE_LIMIT_RPM=15
AI_RATE_LIMIT_TPM=1000000
```

## Error Handling

### Graceful Fallback Strategy

1. **API Key Missing**: Falls back to mock mode automatically
2. **API Rate Limit**: Returns rate limit error via SSE
3. **Network Issues**: Retries with exponential backoff
4. **Content Filtering**: Returns filtered content notice
5. **Token Limit**: Truncates context and continues

### Error Response Format

```python
# SSE Error Event
event: error
data: {
    "success": false,
    "data": null,
    "message": "AI service temporarily unavailable",
    "errorCode": "AI_SERVICE_ERROR"
}
```

### Mock Mode Fallback

When API key is unavailable, the service operates in mock mode:

```python
async def _generate_mock_response(self, user_message: str):
    # Intelligent mock responses based on keywords
    if "quantum" in user_message.lower():
        response = "Quantum computing represents a paradigm shift..."
    elif "hello" in user_message.lower():
        response = "Hello! I'm here to help with your questions..."
    else:
        response = "That's an interesting question. Let me think about it..."
    
    # Simulate streaming
    words = response.split()
    for i, word in enumerate(words):
        yield {
            "content": " ".join(words[:i+1]),
            "is_complete": i == len(words) - 1
        }
        await asyncio.sleep(0.05)  # Realistic typing speed
```

## Performance Optimizations

### Context Management
- **History Limit**: Only last 10 messages for context
- **Token Counting**: Monitor context length to stay within limits
- **Memory Efficiency**: Stream responses without buffering

### Request Optimization
- **Connection Pooling**: Reuse HTTP connections to Gemini API
- **Async Operations**: Non-blocking AI requests
- **Timeout Handling**: 30-second request timeout

### Caching Strategy (Future)
- **Response Caching**: Cache common AI responses
- **Context Caching**: Reuse conversation context
- **Prompt Templates**: Pre-compiled prompt structures

## Blog Generation Feature

### Specialized Blog Prompts

```python
def format_blog_prompt(conversation_content: str, additional_context: str = None):
    base_prompt = f"""
Transform this conversation into an engaging blog post:

{conversation_content}

Requirements:
- Create compelling title and structure
- Expand ideas with examples and insights
- Make it accessible to general audience
- Include proper markdown formatting
"""
    
    if additional_context:
        base_prompt += f"\nAdditional context: {additional_context}"
    
    return base_prompt
```

### Blog Streaming Implementation

```python
async def generate_blog_from_conversation(
    self,
    conversation_content: str,
    additional_context: Optional[str] = None
):
    prompt = ConversationPrompts.format_blog_prompt(
        conversation_content, additional_context
    )
    
    messages = [HumanMessage(content=prompt)]
    
    complete_response = ""
    async for chunk in self.llm.astream(messages):
        complete_response += chunk.content
        yield {
            "content": complete_response,
            "is_complete": False,
            "is_blog": True
        }
    
    yield {
        "content": complete_response,
        "is_complete": True,
        "is_blog": True
    }
```

## Testing Strategy

### Test Categories

**Unit Tests**: LangChain integration, error handling, mock mode
**Integration Tests**: Real API calls, streaming validation, context handling  
**E2E Tests**: Complete conversation workflows, blog generation

### Test Configuration

```python
# tests/conftest.py
@pytest.fixture
def ai_service_mock():
    with patch('app.services.ai_service.ChatGoogleGenerativeAI'):
        yield AIService()

@pytest.fixture
def ai_service_real():
    # Requires GOOGLE_GEMINI_API_KEY in test environment
    return AIService()
```

### Mock Response Testing

```python
@pytest.mark.asyncio
async def test_streaming_response_format():
    ai_service = AIService()
    ai_service.mock_mode = True
    
    responses = []
    async for chunk in ai_service.generate_ai_response("test"):
        responses.append(chunk)
    
    assert len(responses) > 1
    assert responses[-1]["is_complete"] is True
```

## Future Enhancements

### Multi-Provider Support

LangChain architecture enables easy provider switching:

```python
# Future: OpenAI integration
from langchain_openai import ChatOpenAI
self.llm = ChatOpenAI(model="gpt-4", temperature=0.7)

# Future: Anthropic integration  
from langchain_anthropic import ChatAnthropic
self.llm = ChatAnthropic(model="claude-3", temperature=0.7)

# Future: Local model integration
from langchain_community.llms import Ollama
self.llm = Ollama(model="llama2", temperature=0.7)
```

### Advanced Features

**Conversation Memory**: Long-term context persistence
**Prompt Templates**: Structured prompt management
**Response Caching**: Performance optimization
**Multi-modal**: Image and document processing
**Custom Fine-tuning**: Domain-specific model training

### Monitoring and Analytics

**Response Quality**: Track user satisfaction metrics
**Performance Metrics**: Response time, token usage, error rates
**Cost Optimization**: Monitor API usage and costs
**A/B Testing**: Compare different models and parameters

*For setup instructions, see [AI Service Setup](../development/ai-service-setup.md).*
*For API documentation, see [API Specification](../api/specification.md).*
