from typing import Dict, List, Optional, Set
from enum import Enum
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

class Permission(Enum):
    """System permissions"""
    # User Management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    
    # Role Management
    ROLE_CREATE = "role:create"
    ROLE_READ = "role:read"
    ROLE_UPDATE = "role:update"
    ROLE_DELETE = "role:delete"
    
    # Order Management
    ORDER_CREATE = "order:create"
    ORDER_READ = "order:read"
    ORDER_UPDATE = "order:update"
    ORDER_DELETE = "order:delete"
    ORDER_APPROVE = "order:approve"
    
    # Production Management
    PRODUCTION_CREATE = "production:create"
    PRODUCTION_READ = "production:read"
    PRODUCTION_UPDATE = "production:update"
    PRODUCTION_DELETE = "production:delete"
    PRODUCTION_ASSIGN = "production:assign"
    PRODUCTION_START = "production:start"
    PRODUCTION_FINISH = "production:finish"
    
    # Lot Management
    LOT_CREATE = "lot:create"
    LOT_READ = "lot:read"
    LOT_UPDATE = "lot:update"
    LOT_DELETE = "lot:delete"
    LOT_WASTE = "lot:waste"
    LOT_LOG = "lot:log"
    
    # Packaging Management
    PACKAGING_CREATE = "packaging:create"
    PACKAGING_READ = "packaging:read"
    PACKAGING_UPDATE = "packaging:update"
    PACKAGING_DELETE = "packaging:delete"
    
    # Warehouse Management
    WAREHOUSE_CREATE = "warehouse:create"
    WAREHOUSE_READ = "warehouse:read"
    WAREHOUSE_UPDATE = "warehouse:update"
    WAREHOUSE_DELETE = "warehouse:delete"
    WAREHOUSE_RECEIPT = "warehouse:receipt"
    WAREHOUSE_APPROVE = "warehouse:approve"
    
    # Shipment Management
    SHIPMENT_CREATE = "shipment:create"
    SHIPMENT_READ = "shipment:read"
    SHIPMENT_UPDATE = "shipment:update"
    SHIPMENT_DELETE = "shipment:delete"
    SHIPMENT_PLAN = "shipment:plan"
    SHIPMENT_DELIVER = "shipment:deliver"
    
    # Analytics and Reports
    ANALYTICS_FIRE = "analytics:fire"
    ANALYTICS_PERFORMANCE = "analytics:performance"
    ANALYTICS_TERMIN = "analytics:termin"
    ANALYTICS_SALES = "analytics:sales"
    ANALYTICS_WASTE = "analytics:waste"
    ANALYTICS_QUALITY = "analytics:quality"
    ANALYTICS_PRODUCTION = "analytics:production"
    
    # Customer Management
    CUSTOMER_CREATE = "customer:create"
    CUSTOMER_READ = "customer:read"
    CUSTOMER_UPDATE = "customer:update"
    CUSTOMER_DELETE = "customer:delete"
    
    # Product Management
    PRODUCT_CREATE = "product:create"
    PRODUCT_READ = "product:read"
    PRODUCT_UPDATE = "product:update"
    PRODUCT_DELETE = "product:delete"
    
    # Settings Management
    SETTINGS_READ = "settings:read"
    SETTINGS_UPDATE = "settings:update"
    SETTINGS_FIRE_THRESHOLDS = "settings:fire_thresholds"
    SETTINGS_TERMIN_MINIMUM = "settings:termin_minimum"
    
    # File Management
    FILE_UPLOAD = "file:upload"
    FILE_DOWNLOAD = "file:download"
    FILE_DELETE = "file:delete"

class RolePermissions:
    """Role-based permission definitions"""
    
    ADMIN_PERMISSIONS = {
        # Full access to everything
        Permission.USER_CREATE, Permission.USER_READ, Permission.USER_UPDATE, Permission.USER_DELETE,
        Permission.ROLE_CREATE, Permission.ROLE_READ, Permission.ROLE_UPDATE, Permission.ROLE_DELETE,
        Permission.ORDER_CREATE, Permission.ORDER_READ, Permission.ORDER_UPDATE, Permission.ORDER_DELETE, Permission.ORDER_APPROVE,
        Permission.PRODUCTION_CREATE, Permission.PRODUCTION_READ, Permission.PRODUCTION_UPDATE, Permission.PRODUCTION_DELETE, Permission.PRODUCTION_ASSIGN,
        Permission.PRODUCTION_START, Permission.PRODUCTION_FINISH,
        Permission.LOT_CREATE, Permission.LOT_READ, Permission.LOT_UPDATE, Permission.LOT_DELETE, Permission.LOT_WASTE, Permission.LOT_LOG,
        Permission.PACKAGING_CREATE, Permission.PACKAGING_READ, Permission.PACKAGING_UPDATE, Permission.PACKAGING_DELETE,
        Permission.WAREHOUSE_CREATE, Permission.WAREHOUSE_READ, Permission.WAREHOUSE_UPDATE, Permission.WAREHOUSE_DELETE,
        Permission.WAREHOUSE_RECEIPT, Permission.WAREHOUSE_APPROVE,
        Permission.SHIPMENT_CREATE, Permission.SHIPMENT_READ, Permission.SHIPMENT_UPDATE, Permission.SHIPMENT_DELETE,
        Permission.SHIPMENT_PLAN, Permission.SHIPMENT_DELIVER,
        Permission.ANALYTICS_FIRE, Permission.ANALYTICS_PERFORMANCE, Permission.ANALYTICS_TERMIN, Permission.ANALYTICS_SALES,
        Permission.ANALYTICS_WASTE, Permission.ANALYTICS_QUALITY, Permission.ANALYTICS_PRODUCTION,
        Permission.CUSTOMER_CREATE, Permission.CUSTOMER_READ, Permission.CUSTOMER_UPDATE, Permission.CUSTOMER_DELETE,
        Permission.PRODUCT_CREATE, Permission.PRODUCT_READ, Permission.PRODUCT_UPDATE, Permission.PRODUCT_DELETE,
        Permission.SETTINGS_READ, Permission.SETTINGS_UPDATE, Permission.SETTINGS_FIRE_THRESHOLDS, Permission.SETTINGS_TERMIN_MINIMUM,
        Permission.FILE_UPLOAD, Permission.FILE_DOWNLOAD, Permission.FILE_DELETE
    }
    
    MANAGER_PERMISSIONS = {
        # Management level access
        Permission.USER_READ,
        Permission.ORDER_CREATE, Permission.ORDER_READ, Permission.ORDER_UPDATE, Permission.ORDER_APPROVE,
        Permission.PRODUCTION_CREATE, Permission.PRODUCTION_READ, Permission.PRODUCTION_UPDATE, Permission.PRODUCTION_ASSIGN,
        Permission.PRODUCTION_START, Permission.PRODUCTION_FINISH,
        Permission.LOT_CREATE, Permission.LOT_READ, Permission.LOT_UPDATE, Permission.LOT_WASTE, Permission.LOT_LOG,
        Permission.PACKAGING_CREATE, Permission.PACKAGING_READ, Permission.PACKAGING_UPDATE,
        Permission.WAREHOUSE_CREATE, Permission.WAREHOUSE_READ, Permission.WAREHOUSE_UPDATE, Permission.WAREHOUSE_APPROVE,
        Permission.SHIPMENT_CREATE, Permission.SHIPMENT_READ, Permission.SHIPMENT_UPDATE, Permission.SHIPMENT_PLAN,
        Permission.ANALYTICS_FIRE, Permission.ANALYTICS_PERFORMANCE, Permission.ANALYTICS_TERMIN, Permission.ANALYTICS_SALES,
        Permission.ANALYTICS_WASTE, Permission.ANALYTICS_QUALITY, Permission.ANALYTICS_PRODUCTION,
        Permission.CUSTOMER_CREATE, Permission.CUSTOMER_READ, Permission.CUSTOMER_UPDATE,
        Permission.PRODUCT_READ,
        Permission.SETTINGS_READ, Permission.SETTINGS_UPDATE, Permission.SETTINGS_FIRE_THRESHOLDS, Permission.SETTINGS_TERMIN_MINIMUM,
        Permission.FILE_UPLOAD, Permission.FILE_DOWNLOAD
    }
    
    PRODUCTION_OPERATOR_PERMISSIONS = {
        # Production operator access
        Permission.ORDER_READ,
        Permission.PRODUCTION_READ,
        Permission.LOT_CREATE, Permission.LOT_READ, Permission.LOT_UPDATE, Permission.LOT_WASTE, Permission.LOT_LOG,
        Permission.PACKAGING_READ,
        Permission.FILE_UPLOAD, Permission.FILE_DOWNLOAD
    }
    
    PACKAGING_PERMISSIONS = {
        # Packaging operator access
        Permission.ORDER_READ,
        Permission.PRODUCTION_READ,
        Permission.LOT_READ,
        Permission.PACKAGING_CREATE, Permission.PACKAGING_READ, Permission.PACKAGING_UPDATE,
        Permission.WAREHOUSE_READ,
        Permission.FILE_UPLOAD, Permission.FILE_DOWNLOAD
    }
    
    WAREHOUSE_PERMISSIONS = {
        # Warehouse operator access
        Permission.ORDER_READ,
        Permission.PRODUCTION_READ,
        Permission.LOT_READ,
        Permission.PACKAGING_READ,
        Permission.WAREHOUSE_READ, Permission.WAREHOUSE_RECEIPT, Permission.WAREHOUSE_APPROVE,
        Permission.SHIPMENT_READ,
        Permission.FILE_UPLOAD, Permission.FILE_DOWNLOAD
    }
    
    SHIPMENT_PERMISSIONS = {
        # Shipment operator access
        Permission.ORDER_READ,
        Permission.PRODUCTION_READ,
        Permission.LOT_READ,
        Permission.PACKAGING_READ,
        Permission.WAREHOUSE_READ,
        Permission.SHIPMENT_READ, Permission.SHIPMENT_UPDATE, Permission.SHIPMENT_DELIVER,
        Permission.FILE_UPLOAD, Permission.FILE_DOWNLOAD
    }
    
    SALESPERSON_PERMISSIONS = {
        # Salesperson access
        Permission.ORDER_CREATE, Permission.ORDER_READ, Permission.ORDER_UPDATE,  # Only own orders
        Permission.PRODUCTION_READ,
        Permission.LOT_READ,
        Permission.PACKAGING_READ,
        Permission.WAREHOUSE_READ,
        Permission.SHIPMENT_READ,
        Permission.ANALYTICS_SALES,  # Only own sales analytics
        Permission.FILE_UPLOAD, Permission.FILE_DOWNLOAD
    }
    
    # Operator permissions - limited to operational tasks
    OPERATOR_PERMISSIONS = {
        Permission.ORDER_READ,
        Permission.PRODUCTION_CREATE, Permission.PRODUCTION_READ, Permission.PRODUCTION_UPDATE,
        Permission.PRODUCTION_START, Permission.PRODUCTION_FINISH,
        Permission.LOT_CREATE, Permission.LOT_READ, Permission.LOT_UPDATE, Permission.LOT_WASTE, Permission.LOT_LOG,
        Permission.PACKAGING_CREATE, Permission.PACKAGING_READ, Permission.PACKAGING_UPDATE,
        Permission.WAREHOUSE_READ, Permission.WAREHOUSE_UPDATE,
        Permission.SHIPMENT_READ,
        Permission.CUSTOMER_READ,
        Permission.PRODUCT_READ,
        Permission.FILE_UPLOAD, Permission.FILE_DOWNLOAD
    }

class RBACManager:
    """Role-Based Access Control Manager"""
    
    def __init__(self, db: Session):
        self.db = db
        self.role_permissions = {
            'admin': RolePermissions.ADMIN_PERMISSIONS,
            'manager': RolePermissions.MANAGER_PERMISSIONS,
            'operator': RolePermissions.OPERATOR_PERMISSIONS,
            # Legacy role mappings for backward compatibility
            'production_operator': RolePermissions.PRODUCTION_OPERATOR_PERMISSIONS,
            'packaging': RolePermissions.PACKAGING_PERMISSIONS,
            'warehouse': RolePermissions.WAREHOUSE_PERMISSIONS,
            'shipment': RolePermissions.SHIPMENT_PERMISSIONS,
            'salesperson': RolePermissions.SALESPERSON_PERMISSIONS
        }
    
    def has_permission(self, user_id: int, permission: Permission) -> bool:
        """Check if user has specific permission"""
        from ..models.user import User, Role
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            return False
        
        role = self.db.query(Role).filter(Role.id == user.role_id).first()
        if not role:
            return False
        
        # Check if role has permission
        role_permissions = self.role_permissions.get(role.name.lower(), set())
        return permission in role_permissions
    
    def has_any_permission(self, user_id: int, permissions: List[Permission]) -> bool:
        """Check if user has any of the specified permissions"""
        return any(self.has_permission(user_id, perm) for perm in permissions)
    
    def has_all_permissions(self, user_id: int, permissions: List[Permission]) -> bool:
        """Check if user has all of the specified permissions"""
        return all(self.has_permission(user_id, perm) for perm in permissions)
    
    def get_user_permissions(self, user_id: int) -> Set[Permission]:
        """Get all permissions for a user"""
        from ..models.user import User, Role
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            return set()
        
        role = self.db.query(Role).filter(Role.id == user.role_id).first()
        if not role:
            return set()
        
        return self.role_permissions.get(role.name.lower(), set())
    
    def can_access_order(self, user_id: int, order_id: int) -> bool:
        """Check if user can access specific order"""
        from ..models.order import Order
        
        # Admin and managers can access all orders
        if self.has_permission(user_id, Permission.ORDER_READ):
            return True
        
        # Salesperson can only access their own orders
        if self.has_permission(user_id, Permission.ORDER_READ):
            order = self.db.query(Order).filter(Order.id == order_id).first()
            if order and order.salesperson_id == user_id:
                return True
        
        return False
    
    def can_modify_order(self, user_id: int, order_id: int) -> bool:
        """Check if user can modify specific order"""
        from ..models.order import Order
        
        # Admin and managers can modify all orders
        if self.has_permission(user_id, Permission.ORDER_UPDATE):
            return True
        
        # Salesperson can only modify their own orders
        if self.has_permission(user_id, Permission.ORDER_UPDATE):
            order = self.db.query(Order).filter(Order.id == order_id).first()
            if order and order.salesperson_id == user_id:
                return True
        
        return False
    
    def can_access_lot(self, user_id: int, lot_id: int) -> bool:
        """Check if user can access specific lot"""
        from ..models.production import Lot
        
        # Admin, managers, and production operators can access all lots
        if self.has_permission(user_id, Permission.LOT_READ):
            return True
        
        # Other roles can access lots from their department
        lot = self.db.query(Lot).filter(Lot.id == lot_id).first()
        if lot and lot.operator_id == user_id:
            return True
        
        return False
    
    def can_modify_lot(self, user_id: int, lot_id: int) -> bool:
        """Check if user can modify specific lot"""
        from ..models.production import Lot
        
        # Admin and managers can modify all lots
        if self.has_permission(user_id, Permission.LOT_UPDATE):
            return True
        
        # Production operators can modify their own lots
        if self.has_permission(user_id, Permission.LOT_UPDATE):
            lot = self.db.query(Lot).filter(Lot.id == lot_id).first()
            if lot and lot.operator_id == user_id:
                return True
        
        return False
    
    def initialize_default_roles(self) -> bool:
        """Initialize default roles with permissions"""
        from ..models.user import Role
        
        try:
            for role_name, permissions in self.role_permissions.items():
                # Check if role exists
                existing_role = self.db.query(Role).filter(Role.name == role_name).first()
                
                if not existing_role:
                    # Create new role
                    role = Role(
                        name=role_name,
                        permissions={'permissions': [p.value for p in permissions]},
                        description=f"Default {role_name} role"
                    )
                    self.db.add(role)
                else:
                    # Update existing role permissions
                    existing_role.permissions = {'permissions': [p.value for p in permissions]}
            
            self.db.commit()
            logger.info("Default roles initialized successfully")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to initialize default roles: {str(e)}")
            return False
    
    def get_role_permissions(self, role_name: str) -> Set[Permission]:
        """Get permissions for a specific role"""
        return self.role_permissions.get(role_name.lower(), set())
    
    def update_role_permissions(self, role_name: str, permissions: Set[Permission]) -> bool:
        """Update permissions for a specific role"""
        from ..models.user import Role
        
        try:
            role = self.db.query(Role).filter(Role.name == role_name).first()
            if not role:
                return False
            
            role.permissions = {'permissions': [p.value for p in permissions]}
            self.db.commit()
            
            # Update in-memory cache
            self.role_permissions[role_name.lower()] = permissions
            
            logger.info(f"Updated permissions for role {role_name}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update role permissions: {str(e)}")
            return False
