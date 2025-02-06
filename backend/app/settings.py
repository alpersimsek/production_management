import os
import secrets


DATA_DIR = os.getenv("DATA_DIR", "/data")
USERS_DIR = os.getenv("USERS_DIR", "")
API_PREFIX = os.getenv("API_PREFIX", "/api/v1")
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe())
ALGORITHM = os.getenv("ALGORITHM", "HS256")

DATABASE_URL = "sqlite:////db_data/app.db"
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

TOKEN_EXPIRE_MINUTES = 720
MAX_USER_FILES = 200
USER_FILES_SIZE_LIMIT = 10 * 1204**3  # 10 GB


