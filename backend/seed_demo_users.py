#!/usr/bin/env python3
"""
Demo Users Seeding Script for Olgahan Kimya ERP
Creates all test users with proper roles and departments
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
import hashlib

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db import get_db
from app.models.user import User, Role
from app.models.order import Customer
from app.models.product import Product, Formula
from app.models.production import ProductionJob, Lot, LotLog, DefectWaste, Packaging, WeeklyWeighing
from app.models.warehouse import Warehouse, WarehouseReceipt, Inventory
from app.models.shipment import Shipment, ShipmentItem
from app.models.attachment import Attachment, AuditLog
from app.models.settings import Settings
from app.models.notification import Notification

def get_password_hash(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_roles(db):
    """Create default roles"""
    roles_data = [
        {
            "name": "admin",
            "permissions": {
                "users": ["create", "read", "update", "delete"],
                "orders": ["create", "read", "update", "delete"],
                "customers": ["create", "read", "update", "delete"],
                "products": ["create", "read", "update", "delete"],
                "production": ["create", "read", "update", "delete"],
                "warehouse": ["create", "read", "update", "delete"],
                "shipments": ["create", "read", "update", "delete"],
                "analytics": ["read"],
                "settings": ["read", "update"]
            },
            "description": "Full system access"
        },
        {
            "name": "manager",
            "permissions": {
                "users": ["read"],
                "orders": ["create", "read", "update"],
                "customers": ["create", "read", "update"],
                "products": ["read"],
                "production": ["create", "read", "update"],
                "warehouse": ["read", "update"],
                "shipments": ["create", "read", "update"],
                "analytics": ["read"]
            },
            "description": "Management level access"
        },
        {
            "name": "operator",
            "permissions": {
                "orders": ["read"],
                "customers": ["read"],
                "products": ["read"],
                "production": ["create", "read", "update"],
                "warehouse": ["read", "update"],
                "shipments": ["read"]
            },
            "description": "Operational level access"
        }
    ]
    
    for role_data in roles_data:
        existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not existing_role:
            role = Role(**role_data)
            db.add(role)
            print(f"Created role: {role_data['name']}")
        else:
            print(f"Role already exists: {role_data['name']}")
    
    db.commit()
    return db.query(Role).all()

def create_demo_users(db, roles):
    """Create all demo users"""
    # Get role IDs
    role_map = {role.name: role.id for role in roles}
    
    demo_users = [
        # Admin Users
        {
            "full_name": "Ahmet Yılmaz",
            "email": "ahmet@olgahan.com",
            "password": "admin123",
            "role_id": role_map["admin"],
            "department": "Üretim",
            "is_active": True
        },
        
        # Manager Users
        {
            "full_name": "Fatma Özkan",
            "email": "fatma@olgahan.com",
            "password": "manager123",
            "role_id": role_map["manager"],
            "department": "Üretim",
            "is_active": True
        },
        {
            "full_name": "Ayşe Demir",
            "email": "ayse@olgahan.com",
            "password": "manager123",
            "role_id": role_map["manager"],
            "department": "Depo",
            "is_active": False
        },
        {
            "full_name": "Elif Korkmaz",
            "email": "elif@olgahan.com",
            "password": "manager123",
            "role_id": role_map["manager"],
            "department": "Paketleme",
            "is_active": True
        },
        {
            "full_name": "Selin Aktaş",
            "email": "selin@olgahan.com",
            "password": "manager123",
            "role_id": role_map["manager"],
            "department": "Sevkiyat",
            "is_active": True
        },
        {
            "full_name": "Gülay Yılmaz",
            "email": "gulay@olgahan.com",
            "password": "manager123",
            "role_id": role_map["manager"],
            "department": "Plasiyer",
            "is_active": True
        },
        
        # Operator Users
        {
            "full_name": "Mehmet Kaya",
            "email": "mehmet@olgahan.com",
            "password": "operator123",
            "role_id": role_map["operator"],
            "department": "Paketleme",
            "is_active": True
        },
        {
            "full_name": "Ali Çelik",
            "email": "ali@olgahan.com",
            "password": "operator123",
            "role_id": role_map["operator"],
            "department": "Üretim",
            "is_active": True
        },
        {
            "full_name": "Zeynep Arslan",
            "email": "zeynep@olgahan.com",
            "password": "operator123",
            "role_id": role_map["operator"],
            "department": "Depo",
            "is_active": True
        },
        {
            "full_name": "Mustafa Yıldız",
            "email": "mustafa@olgahan.com",
            "password": "operator123",
            "role_id": role_map["operator"],
            "department": "Sevkiyat",
            "is_active": True
        },
        {
            "full_name": "Hasan Güneş",
            "email": "hasan@olgahan.com",
            "password": "operator123",
            "role_id": role_map["operator"],
            "department": "Plasiyer",
            "is_active": False
        },
        {
            "full_name": "Burak Şahin",
            "email": "burak@olgahan.com",
            "password": "operator123",
            "role_id": role_map["operator"],
            "department": "Üretim",
            "is_active": True
        }
    ]
    
    created_users = []
    for user_data in demo_users:
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing_user:
            # Hash the password
            user_data["password_hash"] = get_password_hash(user_data["password"])
            del user_data["password"]  # Remove plain password
            
            user = User(**user_data)
            db.add(user)
            created_users.append(user)
            print(f"Created user: {user_data['full_name']} ({user_data['email']})")
        else:
            print(f"User already exists: {user_data['full_name']} ({user_data['email']})")
    
    db.commit()
    return created_users

def create_sample_customers(db):
    """Create sample customers"""
    customers_data = [
        {
            "name": "ABC Kimya Ltd.",
            "email": "info@abckimya.com",
            "phone": "+90 212 555 0101",
            "address": "İstanbul, Türkiye",
            "tax_number": "1234567890",
            "is_active": True
        },
        {
            "name": "XYZ Deterjan A.Ş.",
            "email": "satış@xyzdeterjan.com",
            "phone": "+90 216 555 0202",
            "address": "Ankara, Türkiye",
            "tax_number": "0987654321",
            "is_active": True
        },
        {
            "name": "DEF Temizlik Ürünleri",
            "email": "info@deftemizlik.com",
            "phone": "+90 232 555 0303",
            "address": "İzmir, Türkiye",
            "tax_number": "1122334455",
            "is_active": True
        }
    ]
    
    for customer_data in customers_data:
        existing_customer = db.query(Customer).filter(Customer.name == customer_data["name"]).first()
        if not existing_customer:
            customer = Customer(**customer_data)
            db.add(customer)
            print(f"Created customer: {customer_data['name']}")
        else:
            print(f"Customer already exists: {customer_data['name']}")
    
    db.commit()

def create_sample_products(db):
    """Create sample products"""
    products_data = [
        {
            "name": "Poşet Deterjan",
            "code": "POSET-001",
            "product_type": "deterjan",
            "unit": "kg",
            "efficiency": 95.50,
            "is_active": True
        },
        {
            "name": "Sıvı Deterjan",
            "code": "SIYI-001",
            "product_type": "deterjan",
            "unit": "lt",
            "efficiency": 92.75,
            "is_active": True
        },
        {
            "name": "Çamaşır Suyu",
            "code": "CAMASIR-001",
            "product_type": "temizlik",
            "unit": "lt",
            "efficiency": 88.00,
            "is_active": True
        }
    ]
    
    for product_data in products_data:
        existing_product = db.query(Product).filter(Product.code == product_data["code"]).first()
        if not existing_product:
            product = Product(**product_data)
            db.add(product)
            print(f"Created product: {product_data['name']}")
        else:
            print(f"Product already exists: {product_data['name']}")
    
    db.commit()

def main():
    """Main seeding function"""
    print("🌱 Starting database seeding...")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create roles
        print("\n📋 Creating roles...")
        roles = create_roles(db)
        
        # Create demo users
        print("\n👥 Creating demo users...")
        users = create_demo_users(db, roles)
        
        # Create sample data
        print("\n🏢 Creating sample customers...")
        create_sample_customers(db)
        
        print("\n📦 Creating sample products...")
        create_sample_products(db)
        
        print(f"\n✅ Database seeding completed successfully!")
        print(f"   - Created {len(roles)} roles")
        print(f"   - Created {len(users)} users")
        print(f"   - Created sample customers and products")
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
