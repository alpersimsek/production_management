from fastapi import APIRouter
router = APIRouter()

@router.get('/')
async def get_shipments():
    return {"shipments": []}

@router.post('/')
async def create_shipment():
    return {"message": "Shipment created"}

