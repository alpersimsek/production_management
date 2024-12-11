from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
from api.middlewares import DBSessionMiddleware, AuthMiddleware
from app.session import init_db
from storage import FileStorage
import settings
from api.routers import UserRouter, FilesRouter


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

def init_middlewares():
    middleware = [
        Middleware(DBSessionMiddleware),
        Middleware(AuthMiddleware),
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
    ]
    return middleware

def get_app():
    storage = FileStorage(settings.DATA_DIR)
    middleware = init_middlewares()
    app = FastAPI(lifespan=lifespan, middleware=middleware)

    # Initialize api routers
    api_router: APIRouter = APIRouter(prefix=settings.API_PREFIX)
    user_router = UserRouter()
    file_router = FilesRouter(storage)

    api_router.include_router(user_router, tags=["users"])
    api_router.include_router(file_router, tags=["files"])
    app.include_router(api_router)
    return app