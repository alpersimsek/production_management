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
    logger.debug("Database session opened")
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
        logger.debug("Database connection closed")

