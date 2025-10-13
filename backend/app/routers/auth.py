from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta
from ..db import get_db
from ..security.auth import authenticate_user, create_access_token, create_refresh_token, TokenData
from ..schemas.auth import LoginRequest, Token
from ..models.user import User, Role
from jose import JWTError, jwt

router = APIRouter()
security = HTTPBearer()

@router.post('/login', response_model=Token)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user role
    role = db.query(Role).filter(Role.id == user.role_id).first()
    role_name = role.name if role else "user"
    
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": role_name}, 
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "email": user.email, "role": role_name}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post('/logout')
async def logout():
    return {"message": "Successfully logged out"}

@router.get('/me')
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, "change_me", algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id, email=payload.get("email"), role=payload.get("role"))
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == int(token_data.user_id)).first()
    if user is None:
        raise credentials_exception
    
    role = db.query(Role).filter(Role.id == user.role_id).first()
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": role.name if role else "user",
        "is_active": user.is_active
    }

