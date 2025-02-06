from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from alembic import command
from alembic.config import Config
from database.models import Base, Role, User
from services import UserService
import settings
import os


engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False},
    echo=True
)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    db_session = Session()
    try:
        # Base.metadata.create_all(bind=engine)
        # Run migrations
        alembic_cfg = Config("./database/alembic.ini")
        alembic_cfg.set_main_option('sqlalchemy.url', settings.DATABASE_URL)

        # migrations = os.path.join("database", "migrations", "versions")

        # # Check if the versions folder is empty or does not exist
        # if not os.path.exists(migrations) or not os.listdir(migrations):
        #     print("No migrations found. Creating initial migration...")
        #     # Generate an initial migration
        #     command.revision(alembic_cfg, autogenerate=True, message="Initial migration")

        command.upgrade(alembic_cfg, "head")  # Apply all migrations

        # Create the admin user
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
        print(f"ERROR: ", {e})
        raise e
    finally:
        db_session.close()


