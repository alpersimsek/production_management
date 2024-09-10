from fastapi import APIRouter, HTTPException
from app.database import create_user, delete_user, list_users, update_user_password
from app.schemas import UserCreate, UserOut, UpdatePassword
from app.utils import hash_password

router = APIRouter()

@router.post("/create_user", response_model=UserOut)
async def create_user_route(user: UserCreate):
    # Check if the username already exists
    existing_users = list_users()
    if any(existing_user['username'] == user.username for existing_user in existing_users):
        raise HTTPException(status_code=400, detail="Username already exists")

    # Create new user
    create_user(user.username, hash_password(user.password), user.role)
    return {"username": user.username, "role": user.role}

@router.get("/list_users")
async def list_users_route():
    users = list_users()

    # Exclude the admin from the returned list
    filtered_users = [user for user in users if user['username'] != 'admin']
    return filtered_users

@router.put("/update_password/{username}")
async def update_password_route(username: str, update_password: UpdatePassword):
    # Update the password of the user
    updated = update_user_password(username, hash_password(update_password.password))
    if updated:
        return {"detail": "Password updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")

@router.delete("/delete_user/{username}")
async def delete_user_route(username: str):
    # Ensure admin cannot be deleted
    if username == "admin":
        raise HTTPException(status_code=400, detail="Cannot delete the admin user")

    delete_user(username)
    return {"detail": "User deleted successfully"}
