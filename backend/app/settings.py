import os
import pathlib
import secrets


DATA_DIR = os.getenv("DATA_DIR", pathlib.Path.home().joinpath("data"))
USERS_DIR = os.getenv("USERS_DIR", "")
API_PREFIX = os.getenv("API_PREFIX", "/api/v1")
SECRET_KEY = os.getenv("SECRET_KEY", "red-fox-jumps-over-the-fence")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# DATABASE_URL = "sqlite:////db_data/app.db"
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", 5432)
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "pgadm1324")
DB_NAME = os.environ.get("DB_NAME", "gdpr")
DATABASE_URL = (
    f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

TOKEN_EXPIRE_MINUTES = 720  # 12 hours
SIGNED_URL_EXPIRY_MINUTES = 5  # 5 minutes
MAX_USER_FILES = 200
REPORT_STEP = 100_000  # 100 KB
USER_STORAGE_LIMIT = 10 * 1204**3  # 10 GB
