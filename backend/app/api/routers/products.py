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
