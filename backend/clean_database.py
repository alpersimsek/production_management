#!/usr/bin/env python3
"""
Database cleanup script for Demo Kimya ERP
Removes all data but keeps database schemas
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set environment variable for local database
os.environ["DATABASE_URL"] = "postgresql+psycopg://demo:demo@localhost:5433/demo"

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
from app.models.attachment import Attachment

def clean_database():
    """Remove all data from database tables while keeping schemas"""
    print("🧹 Starting database cleanup...")
    
    with Session(engine) as db:
        try:
            # Delete all data from tables (in reverse dependency order)
            print("  📦 Cleaning attachments...")
            db.query(Attachment).delete()
            
            print("  📋 Cleaning notifications...")
            db.query(Notification).delete()
            
            print("  ⚙️ Cleaning settings...")
            db.query(Settings).delete()
            
            print("  🚚 Cleaning shipments...")
            db.query(ShipmentItem).delete()
            db.query(Shipment).delete()
            
            print("  📦 Cleaning warehouse data...")
            db.query(Inventory).delete()
            db.query(WarehouseReceipt).delete()
            db.query(Warehouse).delete()
            
            print("  🏭 Cleaning production data...")
            db.query(WeeklyWeighing).delete()
            db.query(Packaging).delete()
            db.query(DefectWaste).delete()
            db.query(LotLog).delete()
            db.query(Lot).delete()
            db.query(ProductionJob).delete()
            
            print("  📋 Cleaning orders...")
            db.query(OrderItem).delete()
            db.query(Order).delete()
            db.query(Customer).delete()
            
            print("  🧪 Cleaning products...")
            db.query(Formula).delete()
            db.query(Product).delete()
            
            print("  👥 Cleaning users...")
            db.query(User).delete()
            db.query(Role).delete()
            
            # Commit all changes
            db.commit()
            
            print("✅ Database cleanup completed successfully!")
            print("📊 Database is now empty and ready for fresh data entry from frontend")
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
            db.rollback()
            return False
    
    return True

if __name__ == "__main__":
    success = clean_database()
    if success:
        print("\n🎉 Database is ready for frontend data entry!")
        print("💡 You can now add data through the frontend interface")
    else:
        print("\n💥 Database cleanup failed!")
        sys.exit(1)
