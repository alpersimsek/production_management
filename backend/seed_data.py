#!/usr/bin/env python3
"""
Seed data script for Olgahan Kimya ERP
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set environment variable for local database
os.environ["DATABASE_URL"] = "postgresql+psycopg://olgahan:olgahan@localhost:5433/olgahan"

from sqlalchemy.orm import Session
from app.db import engine
from app.models.user import User, Role
from app.models.product import Product, Formula
from app.models.order import Customer, Order, OrderItem
from app.models.production import ProductionJob, Lot, LotLog, DefectWaste, Packaging, WeeklyWeighing
from app.models.warehouse import Warehouse, WarehouseReceipt, Inventory
from app.models.shipment import Shipment, ShipmentItem
from app.models.notification import Notification
from app.models.settings import Settings
from app.security.auth import get_password_hash
from datetime import date, datetime, timedelta
from decimal import Decimal

def create_roles(db):
    """Create system roles"""
    roles_data = [
        {
            "name": "admin",
            "permissions": {
                "users": ["create", "read", "update", "delete"],
                "orders": ["create", "read", "update", "delete"],
                "production": ["create", "read", "update", "delete"],
                "warehouse": ["create", "read", "update", "delete"],
                "shipments": ["create", "read", "update", "delete"],
                "analytics": ["read"],
                "settings": ["create", "read", "update", "delete"]
            },
            "description": "System Administrator"
        },
        {
            "name": "plasiyer",
            "permissions": {
                "customers": ["create", "read", "update"],
                "orders": ["create", "read", "update"],
                "analytics": ["read"]
            },
            "description": "Sales Representative"
        },
        {
            "name": "uretim",
            "permissions": {
                "production": ["create", "read", "update"],
                "lots": ["create", "read", "update"],
                "packaging": ["create", "read", "update"],
                "analytics": ["read"]
            },
            "description": "Production Operator"
        },
        {
            "name": "depo",
            "permissions": {
                "warehouse": ["create", "read", "update"],
                "inventory": ["create", "read", "update"],
                "shipments": ["read", "update"],
                "analytics": ["read"]
            },
            "description": "Warehouse Operator"
        },
        {
            "name": "sevkiyat",
            "permissions": {
                "shipments": ["create", "read", "update"],
                "warehouse": ["read"],
                "analytics": ["read"]
            },
            "description": "Shipping Operator"
        }
    ]
    
    for role_data in roles_data:
        existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not existing_role:
            role = Role(**role_data)
            db.add(role)
    
    db.commit()
    print("✓ Roles created")

def create_users(db):
    """Create test users"""
    users_data = [
        {
            "full_name": "Admin User",
            "email": "admin@olgahan.com",
            "password_hash": get_password_hash("admin123"),
            "role_id": 1,  # admin
            "phone": "+90 555 000 0001",
            "department": "IT"
        },
        {
            "full_name": "Ahmet Yılmaz",
            "email": "ahmet@olgahan.com",
            "password_hash": get_password_hash("plasiyer123"),
            "role_id": 2,  # plasiyer
            "phone": "+90 555 000 0002",
            "department": "Satış"
        },
        {
            "full_name": "Mehmet Demir",
            "email": "mehmet@olgahan.com",
            "password_hash": get_password_hash("uretim123"),
            "role_id": 3,  # uretim
            "phone": "+90 555 000 0003",
            "department": "Üretim"
        },
        {
            "full_name": "Ayşe Kaya",
            "email": "ayse@olgahan.com",
            "password_hash": get_password_hash("depo123"),
            "role_id": 4,  # depo
            "phone": "+90 555 000 0004",
            "department": "Depo"
        },
        {
            "full_name": "Fatma Özkan",
            "email": "fatma@olgahan.com",
            "password_hash": get_password_hash("sevkiyat123"),
            "role_id": 5,  # sevkiyat
            "phone": "+90 555 000 0005",
            "department": "Sevkiyat"
        }
    ]
    
    for user_data in users_data:
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing_user:
            user = User(**user_data)
            db.add(user)
    
    db.commit()
    print("✓ Users created")

def create_customers(db):
    """Create sample customers"""
    customers_data = [
        {
            "name": "ABC Market Zinciri",
            "email": "siparis@abcmarket.com",
            "phone": "+90 212 555 0101",
            "address": "İstanbul, Türkiye",
            "tax_number": "1234567890",
            "is_active": True
        },
        {
            "name": "XYZ Süpermarket",
            "email": "info@xyzsmarket.com",
            "phone": "+90 312 555 0202",
            "address": "Ankara, Türkiye",
            "tax_number": "0987654321",
            "is_active": True
        },
        {
            "name": "DEF Mağazaları",
            "email": "satinalma@defmagaza.com",
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
    
    db.commit()
    print("✓ Customers created")

def create_products(db):
    """Create sample products"""
    products_data = [
        {
            "name": "Market Poşeti 30x40",
            "code": "POS001",
            "product_type": "poset",
            "unit": "kg",
            "efficiency": Decimal("95.5"),
            "is_active": True
        },
        {
            "name": "Bulaşık Deterjanı",
            "code": "DET001",
            "product_type": "deterjan",
            "unit": "kg",
            "efficiency": Decimal("92.0"),
            "is_active": True
        },
        {
            "name": "Temizlik Malzemesi",
            "code": "ALS001",
            "product_type": "al-sat",
            "unit": "adet",
            "efficiency": Decimal("88.5"),
            "is_active": True
        }
    ]
    
    for product_data in products_data:
        existing_product = db.query(Product).filter(Product.code == product_data["code"]).first()
        if not existing_product:
            product = Product(**product_data)
            db.add(product)
    
    db.commit()
    print("✓ Products created")

def create_warehouses(db):
    """Create sample warehouses"""
    warehouses_data = [
        {
            "code": "WH001",
            "name": "Ana Depo",
            "location": "Fabrika Merkez",
            "capacity_m3": Decimal("1000.0"),
            "is_active": True
        },
        {
            "code": "WH002",
            "name": "Yan Depo",
            "location": "Fabrika Yan",
            "capacity_m3": Decimal("500.0"),
            "is_active": True
        }
    ]
    
    for warehouse_data in warehouses_data:
        existing_warehouse = db.query(Warehouse).filter(Warehouse.code == warehouse_data["code"]).first()
        if not existing_warehouse:
            warehouse = Warehouse(**warehouse_data)
            db.add(warehouse)
    
    db.commit()
    print("✓ Warehouses created")

def create_notifications(db):
    """Create sample notifications"""
    notifications_data = [
        {
            "user_id": 1,  # admin
            "title": "Hoş Geldiniz!",
            "message": "Olgahan Kimya ERP sistemine hoş geldiniz. Sistem başarıyla kuruldu.",
            "notification_type": "success",
            "is_read": False
        },
        {
            "user_id": 2,  # plasiyer
            "title": "Yeni Sipariş",
            "message": "ABC Market Zinciri'nden yeni bir sipariş geldi. Lütfen kontrol edin.",
            "notification_type": "info",
            "is_read": False
        },
        {
            "user_id": 3,  # uretim
            "title": "Üretim Hatası",
            "message": "Lot #LOT001'de verim düşüklüğü tespit edildi. Lütfen kontrol edin.",
            "notification_type": "warning",
            "is_read": False
        }
    ]
    
    for notification_data in notifications_data:
        notification = Notification(**notification_data)
        db.add(notification)
    
    db.commit()
    print("✓ Notifications created")

def create_settings(db):
    """Create system settings"""
    settings_data = [
        {
            "key": "company_name",
            "value": {"value": "Olgahan Kimya"},
            "description": "Şirket adı",
            "updated_by": 1
        },
        {
            "key": "fire_threshold_level1",
            "value": {"percentage": 5.0},
            "description": "Seviye 1 yangın eşiği (%)",
            "updated_by": 1
        },
        {
            "key": "fire_threshold_level2",
            "value": {"percentage": 10.0},
            "description": "Seviye 2 yangın eşiği (%)",
            "updated_by": 1
        },
        {
            "key": "default_currency",
            "value": {"currency": "TRY"},
            "description": "Varsayılan para birimi",
            "updated_by": 1
        }
    ]
    
    for setting_data in settings_data:
        existing_setting = db.query(Settings).filter(Settings.key == setting_data["key"]).first()
        if not existing_setting:
            setting = Settings(**setting_data)
            db.add(setting)
    
    db.commit()
    print("✓ Settings created")

def main():
    """Main seed function"""
    print("🌱 Starting seed data creation...")
    
    with Session(engine) as db:
        try:
            create_roles(db)
            create_users(db)
            create_customers(db)
            create_products(db)
            create_warehouses(db)
            create_notifications(db)
            create_settings(db)
            
            print("\n✅ Seed data creation completed successfully!")
            print("\n📋 Test Users:")
            print("  Admin: admin@olgahan.com / admin123")
            print("  Plasiyer: ahmet@olgahan.com / plasiyer123")
            print("  Üretim: mehmet@olgahan.com / uretim123")
            print("  Depo: ayse@olgahan.com / depo123")
            print("  Sevkiyat: fatma@olgahan.com / sevkiyat123")
            
        except Exception as e:
            print(f"❌ Error creating seed data: {e}")
            db.rollback()
            raise

if __name__ == "__main__":
    main()
