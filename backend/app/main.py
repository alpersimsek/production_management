from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import Response
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

class LargeFileMiddleware:
    """Middleware to handle large file uploads by increasing request size limits."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Set maximum request size to 8GB + buffer
            scope["max_content_length"] = 9 * 1024 * 1024 * 1024  # 9GB limit
        
        await self.app(scope, receive, send)


def get_app():
    storage = FileStorage(settings.DATA_DIR)
    middleware = init_middlewares()
    app = FastAPI(
        lifespan=lifespan, 
        middleware=middleware, 
        debug=True,
        # Increase file upload limits for large files
        title="GDPR Tool API",
        description="API for GDPR compliance tool with support for large file uploads (up to 8GB)",
        version="1.0.0"
    )
    
    # Add middleware for large file uploads
    app.add_middleware(LargeFileMiddleware)

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
