from fastapi import APIRouter
router = APIRouter()

@router.get('/')
async def get_packaging():
    return {"packaging": []}

@router.post('/')
async def create_packaging():
    return {"message": "Packaging created"}

