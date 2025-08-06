# AI Service Setup Guide

Complete setup guide for LangChain + Google Gemini 2.5 Flash integration.

## Overview

The AI service uses LangChain framework with Google Gemini 2.5 Flash for production AI responses. The architecture supports streaming responses via Server-Sent Events and includes comprehensive error handling with graceful fallback to mock mode.

## Prerequisites

- Google API account with Gemini API access
- Python 3.12+ with project dependencies installed
- PostgreSQL database configured

## API Key Setup

### 1. Get Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the API key (starts with `AIzaSy`)

### 2. Configure Environment

Add to your `.env` file:

```bash
# Required for AI features
GOOGLE_GEMINI_API_KEY=your-api-key-here

# Optional (have defaults)
AI_MODEL_NAME=gemini-2.5-flash-latest
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=2048
AI_TOP_P=0.9
AI_TOP_K=40

# Safety and rate limiting
AI_ENABLE_SAFETY_FILTERS=true
AI_REQUEST_TIMEOUT=30
AI_RATE_LIMIT_RPM=15
AI_RATE_LIMIT_TPM=1000000
```

### 3. Verify Configuration

```bash
cd backend
python -c "from app.core.config import settings; print(f'API Key configured: {bool(settings.GOOGLE_GEMINI_API_KEY)}')"
```

## Testing the Integration

### Basic Health Check

```bash
cd backend
python test_ai_integration_simple.py
```

Expected output:
```
✅ AI Service running in production mode with real API
✅ AI Service health: healthy in production mode
✅ All imports successful
```

### Run AI Test Suite

**Total: 61 comprehensive AI integration tests**
- 8 configuration validation tests  
- 24 LangChain + Gemini integration unit tests
- 10 real API integration tests
- 9 conversation endpoint integration tests  
- 10 end-to-end workflow tests

```bash
# Unit tests (fast)
pytest tests/unit/services/test_langchain_gemini_integration.py -v

# Integration tests (requires API key)
pytest tests/integration/test_ai_service_integration.py -v

# E2E tests (full workflow)
pytest tests/e2e/test_ai_conversation_flow_e2e.py -v

# All AI tests
pytest tests/ -k "ai" -v
```

### Manual API Test

Start the server and test streaming endpoints:

```bash
# Start server
uvicorn app.main:app --reload

# In another terminal, test conversation
curl -X POST http://localhost:8000/api/v1/conversations/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{"title": "Test AI Integration"}'

# Test streaming (replace conversation_id and message_id)
curl -N http://localhost:8000/api/v1/conversations/{conversation_id}/stream?message_id={message_id} \
  -H "Authorization: Bearer your-jwt-token"
```

## Configuration Details

### Model Selection

**Current**: `gemini-2.5-flash-latest`
- Optimized for speed and cost
- Best for MVP and real-time responses
- 8192 token context window

**Alternative**: `gemini-pro`
- Higher quality for complex tasks
- Slower response times
- Higher cost per request

### Parameters

**Temperature (0.0-1.0)**
- `0.7`: Balanced creativity and consistency (default)
- `0.0`: Deterministic responses
- `1.0`: Maximum creativity

**Max Tokens (1-8192)**
- `2048`: Default for conversations
- `4096`: For longer blog posts
- `8192`: Maximum for complex content

**Top-P (0.0-1.0)**
- `0.9`: Nucleus sampling parameter (default)
- Controls diversity of token selection

**Top-K (1-100)**
- `40`: Number of highest probability tokens to consider (default)
- Lower values = more focused responses

### Rate Limits (Free Tier)

- **Requests per minute**: 15 RPM
- **Tokens per minute**: 1,000,000 TPM
- **Requests per day**: 1,500 RPD

Monitor usage in Google AI Studio dashboard.

## Architecture Details

### LangChain Integration

```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage

# Initialization
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-latest",
    temperature=0.7,
    max_tokens=2048
)

# Streaming responses
async for chunk in llm.astream(messages):
    yield chunk.content
```

### Database Session Isolation

Streaming responses use separate database sessions to avoid transaction conflicts:

```python
# Streaming uses new session
from app.core.database import SessionLocal
new_db = SessionLocal()
try:
    # Save AI response
    ai_message = Message(...)
    new_db.add(ai_message)
    new_db.commit()
finally:
    new_db.close()
```

### Error Handling

1. **API Key Missing**: Falls back to mock mode
2. **API Error**: Graceful error response via SSE
3. **Network Timeout**: Retry with exponential backoff
4. **Rate Limit**: Queue request or return error

## Troubleshooting

### Common Issues

**"Mock mode active"**
- Check `GOOGLE_GEMINI_API_KEY` is set correctly
- Verify API key format starts with `AIzaSy`
- Test API key in Google AI Studio

**"API connection failed"**
- Check internet connection
- Verify API key hasn't expired
- Check rate limits in Google AI Studio

**"Streaming timeout"**
- Increase `AI_REQUEST_TIMEOUT` value
- Check network stability
- Monitor API response times

**"Database session conflicts"**
- Verify session isolation in streaming endpoints
- Check for uncommitted transactions
- Review database connection pool settings

### Debug Tools

**AI Service Health**:
```bash
curl http://localhost:8000/api/v1/conversations/health
```

**Debug Streaming**:
```bash
cd backend
python debug_streaming.py
```

**Simple Integration Test**:
```bash
cd backend
python debug_simple.py
```

### Log Analysis

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
uvicorn app.main:app --reload --log-level debug
```

Key log patterns:
- `"LangChain AI service initialized successfully"`: Production mode active
- `"Running in mock mode"`: API key issue
- `"AI service health: healthy"`: Service operational

## Production Considerations

### Security
- Never commit API keys to repository
- Use environment variables or secret management
- Monitor API key usage regularly

### Performance
- Cache frequent AI responses (future enhancement)
- Implement request queuing for rate limiting
- Monitor response times and error rates

### Monitoring
- Track API usage against quotas
- Monitor streaming connection stability
- Log AI service health checks

### Scaling
- Consider multiple API keys for higher limits
- Implement load balancing for AI requests
- Plan for Google AI Premium features

## Future Enhancements

### Provider Flexibility
LangChain architecture supports easy provider switching:
- OpenAI GPT models
- Anthropic Claude
- Local LLM deployments
- Multiple providers simultaneously

### Advanced Features
- Conversation memory and context persistence
- Custom prompt templates and chains
- AI response caching and optimization  
- Multi-modal capabilities (images, documents)

*For API usage examples, see [API Specification](../api/specification.md).*
*For architecture details, see [Architecture](../architecture/) section.*
