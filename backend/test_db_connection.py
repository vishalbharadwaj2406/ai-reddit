#!/usr/bin/env python3
"""
Database Connection Test Script

This script tests the database connection before we start building models.
It's a critical first step to ensure everything is properly configured.
"""

import os
import sys
from sqlalchemy import create_engine, text

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from app.core.config import settings
from app.core.database import DatabaseManager


def test_database_connection():
    """Test database connection and basic operations."""
    print("🔗 Testing Database Connection...")
    print(f"📊 Database URL: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'Not configured'}")
    
    try:
        # Test basic connectivity
        print("\n1️⃣ Testing basic connectivity...")
        health_check = DatabaseManager.health_check()
        
        if health_check:
            print("✅ Database connection successful!")
        else:
            print("❌ Database connection failed!")
            return False
            
        # Test engine creation
        print("\n2️⃣ Testing SQLAlchemy engine...")
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as connection:
            # Test a simple query
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ PostgreSQL Version: {version}")
            
        # Test session creation
        print("\n3️⃣ Testing session management...")
        db_session = DatabaseManager.get_session()
        
        # Test a simple query through session
        result = db_session.execute(text("SELECT current_database()"))
        db_name = result.fetchone()[0]
        print(f"✅ Connected to database: {db_name}")
        
        db_session.close()
        
        print("\n🎉 All database tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Database test failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("- Check if your Supabase database is running")
        print("- Verify the DATABASE_URL in .env file")
        print("- Ensure your IP is allowed in Supabase settings")
        print("- Check username/password credentials")
        return False


if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1)
