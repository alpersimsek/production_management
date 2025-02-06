from fastapi import APIRouter, HTTPException, Request, status
from api.schemas import UserCreate, UserResponse, UpdatePassword, UserLogin, UserToken
from services import UserService


class UserRouter(APIRouter):

    def __init__(self):
        super().__init__()

        # Routes
        self.post("/login", response_model=UserToken)(self.login)
        self.post("/create", response_model=UserResponse)(self.create_user)
        self.get("/", response_model=list[UserResponse])(self.get_users)
        self.put("/update_password", response_model=UserResponse)(self.update_password)

    def login(self, data: UserLogin, req: Request):
        user_service = UserService(req.state.db)
        user = user_service.authenticate(data.username, data.password)
        if user:
            token = user_service.create_token(
                data={"user_id": user.id, "role": user.role.value}
            )
            return UserToken(access_token=token, token_type="bearer", role=user.role)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def create_user(self, user: UserCreate, req: Request):
        user_service = UserService(req.state.db)

        existing_user = user_service.get_user_by_username(user.username)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

        new_user = user_service.create_user(user.username, user.password, user.role)
        return UserResponse.model_validate(new_user)
    
    def get_users(self, req: Request):
        user_service = UserService(req.state.db)
        users = user_service.get_all()

        # Exclude the admin from the returned list
        return [UserResponse(user) for user in users if user.username != "admin"]

    def update_password(self, data: UpdatePassword, req: Request):
        user_service = UserService(req.state.db)
        user = user_service.update_password(data.username, data.password)
        if user:
            return {"detail": "Password updated successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    def delete_user(self, username: str, req: Request):
        if username == "admin":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete the admin user")
        
        user_service = UserService(req.state.db)
        user_service.delete_user(username)

        return {"detail": "User deleted successfully"}
