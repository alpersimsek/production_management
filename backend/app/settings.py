"""
GDPR Tool Settings - Application Configuration

This module contains all application configuration settings for the GDPR compliance tool.
It manages environment variables, database connections, security settings, and processing limits.

Key Configuration Areas:
- Database Settings: PostgreSQL connection parameters and URL construction
- Security Settings: JWT secret keys, algorithms, and token expiration times
- File Processing: Storage limits, processing steps, and user quotas
- API Configuration: API prefix and endpoint settings
- Exception Patterns: Regex patterns for excluding certain values from masking
- Admin Settings: Default admin user credentials

Environment Variables:
- DATA_DIR: Directory for file storage (default: ~/data)
- DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME: Database connection parameters
- SECRET_KEY: JWT signing secret (default: development key)
- ADMIN_USERNAME, ADMIN_PASSWORD: Admin user credentials
- API_PREFIX: API route prefix (default: /api/v1)

Processing Limits:
- MAX_USER_FILES: Maximum files per user (200)
- USER_STORAGE_LIMIT: Maximum storage per user (10GB)
- REPORT_STEP: Progress reporting interval (100KB)
- TOKEN_EXPIRE_MINUTES: JWT token expiration (12 hours)
- SIGNED_URL_EXPIRY_MINUTES: Download URL expiration (5 minutes)

Security Features:
- JWT token-based authentication with configurable expiration
- Signed URL system for secure file downloads
- Exception patterns to prevent masking of system values
- Environment-based configuration for production security
"""

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

EXCEPTION_PATTERNS = {
    "phone_num": [
        r'^\-?\d{4}\.\d{2}\.\d{2}\-\d{6}$',  # Matches -2025.05.05-001833 or 2025.05.05-001833
        r'^\d{4}\.\d{2}\.\d{2}$',  # Matches 2025.05.05
    ],
    "username": [
        r'^null$',  # Excludes 'null' from being caught as username
        r'^NULL$',  # Case insensitive exclusion
        r'^undefined$',  # Excludes 'undefined' as well
        r'^UNDEFINED$',  # Case insensitive exclusion
        r'^none$',  # Excludes 'none' as well
        r'^NONE$',  # Case insensitive exclusion
    ],
}

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

TOKEN_EXPIRE_MINUTES = 720  # 12 hours
SIGNED_URL_EXPIRY_MINUTES = 5  # 5 minutes
MAX_USER_FILES = 200
REPORT_STEP = 100_000  # 100 KB
USER_STORAGE_LIMIT = 10 * 1204**3  # 10 GB


'''
Note: Regex patterns are now configured in the database rules table.
This file only contains application configuration settings.
'''