from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from ..db import get_db
from ..models.order import Order, OrderItem, Customer
from ..models.user import User, Role
from ..models.product import Product
from ..schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderItemCreate, OrderItemUpdate, OrderItemResponse
from ..utils.rbac import RBACManager, Permission
from ..utils.termin_manager import TerminColorManager
from ..security.auth import get_current_user

router = APIRouter()

def get_rbac_manager(db: Session = Depends(get_db)) -> RBACManager:
    return RBACManager(db)

def get_termin_manager(db: Session = Depends(get_db)) -> TerminColorManager:
    return TerminColorManager(db)

@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    customer_id: Optional[int] = Query(None),
    salesperson_id: Optional[int] = Query(None),
    due_date_from: Optional[date] = Query(None),
    due_date_to: Optional[date] = Query(None),
    color_code: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager),
    termin_manager: TerminColorManager = Depends(get_termin_manager)
):
    """Get list of orders with filtering and color coding"""
    try:
        if not rbac.has_permission(current_user.id, Permission.ORDER_READ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        query = db.query(Order).join(Customer)
        
        # Apply filters
        if search:
            query = query.filter(
                Customer.name.ilike(f"%{search}%") |
                Order.order_number.ilike(f"%{search}%")
            )
        
        if status:
            query = query.filter(Order.status == status)
        
        if customer_id:
            query = query.filter(Order.customer_id == customer_id)
        
        if salesperson_id:
            query = query.filter(Order.salesperson_id == salesperson_id)
        
        if due_date_from:
            query = query.filter(Order.due_date >= due_date_from)
        
        if due_date_to:
            query = query.filter(Order.due_date <= due_date_to)
        
        # Salesperson can only see their own orders
        role = db.query(Role).filter(Role.id == current_user.role_id).first()
        if role and role.name == "salesperson":
            query = query.filter(Order.salesperson_id == current_user.id)
        
        orders = query.offset(skip).limit(limit).all()
        
        # Add color coding and customer name
        result = []
        for order in orders:
            try:
                order_dict = OrderResponse.from_orm(order).dict()
                color_code, color_description, days_remaining = termin_manager.get_order_color_code(order)
                order_dict.update({
                    "color_code": color_code,
                    "color_description": color_description,
                    "days_remaining": days_remaining,
                    "customer_name": order.customer.name if order.customer else "Unknown Customer"
                })
                result.append(order_dict)
            except Exception as e:
                # If there's an error with one order, skip it but continue
                print(f"Error processing order {order.id}: {e}")
                continue
        
        # Filter by color code if specified
        if color_code:
            result = [order for order in result if order["color_code"] == color_code]
        
        return result
        
    except Exception as e:
        print(f"Error in get_orders: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager),
    termin_manager: TerminColorManager = Depends(get_termin_manager)
):
    """Get order by ID with color coding"""
    try:
        if not rbac.can_access_order(current_user.id, order_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        order_dict = OrderResponse.from_orm(order).dict()
        color_code, color_description, days_remaining = termin_manager.get_order_color_code(order)
        order_dict.update({
            "color_code": color_code,
            "color_description": color_description,
            "days_remaining": days_remaining
        })
        
        return order_dict
        
    except Exception as e:
        print(f"Error in get_order: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Create new order"""
    try:
        if not rbac.has_permission(current_user.id, Permission.ORDER_CREATE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        # Verify customer exists
        customer = db.query(Customer).filter(Customer.id == order_data.customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer not found"
            )
        
        # Generate order number
        order_number = f"ORD-{date.today().strftime('%Y%m%d')}-{db.query(Order).count() + 1:04d}"
        
        # Create order
        order = Order(
            order_number=order_number,
            customer_id=order_data.customer_id,
            salesperson_id=order_data.salesperson_id or current_user.id,
            due_date=order_data.due_date,
            total_amount=order_data.total_amount,
            discount_amount=order_data.discount_amount or 0,
            markup_amount=order_data.markup_amount or 0,
            fuel_cost=order_data.fuel_cost or 0,
            notes=order_data.notes,
            created_by=current_user.id
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        return order
        
    except Exception as e:
        print(f"Error in create_order: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_data: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Update order"""
    try:
        if not rbac.can_modify_order(current_user.id, order_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Update order fields
        update_data = order_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(order, key, value)
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        return order
        
    except Exception as e:
        print(f"Error in update_order: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.delete("/{order_id}")
async def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Delete order"""
    try:
        if not rbac.has_permission(current_user.id, Permission.ORDER_DELETE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # First delete all order items
        db.query(OrderItem).filter(OrderItem.order_id == order_id).delete()
        
        # Then delete the order
        db.delete(order)
        db.commit()
        
        return {"message": "Order deleted successfully"}
        
    except Exception as e:
        print(f"Error in delete_order: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/{order_id}/items", response_model=List[OrderItemResponse])
async def get_order_items(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Get order items"""
    try:
        if not rbac.can_access_order(current_user.id, order_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
        return order_items
        
    except Exception as e:
        print(f"Error in get_order_items: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/{order_id}/items", response_model=OrderItemResponse)
async def create_order_item(
    order_id: int,
    item_data: OrderItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Create order item"""
    try:
        if not rbac.can_modify_order(current_user.id, order_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        # Verify order exists
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Verify product exists
        product = db.query(Product).filter(Product.id == item_data.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product not found"
            )
        
        # Calculate total price
        total_price = item_data.quantity * item_data.unit_price
        
        order_item = OrderItem(
            order_id=order_id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            total_price=total_price,
            notes=item_data.notes
        )
        
        db.add(order_item)
        db.commit()
        db.refresh(order_item)
        
        return order_item
        
    except Exception as e:
        print(f"Error in create_order_item: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.put("/items/{item_id}", response_model=OrderItemResponse)
async def update_order_item(
    item_id: int,
    item_data: OrderItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Update order item"""
    try:
        order_item = db.query(OrderItem).filter(OrderItem.id == item_id).first()
        if not order_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order item not found"
            )
        
        if not rbac.can_modify_order(current_user.id, order_item.order_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        # Update order item fields
        update_data = item_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(order_item, key, value)
        
        db.add(order_item)
        db.commit()
        db.refresh(order_item)
        
        return order_item
        
    except Exception as e:
        print(f"Error in update_order_item: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.delete("/items/{item_id}")
async def delete_order_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Delete order item"""
    try:
        order_item = db.query(OrderItem).filter(OrderItem.id == item_id).first()
        if not order_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order item not found"
            )
        
        if not rbac.can_modify_order(current_user.id, order_item.order_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        db.delete(order_item)
        db.commit()
        
        return {"message": "Order item deleted successfully"}
        
    except Exception as e:
        print(f"Error in delete_order_item: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )