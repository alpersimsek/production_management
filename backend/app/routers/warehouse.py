from fastapi import APIRouter
router = APIRouter()

@router.get('/')
async def get_warehouses():
    return {"warehouses": []}

@router.post('/')
async def create_warehouse():
    return {"message": "Warehouse created"}

