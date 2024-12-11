from pydantic import BaseModel

# Schema for login input (username and password)
class Login(BaseModel):
    username: str
    password: str

# Schema for the JWT token response
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

# Schema for user creation input
class UserCreate(BaseModel):
    username: str
    password: str
    role: str

# Schema for user output (e.g., listing users)
class UserOut(BaseModel):
    username: str
    role: str

class UpdatePassword(BaseModel):
    username: str
    password: str