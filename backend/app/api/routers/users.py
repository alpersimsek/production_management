from fastapi import APIRouter, HTTPException, Request, status
from app.api.schemas import UserCreate, UserOut, UpdatePassword, Login, Token
from services import UserService


class UserRouter(APIRouter):

    def __init__(self):
        super().__init__()

        # Routes
        self.post("/login", response_model=Token)(self.login)
        self.post("/create", response_model=Token)(self.create_user)
        self.get("/", response_model=Token)(self.create_user)
        self.put("/update_password/{username}", response_model=UserOut)(self.update_password)

    def login(self, data: Login, req: Request):
        user_service = UserService(req.state.db)
        user = user_service.authenticate(data.username, data.password)
        if user:
            token = user_service.create_token(
                data={"user_id": user.id, "role": user.role}
            )
            return Token(access_token=token, token_type="bearer", role=user.role)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def create_user(user: UserCreate, req: Request):
        user_service = UserService(req.state.db)

        existing_user = user_service.get_user_by_username(user.username)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

        new_user = user_service.create_user(user.username, user.password, user.role)
        return UserOut(username=new_user.username, role=new_user.role)
    
    def get_users(req: Request):
        user_service = UserService(req.state.db)
        users = user_service.get_all()

        # Exclude the admin from the returned list
        filtered_users = [user for user in users if user.username != "admin"]
        return filtered_users

    def update_password(data: UpdatePassword, req: Request):
        user_service = UserService(req.state.db)
        user = user_service.update_password(data.username, data.password)
        if user:
            return {"detail": "Password updated successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    def delete_user(username: str, req: Request):
        if username == "admin":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete the admin user")
        
        user_service = UserService(req.state.db)
        user_service.delete_user(username)

        return {"detail": "User deleted successfully"}
