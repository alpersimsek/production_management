from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from alembic import command
from alembic.config import Config
from app.database.models import Base, Role
from services import UserService
import settings


engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False},
    echo=True
)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    db_session = Session()
    try:
        Base.metadata.create_all(bind=engine)

        # Create the admin user before running migrations
        user_service = UserService(db_session)
        user_service.create_user(
            settings.ADMIN_USERNAME, settings.ADMIN_PASSWORD, role=Role.ADMIN
        )
        db_session.commit()
        
        # Run migrations
        # alembic_cfg = Config("./alembic.ini")
        # alembic_cfg.set_main_option('sqlalchemy.url', settings.DATABASE_URL)
        # command.upgrade(alembic_cfg, "head")  # Apply all migrations

    finally:
        db_session.close()

