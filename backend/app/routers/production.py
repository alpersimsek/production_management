from fastapi import APIRouter
router = APIRouter()

@router.get('/')
async def get_production_jobs():
    return {"production_jobs": []}

@router.post('/')
async def create_production_job():
    return {"message": "Production job created"}

