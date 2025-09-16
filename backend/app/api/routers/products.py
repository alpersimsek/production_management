"""
GDPR Tool Products Router - Product Management API Endpoints

This module provides REST API endpoints for managing products in the GDPR compliance tool.
It handles product retrieval and management for the product-based processing system.

Key Endpoints:
- GET /products: Retrieve all available products

Product Features:
- Product Listing: Get all products available in the system
- Product-Based Processing: Products are used for intelligent preset selection
- Preset Association: Products can have multiple presets with different configurations
- Header Matching: Products enable header-based preset selection for files

Product-Based Processing:
- Product Selection: Users can select products during file processing
- Preset Matching: System matches file headers against product-specific presets
- Rule Application: Applies rules associated with matched presets
- Fallback Strategy: Uses all product presets if no header match is found

Security Features:
- JWT Authentication: All endpoints require valid authentication
- User Context: User-specific access and filtering
- Error Handling: Comprehensive error responses with proper HTTP status codes

The router integrates with ProductService for business logic and provides
a simple but essential API for product management in GDPR data processing workflows.
"""

from fastapi import APIRouter, HTTPException, Request, status
from api.schemas import ProductResponse, ProductCreate
from services import ProductService
from typing import List
from logger import logger


class ProductsRouter(APIRouter):
    def __init__(self):
        super().__init__()

        # Product Routes
        self.get("/products", response_model=List[ProductResponse])(self.get_products)
        self.post("/products", response_model=ProductResponse)(self.create_product)
        self.delete("/products/{product_id}")(self.delete_product)

    def get_products(self, req: Request):
        """Get all products."""
        product_service = ProductService(req.state.db)
        try:
            products = product_service.get_all()
            return [ProductResponse.model_validate(product) for product in products]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    def create_product(self, req: Request, product_data: ProductCreate):
        """Create a new product."""
        product_service = ProductService(req.state.db)
        try:
            # Create new product instance
            from database.models import Product
            new_product = Product(name=product_data.name)
            created_product = product_service.create(new_product)
            
            # Log successful product creation
            logger.info({
                "event": "product_created",
                "product_name": created_product.name,
                "username": req.state.user.username if hasattr(req.state, 'user') and req.state.user else "unknown"
            })
            
            return ProductResponse.model_validate(created_product)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    def delete_product(self, req: Request, product_id: int):
        """Delete a product if it has no presets."""
        product_service = ProductService(req.state.db)
        try:
            # Check if product exists
            product = product_service.get_by_id(product_id)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="Product not found"
                )
            
            # Check if product has presets
            if product.presets and len(product.presets) > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot delete product '{product.name}' because it has {len(product.presets)} preset(s) associated with it. Please delete all presets first."
                )
            
            # Delete the product
            product_service.delete(product_id)
            
            # Log successful product deletion
            logger.info({
                "event": "product_deleted",
                "product_id": product_id,
                "product_name": product.name,
                "username": req.state.user.username if hasattr(req.state, 'user') and req.state.user else "unknown"
            })
            
            return {"message": f"Product '{product.name}' deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )
