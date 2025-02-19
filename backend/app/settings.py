import os
import secrets


DATA_DIR = os.getenv("DATA_DIR", "data")
USERS_DIR = os.getenv("USERS_DIR", "")
API_PREFIX = os.getenv("API_PREFIX", "/api/v1")
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe())
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# DATABASE_URL = "sqlite:////db_data/app.db"
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', 5432)
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_NAME = os.environ.get('DB_NAME', 'postgres')
DATABASE_URL = f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

TOKEN_EXPIRE_MINUTES = 720
MAX_USER_FILES = 200
REPORT_STEP = 100_000  # 100 KB
USER_STORAGE_LIMIT = 10 * 1204**3  # 10 GB


