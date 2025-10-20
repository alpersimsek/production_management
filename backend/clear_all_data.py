#!/usr/bin/env python3
"""
Clear all data from database except admin user and roles
Keeps only essential system data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set environment variable for local database
os.environ["DATABASE_URL"] = "postgresql+psycopg://olgahan:olgahan@localhost:5433/olgahan"

from sqlalchemy.orm import Session
from app.db import engine
from app.models.user import User, Role
from app.models.order import Order, OrderItem, Customer
from app.models.product import Product, Formula
from app.models.production import ProductionJob, Lot, LotLog, DefectWaste, Packaging, WeeklyWeighing
from app.models.warehouse import Warehouse, WarehouseReceipt, Inventory
from app.models.shipment import Shipment, ShipmentItem
from app.models.attachment import Attachment, AuditLog
from app.models.settings import Settings
from app.models.notification import Notification

def clear_all_data():
    """Clear all data except admin user and roles"""
    print("🧹 Clearing all data from database...")
    
    try:
        with Session(engine) as db:
            # Clear in correct order to respect foreign key constraints
            
            # Clear notifications
            print("📢 Clearing notifications...")
            db.query(Notification).delete()
            
            # Clear attachments and audit logs
            print("📎 Clearing attachments and audit logs...")
            db.query(Attachment).delete()
            db.query(AuditLog).delete()
            
            # Clear settings
            print("⚙️ Clearing settings...")
            db.query(Settings).delete()
            
            # Clear shipments (items first, then shipments)
            print("🚚 Clearing shipments...")
            db.query(ShipmentItem).delete()
            db.query(Shipment).delete()
            
            # Clear production data (in dependency order)
            print("🏭 Clearing production data...")
            db.query(WeeklyWeighing).delete()
            db.query(Packaging).delete()
            db.query(DefectWaste).delete()
            db.query(LotLog).delete()
            db.query(Lot).delete()
            db.query(ProductionJob).delete()
            
            # Clear warehouse data (in dependency order)
            print("📦 Clearing warehouse data...")
            db.query(Inventory).delete()
            db.query(WarehouseReceipt).delete()
            db.query(Warehouse).delete()
            
            # Clear orders (items first, then orders)
            print("📋 Clearing orders...")
            db.query(OrderItem).delete()
            db.query(Order).delete()
            
            # Clear products (formulas first, then products)
            print("🧪 Clearing products...")
            db.query(Formula).delete()
            db.query(Product).delete()
            
            # Clear customers
            print("👥 Clearing customers...")
            db.query(Customer).delete()
            
            # Clear all users except admin
            print("👤 Clearing non-admin users...")
            db.query(User).filter(User.email != "admin@demo.com").delete()
            
            db.commit()
            
            print("✅ All data cleared successfully!")
            print("🔑 Admin user and roles preserved")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💥 Clear failed!")
        return False
    
    return True

if __name__ == "__main__":
    clear_all_data()