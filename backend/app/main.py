from fastapi import FastAPI
from app.database import init_db
from app.utils import create_required_directories, create_admin_user
from app.auth import router as auth_router
from app.users import router as users_router
from app.files import router as files_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (i.e., any domain and any port)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],   # Allow all headers
)


@app.on_event("startup")
async def startup_event():
    # Initialize the database and create admin user if not exists
    init_db()
    create_required_directories()
    create_admin_user()

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(users_router, prefix="/admin", tags=["users"])
app.include_router(files_router, prefix="/files", tags=["files"])
