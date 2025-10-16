from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..db import get_db
from ..models.product import Product, Formula
from ..models.user import User
from ..schemas.product import ProductCreate, ProductUpdate, ProductResponse, FormulaCreate, FormulaResponse
from ..utils.rbac import RBACManager, Permission
from ..security.auth import get_current_user

router = APIRouter()

def get_rbac_manager(db: Session = Depends(get_db)) -> RBACManager:
    return RBACManager(db)

@router.get("/", response_model=List[ProductResponse])
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    product_type: Optional[str] = Query(None),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Get list of products"""
    if not rbac.has_permission(current_user.id, Permission.PRODUCT_READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    query = db.query(Product)
    
    if active_only:
        query = query.filter(Product.is_active == True)
    
    if search:
        query = query.filter(
            Product.name.ilike(f"%{search}%") |
            Product.code.ilike(f"%{search}%")
        )
    
    if product_type:
        query = query.filter(Product.product_type == product_type)
    
    products = query.offset(skip).limit(limit).all()
    return products

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Get product by ID"""
    if not rbac.has_permission(current_user.id, Permission.PRODUCT_READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product

@router.post("/", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Create new product"""
    if not rbac.has_permission(current_user.id, Permission.ORDER_CREATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if product with same code already exists
    existing_product = db.query(Product).filter(Product.code == product_data.code).first()
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this code already exists"
        )
    
    product = Product(**product_data.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    
    return product

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Update product"""
    if not rbac.has_permission(current_user.id, Permission.ORDER_UPDATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if code is being changed and if it already exists
    if product_data.code and product_data.code != product.code:
        existing_product = db.query(Product).filter(Product.code == product_data.code).first()
        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product with this code already exists"
            )
    
    # Update product fields
    for field, value in product_data.dict(exclude_unset=True).items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    
    return product

@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Delete product (soft delete)"""
    if not rbac.has_permission(current_user.id, Permission.ORDER_DELETE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Soft delete - just mark as inactive
    product.is_active = False
    db.commit()
    
    return {"message": "Product deleted successfully"}

# Formula endpoints
@router.get("/{product_id}/formulas", response_model=List[FormulaResponse])
async def get_product_formulas(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Get formulas for a product"""
    if not rbac.has_permission(current_user.id, Permission.PRODUCTION_READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    formulas = db.query(Formula).filter(
        Formula.product_id == product_id,
        Formula.is_active == True
    ).order_by(Formula.valid_from.desc()).all()
    
    return formulas

@router.post("/{product_id}/formulas", response_model=FormulaResponse)
async def create_product_formula(
    product_id: int,
    formula_data: FormulaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rbac: RBACManager = Depends(get_rbac_manager)
):
    """Create new formula for a product"""
    if not rbac.has_permission(current_user.id, Permission.PRODUCTION_CREATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if formula version already exists for this product
    existing_formula = db.query(Formula).filter(
        Formula.product_id == product_id,
        Formula.version == formula_data.version
    ).first()
    if existing_formula:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formula with this version already exists for this product"
        )
    
    formula = Formula(
        product_id=product_id,
        **formula_data.dict()
    )
    db.add(formula)
    db.commit()
    db.refresh(formula)
    
    return formula
