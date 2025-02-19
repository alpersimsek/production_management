from pydantic import BaseModel, field_validator, computed_field
from fastapi import UploadFile
from datetime import datetime
from typing import Optional

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

class UserDelete(BaseModel):
    username: str

# File Schemas
class FileResponse(BaseModel):
    id: str
    filename: str
    file_size: int
    content_type: str
    status: str
    create_date: str
    product_id: Optional[int]
    preset_id: Optional[int]

    class Config:
        from_attributes = True

    @field_validator("create_date", mode="before")
    @classmethod
    def validate_create_date(cls, v):
        if isinstance(v, datetime):
            return v.isoformat()  # Convert datetime to string
        return v