from fastapi import APIRouter
router = APIRouter()

@router.get('/')
async def get_lots():
    return {"lots": []}

@router.post('/')
async def create_lot():
    return {"message": "Lot created"}

