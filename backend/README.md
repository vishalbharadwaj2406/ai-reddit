# [APP_NAME] Backend

## Quick Start

1. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Set Up Environment Variables**
```bash
cp .env.example .env
# Edit .env with your actual values
```

4. **Run the Application**
```bash
uvicorn app.main:app --reload
```

## Architecture Overview

This backend follows a **layered architecture** pattern:

```
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── api/v1/              # API endpoints organized by version
│   │   ├── users/           # User-related endpoints
│   │   ├── conversations/   # Conversation-related endpoints
│   │   ├── posts/           # Post-related endpoints
│   │   └── auth/            # Authentication endpoints
│   ├── services/            # Business logic layer
│   ├── repositories/        # Data access layer
│   ├── models/              # Database models (SQLAlchemy)
│   ├── schemas/             # Request/Response models (Pydantic)
│   ├── core/                # Configuration, database, utilities
│   └── dependencies/        # Shared dependencies for routes
```

## Layer Responsibilities

- **API Layer** (`api/v1/`): Handle HTTP requests/responses, validation
- **Services Layer** (`services/`): Business logic, orchestration
- **Repository Layer** (`repositories/`): Database operations, queries
- **Models Layer** (`models/`): Database table definitions
- **Schemas Layer** (`schemas/`): Data validation and serialization

## Development Guidelines

1. **Keep routes thin** - Move business logic to services
2. **Use dependency injection** - For database sessions, authentication
3. **Validate everything** - Use Pydantic schemas for all inputs
4. **Handle errors gracefully** - Return proper HTTP status codes
5. **Add type hints** - Makes code more maintainable

## API Documentation

Once running, visit:
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc