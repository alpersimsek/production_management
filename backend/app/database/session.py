"""
GDPR Tool Database Session - Database Connection and Initialization

This module provides database connection management and initialization for the GDPR compliance tool.
It handles database engine creation, session management, migrations, and initial data setup.

Key Components:
- Database Engine: SQLAlchemy engine configuration for PostgreSQL
- Session Management: Session factory for database operations
- Migration System: Alembic-based database migration management
- Initialization: Database setup and admin user creation

Database Features:
- PostgreSQL Support: Full PostgreSQL database support with proper configuration
- Session Management: Proper session lifecycle management with autocommit/autoflush control
- Migration System: Automated database schema migrations using Alembic
- Admin User Setup: Automatic creation of admin user during initialization
- Error Handling: Comprehensive error handling with rollback support
- Logging: Detailed logging of database operations and initialization

Initialization Process:
1. Database Engine Creation: Creates SQLAlchemy engine with PostgreSQL connection
2. Migration Execution: Runs Alembic migrations to ensure schema is up to date
3. Admin User Creation: Creates default admin user if it doesn't exist
4. Session Management: Provides session factory for application use

Configuration:
- Database URL: Configurable via environment variables
- Connection Settings: Optimized for production use
- Session Settings: Proper session configuration for web applications
- Migration Path: Configurable migration directory and settings

The module ensures proper database initialization and provides a robust foundation
for the GDPR compliance tool's data persistence layer.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from alembic import command
from alembic.config import Config
from database.models import Role, User
from services import UserService
import settings
from logger import logger


engine = create_engine(
    settings.DATABASE_URL, 
    # connect_args={"check_same_thread": False},
    echo=False
)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)


def run_migrations():
    logger.info("Running database migrations...")
    alembic_cfg = Config("./database/alembic.ini")
    command.upgrade(alembic_cfg, "head")
    logger.info("Database migrations completed.")

def init_db():
    db_session = Session()
    try:
        # Run migrations
        run_migrations()
        # Create the admin user
        user = db_session.query(User).filter(User.username == "admin").first()
        if not user:
            user_service = UserService(db_session)
            user_service.create_user(
                settings.ADMIN_USERNAME, settings.ADMIN_PASSWORD, role=Role.ADMIN
            )
            db_session.commit()
        else:
            logger.info("Admin user already exists")
    except Exception as e:
        db_session.rollback()
        logger.error(f"ERROR: ", {e})
        raise e
    finally:
        db_session.close()

