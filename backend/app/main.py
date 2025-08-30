"""
AI Social Backend - Main Application Entry Point
Simple BFF (Backend for Frontend) pattern implementation.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from pathlib import Path

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

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS.split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
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

    # BFF Next.js Serving
    frontend_build_path = Path(__file__).parent.parent.parent / "frontend" / "website" / ".next"
    
    print(f"Looking for Next.js build at: {frontend_build_path}")
    print(f"Next.js build exists: {frontend_build_path.exists()}")
    
    if frontend_build_path.exists():
        # Static assets MUST be mounted BEFORE any catch-all routes
        next_static_path = frontend_build_path / "static"
        if next_static_path.exists():
            app.mount("/_next/static", StaticFiles(directory=str(next_static_path)), name="next_static")
            print(f"✅ Mounted /_next/static from {next_static_path}")
        
        # Public assets from frontend/website/public
        public_path = Path(__file__).parent.parent.parent / "frontend" / "website" / "public"
        if public_path.exists():
            app.mount("/images", StaticFiles(directory=str(public_path)), name="public_assets")
            print(f"✅ Mounted /images from {public_path}")
    
    else:
        print("❌ Next.js build directory not found")

    # Frontend routes AFTER static mounts but BEFORE catch-all
    if frontend_build_path.exists():
        # For BFF pattern with Next.js server build, we need to serve index.html for all routes
        # that don't match API or static assets
        
        # Try to serve from the app directory first
        app_html_path = frontend_build_path / "server" / "app"
        
        @app.get("/")
        async def serve_index():
            # Look for index.html in the server app directory
            possible_paths = [
                app_html_path / "index.html",
                app_html_path / "page.html",
                frontend_build_path / "server" / "pages" / "index.html"
            ]
            
            for path in possible_paths:
                if path.exists():
                    return FileResponse(path)
            
            raise HTTPException(status_code=404, detail="Frontend index not found")
        
        # SPA catch-all LAST - least specific - CRITICAL: This must be LAST
        @app.get("/{path:path}")
        async def serve_spa(path: str):
            # Don't interfere with API routes
            if path.startswith(("api/", "docs", "redoc", "_next/", "images/")):
                raise HTTPException(status_code=404, detail="Not Found")
            
            # For SPA routing, always return the main app HTML
            possible_paths = [
                app_html_path / "index.html",
                app_html_path / "page.html",
                frontend_build_path / "server" / "pages" / "index.html"
            ]
            
            for path_option in possible_paths:
                if path_option.exists():
                    return FileResponse(path_option)
            
            raise HTTPException(status_code=404, detail="Page not found")

    return app


# Create the app
app = create_application()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)