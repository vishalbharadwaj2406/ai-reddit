"""
AIkya Backend - Main Application Entry Point

This file is the heart of our FastAPI application. It:
1. Creates the FastAPI app instance
2. Sets up middleware (CORS, etc.)
3. Includes all API routers
4. Handles startup/shutdown events
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import configuration
from app.core.config import settings

# Import API routers
# NOTE: Some routers may not work until schemas/services are implemented
try:
    from app.api.v1.auth import router as auth_router
    from app.api.v1.users import router as users_router
    from app.api.v1.conversations import router as conversations_router
    from app.api.v1.posts import router as posts_router
except ImportError as e:
    print(f"⚠️  Warning: Some API modules couldn't be imported: {e}")
    print("This is normal during initial setup. Routes will be added as modules are implemented.")


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.

    This function creates the app instance and sets up all configuration.
    We use a factory pattern here to make testing easier later.
    """

    # Create FastAPI instance with metadata
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="AIkya - AI-powered conversation platform",
        docs_url="/docs",  # Swagger UI
        redoc_url="/redoc",  # ReDoc documentation
    )

    # Add CORS middleware
    # This allows our frontend (running on localhost:3000) to make requests
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS.split(","),
        allow_credentials=True,
        allow_methods=["*"],  # Allow all HTTP methods
        allow_headers=["*"],  # Allow all headers
    )

    # Include API routers with version prefix
    # Each router handles a different resource collection
    try:
        app.include_router(
            auth_router,
            prefix="/api/v1/auth",
            tags=["authentication"]
        )
        app.include_router(
            users_router,
            prefix="/api/v1/users",
            tags=["users"]
        )
        app.include_router(
            conversations_router,
            prefix="/api/v1/conversations",
            tags=["conversations"]
        )
        app.include_router(
            posts_router,
            prefix="/api/v1/posts",
            tags=["posts"]
        )
    except NameError:
        print("⚠️  Some routers not available yet - they'll be added as modules are implemented")

    return app


# Create the app instance
app = create_application()


@app.get("/")
async def root():
    """
    Root endpoint - simple health check.

    This is useful for:
    - Verifying the server is running
    - Load balancer health checks
    - Basic API testing
    """
    return {
        "message": "AIkya API is running!",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns the status of the application.
    In production, this might check database connectivity, etc.
    """
    return {"status": "healthy"}


# Application lifecycle events
@app.on_event("startup")
async def startup_event():
    """
    Code to run when the application starts up.

    Good place to:
    - Initialize database connections
    - Set up logging
    - Pre-load AI models
    - Connect to external services
    """
    print(f"🚀 {settings.APP_NAME} starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Code to run when the application shuts down.

    Good place to:
    - Close database connections
    - Clean up resources
    - Save any pending data
    """
    print(f"🛑 {settings.APP_NAME} shutting down...")


# If running this file directly (for development)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on code changes (development only)
    )