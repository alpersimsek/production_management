from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from database.session import Session
from database.models import User
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
        excluded_routes = ["/api/v1/login", "/docs", "/openapi.json"]

        if req.url.path in excluded_routes:
            return await call_next(req)
        
        header = req.headers.get("Authorization")
        if header is None or not header.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authenticated")
        
        token = header.split(" ")[1]

        payload = self.validate_token(token)

        user_id: str = payload.get("user_id")            

        # Fetch user from the database
        db = req.state.db
        user = db.query(User).filter(User.id == user_id).first()

        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")

        # Attach user to the request
        req.state.user = user
        
        response = await call_next(req)
        return response
    
    def validate_token(self, token: str):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")
        

class RBACMiddleware(BaseHTTPMiddleware):
    """
    Middleware that verifies if the current user has the required role to access a route.
    """

    def __init__(self, app, allowed_roles=None):
        super().__init__(app)
        self.allowed_roles = allowed_roles or []

    def dispatch(self, request: Request, call_next):
        # Fetch user roles from request (you might have the user roles in request state after authentication)
        user_roles = request.state.user_roles if hasattr(request.state, 'user_roles') else []

        # Check if user has at least one of the allowed roles
        if not any(role in self.allowed_roles for role in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource."
            )

        # Proceed to the next middleware or route
        response = call_next(request)
        return response
