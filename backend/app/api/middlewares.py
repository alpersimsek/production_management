"""
GDPR Tool API Middlewares - Request Processing and Authentication

This module contains middleware components that handle request processing, authentication,
and authorization for the GDPR compliance tool API.

Key Components:
- DBSessionMiddleware: Manages database session lifecycle per request
- AuthMiddleware: Handles JWT token authentication and user validation
- RBACMiddleware: Role-based access control for route protection

DBSessionMiddleware Features:
- Automatic database session creation and cleanup per request
- Transaction management with automatic commit/rollback
- Read-only operation detection (GET, OPTIONS, HEAD)
- Exception handling with proper session cleanup

AuthMiddleware Features:
- JWT token validation and user authentication
- Excluded routes for public access (login, docs, openapi)
- Token-based file download access
- User context injection into request state
- Comprehensive error handling for authentication failures

RBACMiddleware Features:
- Role-based access control for protected routes
- Configurable allowed roles per route
- User role validation against required permissions
- Flexible role checking with multiple role support

Security Features:
- Bearer token authentication
- JWT token validation with secret key verification
- User existence verification
- Role-based authorization
- Secure file download with token validation

The middleware stack ensures secure, authenticated access to the GDPR tool API
while providing proper database session management and role-based authorization.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from services import UserService
from database.session import Session
from database.models import User, Role
from jose import jwt, JWTError
import settings


class DBSessionMiddleware(BaseHTTPMiddleware):
    """Middleware that handles the lifecycle of the Database session per request."""

    async def dispatch(self, request: Request, call_next):
        # Create a new database session
        request.state.db = Session()

        try:
            # Process the request and get the response
            response = await call_next(request)
            # Only commit if it is not a read-only operation (eg. POST, PUT, PATCH, DELETE)
            if request.method not in ("GET", "OPTIONS", "HEAD"):
                request.state.db.commit()

        except Exception as e:
            # Rollback the session if an error occurs
            request.state.db.rollback()
            raise e
        finally:
            # Always close the session
            request.state.db.close()

        return response


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, req: Request, call_next):
        # Allow preflight OPTIONS requests to pass through
        if req.method == "OPTIONS":
            return await call_next(req)

        excluded_routes = [f"{settings.API_PREFIX}/login", "/docs", "/openapi.json"]

        if req.url.path in excluded_routes:
            return await call_next(req)

        if (
            req.url.path.startswith(f"{settings.API_PREFIX}/files/download")
            and "token" in req.query_params
        ):
            return await call_next(req)

        header = req.headers.get("Authorization")
        if header is None or not header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authenticated"
            )

        token = header.split(" ")[1]

        user_service = UserService(req.state.db)
        payload = user_service.validate_token(token)

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        if payload.get("sub") != "user_auth":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        # Fetch user from the database
        user_id: str = payload.get("user_id")
        user = user_service.get_by_id(user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials"
            )

        # Attach user to the request
        req.state.user = user

        response = await call_next(req)
        return response


class RBACMiddleware(BaseHTTPMiddleware):
    """
    Middleware that verifies if the current user has the required role to access a route.
    """

    def __init__(self, app, allowed_roles=None):
        super().__init__(app)
        self.allowed_roles = allowed_roles or []

    def dispatch(self, request: Request, call_next):
        # Fetch user roles from request (you might have the user roles in request state after authentication)
        user_roles = (
            request.state.user_roles if hasattr(request.state, "user_roles") else []
        )

        # Check if user has at least one of the allowed roles
        if not any(role in self.allowed_roles for role in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource.",
            )

        # Proceed to the next middleware or route
        response = call_next(request)
        return response
