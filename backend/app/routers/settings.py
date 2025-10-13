from fastapi import APIRouter
router = APIRouter()

@router.get('/fire-thresholds')
async def get_fire_thresholds():
    return {
        "poset": {"level1_percent": 3, "level1_kg": 15, "level2_percent": 6, "level2_kg": 30},
        "deterjan": {"level1_percent": 2, "level1_kg": 10, "level2_percent": 4, "level2_kg": 20}
    }

