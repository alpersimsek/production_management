from pydantic import BaseModel, field_validator, computed_field, Field
from fastapi import UploadFile
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from database.models import File, RuleCategory


# User Schemas
class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: str


class UserCreate(BaseModel):
    username: str
    password: str
    role: str


class UserResponse(BaseModel):
    id: str
    username: str
    role: str

    class Config:
        from_attributes = True

    @field_validator("id", mode="before")
    @classmethod
    def validate_create_date(cls, v):
        if isinstance(v, UUID):
            return str(v)  # Convert UUID to string
        return v


class UpdatePassword(BaseModel):
    password: str


class UserDelete(BaseModel):
    username: str


# File Schemas
class FileResponse(BaseModel):
    """File response schema."""

    id: str
    filename: str
    file_size: int = Field(..., example=1024)
    extracted_size: Optional[int] = Field(default=None, example=512)
    completed_size: Optional[int] = Field(default=0, example=512)
    time_remaining: Optional[int] = Field(default=None, example=30)
    status: str
    content_type: str
    create_date: datetime
    product_id: Optional[int] = None
    preset_id: Optional[int] = None

    class Config:
        from_attributes = True

    @field_validator("create_date", mode="before")
    @classmethod
    def validate_create_date(cls, v):
        if isinstance(v, datetime):
            return v.isoformat()  # Convert datetime to string
        return v

    @classmethod
    def model_validate(cls, obj: File) -> "FileResponse":
        """Convert File model to FileResponse schema."""
        return cls(
            id=obj.id,
            filename=obj.filename,
            file_size=obj.file_size,
            extracted_size=obj.extracted_size,
            completed_size=obj.completed_size,
            time_remaining=obj.time_remaining,
            status=obj.status.value,  # Use the string value of the enum
            content_type=obj.content_type.value,  # Use the string value of the enum
            create_date=obj.create_date,
        )


# Masking Map Schemas
class MaskingMapResponse(BaseModel):
    """Schema for returning masking map information."""

    id: int
    original_value: str
    masked_value: str
    category: str
    created_at: datetime

    class Config:
        from_attributes = True

    @field_validator("created_at", mode="before")
    @classmethod
    def validate_create_date(cls, v):
        if isinstance(v, datetime):
            return v.isoformat()  # Convert datetime to string
        return v

    @field_validator("category", mode="before")
    @classmethod
    def validate_category(cls, v):
        if hasattr(v, "value"):
            return v.value  # Convert enum to string
        return v

    @classmethod
    def model_validate(cls, obj):
        """Convert MaskingMap model to MaskingMapResponse schema."""
        return cls(
            id=obj.id,
            original_value=obj.original_value,
            masked_value=obj.masked_value,
            category=obj.category,
            created_at=obj.created_at,
        )


class MaskingMapSearch(BaseModel):
    """Schema for searching masking maps."""

    query: Optional[str] = None
    categories: Optional[List[str]] = None
    limit: Optional[int] = 100
    offset: Optional[int] = 0
    sort: Optional[str] = "created_at:desc"  # Format: field:direction


# Product Schemas
class ProductResponse(BaseModel):
    """Schema for returning product information."""

    id: int
    name: str

    class Config:
        from_attributes = True


# Rule Schemas
class RuleResponse(BaseModel):
    """Schema for returning rule information."""

    id: int
    name: str
    category: str
    config: Dict[str, Any]

    class Config:
        from_attributes = True

    @field_validator("category", mode="before")
    @classmethod
    def validate_category(cls, v):
        if hasattr(v, "value"):
            return v.value  # Convert enum to string
        return v


class RuleCreate(BaseModel):
    """Schema for creating a new rule."""

    name: str
    category: str
    config: Dict[str, Any]


class RuleUpdate(BaseModel):
    """Schema for updating an existing rule."""

    name: Optional[str] = None
    category: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


# Preset Schemas
class PresetResponse(BaseModel):
    """Schema for returning preset information."""

    id: int
    name: str
    product_id: int
    header: str
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True


class PresetCreate(BaseModel):
    """Schema for creating a new preset."""

    name: str
    product_id: int
    header: str


class PresetUpdate(BaseModel):
    """Schema for updating an existing preset."""

    name: Optional[str] = None
    product_id: Optional[int] = None
    header: Optional[str] = None


# Preset Rule Schemas
class PresetRuleResponse(BaseModel):
    """Schema for returning preset rule information."""

    preset_id: int
    rule_id: int
    action: Dict[str, Any]
    rule: Optional[RuleResponse] = None

    class Config:
        from_attributes = True


class PresetRuleCreate(BaseModel):
    """Schema for creating a new preset rule association."""

    preset_id: int
    rule_id: int
    action: Dict[str, Any]


class PresetRuleUpdate(BaseModel):
    """Schema for updating an existing preset rule association."""

    action: Dict[str, Any]
