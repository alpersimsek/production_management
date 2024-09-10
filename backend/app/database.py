import sqlite3
from app.utils import get_db_connection

# Function to initialize the database and create the users table if it doesn't exist
def init_db():
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

# CRUD operations for the users
def get_user_by_username(username: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    return user

def create_user(username: str, password: str, role: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                   (username, password, role))

    conn.commit()
    conn.close()

def list_users():
    """
    Function to fetch all users from the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT username, role FROM users")
    users = cursor.fetchall()

    conn.close()

    return [{"username": user["username"], "role": user["role"]} for user in users]

def delete_user(username: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE username = ?", (username,))

    conn.commit()
    conn.close()

def update_user_password(username: str, new_password: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the user exists
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user:
        cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
        conn.commit()
        conn.close()
        return True
    else:
        conn.close()
        return False

def get_db_connection():
    conn = sqlite3.connect('app.db')
    conn.row_factory = sqlite3.Row  # This returns rows as dictionaries
    return conn