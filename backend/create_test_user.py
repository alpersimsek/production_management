#!/usr/bin/env python3
"""
Script to create a test user for authentication
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set environment variable for local database
os.environ["DATABASE_URL"] = "postgresql+psycopg://olgahan:olgahan@localhost:5433/olgahan"

from sqlalchemy.orm import Session
from app.db import engine
from app.models.user import User, Role
from app.security.auth import get_password_hash

def create_test_user():
    with Session(engine) as db:
        # Create admin role if it doesn't exist
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            admin_role = Role(name="admin", permissions={})
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
        
        # Create test user if it doesn't exist
        test_user = db.query(User).filter(User.email == "admin@olgahan.com").first()
        if not test_user:
            test_user = User(
                email="admin@olgahan.com",
                password_hash=get_password_hash("admin123"),
                full_name="Admin User",
                role_id=admin_role.id,
                is_active=True
            )
            db.add(test_user)
            db.commit()
            print("Test user created successfully!")
            print("Email: admin@olgahan.com")
            print("Password: admin123")
        else:
            print("Test user already exists!")

if __name__ == "__main__":
    create_test_user()
