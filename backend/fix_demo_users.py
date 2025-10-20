#!/usr/bin/env python3
"""
Fix Demo Users Script
Updates passwords and roles for all demo users
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import hashlib

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db import get_db
from app.models.user import User, Role

def get_password_hash(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def fix_demo_users():
    """Fix all demo users passwords and roles"""
    print("🔧 Fixing demo users...")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Get roles
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        manager_role = db.query(Role).filter(Role.name == "manager").first()
        operator_role = db.query(Role).filter(Role.name == "operator").first()
        
        if not admin_role or not manager_role or not operator_role:
            print("❌ Roles not found. Please run seed_demo_users.py first.")
            return
        
        # Define users with correct roles
        users_to_fix = [
            # Admin Users
            {"email": "ahmet@demo.com", "password": "admin123", "role": admin_role},
            
            # Manager Users
            {"email": "fatma@demo.com", "password": "manager123", "role": manager_role},
            {"email": "ayse@demo.com", "password": "manager123", "role": manager_role},
            {"email": "elif@demo.com", "password": "manager123", "role": manager_role},
            {"email": "selin@demo.com", "password": "manager123", "role": manager_role},
            {"email": "gulay@demo.com", "password": "manager123", "role": manager_role},
            
            # Operator Users
            {"email": "mehmet@demo.com", "password": "operator123", "role": operator_role},
            {"email": "ali@demo.com", "password": "operator123", "role": operator_role},
            {"email": "zeynep@demo.com", "password": "operator123", "role": operator_role},
            {"email": "mustafa@demo.com", "password": "operator123", "role": operator_role},
            {"email": "hasan@demo.com", "password": "operator123", "role": operator_role},
            {"email": "burak@demo.com", "password": "operator123", "role": operator_role},
        ]
        
        fixed_count = 0
        for user_data in users_to_fix:
            user = db.query(User).filter(User.email == user_data["email"]).first()
            if user:
                # Update password hash
                user.password_hash = get_password_hash(user_data["password"])
                # Update role
                user.role_id = user_data["role"].id
                db.add(user)
                fixed_count += 1
                print(f"✅ Fixed: {user.full_name} ({user.email}) - Role: {user_data['role'].name}")
            else:
                print(f"❌ User not found: {user_data['email']}")
        
        db.commit()
        print(f"\n🎉 Successfully fixed {fixed_count} users!")
        
    except Exception as e:
        print(f"❌ Error fixing users: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fix_demo_users()


