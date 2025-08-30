"""
AI Social Backend - Main Application Entry Point
Backend-only API serving with cross-origin authentication.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=f"{settings.APP_NAME} - AI conversation platform",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS Middleware - Updated for cross-origin authentication
    def get_cors_origins():
        if settings.ENVIRONMENT == "production":
            if hasattr(settings, 'PRODUCTION_ORIGINS'):
                return settings.PRODUCTION_ORIGINS.split(",")
            else:
                return [settings.FRONTEND_URL]
        return settings.ALLOWED_ORIGINS.split(",")

    cors_origins = get_cors_origins()
    print(f"🌐 CORS Origins: {cors_origins}")  # Debug output

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,  # CRITICAL for cookies
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # Health endpoint
    @app.get("/health")
    async def health():
        return {"status": "healthy", "app": settings.APP_NAME}

    # Import and register API routers
    try:
        from app.api.v1.auth import router as auth_router
        app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
        print("✅ Auth router loaded")
    except ImportError as e:
        print(f"❌ Auth router failed: {e}")

    try:
        from app.api.v1.health import router as health_router
        app.include_router(health_router, tags=["health"])
        print("✅ Health router loaded")
    except ImportError as e:
        print(f"❌ Health router failed: {e}")

    try:
        from app.api.v1.users import router as users_router
        app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
        print("✅ Users router loaded")
    except ImportError as e:
        print(f"❌ Users router failed: {e}")

    try:
        from app.api.v1.conversations import router as conversations_router
        app.include_router(conversations_router, prefix="/api/v1/conversations", tags=["conversations"])
        print("✅ Conversations router loaded")
    except ImportError as e:
        print(f"❌ Conversations router failed: {e}")

    try:
        from app.api.v1.posts import router as posts_router
        app.include_router(posts_router, prefix="/api/v1/posts", tags=["posts"])
        print("✅ Posts router loaded")
    except ImportError as e:
        print(f"❌ Posts router failed: {e}")

    try:
        from app.api.v1.comments import router as comments_router
        app.include_router(comments_router, prefix="/api/v1", tags=["comments"])
        print("✅ Comments router loaded")
    except ImportError as e:
        print(f"❌ Comments router failed: {e}")

    try:
        from app.api.v1.tags import router as tags_router
        app.include_router(tags_router, prefix="/api/v1", tags=["tags"])
        print("✅ Tags router loaded")
    except ImportError as e:
        print(f"❌ Tags router failed: {e}")

    try:
        from app.api.v1.images import router as images_router
        app.include_router(images_router, prefix="/api/v1", tags=["images"])
        print("✅ Images router loaded")
    except ImportError as e:
        print(f"❌ Images router failed: {e}")

    return app


# Create the app
app = create_application()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)