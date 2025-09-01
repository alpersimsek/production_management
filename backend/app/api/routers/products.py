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
from api.schemas import ProductResponse
from services import ProductService
from typing import List


class ProductsRouter(APIRouter):
    def __init__(self):
        super().__init__()

        # Product Routes
        self.get("/products", response_model=List[ProductResponse])(self.get_products)

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
