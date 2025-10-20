#!/usr/bin/env python3
"""
Minimal seed script for Demo Kimya ERP
Creates only admin user and essential roles - everything else from frontend
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

def create_admin_only():
    """Create only admin user and essential roles"""
    print("🌱 Creating admin user and roles...")
    
    try:
        with Session(engine) as db:
            # Check if roles exist, create if not
            print("  👥 Checking roles...")
            
            admin_role = db.query(Role).filter(Role.name == "Admin").first()
            if not admin_role:
                admin_role = Role(
                    name="Admin",
                    description="Full system access"
                )
                db.add(admin_role)
                db.commit()
                print("✅ Admin role created")
            else:
                print("✅ Admin role exists")
            
            manager_role = db.query(Role).filter(Role.name == "Manager").first()
            if not manager_role:
                manager_role = Role(
                    name="Manager",
                    description="Department management access"
                )
                db.add(manager_role)
                db.commit()
                print("✅ Manager role created")
            else:
                print("✅ Manager role exists")
            
            operator_role = db.query(Role).filter(Role.name == "Operator").first()
            if not operator_role:
                operator_role = Role(
                    name="Operator",
                    description="Production operations access"
                )
                db.add(operator_role)
                db.commit()
                print("✅ Operator role created")
            else:
                print("✅ Operator role exists")
            
            # Create admin user
            print("👤 Checking admin user...")
            
            existing_admin = db.query(User).filter(User.email == "admin@demo.com").first()
            if existing_admin:
                print("✅ Admin user already exists")
            else:
                admin_user = User(
                    full_name="Admin User",
                    email="admin@demo.com",
                    password_hash=get_password_hash("admin123"),
                    is_active=True,
                    role_id=1  # Admin role
                )
                
                db.add(admin_user)
                db.commit()
                print("✅ Admin user created")
            print("🎉 Setup complete!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💥 Setup failed!")
        return False
    
    return True

if __name__ == "__main__":
    create_admin_only()