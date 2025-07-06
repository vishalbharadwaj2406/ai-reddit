#!/usr/bin/env python3
"""
Development Setup Script

This script helps set up the development environment:
1. Checks if required environment variables are set
2. Tests database connection
3. Creates database tables
4. Provides helpful debug information

Run this script after setting up your .env file and installing dependencies.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

def check_environment():
    """Check if required environment variables are set."""
    print("🔍 Checking environment variables...")

    required_vars = [
        "DATABASE_URL",
        "JWT_SECRET_KEY",
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET"
    ]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("💡 Make sure to copy env.example to .env and fill in the values")
        return False

    print("✅ All required environment variables are set")
    return True


def test_config():
    """Test that configuration loads correctly."""
    print("🔧 Testing configuration...")

    try:
        from app.core.config import settings, print_settings
        print("✅ Configuration loaded successfully")
        print_settings()
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


def test_database_connection():
    """Test database connection."""
    print("🗄️  Testing database connection...")

    try:
        from app.core.database import DatabaseManager

        if DatabaseManager.health_check():
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database connection failed")
            print("💡 Make sure PostgreSQL is running and DATABASE_URL is correct")
            return False
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False


def create_tables():
    """Create database tables."""
    print("📋 Creating database tables...")

    try:
        from app.core.database import create_tables
        from app.models import *  # Import all models

        create_tables()
        print("✅ Database tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        print("💡 Make sure all models are properly defined")
        return False


def show_table_info():
    """Show information about created tables."""
    print("📊 Database table information:")

    try:
        from app.core.database import DatabaseManager
        DatabaseManager.get_table_info()
    except Exception as e:
        print(f"❌ Error getting table info: {e}")


def main():
    """Run the complete setup process."""
    print("🚀 AIkya Backend Development Setup")
    print("=" * 50)

    steps = [
        ("Environment Check", check_environment),
        ("Configuration Test", test_config),
        ("Database Connection", test_database_connection),
        ("Create Tables", create_tables),
    ]

    for step_name, step_func in steps:
        print(f"\n{step_name}:")
        if not step_func():
            print(f"\n❌ Setup failed at: {step_name}")
            print("Please fix the issue and run the script again.")
            sys.exit(1)

    print("\n📊 Final Database Status:")
    show_table_info()

    print("\n🎉 Development setup completed successfully!")
    print("\n📖 Next steps:")
    print("1. Start the development server: uvicorn app.main:app --reload")
    print("2. Visit http://localhost:8000/docs for API documentation")
    print("3. Run tests: pytest")
    print("4. Start implementing features according to implementation_guide.md")


if __name__ == "__main__":
    main()