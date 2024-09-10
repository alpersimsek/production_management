import os
import hashlib
from passlib.context import CryptContext
from jose import jwt
import sqlite3

# Password hashing and JWT configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key")
ALGORITHM = "HS256"

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# User folder management
def create_user_folders(username):
    user_dir = f"users/{username}"
    os.makedirs(f"{user_dir}/uploads", exist_ok=True)
    os.makedirs(f"{user_dir}/processed", exist_ok=True)
    os.makedirs(f"{user_dir}/extracted", exist_ok=True)
    os.makedirs(f"{user_dir}/process_zip", exist_ok=True)

def remove_user_folders(username):
    user_dir = f"users/{username}"
    if os.path.exists(user_dir):
        for root, dirs, files in os.walk(user_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(user_dir)

# File handling
def handle_file_upload(username, file):
    user_dir = f"users/{username}/uploads"
    
    # Create directory if it doesn't exist
    os.makedirs(user_dir, exist_ok=True)
    
    file_path = os.path.join(user_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

def get_user_files(username):
    """
    Retrieves the list of files uploaded by the user in the uploads and processed directories.
    """
    user_dir = f"users/{username}"
    uploaded_dir = os.path.join(user_dir, 'uploads')
    processed_dir = os.path.join(user_dir, 'processed')
    
    uploaded_files = []
    processed_files = []

    # List uploaded files
    if os.path.exists(uploaded_dir):
        uploaded_files = os.listdir(uploaded_dir)

    # List processed files
    if os.path.exists(processed_dir):
        processed_files = os.listdir(processed_dir)

    return {
        "uploaded_files": uploaded_files,
        "processed_files": processed_files
    }

# GDPR directory setup
def create_required_directories():
    os.makedirs("users/gdpr_map", exist_ok=True)

def create_admin_user():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    admin = cursor.fetchone()

    if not admin:
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ('admin', hash_password('admin'), 'admin')
        )
        conn.commit()

    conn.close()

def get_db_connection():
    conn = sqlite3.connect('app.db')
    conn.row_factory = sqlite3.Row  # This returns rows as dictionaries
    return conn
