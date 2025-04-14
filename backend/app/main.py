from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
import uvicorn.logging
from api.middlewares import DBSessionMiddleware, AuthMiddleware
from database.session import init_db
from storage import FileStorage
import settings
from api.routers import (
    UserRouter,
    FilesRouter,
    MaskingMapRouter,
    PresetsRouter,
    ProductsRouter,
    RulesRouter,
)
import logging
from logger import logger
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting FastAPI application...")
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
    app = FastAPI(lifespan=lifespan, middleware=middleware, debug=True)

    # Initialize api routers
    api_router = APIRouter(prefix=settings.API_PREFIX)
    user_router = UserRouter()
    file_router = FilesRouter(storage)
    masking_router = MaskingMapRouter()
    presets_router = PresetsRouter()
    products_router = ProductsRouter()
    rules_router = RulesRouter()

    api_router.include_router(user_router, tags=["users"])
    api_router.include_router(file_router, tags=["files"])
    api_router.include_router(masking_router, tags=["masking"])
    api_router.include_router(presets_router, tags=["presets"])
    api_router.include_router(products_router, tags=["products"])
    api_router.include_router(rules_router, tags=["rules"])
    app.include_router(api_router)
    return app
