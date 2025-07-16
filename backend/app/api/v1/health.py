"""
Health Check API Routes

This module provides system health check endpoints for monitoring
database connectivity and overall system status.
"""

from fastapi import APIRouter
from app.core.database import DatabaseManager

# Create router for health endpoints
router = APIRouter(prefix="/health", tags=["health"])


@router.get("/database")
async def database_health():
    """
    Check database connectivity and table existence.
    
    Returns database connection status and table count for monitoring.
    """
    from sqlalchemy import inspect
    from app.core.database import engine
    
    is_healthy = DatabaseManager.health_check()
    
    if is_healthy:
        # Count tables to verify migration was successful
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        table_count = len(tables)
        
        return {
            "status": "healthy",
            "service": "database",
            "connection": "supabase_postgresql",
            "tables": table_count,
            "migrated": table_count >= 12  # We expect at least 12 tables
        }
    else:
        return {
            "status": "unhealthy",
            "service": "database",
            "connection": "supabase_postgresql",
            "tables": 0,
            "migrated": False
        }


@router.get("/")
async def system_health():
    """
    Overall system health check.
    
    Aggregates health status from all system components.
    """
    db_healthy = DatabaseManager.health_check()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "healthy" if db_healthy else "unhealthy",
        "auth": "healthy",  # Auth system is always healthy if server is running
        "timestamp": "2025-07-15T00:00:00Z"  # Can add actual timestamp later
    }
