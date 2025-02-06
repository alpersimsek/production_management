from pydantic import BaseModel

# User Schemas
class UserLogin(BaseModel):
    username: str
    password: str

class UserToken(BaseModel):
    access_token: str
    token_type: str
    role: str

class UserCreate(BaseModel):
    username: str
    password: str
    role: str

class UserResponse(BaseModel):
    username: str
    role: str

    class Config:
        from_attributes = True

class UpdatePassword(BaseModel):
    username: str
    password: str

# File Schemas
class FileResponse(BaseModel):
    id: str
    filename: str

    class Config:
        from_attributes = True