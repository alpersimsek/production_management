#!/usr/bin/env python3
"""
Database reset script for Demo Kimya ERP
Drops and recreates database schema - removes all data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set environment variable for local database
os.environ["DATABASE_URL"] = "postgresql+psycopg://demo:demo@localhost:5433/demo"

from sqlalchemy import create_engine, text
from app.db import Base

def reset_database():
    """Drop and recreate database schema"""
    print("🔄 Resetting database schema...")
    
    try:
        # Create engine
        engine = create_engine(os.environ["DATABASE_URL"])
        
        # Drop all tables
        print("  🗑️ Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        
        # Create all tables
        print("  🏗️ Creating fresh schema...")
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database schema reset completed!")
        print("📊 Database is now empty with fresh schema")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during reset: {e}")
        return False

if __name__ == "__main__":
    success = reset_database()
    if success:
        print("\n🎉 Database schema is ready!")
        print("💡 Run 'python minimal_seed.py' to create admin user")
    else:
        print("\n💥 Database reset failed!")
        sys.exit(1)
