"""
GDPR Tool Users Router - User Management and Authentication API Endpoints

This module provides REST API endpoints for user management and authentication in the GDPR compliance tool.
It handles user login, creation, password management, and user administration with role-based access control.

Key Endpoints:
- POST /login: User authentication with JWT token generation
- GET /users: Retrieve all users (admin access)
- POST /users: Create new users with role assignment
- PUT /users/{user_id}: Update user passwords
- DELETE /users/{user_id}: Delete users (with admin protection)

Authentication Features:
- JWT Token Generation: Secure token-based authentication
- Password Hashing: Bcrypt password hashing for security
- Role-Based Access: Admin and user role management
- Token Validation: JWT token validation with expiration
- Session Management: Secure session handling

User Management Features:
- User Creation: Create new users with username, password, and role
- Password Updates: Secure password change functionality
- User Deletion: Safe user removal with admin protection
- User Listing: Retrieve all users with admin filtering
- Username Validation: Prevent duplicate usernames

Security Features:
- Admin Protection: Admin user cannot be deleted
- Role Validation: Proper role assignment and validation
- Password Security: Secure password handling and hashing
- Authentication: JWT-based authentication with proper error handling
- Authorization: Role-based access control for admin operations

User Roles:
- ADMIN: Full system access, user management, system administration
- USER: Standard user access, file processing, data masking

The router integrates with UserService for business logic and provides
a secure user management system with proper authentication and authorization.
"""

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse
from api.schemas import (
    UserCreate,
    UserResponse,
    UpdatePassword,
    UserLogin,
    TokenResponse,
    UserDelete,
)
from services import UserService


class UserRouter(APIRouter):

    def __init__(self):
        super().__init__()

        # Routes
        self.post("/login", response_model=TokenResponse)(self.login)
        self.get("/users", response_model=list[UserResponse])(self.get_users)
        self.post("/users", response_model=UserResponse)(self.create_user)
        self.put("/users/{user_id}")(self.update_password)
        self.delete("/users/{user_id}")(self.delete_user)

    def login(self, data: UserLogin, req: Request):
        user_service = UserService(req.state.db)
        user = user_service.authenticate(data.username, data.password)
        if user:
            token = user_service.create_token(
                data={
                    "sub": "user_auth",
                    "user_id": str(user.id),
                    "role": user.role.value,
                }
            )
            return TokenResponse(
                access_token=token, token_type="bearer", role=user.role
            )
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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )

        new_user = user_service.create_user(user.username, user.password, user.role)
        return UserResponse.model_validate(new_user)

    def get_users(self, req: Request):
        user_service = UserService(req.state.db)
        users = user_service.get_all()

        # Exclude the admin from the returned list
        try:
            ulist = [
                UserResponse.model_validate(user)
                for user in users
                if user.username != "admin"
            ]
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        return ulist

    def update_password(self, user_id: str, data: UpdatePassword, req: Request):
        user_service = UserService(req.state.db)
        user = user_service.update_password(user_id, data.password)
        if user:
            return JSONResponse({"detail": "Password updated successfully"})
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

    def delete_user(self, user_id: str, req: Request):
        user_service = UserService(req.state.db)
        try:
            user_service.delete_user(user_id)
            return JSONResponse({"detail": "User deleted successfully"})
        except ValueError as ex:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ex))
        except Exception as ex:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex)
            )
