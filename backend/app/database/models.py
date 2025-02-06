from sqlalchemy.orm import DeclarativeBase, Relationship, Mapped, mapped_column
from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    DateTime,
    Enum,
    JSON,
    func,
    PrimaryKeyConstraint,
    Text,
)
import uuid
import enum


class ContentType(enum.Enum):
    TEXT = "text"
    PCAP = "pcap"
    DEFAULT = TEXT


class Role(enum.Enum):
    ADMIN = "admin"
    USER = "user"


class FileStatus(enum.Enum):
    CREATED = "created"
    IN_PROGRESS = "in-progress"
    DONE = "done"
    ERROR = "error"


class Base(DeclarativeBase):
    pass


# User model
class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String, default=lambda: str(uuid.uuid4()), primary_key=True, unique=True
    )
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.USER)

    # Relationships
    files: Mapped[list["File"]] = Relationship(
        "File", back_populates="user", cascade="all, delete-orphan"
    )


class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    completed_size: Mapped[int] = mapped_column(Integer, default=0)
    time_remaining: Mapped[int] = mapped_column(Integer, nullable=True)
    content_type: Mapped[str] = mapped_column(String, nullable=False, default=ContentType.DEFAULT)
    status: Mapped[FileStatus] = mapped_column(
        Enum(FileStatus), default=FileStatus.CREATED
    )
    create_date: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    preset_id: Mapped[int] = mapped_column(ForeignKey("presets.id"), nullable=True)
    archive_id: Mapped[int] = mapped_column(Integer, nullable=True, index=True, default=None)

    # Relationships
    user: Mapped[User] = Relationship("User", back_populates="files")
    product: Mapped["Product"] = Relationship("Product")
    preset: Mapped["Preset"] = Relationship("Preset", back_populates="files")


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
    rules: Mapped[list["PresetRule"]] = Relationship("PresetRule", back_populates="preset")
    files: Mapped[list["File"]] = Relationship("File", back_populates="preset")
    product: Mapped["Product"] = Relationship("Product", back_populates="presets")


# Rule table to define individual regex rules
class Rule(Base):
    __tablename__ = "rules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    config: Mapped[str] = mapped_column(JSON, nullable=False)

    # Relationship back to PresetRules
    presets: Mapped[list["PresetRule"]] = Relationship(back_populates="rule")


# PresetRule table acting as a junction table linking Preset and Rule
class PresetRule(Base):
    __tablename__ = "preset_rules"

    preset_id: Mapped[int] = mapped_column(ForeignKey("presets.id"), nullable=False)
    rule_id: Mapped[int] = mapped_column(ForeignKey("rules.id"), nullable=False)
    action: Mapped[str] = mapped_column(JSON, nullable=False)

    # Composite primary key on preset_id and rule_id
    __table_args__ = (PrimaryKeyConstraint("preset_id", "rule_id"),)

    # Relationships
    preset: Mapped[Preset] = Relationship(back_populates="rules")
    rule: Mapped[Rule] = Relationship(back_populates="presets")


class MaskingMap(Base):
    __tablename__ = "masking_map"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    original_value: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    masked_value: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
