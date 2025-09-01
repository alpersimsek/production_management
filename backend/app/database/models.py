"""
GDPR Tool Database Models - Data Models and Schema Definition

This module defines the complete database schema for the GDPR compliance tool using SQLAlchemy.
It includes all data models, relationships, and enums for the application.

Key Components:
- Base Classes: DeclarativeBase for SQLAlchemy model inheritance
- Enums: ContentType, MimeType, Role, FileStatus, RuleCategory
- Models: User, File, Product, Preset, Rule, PresetRule, MaskingMap

Data Models:
- User: User authentication and authorization with role-based access
- File: File metadata, processing status, and archive relationships
- Product: Product definitions for product-based processing
- Preset: Preset configurations with header patterns and product associations
- Rule: Individual data masking rules with category and configuration
- PresetRule: Junction table linking presets to rules with actions
- MaskingMap: Storage for original and masked value mappings

Model Features:
- Relationships: Comprehensive foreign key relationships and cascading
- Enums: Type-safe enumeration values for consistent data
- Indexing: Proper database indexing for performance
- Constraints: Primary keys, foreign keys, and unique constraints
- Timestamps: Automatic timestamp management for audit trails
- JSON Fields: Flexible JSON storage for configuration data

User Model:
- UUID primary key for security
- Username uniqueness and role-based access
- Password storage with proper security
- File relationship with cascade deletion

File Model:
- String ID for file identification
- Processing status tracking with progress information
- Archive support with parent-child relationships
- Product and preset associations for processing
- Content type and MIME type support

Product Model:
- Simple product definition with unique names
- Preset relationships for product-based processing
- Auto-incrementing primary key

Preset Model:
- Product association for product-based processing
- Header patterns for automatic preset selection
- Rule relationships through PresetRule junction table
- File relationships for processing tracking

Rule Model:
- Category-based rule organization
- JSON configuration for flexible rule definitions
- Preset relationships through PresetRule junction table

PresetRule Model:
- Junction table with composite primary key
- Action configuration for rule-specific behavior
- Many-to-many relationship between presets and rules

MaskingMap Model:
- Original and masked value storage
- Category-based organization
- Unique constraints for consistency
- Timestamp tracking for audit trails

The models provide a comprehensive foundation for the GDPR compliance tool's
data persistence and relationship management.
"""

from sqlalchemy.orm import DeclarativeBase, Relationship, Mapped, mapped_column
from sqlalchemy import (
    String,
    Integer,
    BigInteger,
    ForeignKey,
    DateTime,
    Enum,
    JSON,
    UUID,
    func,
    PrimaryKeyConstraint,
)
import uuid
import enum


class ContentType(enum.Enum):
    TEXT = "text"
    PCAP = "pcap"
    ARCHIVE = "archive"
    JSON = "json"
    UNKNOWN = "unknown"
    DEFAULT = UNKNOWN


class MimeType(enum.Enum):
    TEXT = "text/plain"
    PCAP = "application/vnd.tcpdump.pcap"
    ZIP = "application/zip"
    TAR = "application/x-tar"
    GZIP = "application/gzip"
    JSON = "application/x-ndjson"
    TEXTX = "text/x-file"


class Role(enum.Enum):
    ADMIN = "admin"
    USER = "user"


class FileStatus(enum.Enum):
    CREATED = "created"
    IN_PROGRESS = "in-progress"
    DONE = "done"
    ERROR = "error"


class RuleCategory(enum.Enum):
    IPV4_ADDR = "ipv4_addr"
    MAC_ADDR = "mac_addr"
    USERNAME = "username"
    DOMAIN = "domain"
    PHONE_NUM = "phone_num"


class Base(DeclarativeBase):
    pass


# User model
class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.USER)

    # Relationships
    files: Mapped[list["File"]] = Relationship(
        "File", back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )


class File(Base):
    __tablename__ = "files"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    extracted_size: Mapped[int] = mapped_column(BigInteger, nullable=True)
    completed_size: Mapped[int] = mapped_column(BigInteger, default=0)
    time_remaining: Mapped[int] = mapped_column(Integer, nullable=True)
    content_type: Mapped[ContentType] = mapped_column(
        Enum(ContentType), default=ContentType.DEFAULT
    )
    status: Mapped[FileStatus] = mapped_column(
        Enum(FileStatus), default=FileStatus.CREATED
    )
    create_date: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"), nullable=True
    )
    preset_id: Mapped[int] = mapped_column(
        ForeignKey("presets.id", ondelete="SET NULL"), nullable=True
    )
    archive_id: Mapped[int] = mapped_column(
        ForeignKey("files.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Relationships
    user: Mapped[User] = Relationship("User", back_populates="files")
    product: Mapped["Product"] = Relationship("Product")
    preset: Mapped["Preset"] = Relationship("Preset", back_populates="files")

    archive: Mapped["File"] = Relationship(
        "File", remote_side="File.id", back_populates="archive_files"
    )
    archive_files: Mapped[list["File"]] = Relationship("File", back_populates="archive")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    # Relationships
    presets: Mapped[list["Preset"]] = Relationship("Preset", back_populates="product")


class Preset(Base):
    __tablename__ = "presets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    header: Mapped[str] = mapped_column(String, nullable=False)

    # Relationships
    rules: Mapped[list["PresetRule"]] = Relationship(
        "PresetRule", back_populates="preset"
    )
    files: Mapped[list["File"]] = Relationship("File", back_populates="preset")
    product: Mapped["Product"] = Relationship("Product", back_populates="presets")


# Rule table to define individual regex rules
class Rule(Base):
    __tablename__ = "rules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[RuleCategory] = mapped_column(Enum(RuleCategory), nullable=False)
    config: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Relationship back to PresetRules
    presets: Mapped[list["PresetRule"]] = Relationship(back_populates="rule")


# PresetRule table acting as a junction table linking Preset and Rule
class PresetRule(Base):
    __tablename__ = "preset_rules"

    preset_id: Mapped[int] = mapped_column(ForeignKey("presets.id"), nullable=False)
    rule_id: Mapped[int] = mapped_column(ForeignKey("rules.id"), nullable=False)
    action: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Composite primary key on preset_id and rule_id
    __table_args__ = (PrimaryKeyConstraint("preset_id", "rule_id"),)

    # Relationships
    preset: Mapped[Preset] = Relationship(back_populates="rules")
    rule: Mapped[Rule] = Relationship(back_populates="presets")


class MaskingMap(Base):
    __tablename__ = "masking_map"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    original_value: Mapped[str] = mapped_column(
        String, nullable=False, unique=True, index=True
    )
    masked_value: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[RuleCategory] = mapped_column(Enum(RuleCategory), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
