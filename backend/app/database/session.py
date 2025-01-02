from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from alembic import command
from alembic.config import Config
from database.models import Base, Role, User
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

        # Run migrations
        # alembic_cfg = Config("./alembic.ini")
        # alembic_cfg.set_main_option('sqlalchemy.url', settings.DATABASE_URL)
        # command.upgrade(alembic_cfg, "head")  # Apply all migrations

        # Create the admin user before running migrations
        user = db_session.query(User).filter(User.username == "admin").first()
        if not user:
            user_service = UserService(db_session)
            user_service.create_user(
                settings.ADMIN_USERNAME, settings.ADMIN_PASSWORD, role=Role.ADMIN
            )
            db_session.commit()
        else:
            print("Admin user already exists.")
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        db_session.close()

