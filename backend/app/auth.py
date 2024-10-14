from fastapi import APIRouter, HTTPException
from app.utils import verify_password, create_access_token,create_user_folders
from app.schemas import Login, Token
from app.database import get_user_by_username

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(login_data: Login):
    user = get_user_by_username(login_data.username)
    
    if not user or not verify_password(login_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    create_user_folders(user["username"])

    # Generate JWT token
    token = create_access_token(data={"sub": user["username"], "role": user["role"]})
    
    return {"access_token": token, "token_type": "bearer", "role": user["role"]}
